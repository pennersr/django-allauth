import warnings

warnings.warn("The 'dropbox_oauth2' provider is deprecated "
              "and will no longer work after September 28, 2017 when "
              "the Dropbox v1 API and URL endpoints are removed. "
              "Upgrade to the 'dropbox' provider which has been updated "
              "to use OAuth2 and the Dropbox v2 API.", DeprecationWarning)
