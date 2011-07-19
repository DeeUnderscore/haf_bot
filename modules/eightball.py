"""
Bot Module: Eightball

Provides a simple eightball thingy
"""

from BotModule import BotModule
import random

def eightball_funct(self, user, channel, args):
	responses=["It is certain",
	           "It is decidedly so",
	           "Without a doubt",
	           "Yes - definitely",
	           "You may rely on it",
	           "As I see it, yes",
	           "Most likely",
	           "Outlook good",
	           "Signs point to yes",
	           "Yes",
	           "Reply hazy, try again",
	           "Ask again later",
	           "Better not tell you now",
	           "Cannot predict now",
	           "Concentrate and ask again",
	           "Don't count on it",
	           "My reply is no",
	           "My sources say no",
	           "Outlook not so good",
	           "Very doubtful",
	           "FUCK YOU!"]
	
	response = random.choice(responses)
	user_nick = user.split("!", 1)[0]
	self.msg(channel, "{0}: {1}".format(user_nick, response))
	
eightball = BotModule({'8ball': eightball_funct})

