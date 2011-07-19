from BotModule import BotModule
import urllib2
import json
from datetime import date, time

def reddit(self, user, channel, args):
    if args:
        uname = args
    else:
        # user is in the format "nick_name!~real_name@host.name"
        uname = user.split("!", 1)[0]

    try:
        # Let the JSON module read in the response from Reddit's User API
        data = json.load(urllib2.urlopen("http://reddit.com/user/%s/about.json" % uname))["data"]
        # Feed the JSON-sourced dictionary to a format string
        epoch_time = data["created_utc"]
        created_date = date.fromtimestamp(int(epoch_time))
        age = date.today() - created_date

        if (age.days>365):
            days = age.days%365
            years = age.days/365
            age_str = " Redditor for %s year(s) and %s day(s)." % (years, days)
        else:
            age_str = " Redditor for %s day(s)." % age.days
        
        link_velocity = data["link_karma"] / float(age.days)
        comment_velocity = data["comment_karma"] / float(age.days)
        
        self.msg(
            channel,
            "User: {name}  Link Karma: {link_karma} ".format(**data) + \
            "({0:.2f} per day)  ".format(link_velocity) + \
            "Comment Karma: {comment_karma} ".format(**data) + \
            "({0:.2f} per day)  ".format(comment_velocity) + age_str
        )
    except urllib2.HTTPError, e:
        if e.code == 404:
            self.msg(channel, "User: %s does not exist." % uname)
        else:
            self.msg(channel, "Reddit is down!")
    except KeyError:
        # Happens when the data is malformed, and we can't get what we want from the JSON
        self.msg(channel, "Reddit broke :(")
        
bot_modules = [BotModule({"reddit": reddit})]
