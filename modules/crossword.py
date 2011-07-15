"""
Bot Module: crossword

Patches' means of facilitating borrowing of NYT crosswords
"""
from BotModule import BotModule
from datetime import date, timedelta


def crossword(self, user, channel, args):
    """ Respons with a URL to Today's NYT crossword """
    if args and args.count("puz") > 0:
        folder="puzs"
    elif args and args.count("grey") > 0:
        folder = "pdfs2"
    else:
        folder="pdfs"
    today=date.today()
    filename = "%02d.%02d.%02d.%s" % (
        today.year-2000, today.month, today.day, folder.rstrip('2').rstrip('s')
    )
    self.msg(channel, "http://jacobshufro.com/xwords/%s/%s" % (folder, filename))

bot_modules = [BotModule({"crossword": crossword})]