# visprotocol

To get set up as a new user, you'll need to make two user-specific files:
1) A config.yaml file. Look under config/ to see examples. The file naming convention is [username]_config.yaml
    This defines the fly metadata you will be able to enter, the default file locations, and your rig configuration parameters.
    The first time you want to save protocol parameters, you'll have to make a directory at resources/username/parameter_presets to save the preset .yaml file in,  then you can commit and push as normal.

2) A protocol.py file. Look under protocol/ to see examples. The file naming convention is [username]_protocol.py.
    This [username] in the filename should match the filename of your config.yaml file, and the username field of the config.yaml should match this as well.
    This module should define your user-specific base parent class, which is a subclass of the clandinin_protocol.BaseProtocol.
    It should also define any protocol classes you would like.
    Finally, add your module to the import statement in protocol. _ init _ .py.
