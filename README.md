# NASA ROSES DATASTORE

Code repository for the NASA ROSES DATASTORE API. 
The NASA ROSES project is under development by the Desert Research Institute, NASA for NOAA
### Links & Resources

You can find the most up-to-date deployments [here](http://open-et-1.appspot.com/).

- [Earth Engine Documentation](https://sites.google.com/site/earthengineapidocs/)
- [Earth Engine Access Library](https://code.google.com/p/earthengine-api/wiki/Installation)
- [Earth Engine Playground](https://code.earthengine.google.com/)
- [Google Cloud Platform](https://cloud.google.com/appengine/docs/python/gettingstartedpython27/helloworld)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)

### Installing & Running Google Earth Engine Python API
- Links:
    - https://docs.google.com/document/d/1tvkSGb-49YlSqW3AGknr7T_xoRB1KngCD3f2uiwOS3Q/edit
- Installation
    To create the "nasa-roses-datastore" conda environment, execute the following:
    ```
    conda remove --name nasa-roses-datastore --all
    conda create --name nasa-roses-datastore python=2.7
    ```

    To activate the "nasa-roses-datastore" environement on MacOS:
    ```
    source activate nasa-roses-datastore
    ```
    To activate the "nasa-roses-datastore" environment on Windows:
    ```
    activate nasa-roses-datastore
    ```

    To install the necessary Python modules:
    ```
    conda install numpy=1.6.2=py27_4 oauth2client httplib2 cryptography pyOpenSSL cffi
    
    pip install earthengine-api
    
    pip install --no-cache-dir --only-binary :all: grpcio==1.10.1
    
    pip install --upgrade google-cloud
    ```
    
- Copy the privatekey.json that you generated at [https://console.cloud.google.com]
  into the project directory
    
- Set Developer information in the config.py file:
    ```
    EE_ACCOUNT = 'xxxx.gserviceaccount.com'
    EE_PRIVATE_KEY_FILE = 'privatekey.json'
    ```

- Testing installation and authentication:
    ```
    python
    import config
    import ee
    ee.Initialize(ee.ServiceAccountCredentials(config.EE_ACCOUNT, config.EE_PRIVATE_KEY_FILE))
    print(ee.Image('srtm90_v4').getThumbUrl())"
    ```

- To populate the DATASTORE or the nasa-roses-datastore repo
    ```
    source acticate nasa-rose-db
    cd nasa-roses-datastore
    ```
    - Set the account and credential info in config.py
    ```
    EE_ACCOUNT = '@nasa-roses-datastore.iam.gserviceaccount.com'
    # The private key associated with your service account in JSON format.
    EE_PRIVATE_KEY_FILE = 'nasa-roses-datastore.json'
    EE_CREDENTIALS = ee.ServiceAccountCredentials(EE_ACCOUNT, EE_PRIVATE_KEY_FILE)
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'nasa-roses-datastore.json'
    ```

    - run the statndalone population script
    ```
    python ET_starts_cron.py
    ```

   
### Repository Organization:

### NOTES
