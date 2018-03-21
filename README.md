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
    To create the "ee-python" conda environment, execute the following:
    ```
    conda remove --name ee-python --all
    conda create --name ee-python python=2.7
    ```

    To activate the "ee-python" environement on MacOS:
    ```
    source activate ee-python
    ```
    To activate the "ee-python" environment on Windows:
    ```
    activate ee-python
    ```

    To install the necessary external Python modules:
    ```
    conda install numpy=1.6.2=py27_4 oauth2client httplib2 cryptography pyOpenSSL cffi
    pip install earthengine-api
    ```

    The following command will install the the external Python modules listed in the requirements.txt file into the lib folder for upload to AppEngine.
    ```
    pip install -r requirements.txt -t lib
    ```
    You will need to tell app engine to add the lib folder to the third party libraries as follows:
    ```
    # appengine_config.py
    from google.appengine.ext import vendor

    # Add any libraries install in the "lib" folder.
    vendor.add('lib')
    ```


    Make symbolic link to private key:
        - `ln -s ~/.keys/privatekey.pem`
    Set Developer information:
        - `x@developer.gserviceaccount.com` in config.py

- Testing installation and authentication:

    `python -c "import ee; print ee.__version__"`

    `python -c "import os; import ee; MY_SERVICE_ACCOUNT = os.environ.get('MY_SERVICE_ACCOUNT'); MY_PRIVATE_KEY_FILE = os.environ.get('MY_PRIVATE_KEY_FILE'); ee.Initialize(ee.ServiceAccountCredentials(MY_SERVICE_ACCOUNT, MY_PRIVATE_KEY_FILE)); print(ee.Image('srtm90_v4').getThumbUrl())"`

- Configuring App Engine to use the conda Environment:
    Install Google App Engine for Python and clone Earth Engine API repository.
    `~/Development/google_appengine/dev_appserver.py .`

### Repository Organization:

