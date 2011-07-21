"""
Provides a static lookup table for command names

Provides lookup tables for triggers and commands and facilities for loading and
reloading of bot modules.
"""

import modules.lib.botconfig as botconfig
import re
import sys

def load_modules():
    """Used for reloading of imported modules"""
    
    # A note about implementation:
    # Each module file must contain a BotModule object with the same name as the
    # name of the module. We call on that object's install method, passing it
    # the table handlers. By default, the object will just append its command
    # tables to the tables within the handlers. BotModule can be subclassed,
    # however, and the install() method overridden for dynamic registration
    # of triggers and commands, etc. 
    
    global modules
    
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
            
            # we rely on the module containing a variable with the same name
            # as the name of the module
            bot_module = getattr(module, name.rsplit('.', 1)[1])
            bot_module.install(ctable, help, triggers)
            
            modules.append(module)
        except ImportError:
            # something fudged up on import
            print "Error when importing {0}, module not loaded.".format(name)
            raise
        except (AttributeError, TypeError):
            # module is something other than a proper bot module
            print "Error when importing {0}: invalid module.".format(name)
            raise

def reload_modules():
    """
    Attempts to reload modules & config
    """
    global modules
    global config
    
    reload(botconfig)  

    config = botconfig.config  
    # I dread considering whether or not this is thread-safe 
    for module in modules:
        reload(module)
 
    load_modules()

class TableHandler:
    """
    Base class for the handlers
    """
    
    def __init__(self, table=None):
        if not table: 
            table = {}
        self.table = table
    
    def register_entry(self, content):
        """
        Registers a new command or dictionary of commands
        """
        if type(content) is tuple and len(content) == 2:
            self.table[content[0]] = content[1]
        else:
            self.table.update(content)
        
    def deregister_entry(self, command):
        """
        Removes a specific command
        """
        if command in self.table:
            del self.table[command]

# we keep our own list of imported modules for later reloading
modules = []
ctable = TableHandler()
help = TableHandler()   # note that help is as of yet unimplemented
triggers = TableHandler()

# for reloads, we did not do from...import
config = botconfig.config

load_modules()

