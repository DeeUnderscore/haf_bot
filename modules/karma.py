"""
Bot Module: Karma

Provides support for upvoting and downvoting people on IRC
"""
from lib.database import db
from BotModule import BotModule
import re

karma_regex = re.compile("([\w-]+)(\+\+|--)", re.M)

def karma_funct (self, user, channel, args):
    """ Responds with a list of karma records. """

    # Check for any sub-commands (like merge)
    args = args.split(" ")
    if args[0]:
        karma_record = db.karma.find_one({"nick" : args[0]})
        karma = int(karma_record["karma"] if karma_record else 0)
        karma_text = "{0}: {1}".format(args[0], karma)
    else:
        # TODO: Make this into a for loop if someone complains >_>
        # Put together a readable karma list, and display it'
        all = [x for x in db.karma.find()]
        all.sort(lambda x, y: cmp(y["karma"], x["karma"]))
        top_5 = all[:5]
        bottom_5 = all[-5:]
        karmaValues = lambda y: ", ".join(["%s(%s)" % (x["nick"], int(x["karma"])) for x in y])
        karma_text = "Top 5: %s | Bottom 5: %s" % (karmaValues(top_5), karmaValues(bottom_5))
    
    self.msg(channel, str(karma_text))
    
def karma_trigger(self, user, channel, args, match):
    """
    Trigger for increasing or decreasing karmas
    """
    # Disable karma from PMs
    if not channel.startswith("#"):
        return

    # Karma Trigger
    # We need to apply the regex again since triggers match only once
    for nick, points in karma_regex.findall(args):
        # (I resisted the urge to make it a one-liner)
        if points == "++":
            points = +1
        else:
            points = -1
        
        # This is an upsert 
        db.karma.update({"nick": nick}, {"$inc": {"karma": points}}, upsert=True)

trigger_tuple = (karma_regex, karma_trigger)

karma = BotModule( commands={"karma": karma_funct},
                   triggers={"karma": trigger_tuple} )