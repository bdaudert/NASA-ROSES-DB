#!/usr/bin/env python

import os
import logging
import json
import urllib2
import hashlib

import ee
# Needed to add data to datastore from outside app engine
from google.cloud import datastore

import config
import Utils


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
        self.year = year
        if self.region in ['Mason', 'US_fields']:
            self.geoFName = region + '_' + year + '_GEOM.geojson'
        else:
            self.geoFName = region + '_GEOM.geojson'
        self.dataset = dataset
        self.et_model = et_model
        self.missing_value = -9999
        self.geo_bucket_url = config.GEO_BUCKET_URL
        # Needed to add data to datastore from outside app engine
        self.client = datastore.Client(config.PROJECT_ID)

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
        coll_name = config.statics['ee_coll_name'][ds][m][t_res]
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

    def set_meta_properties(self, geo_props, geom):
        '''
        Populates metadata from the geo properties
        Defined in the geojson data file
        '''
        props = {}
        for prop in config.statics['geo_meta_cols'][self.region]:
            if prop in geo_props.keys():
                props[prop] = geo_props[prop]
        return props

    def compute_et_stats(self, coll, var, geom):
        '''
        Computes annual, seasonal (April - Sept) and monthly et stats
        :param coll:
        :param var:
        :param geom:
        :return:
        '''
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

        etdata = {}
        imgs = []
        for res in config.statics['start_end_mon_days_by_res'].keys():
            # logging.info('PROCESSING STATISTIC ' + res)
            # Filer collection by date
            dS_str = str(self.year) + '-' +\
                config.statics['start_end_mon_days_by_res'][res][0]
            dE_str = str(self.year) + '-' +\
                config.statics['start_end_mon_days_by_res'][res][1]
            coll_t = self.filter_coll_by_dates(coll, dS_str, dE_str)
            temporal_stat = config.statics['t_stat_by_var'][var]
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

        for res_idx, res in enumerate(config.statics['start_end_mon_days_by_res'].keys()):
            if 'features' not in f_data.keys() or not f_data['features']:
                etdata['data_' + res] = -9999
                continue
            try:
                feat = f_data['features'][res_idx]
            except:
                etdata['data_' + res] = -9999
                continue

            if 'properties' not in feat.keys():
                etdata['data_' + res] = -9999
                continue
            try:
                val = feat['properties'][var + '_' + res]
                etdata['data_' + res] = round(val, 4)
            except:
                etdata['data_' + res] = -9999
                continue
        return etdata

    def set_db_data_entity(self, UNIQUE_ID, feat_idx, etdata, var):
        '''
        sets up datastore client and datastore entity belonging to DATA
        Args:
            UNIQUE_ID,: unique identity of the feature, used to define the db key
            f_idx: feature index, need this to query for multiple features
            etdata: dictionary of etdata
        Returns:
            datstore entitity
        '''
        # Instantiates a client and the datastore kind DATA
        db_key = self.client.key('DATA', UNIQUE_ID,)
        entity = datastore.Entity(key=db_key)
        entity.update({
            'feat_idx': feat_idx,
            'region': self.region,
            'year': int(self.year),
            'dataset': self.dataset,
            'et_model': self.et_model,
            'variable': var
        })
        # Set the etdata
        for key, val in etdata.iteritems():
            entity.update({
                key: val
            })
        return entity

    def set_db_metadata_entity(self, UNIQUE_ID, feat_idx, meta_props):
        '''
        sets up datastore client and datastore entity belonging to METADATA
        Args:
            UNIQUE_ID,: unique identity of the feature, used to define the db key
            f_idx: feature index, need this to query for multiple features
            etdata: dictionary of etdata
        Returns:
            datstore entitity
        '''
        # Instantiates a client and the datastore kind DATA

        db_key = self.client.key('METADATA', UNIQUE_ID, )
        entity = datastore.Entity(key=db_key)
        entity.update({
            'feat_idx': feat_idx,
            'region': self.region,
            'year': int(self.year)
        })
        # Set the metadata
        for key, val in meta_props.iteritems():
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

    def get_data_and_set_db_entities(self, compute=True):
        '''
        Gets geo features from geojson file
        and computes the et stats for all variables
        and temporal resolutions

        if compute is True, we compute the et stats in EE
        if compute is False, we read the et data from a local
        data file (et data was provided in the data file)
        '''
        # FIX ME: add more vars as data comes online
        # MODIS SSEBop only has et right now
        t_res_list = config.statics['all_t_res']
        var_list = ['et']
        # Read the geo data from the bucket
        geo_data = self.read_data_from_bucket()
        if 'features' not in geo_data.keys():
            logging.error('NO DATA FOUND IN BUCKET, FILE: ' + self.geoFName)

        data_entities = []
        meta_entities = []
        if not compute:
            # Get the etdata from the local file
            fl = config.LOCAL_DATA_DIR + self.et_model + '/' + self.region + '_' + self.year + '_DATA.json'
            with open(fl) as f:
                j_data = json.load(f)
                local_etdata = j_data['features']
        else:
            # Get the colllections so we don't have to do it for each feature
            colls = {}
            for t_res in t_res_list:
                coll = self.get_collection(t_res)
                for var in var_list:
                    coll = self.filter_coll_by_var(coll, var)
                    colls[t_res + '_' + var] = coll
        for f_idx, geo_feat in enumerate(geo_data['features']):
            feat_coords = geo_feat['geometry']['coordinates']
            if geo_feat['geometry']['type'] == 'MultiPolygon':
                geom_coords = Utils.orient_polygons_ccw(feat_coords)
                geom = ee.Geometry.MultiPolygon(geom_coords)
            elif geo_feat['geometry']['type'] == 'Polygon':
                geom_coords = [Utils.orient_polygon_ccw(c) for c in feat_coords]
                geom = ee.Geometry.Polygon(geom_coords)
            else:
                continue
            # Add metadata to METADATA Datastore entity
            meta_props = self.set_meta_properties(geo_feat['properties'], geo_feat['geometry'])
            unique_meta_str = ('-').join([self.region, self.year, str(f_idx)])
            UNIQUE_META_ID = hashlib.md5(unique_meta_str).hexdigest()
            meta_entities.append(self.set_db_metadata_entity(UNIQUE_META_ID, str(f_idx), meta_props))
            for var in var_list:
                unique_str = ('-').join([self.region, self.dataset, self.et_model, self.year, var, str(f_idx)])
                UNIQUE_ID = hashlib.md5(unique_str).hexdigest()
                if compute:
                    etdata = self.compute_et_stats(coll, var, geom)
                else:
                    etdata = {}
                    for res in config.statics['start_end_mon_days_by_res'].keys():
                        etdata_key = var + '_' + res
                        new_key = 'data_' + res
                        try:
                            etdata[new_key] = local_etdata[f_idx]['properties'][etdata_key]
                        except:
                            etdata[new_key] = -9999
                data_entities.append(self.set_db_data_entity(UNIQUE_ID, f_idx, etdata, var))
        return data_entities, meta_entities

