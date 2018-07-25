# !/usr/bin/env python

import logging
from datetime import datetime

import eeMethods
from config import statics

###################################################
# M A I N
###################################################
if __name__ == "__main__":
    startTime = datetime.now()
    print startTime
    # for region in ['US_states_west_500k', 'US_counties_west_500k', 'Mason']:
    for region in ['US_states_west_500k']:
        if region == 'Mason':
            # Compute ee stats in EE
            comp = True
        else:
            # use fake data on localhost
            comp = False
        for ds in ['MODIS']:
            yr_range = statics['all_years'][ds]
            for et_model in ['SSEBop']:
                # for yr in range(int(yr_range[0]), int(yr_range[1])):
                for yr in range(int(yr_range[0]), int(yr_range[0]) + 1):
                    year = str(yr)
                    msg = 'PROCESSING Region/Year/Dataset/Model ' + region + '/' + year + '/' + ds + '/' + et_model
                    logging.info(msg)
                    ET_helper = eeMethods.ET_Util(region, year, ds, et_model)
                    data_entities, meta_entities = ET_helper.get_data_and_set_db_entities(compute=comp)
                    ET_helper.add_to_db(data_entities)
                    ET_helper.add_to_db(meta_entities)
    print datetime.now() - startTime


