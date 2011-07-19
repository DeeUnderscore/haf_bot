class BotModule:
    def __init__(self, commands={}, help={}, triggers={}):
        # contains pairs of help topics and help strings for the module. They will
        # be appended to global help
        self.help = help
        
        # contains key-value pairs of commands and their respective functions. This
        # is the main way that commands are loaded
        self.commands = commands
        
        # contains key-value pairs of triggers. The key is only used as an
        # unique identifier. The value is a tuple of a compiled regex used to 
        # find matches and a function to apply to the irc message when a 
        # match is found 
        print triggers
        self.triggers = triggers
        
        self.active = False
        
    def install(self, command_handler, help_handler, trigger_handler):
        self.command_handler = command_handler
        self.command_handler.register_entry(self.commands)
        
        self.help_handler = help_handler
        self.help_handler.register_entry(self.help)
        
        self.trigger_handler = trigger_handler
        self.trigger_handler.register_entry(self.triggers)
        
        self.active = True
    
    def uninstall(self):
        # step through all commands and deregister every one
        for command in self.commands.keys():
            self.command_handler.deregister_entry(command)
        
        for help in self.help.keys():
            self.help_handler.deregister_entry(help)
            
        for trigger in self.triggers.keys():
            self.trigger_handler.deregister_entry(trigger)
            
        self.active = False 