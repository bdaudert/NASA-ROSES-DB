# !/usr/bin/env python
import sys
from datetime import datetime

sys.path.append("/Users/bdaudert/EE/nasa-roses-datastore")

import database_methods

###################################################
# M A I N
###################################################
if __name__ == "__main__":
    startTime = datetime.now()
    print(startTime)
    for region in ['US_states_west_500k', 'US_counties_west_500k', 'Mason']:
        # for region in ['US_states_west_500k']:
        if region == 'Mason':
            # Compute ee stats in EE
            comp = True
        else:
            # use fake data on localhost
            comp = False
        for ds in ['MODIS']:
            database_methods.populate_datastore(region, ds, et_model, compute=comp)
    print(datetime.now() - startTime)


