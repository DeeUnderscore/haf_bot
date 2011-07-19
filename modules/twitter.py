"""
Twitter module for twiting twits on twitter
"""

# yes, I know they're called "tweets"

import oauth2 as oauth
import time
import urllib, urllib2
import json
import re
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
        
def reply_twit(self, user, channel, args):
    """
    Replies to a given twit by id
	
	The needs to be provided a tweet id to respond to. It will parse the id
	out of a URL if it is given one.
	""" 
    nick = user.split("!", 1)[0]
    
    if not args:
        self.msg(channel, "{0}: Needs an id and a message.".format(nick))
        return
    
    args = args.split(" ", 1)
    tid = args[0]
    tweet = args[1]
    
    if len(tweet) > 140:
        self.msg(channel, "{0}: Sorry, but that's more than one hundred and forty characters, and Twitter is pretty serious about not allowing that.".format(nick))
        return 

    # extract the id 
    if not tid.isdigit():
        # we need to include "status" because twitter names can be all digits
        matched = re.search("status/(\d+)(?:/.*)?$", tid)
        if matched:
            tid = matched.group(1)
        else:
            self.msg(channel, "{0}: Could not find twit id to reply to.".format(nick))
            return 
            
    # Even though this does not require auth, we get higher rate limits if we
    # auth. Just in case someone wants to post more than 150 replies in an hour.
    url = base_url + "statuses/show.json?id=" + tid
    resp, content = twit_request(url, {}, 'GET')
    if resp['status'] != "200":
        self.msg(channel, "{0}: Could not find the twit with id {1}.".format(nick, tid))
        return
    jcontent = json.loads(content)
    reply_to = '@' + jcontent['user']['screen_name']
        
    # Twitter will disregard the reply to field if the name of the addressee is 
    # not mentioned in the message text itself, so we check for that
    if not reply_to in tweet:
        self.msg(channel, "{0}: Twitter requires that you include the name of the addressee ('{1}') in your message.".format(nick, reply_to))
        return

    # finally, we should be all ok to send this out
    url = base_url + "statuses/update.json"
    params = {'status': tweet, 'in_reply_to_status_id': tid}
    
    resp, content = twit_request(url, params)
    
    if resp["status"] != "200":
        self.msg(channel, "{0}: Well, it looked like a valid twit, but Twitter refused to post it.".format(nick))
    else:
        jcontent = json.loads(content)
        status_url = "https://twitter.com/{0}/status/{1}".format(account, jcontent["id_str"])
        self.msg(channel, "Reply posted: {0} ({1})".format(jcontent["text"].encode("utf-8"), status_url))

def twit_request(url, args, method="POST"):
    """Handler for twitter requests"""
    

    req_body = urllib.urlencode(args)
    
    consumer = oauth.Consumer(key=consumer_key, secret=consumer_secret)
    token = oauth.Token(key=oauth_token, secret=oauth_secret)
    client = oauth.Client(consumer, token)
    
    
    resp, content = client.request(url, method, body=req_body)
    return (resp, content)
    
    
twitter = BotModule({"twit": twit, "twit.reply": reply_twit})
print "Twit module loaded."