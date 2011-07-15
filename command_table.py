"""
Provides a static lookup table for command names

Since command names have to adhere to python naming rules, this variable is 
provided so that we can use arbitrary strings for commands in the actual
irc channel.
"""

import modules.lib.botconfig as botconfig
import re
import sys

# we keep our own list of imported modules for later reloading
modules = []
table = {}
help = {}
globvar = "Global"
# for reloads, we did not do from...import
config = botconfig.config

def load_modules():
    """Used for reloading of imported modules"""
    
    # A note about implementation:
    # Since the way that bot.py is designed to use global functions, we use the
    # module objects as a way of storing references to those functions (instead
    # of having them be class functions). Perhaps at a later date, the bot could
    # be rewritten to use subclasses that contain methods for a more oopish approach
    
    global modules
    global table
    global help
    
    module_names = config.get("bot", "load_modules")
    # this could be done nicer but it works if the config file is valid
    module_names = re.split("[,\s]+", module_names)
    module_names = [("modules." + module_name) for module_name in module_names]
    
    for name in module_names:
        try:
        	# here, __import__ will only load the top level module
        	# (ie, modules/__init__). We discard that
            __import__(name)
            
            # we then get a reference to the freshly loaded module by 
            # looking it up in sys.modules
            module = sys.modules[name]
            
            # This again is somewhat hacky as it relies on bot_modules
            # being present in the python module.
            for bot_module in module.bot_modules:  
                table.update(bot_module.commands)
                help.update(bot_module.help)         
            modules.append(module)
        except ImportError:
            # something fudged up on import
            print "Error when importing {0}, module not loaded.".format(name)
            raise
        except (AttributeError, TypeError):
            # module is something other than a proper bot module
            print "Error when importing {0}: invalid module.".format(name)

def reload_modules():
    """
    Attempts to reload modules & config
    """
    global modules
    global table
    global help
    global config
    
    reload(botconfig)  

    config = botconfig.config  
    # I dread considering whether or not this is thread-safe 
    for module in modules:
        reload(module)
 
    table = {}
    help = {}
    load_modules()


load_modules()
