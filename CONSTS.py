import yaml


# This file hijacks the order in which Python parses the file in order to create user-configurable items.
class C(object):
    USERNAME = ''
    PASSWORD = ''

    ELASTICSEARCH_BASE_URL = ''

    ELASTICSEARCH_CREDENTIALS = None
    ELASTICSEARCH_USE_SSL = True
    ELASTICSEARCH_VERIFY_SSL = False

    # Below are items that the user should not be allowed to set via configuration file
    # This section only exists so IDEs won't complain about missing variables.
    NOTHING_YET = None


# This takes the contents of config.yaml and creds.yaml and updates the values in class C
for configuration_filename in ['config.yaml', 'creds.yaml']:
    _fin = open(configuration_filename, 'r')
    yams = _fin.read()
    _fin.close()
    yaml_config = yaml.load(yams, Loader=yaml.SafeLoader)
    for k, v in yaml_config.items():
        setattr(C, k, v)


# Finally, set the constant values where the user can no longer update them
C.NOTHING_YET = None
