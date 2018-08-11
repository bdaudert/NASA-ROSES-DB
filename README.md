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
    To create the "nasa-roses-datastore" conda environment in the appengine standard environment, execute the following:
    ```
    conda remove --name nasa-roses-datastore --all
    conda create --name nasa-roses-datastore python=2.7
    ```

    To activate the "nasa-roses-datastore" environement
    - MacOS:
    ```
    source activate nasa-roses-datastore
    ```
    - Windows:
    ```
    activate nasa-roses-datastore
    ```

    To install the necessary Python modules:
    ```
    conda install numpy=1.6.2=py27_4 oauth2client httplib2 cryptography pyOpenSSL cffi
    
    pip install earthengine-api
    ```

    To run the standalone datastore population script for populating the local DATASTOR
    ```
    pip install --no-cache-dir --only-binary :all: grpcio==1.10.1
    
    pip install --upgrade google-cloud

    pip install --upgrade google-cloud-datastore
    ```
    Create the requirements.txt file.
    At a minimum the requirements.txt file should look like this
    ```
    earthengine-api >= 0.1.100
    httplib2
    Jinja2 == 2.6
    numpy == 1.6.2
    oauth2client
    six
    ```
    The following command will install the the external Python modules listed in the requirements.txt file into the lib folder for upload to AppEngine.
    ```
    pip install -r requirements.txt -t lib
 

- Copy the privatekey.json that you generated at [https://console.cloud.google.com]
  into the project directory
    
- Set Developer information in the config.py file:
    ```
    EE_ACCOUNT = 'xxxx.gserviceaccount.com'
    EE_PRIVATE_KEY_FILE = 'privatekey.json'
    ```
    iIn config.py you will also need to tell app engine to add the lib folder to the third party libraries as follows:
    ```
    from google.appengine.ext import vendor
    # Add any libraries install in the "lib" folder.
    vendor.add('lib')
    ```

- Testing installation and authentication:
    ```
    python
    import config
    import ee
    ee.Initialize(ee.ServiceAccountCredentials(config.EE_ACCOUNT, config.EE_PRIVATE_KEY_FILE))
    print(ee.Image('srtm90_v4').getThumbUrl())
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

   
### Repository Organization:
- Coming soon!

After initializing and activating the conda environment, the development server can be started from within the project folder.  The port only needs to be specificied if not using the default value of 8080.

```
dev_appserver.py --port 8080 app.yaml
```
To run in debugging mode:
```
dev_appserver.py --port 8080 --log_level=debug app.yaml
```
To run in debugging mode with a default bucket set:
```
dev_appserver.py --port 8080 --log_level=debug app.yaml --default_gcs_bucket_name <bucket name>
```
The app can be then be deployed from within the project folder (the project and version flags may not be necessary).
```
gcloud app deploy --project nasa-roses-datastore --version 1
```

To update the cron or queue information, these must be explicitly listed in the DEPLOYABLES section of the gcloud call (see: https://cloud.google.com/sdk/gcloud/reference/app/deploy).

```
gcloud app deploy app.yaml cron.yaml --project nasa-roses-datastore --version 1
```

To update GCloud:
```
gcloud components update
```

