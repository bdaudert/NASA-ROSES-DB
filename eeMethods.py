#!/usr/bin/env python

import os
import logging
import json
import urllib2
import hashlib

import ee
# Needed to store data to datastore from outside app engine
from google.cloud import datastore

from config import statics
# from config import GEO_BUCKET_NAME
from config import GEO_BUCKET_URL

import Utils

# Initialize ee
ee.Initialize()

# Set logging level
logging.basicConfig(level=logging.DEBUG)




class ET_Util(object):
    '''
    Computes ET statistics for all temporal resolutions
    Args:
        :region Unique ID of geojson obbject, e.g. USFields
        :geoFName geojson file name
        :year year of geojson dataset, might be ALL if not USFields
            USField geojsons change every year
        :dataset MODSI, Landsat or gridMET
        :et_model Evapotranspiration modfel, e.g. SIMS, SSEBop, METRIC
    '''
    def __init__(self, region, year, dataset, et_model):
        self.region = region
        self.geoFName = region + '_' + year + '.geojson'
        self.year = year
        self.dataset = dataset
        self.et_model = et_model
        self.missing_value = -9999
        self.geo_bucket_url = GEO_BUCKET_URL
        self.client = datastore.Client('open-et-1')

    def read_data_from_bucket(self):
        f = self.geo_bucket_url + self.geoFName
        contents = json.load(urllib2.urlopen(f))
        return contents

    def get_collection(self, t_res):
        '''
        Gets the ee collection (by name)
        :param dataset: MODIS or LANDSAT
        :param model: et model: SSEBop, SIMS, METRIC etc
        :return: ee.ImageCollection
        '''
        ds = self.dataset
        m = self.et_model
        coll_name = statics['ee_coll_name'][ds][m][t_res]
        logging.info('EE CALL: ee.ImageCollection({})'.format(coll_name))
        coll = ee.ImageCollection(coll_name)
        return coll

    def filter_coll_by_dates(self, coll, dS_str, dE_str):
        '''
        Gets the ee collection (by nameand tem_res)
        and filters by variable and start/end dates

        :param coll ee.ImageCollection
        :param variable:
            "et": "Actual ET",
            "etrf": "Fractional ET",
            "etr": "Reference ET",
            "pr": "Precipitation"
        :param dS_str start date, format yyyy-mm-dd
        :param dE_str end date, format yyyy-mm-dd
        :return: ee.ImageCollection filtered by variable and dates
        '''
        dS_obj = ee.Date(dS_str, 'GMT')
        dE_obj = ee.Date(dE_str, 'GMT')
        # logging.debug('EE CALL: collection.filterDate({}, {})'
        #              .format(dS_str, dE_str))
        f_coll = coll.map(lambda x: x.double())\
            .filterDate(dS_obj, dE_obj.advance(1, 'day'))
        return f_coll

    def filter_coll_by_var(self, coll, variable):
        '''
        Gets the ee collection (by nameand tem_res)
        and filters by variable and start/end dates

        :param coll ee.ImageCollection
        :param variable:
            "et": "Actual ET",
            "etrf": "Fractional ET",
            "etr": "Reference ET",
            "pr": "Precipitation"
        :return: ee.ImageCollection filtered by variable
        '''
        # logging.debug('EE CALL: collection.select({})'.format(variable))
        return coll.select([variable], [variable])

    def reduce_collection_to_img(self, coll, stat):
        '''
        Reduces the ee.ImageCollection to a single ee image by applying
        the statistic stat

        :param coll ee.ImageCollection
        :param stat statistic: max, min, mean, median
        :return: ee.Image
        '''

        if stat == 'Median':
            img = coll.median()
        elif stat == 'Mean':
            img = coll.mean()
        elif stat == 'Max':
            img = coll.max()
        elif stat == 'Min':
            img = coll.min()
        elif stat == 'Total':
            img = coll.sum()
        else:
            img = coll.mean()
        return img

    def set_geo_properties(self, geo_props):
        '''
        Populates metadata from the geo properties
        Defined in the geojson data file
        '''
        props = {}
        for prop in statics['geo_meta_cols']:
            if prop in geo_props.keys():
                props[prop] = geo_props[prop]
        return props

    def compute_et_stats(self, coll, var, geom, t_res):
        def average_over_region(img):
            '''
            Averages the ee.Image over all pixels of ee.Geometry
            '''
            reduced_image_data = img.reduceRegion(
                ee.Reducer.mean(),
                geometry=geom,
                scale=1000,
                tileScale=1,
                crs='EPSG:4326',
                crsTransform=None,
                bestEffort=True
            )
            return ee.Feature(None, reduced_image_data)

        et_data = {}
        imgs = []
        # logging.info('PROCESSING VARIABLE ' + str(v))
        stat_names = statics['stats_by_var_res'][var][t_res]
        for stat_name in stat_names:
            # logging.info('PROCESSING STATISTIC ' + str(stat_name))
            res = stat_name.split('_')[1]
            # Filer collection by date
            dS_str = str(self.year) + '-' +\
                statics['start_end_mon_days_by_res'][res][0]
            dE_str = str(self.year) + '-' +\
                statics['start_end_mon_days_by_res'][res][1]
            coll_t = self.filter_coll_by_dates(coll, dS_str, dE_str)
            temporal_stat = statics['t_stat_by_var']
            img = self.reduce_collection_to_img(coll_t, temporal_stat)
            # feats = ee.FeatureCollection(average_over_region(img))
            imgs.append(img)
        ee_imgs = ee.ImageCollection(imgs)
        feats = ee.FeatureCollection(ee_imgs.map(average_over_region))

        try:
            f_data = feats.getInfo()
        except Exception as e:
            f_data = {'features': []}
            logging.error(e)

        for stat_idx, stat in enumerate(stat_names):
            if 'features' not in f_data.keys() or not f_data['features']:
                et_data[stat] = -9999
                continue
            try:
                feat = f_data['features'][stat_idx]
            except:
                et_data[stat] = -9999
                continue

            if 'properties' not in feat.keys():
                et_data[stat] = -9999
                continue
            try:
                val = feat['properties'][var]
                et_data[stat] = round(val, 4)
            except:
                et_data[stat] = -9999
                continue
        return et_data

    def set_db_data_entity(self, UNIQUE_ID, et_data):
        '''
        sets up datastore client and datastore entity
        Args:
            UNIQUE_ID,: unique identity of the feature, used to define the db key
            et_data: dictionary of et_data
        Returns:
            datstore entitity
        '''
        # Instantiates a client
        db_key = self.client.key('DATA', UNIQUE_ID,)
        entity = datastore.Entity(key=db_key)
        entity.update({
            'region': self.region,
            'year': int(self.year),
            'dataset': self.dataset,
            'et_model': self.et_model
        })
        for key, val in et_data.iteritems():
            entity.update({
                key: val
            })
        return entity

    def set_db_meta_entity(self, UNIQUE_ID, geo_props):
        '''
        sets up datastore client and datastore entity
        Args:
            UNIQUE_ID,: unique identity of the feature, used to define the db key
            geo_props: properties of the geometry feature
        Returns:
            datstore entitity
        '''
        # Instantiates a client

        db_key = self.client.key('METADATA', UNIQUE_ID)
        entity = datastore.Entity(key=db_key)
        entity.update({
            'region': self.region,
            'year': int(self.year),
            'dataset': self.dataset,
            'et_model': self.et_model
        })
        for key, val in geo_props.iteritems():
            entity.update({
                key: val
            })
        return entity

    def add_to_db(self, entity_list):
        '''
        Adds multiple data to datastore via the datastore client
        NOTES:
            can be run outside of app engine
            we can only add 500 entries to bd at a time
        '''
        ent_len = len(entity_list)
        num_chunks = ent_len / 500
        if ent_len % 500 != 0:
            end_chunk_len = ent_len % 500
            num_chunks += 1
        num_added = 0
        count = 0
        while num_added < ent_len:
            count +=1
            logging.info('ADDING CHUNK {0} of {1}'.format(str(count), str(num_chunks)))
            start =  num_added
            end = start + 500
            if end > ent_len:
                end = start + end_chunk_len
            ents_to_add = entity_list[start:end]
            self.client.put_multi(ents_to_add)
            num_added = end


    def get_data_and_set_db_identities(self):
        '''
        Gets geo features from geojson file
        and computes the et stats for all variables
        and temporal resolutions
        '''
        # FIX ME: add more vars as data comes online
        # MODIS SSEBop only has et right now
        t_res_list = statics['all_t_res']
        var_list = ['et']

        # Get the colllections so we don't have to do it for each feature
        colls = {}
        for t_res in t_res_list:
            coll = self.get_collection(t_res)
            for var in var_list:
                coll = self.filter_coll_by_var(coll, var)
                colls[t_res + '_' + var] = coll

        geo_data = self.read_data_from_bucket()
        if 'features' not in geo_data.keys():
            logging.error('NO DATA FOUND IN BUCKET, FILE: ' + self.geoFName)

        meta_entities = []
        data_entities = []
        # for f_idx, geo_feat in enumerate(geo_data['features'][0:1]):
        for f_idx, geo_feat in enumerate(geo_data['features']):
            geom_coords = geo_feat['geometry']['coordinates']
            geom_coords = [Utils.orient_poly_ccw(c) for c in geom_coords]
            geom = ee.Geometry.Polygon(geom_coords)
            geo_props = self.set_geo_properties(geo_feat['properties'])
            '''
            Create a UNIQUE_ID for the geo feature
            This ID will be used in both METADATA and DATA entities
            '''
            unique_str = ('-').join([self.region, self.dataset, self.et_model, self.year, str(f_idx)])
            UNIQUE_ID = hashlib.md5(unique_str).hexdigest()
            meta_entities.append(self.set_db_meta_entity(UNIQUE_ID, geo_props))
            et_data = {}
            for t_res in t_res_list:
                for var in var_list:
                    coll = colls[t_res + '_' + var]
                    et_data.update(self.compute_et_stats(coll, var, geom, t_res))
            data_entities.append(self.set_db_data_entity(UNIQUE_ID, et_data))
        return meta_entities, data_entities

