import re
import random
from BotModule import BotModule

def roll_dice(self, user, channel, args):
    
    if args.isdigit():
        dice = 1
        sides = int(args)
    else:
        match = re.search("(\d+)d(\d+)", args)
        if match:
            dice = int(match.group(1))
            # 0-sided dice break the universe
            sides = (lambda x: x if x>0 else 6)(int(match.group(2)))
        else:
            dice = 1
            sides = 6
    
    rolls = []
    
    for i in range(dice):
        rolls.append(str(random.randint(1, sides)))
    
    user = user.split("!", 1)[0]
    
    result = "Rolled {0}d{1}: ".format(dice, sides)
    result +=  (' '.join(rolls))
    
    
    self.msg(channel, user + ": " + result )
        
dice = BotModule({"roll": roll_dice})