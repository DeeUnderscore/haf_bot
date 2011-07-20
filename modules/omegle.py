import BotModule
import lib.omegle as libomegle
import re

class OmegleModule(BotModule.BotModule):
    """
    Class for handling dyamic registration of Omegle bot commands and triggers.
    
    Limitation: it can only handle one-channel bots.
    """
    
    def __init__(self):
        start_command = {"omegle": self.omegle_start}
        BotModule.BotModule.__init__(self, commands=start_command)
        self.running = False
    
    def omegle_start(self, bot, user, channel, args):
        """
        Starts the omegle bot
        """
        if self.running:
            # This should never be reached
            bot.msg(channel, "Omegle bot already running.")
            return
            
        if "p" in args:
            bot.msg(channel, "Omegle bot starting in PROMISCUOUS mode. Everything said in channel will be sent to Omegle. (commands: o.next, o.stop)")
            self.promiscuous = True
        else:
            bot.msg(channel, "Omegle bot starting in EXPLICIT mode. To send to omegle, use '!o <message>'. (commands: o.next, o.stop)")
            self.promiscuous = False
            
        self.command_handler.deregister_entry("omegle")
        self.handler = HafHandler(bot, channel, self)
        self.spawn_chat()
            
    def spawn_chat(self):
        """
        Spawns a new chat object and fires it.
        """
        self.omegle_bot = libomegle.OmegleChat() 
        self.omegle_bot.connect_events(self.handler)
        self.command_handler.register_entry({"o.next": self.omegle_next,
                                             "o.stop": self.omegle_stop})
        if self.promiscuous:
            everything = re.compile(".*")
            self.trigger_handler.register_entry({"omegle_trigger": (everything, self.promiscuous_trigger)})
            self.promiscuous = True
        else:
            self.command_handler.register_entry({"o": self.omegle_send})
            
        self.running = True
        self.omegle_bot.connect(True)
            
    def clean_up(self):
        """
        Cleans up after itself
        """
        if self.promiscuous:
            self.trigger_handler.deregister_entry("omegle_trigger")
        else:
            self.command_handler.deregister_entry("o")
        
        self.command_handler.deregister_entry("o.next")
        self.command_handler.deregister_entry("o.stop")
        self.running = False
        self.command_handler.register_entry({"omegle": self.omegle_start})
        
    def promiscuous_trigger(self, bot, user, channel, msg, match):
        """
        When active, sends everything from the channel to omegle
        """
        user = user.split("!", 1)[0]
        if user != bot.nickname and not msg.startswith("!"):
            self.omegle_bot.say(msg)
        
    def omegle_send(self, bot, user, channel, args):
        """
        In explicit mode, this command sends to omegle
        """
        self.omegle_bot.say(args)
        
    def omegle_next(self, bot, user, channel, args):
        """
        Disconnects from current session and requests a new one
        """
        self.omegle_bot.disconnect()
        self.omegle_bot.waitForTerminate()
        bot.msg(channel, "[omegle] Disconnected, attempting reconnect.")
        self.spawn_chat()
        
    def omegle_stop(self, bot, user, channel, args):
        """
        Stops current omegle session.
        """
        self.omegle_bot.disconnect()
        self.omegle_bot.waitForTerminate()
        bot.msg(channel, "[omegle] Disconnected.")
        self.clean_up()
        
        
class HafHandler(libomegle.EventHandler):
    """
    Base omegle event handler for the irc bot
    """
    def __init__(self, bot, channel, module):
        self.bot = bot
        self.channel = channel
        self.module = module
    
    def connected(self, chat, var):
        self.bot.msg(self.channel, "[omegle] Connected.")
        
    def gotMessage(self,chat,message):
        self.bot.msg(self.channel, "omegle>> " + message[0])
        
    def strangerDisconnected(self,chat,var):
        self.bot.msg(self.channel, "[omegle] Disconnected.")
        self.module.clean_up()
        
omegle = OmegleModule()