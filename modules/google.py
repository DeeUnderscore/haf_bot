"""
Bot Module: Google

Provides commands for accessing several Google services
"""


from BotModule import BotModule
import urllib2
import json

def gis(self, user, channel, args):
	""" Google image search"""
	
	gis_url = "http://images.google.com/search?tbm=isch&q="
	args = urllib2.quote(args)
	self.msg(channel, gis_url + args)
	
def google(self, user, channel, args):
	"""Searches for things on google"""
	
	google_url = "http://www.google.com/search?q="
	args = urllib2.quote(args)
	self.msg(channel, google_url + args)
	
def translate(self, user, channel, args):

    """	Translates text into english from a detected language. """
    if args:
    	# this appears to contain a key. Oh well?
        translate_url = "https://www.googleapis.com/language/translate/v2?key=AIzaSyD_Qg6EVKkhRnUAYBwG5UL4sBjzJTJgX7k&q={0}&target=en" 
        translate_url = translate_url.format(urllib2.quote(args))
        data = json.load(urllib2.urlopen(translate_url))
        # unicoding this because str() would freak out if given utf8 text
        text = unicode(data['data']['translations'][0]['translatedText'])
        language = str(data['data']['translations'][0]['detectedSourceLanguage'])
        # unicode to unicode comparison
        if args.decode('utf8') == text:
            reply = "No translation found."
        else:
            # encode text for sending 
            reply = "\"%s\" Translated from: %s" % (text.encode('utf-8'), language)
        self.msg(channel, reply)
    else:
        self.msg(channel,
                 "Usage: !translate <phrase to be translated into english>")


google = BotModule({"g": google, "gis": gis, "translate": translate})
