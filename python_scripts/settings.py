"""Provide environment settings for app"""
import os
from google.cloud import datastore


class Settings():
    """
    Singleton Class to manage environment settings.
    This will only instantiate a storage client when needed, then reuse it for future requests.
    Usage:

    from settings import Settings
    value = Settings.get_setting('ENV_VAR')

    # You can also use it passing a default value
    value = Settings.get_setting('ENV_VAR', 'default value')
    """

    _project = os.getenv('GOOGLE_CLOUD_PROJECT', os.getenv('GC_PROJ', default=None))
    _ds_values = {}

    @staticmethod
    def get_setting(name, default=None):
        """Get a given setting"""

        if not name:
            raise ValueError('Setting name must not be empty')

        if Settings._project and not Settings._ds_values:
            ds_client = datastore.Client()
            key = ds_client.key('AE_ENV', 'API')
            print(key)
            Settings._ds_values = ds_client.get(key)
            print(Settings._ds_values)

        return os.getenv(name, Settings._ds_values.get(name, default))
