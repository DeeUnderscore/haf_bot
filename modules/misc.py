from BotModule import BotModule
import urllib2


def fuck(self, user, channel, args):
    """
    https://plus.google.com/111528911333263728657/posts/cSx5w5aaUv1
    """
    
    fucks = urllib2.urlopen('http://rage.thewaffleshop.net/').read()
    self.msg(channel, fucks)
    
misc = BotModule(commands={'fuck': fuck})