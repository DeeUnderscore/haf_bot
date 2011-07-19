"""
Handles parsing of the config file
"""

import ConfigParser

config = ConfigParser.SafeConfigParser()

try:
    cfg_file = open("cfg/config.cfg", "r")
    config.readfp(cfg_file)
except IOError:
    print "Cannot open config file."
    raise