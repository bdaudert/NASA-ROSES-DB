#!/usr/bin/env python

'''
Methods to query the daatstore from within appengine
using the ndb model
'''
import logging
import hashlib

# Needed to read data from datastore within app engine
from google.appengine.ext import ndb

# NOTE: this needs to agree with the setup in standalone population script
class DATA(ndb.Expando):
    feat_idx = ndb.IntegerProperty()
    region = ndb.StringProperty()
    year = ndb.IntegerProperty()
    dataset = ndb.StringProperty()
    et_model = ndb.StringProperty()
    variable = ndb.StringProperty()

class Query_Util(object):
    '''
    Methods to query the datastore from within appengine
    '''
    def __init__(self, region, year, dataset, et_model, variable):
        self.region = region
        self.year = int(year)
        self.et_model = et_model
        self.variable = variable

    def read_feat_data_from_db(self, feat_index_list):
        '''
        Reads multiple feature's data from db using unique indices
        :param feat_idx: feature index (db property)
        :return: dict of data for the feature
        '''
        # FIX ME: not tested
        feature_data = {
            'type': 'FeatureCollection',
            'features': []
        }
        for feat_idx in feat_index_list:
            unique_str = ('-').join([self.region, self.dataset, self.et_model, str(self.year), str(feat_idx)])
            UNIQUE_ID = hashlib.md5(unique_str).hexdigest()
            query_data = ndb.Key('DATA', UNIQUE_ID).get()
            if not query_data:
                continue
            featdata = {'properties': query_data.to_dict()}
            feature_data['features'].append(featdata)

        if not feature_data['features']:
            logging.error('NO FEATURE DATA IN DATABASE')
        else:
            logging.info('SUCCESSFULLY READ FEATURE DATA FROM DATABASE')
        return feature_data

    def read_data_from_db(self):
        '''
        Reads all features for region, year, dataset, et_model
        :return:  dict of data for the features
        '''

        all_data = {
            'type': 'FeatureCollection',
            'features': []
        }
        '''
        qry = ndb.Query(kind='DATA').filter(
            DATA.year == self.year,
            DATA.region == self.region,
            DATA.dataset == self.dataset,
            DATA.et_model == self.et_model
        )
        '''
        qry = DATA.query(
            DATA.region == self.region,
            DATA.year == int(self.year),
            DATA.dataset == self.dataset,
            DATA.et_model == self.et_model
        )
        query_data = qry.fetch()
        if len(query_data) > 0:
            all_data['features'] = [{'properties': q.to_dict()} for q in query_data]
            logging.info('SUCCESSFULLY READ DATA FROM DB')
        else:
            logging.error('NO DATA FOUND IN DB')
        return all_data