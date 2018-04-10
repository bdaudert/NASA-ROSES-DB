# !/usr/bin/env python

import logging
from datetime import datetime

import eeMethods


###################################################
# M A I N
###################################################
if __name__ == "__main__":
    startTime = datetime.now()
    print startTime
    for region in ['Mason']:
        region_data = []
        for year in ['2003']:
            msg = 'PROCESSING Region/Year ' + region + '/' + year
            logging.info(msg)
            for ds in ['MODIS']:
                for et_model in ['SSEBop']:
                    msg = 'PROCESSING Dataset/et_model ' + ds + '/' + et_model
                    logging.info(msg)
                    ET_helper = \
                        eeMethods.ET_Util(region, year, ds, et_model)
                    meta_entities, data_entities = \
                        ET_helper.get_data_and_set_db_identities()
                    ET_helper.add_to_db(meta_entities)
                    ET_helper.add_to_db(data_entities)
    print datetime.now() - startTime


