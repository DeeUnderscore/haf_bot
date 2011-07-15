

class BotModule:
    
    def __init__(self, commands={}, help={}):
        # contains pairs of help topics and help strings for the module. They will
        # be appended to global help
        self.help = help
        # contains key-value pairs of commands and their respective functions. This
        # is the main way that commands are loaded
        self.commands = commands