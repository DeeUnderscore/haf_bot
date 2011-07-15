"""
Bot Module: Karma

Provides support for upvoting and downvoting people on IRC
"""
from lib.database import db
from BotModule import BotModule

def karma (self, user, channel, args):
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
        karma_text = karma_text.replace("<random>", str(random.randint(-1000, 1000)))
    
    self.msg(channel, str(karma_text))
    
# TODO: Integrate triggers with the module system so we can have that code here

bot_modules = [BotModule({"karma": karma})]