from lib.database import db
import random 
from BotModule import BotModule

def weighed_pick(list, size):
    choice = random.randint(0, size-1)
    
    for item in list:
        if choice <= item[1]:
            return item[0]
        else:
            choice -= item[1]

def gibberize(self, user, channel, arg):
    col = db['markov']
    nick = user.split("!", 1)[0]
    gibberish = ""
    prev = None
    
    done = False
    while not done:
        record = col.find_one({"word": prev})
        if not record:
            done = True
            break 
        prev = weighed_pick(record['following'], record['wordcount'])
        if prev != None:
            if gibberish != "" and prev not in "<>,!?.8=[]():":
                gibberish += " "
            gibberish += prev
        else:
            done = True
            
    self.msg(channel, "{0}: {1}".format(nick, gibberish))

markov = BotModule({"gibberish": gibberize})