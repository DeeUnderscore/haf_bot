"""
last.fm module

Adds some last.fm functionality to the bot: registers nicknames, displays
currently playing songs for registered nicknames, compares people
"""

from xml.dom import minidom
import urllib2
from urllib import urlencode
import datetime
from lib.database import db
from lib.botconfig import config
from BotModule import BotModule

lfm_url = "http://ws.audioscrobbler.com/2.0/"
api_key = config.get("lastfm", "api_key")


def register_nickname(self, user, channel, args):
	""" Adds a irc nickname -> last.fm username mapping record to the db"""
	irc_name = user.split("!", 1)[0]
	if not args:
		self.msg(channel, "{0}: Please provide a last.fm username".format())
		return 
	# discard everything after the first space - lastfm usernames have no spaces
	args = args.split(" ",1)[0]
	data = minidom.parse(lfm_call({"user": args, "method": "user.getInfo"}))
	
	# if status is failed, we weren't able to fetch the profile
	if data.getElementsByTagName("lfm")[0].attributes["status"].value == "failed":
		self.msg(channel, "{0}: Cannot find profile. Is the username correct?".format(irc_name)) 
		return
	
	# this is an upsert - we assume that if it's set already, the user wants to 
	# overwrite anyway
	db.lastfm.update({"irc_nick": irc_name},
	                 {"$set": {"irc_nick": irc_name, "lastfm": args}},
	                 True)
	
	# build response in an ugly way 
	notify = {}
	notify["nick"] = irc_name
	notify["lastfm"] = args
	notify["fullname"] = data.getElementsByTagName("realname")[0].firstChild.data
	notify["url"] = data.getElementsByTagName("url")[0].firstChild.data
	self.msg(channel,
	         "{nick} is now mapped to {lastfm} ({fullname}, {url})".format(**notify))	
		
def now_playing(self, user, channel, args):
	"""Displays currently playing track, or last played track"""
	
	nick = user.split("!", 1)[0]
	# if args are there, we assume we're looking up someone else
	if args:
		args = args.split(" ",1)[0]
		# if it's in the db, we go by that. if not, we assume it's an explicit
		# last.fm username
		found_name = lookup_name(args)
		if found_name:
			lfm_name = found_name
		else:
			lfm_name = args
	# if no args, we use the db to look up the person making the request
	else:
		found_name = lookup_name(nick)
		if found_name:
			lfm_name = found_name
		else:
			# if not in db, we inform the user that he should register
			self.msg(channel, "{0}: No record for you. Please register with !lastfm.register".format(nick))
			return
	# if we request recent tracks for a username that does not exist, last.fm
	# will be more than happy to return an OK status and give us no tracks at
	# all. So, we check if the user exists first.
	
	if not check_exists(lfm_name):
		self.msg(channel, "{0}: User {1} does not exist on last.fm".format(nick, lfm_name))
		return
	
	params = {}
	params["method"] = "user.getRecentTracks"
	params["user"] = lfm_name
	params["limit"] = "1"
	data = minidom.parse(lfm_call(params))
	
	# if the bastard never played any tracks
	if len(data.getElementsByTagName("track")) == 0:
		self.msg(channel, "{0} has never played a track :(".format(lfm_name))
		return
	
	now = False
	# the track will have a nowplaying=true if it is playing now, but it won't
	# have anything at all if it's not playing now. We can't check for nowplaying
	# value, so we just check if it exists at all
	if data.getElementsByTagName("track")[0].hasAttribute("nowplaying"):
		now = True
	
	notify = {}
	# last.fm returns stuff in utf-8, and we might have to handle that
	notify["artist"] = data.getElementsByTagName("artist")[0].firstChild.data.encode('utf-8')
	notify["track"] = data.getElementsByTagName("name")[0].firstChild.data.encode('utf-8')
	track_timestamp = data.getElementsByTagName("date")[0].attributes["uts"].value
	
	# full response to send to channel
	rs = ""
	
	# if looked up using explicit lfm usernmae
	if args == lfm_name:
		rs = args
	# if looked up for someone else
	elif args:
		rs = "{0} ({1})".format(args, lfm_name)
	# lookup for user themselves
	else:
		rs = "{0} ({1})".format(nick, lfm_name)

	if not now: 
		# (sic) 
		track_time = datetime.datetime.utcfromtimestamp(float(track_timestamp))
		notify["when"] = readable_tdelta(track_time)
		rs += " last track: {artist} - {track} (played {when} ago)".format(**notify)
	else:
		rs += " now playing: {artist} - {track}".format(**notify)
	
	self.msg(channel, rs)
	
def compare(self, user, channel, args):
	# TODO: Local comparison of artists for more accurate results?
	
	args = args.split(" ")
	
	nick = user.split("!", 1)[0]
	names = [None] * 2
	# if only one param provided we assume user wants to compare against that
	if len(args) == 0:
		self.msg(channel, "{0}: You must provide at least one username to compare to.".format(nick))
	elif len(args) == 1:

		found_name = lookup_name(nick)
		if found_name:
			names[0] = found_name
			names[1] = lookup_name(args[0])
			# if name was not in database, treat it as literal, check if exists
			if not names[1]:
				if not check_exists(args[0]):
					self.msg(channel, "{0}: {1} does not exist on last.fm".format(nick, args[0]))
					return 
				else:
					names[1] = args[0]
		else:
			# if we only got one param and the user isn't registered we complain
			self.msg(channel,
			         "{0}: You must either be registered or specify two usernames to compare".format(nick))
			
	else:
		names = args[0:2]
			
		for i,name in enumerate(names):
			new_name = lookup_name(name)
			if new_name:
				names[i] = new_name
			elif not check_exists(name):
				self.msg(channel, "{0}: {1} does not exist on last.fm".format(nick, name))
		
	params = {}
	params["method"] = "tasteometer.compare"
	params["type1"] = params["type2"] = "user"
	params["value1"] = names[0]
	params["value2"] = names[1]
	
	data = minidom.parse(lfm_call(params))
	
	notify = {}
	# score is in fraction of 1, so we multiply it by 100 to get percentage 
	# for later formatting
	notify["score"] = float(data.getElementsByTagName("score")[0].firstChild.data) * 100
	notify["user1"] = names[0]
	notify["user2"] = names[1]
	
	notify["matches"] = ""
	for artist in data.getElementsByTagName("artists")[0].getElementsByTagName("artist"):
		artist_name = artist.getElementsByTagName("name")[0].firstChild.data
		notify["matches"] += artist_name + ", "

	# strip the trailing ", "
	notify["matches"] = notify["matches"][:-2]
	
	notify_string = "{user1} - {user2}: {score:.2f}% compatible, " + \
	                "artists in common include: {matches}."
	
	self.msg(channel, notify_string.format(**notify).encode("utf-8"))
			
def lfm_call(args):
	"""Calls the last.fm API with all the proper request formatting"""

	args["api_key"] = api_key
	args_string = urlencode(args)
	url = lfm_url + "?" + args_string
	req = urllib2.Request(url)
	req.add_header("User-agent", "haf_bot/1.0 (Python-urllib)")
	
	opener = urllib2.build_opener()
	try:
		data = opener.open(req)
	# in case of an error, we can catch the exception which contains ther response
	# and handle it in the calling function. Can this break? Probably.
	except urllib2.HTTPError, error:
		data = error

	return data

def lookup_name(name):
	"""Looks up name in the database. If not present, returns None"""
	record = db.lastfm.find_one({"irc_nick": name})
	if record:
		return record["lastfm"]
	else:
		return None
	
def check_exists(name):
	"""Checks if name exists on last.fm"""
	
	usr_data = minidom.parse(lfm_call({"user": name, "method": "user.getInfo"}))
	
	if usr_data.getElementsByTagName("lfm")[0].attributes["status"].value == "failed":
		return False
	else:
		return True
	
def readable_tdelta(other_time):
	"""
	Returns a human-readable string with the difference between current time
	and other_time. Expects UTC.
	
	Formats returned:
	"x months, y days"
	"x days"
	"x hours, y minutes"
	"x minutes"
	"x seconds"
	(if y days or y minutes is 0 it is dropped entirely)
	"""
	
	now = datetime.datetime.utcnow()
	delta = now - other_time
	
	delta_string = ""
	
	# for months:
	if delta.days > 30:
		months = delta.days / 30
		delta_string += str(months) + " month"
		delta_string += "s" if (months > 1) else ""
	if delta.days >= 1:
		days = delta.days % 30
		if days != 0:
			if delta_string != "":
				delta_string += ", "
			delta_string += (str(days) + " day")
			delta_string += "s" if days > 1 else ""
	else:
		# 3600s = 1h
		hours = delta.seconds / 3600
		# leftover seconds in minutes
		minutes = (delta.seconds - (3600 * hours))/60
		# leftover seconds
		seconds = (delta.seconds - (3600 * hours) - (60 * minutes))
		
		if hours >= 1:
			delta_string += (str(hours) + " hour")
			delta_string += "s" if hours > 1 else ""
			
		if minutes >= 1:
			if delta_string != "":
				delta_string += ", "
			delta_string += (str(minutes) + " minute")
			delta_string += "s" if minutes > 1 else ""
		elif hours < 1:
			delta_string += str(seconds) + " second"
			delta_string += "s" if seconds > 1 else ""
			
	return delta_string

table = {}
table["lastfm.register"] = register_nickname
table["np"] = now_playing
table["compare"] = compare
lastfm = BotModule(table)
del table
print "Last.fm module loaded"