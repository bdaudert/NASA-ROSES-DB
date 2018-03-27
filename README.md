# NASA ROSES DB

Code repository for the NASA ROSES database code. The NASA ROSES project is under development by the Desert Research Institute, NASA for NOAA
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
    To create the "roses-db" conda environment, execute the following:
    ```
    conda remove --name roses-db --all
    conda create --name roses-db python=2.7
    ```

    To activate the "roses-db" environement on MacOS:
    ```
    source activate roses-db
    ```
    To activate the "roses-db" environment on Windows:
    ```
    activate roses-db
    ```

    To install the necessary Python modules:
    ```
    conda install numpy=1.6.2=py27_4 oauth2client httplib2 cryptography pyOpenSSL cffi
    
    pip install earthengine-api
    
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


   
### Repository Organization:

### NOTES
- Metadata (feature coordinates etc. ) are safed separately from the actual ET data 
- OBJECTID should be unique for each geometry feature
- Each feature will be saved separately
- The ET data for each feature will be saved separately
- OBJECTID will be used to query that database
