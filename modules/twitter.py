"""
Twitter module for twiting twits on twitter
"""

import oauth2 as oauth
import time
import urllib
import json
from lib.botconfig import config
from BotModule import BotModule

# Import relevant config 
oauth_token = config.get("twitter", "oauth_token")
oauth_secret = config.get("twitter", "oauth_secret")
consumer_key = config.get("twitter", "consumer_key")
consumer_secret = config.get("twitter", "consumer_secret")
account = config.get("twitter", "account")

base_url = "https://api.twitter.com/1/"

def twit(self, user, channel, args):
    """Twits."""
    
    nick = user.split("!", 1)[0]
    
    if not args:
        self.msg(channel, "{0}: Needs something to twit, yo.".format(nick))
        return
        
    if len(args) > 140:
        self.msg(channel, "{0}: Dear sir/madam. As you perhaps already know, the website Twitter prides itself in enforcing brevity amongst its users by limiting each of their individual postings to 140 characters. The message that you have so kindly provided exceeds that limit. In this situation, I am unfortunately unable to process your request.".format(nick))
        return
    
    url = base_url + "statuses/update.json"
    
    params = {"status" : args}
    
    resp, content = twit_request(url, params)
    
    if resp["status"] != "200":
        self.msg(channel, "{0}: Oh woe is me! Twitter has refused to twit that twit.".format(nick))
    else:
        jcontent = json.loads(content)
        status_url = "https://twitter.com/{0}/status/{1}".format(account, jcontent["id_str"])
        self.msg(channel, "Successfully twitted: {0} ({1})".format(jcontent["text"].encode("utf-8"), status_url))
        # TODO: Use bitly?
        
def twit_request(url, args):
    """Handler for twitter requests"""
    
    # append stuff and things
    args['oauth_version'] = "1.0"
    args['oauth_nonce'] = oauth.generate_nonce()
    args['oauth_timestamp'] = int(time.time())
    req_body = urllib.urlencode(args)
    
    consumer = oauth.Consumer(key=consumer_key, secret=consumer_secret)
    token = oauth.Token(key=oauth_token, secret=oauth_secret)
    client = oauth.Client(consumer, token)
    
    
    resp, content = client.request(url, method="POST", body=req_body)
    
    return (resp, content)
    
    
bot_modules = [BotModule({"twit": twit})]
print "Twit module loaded."