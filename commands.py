__author__ = "pyton_guy"
# ATTN: THIS MODULE IS DEPRECATED
# leaving it here since help() hasn't been reimplemented yet

"""
Commands for the #/r/nyc Freenode IRC bot

This module is used by bot.py and is separate so that it can be hot-swapped.
So if a command breaks, or a new one needs to be added, we don't need to
disconnect the bot from IRC to fix it. This bot is built for five-nines!
"""

import sys
import random
import urllib2
import json
import inspect
import re
from datetime import date, timedelta
import time
# import json
from database import db





def help (self, user, channel, args):
    """ Reponds with a list of commands. """

    funcs = [member for member in inspect.getmembers(sys.modules[__name__]) if inspect.isfunction(member[1])]
    command_pairs = [f for f in funcs if len(inspect.getargspec(f[1])[0]) == 4]
    self.msg(channel, "Commands: %s" % ", ".join([command_pair[0] for command_pair in command_pairs]))

