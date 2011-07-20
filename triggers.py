__author__ = "pyton_guy"

"""
Triggers for the #/r/nyc Freenode IRC bot

This module is used by bot.py and is separate so that it can be hot-swapped.
So if a trigger breaks, or a new one needs to be added, we don't need to
disconnect the bot from IRC to fix it. This bot is built for five-nines!
"""

import re
from command_table import triggers

def process_message (self, user, channel, msg):
    """ 
    Steps through all the registered triggers and executes the associated
    function on positive match.
    """
    
    trigger_table = triggers.table
    for trigger in trigger_table.values():
        # trigger[0] is the regex to match
        match = re.search(trigger[0], msg)
        if match:
            # trigger[1] is the function to execute on match
            trigger[1](self, user, channel, msg, match)