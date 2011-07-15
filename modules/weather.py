#!/usr/bin/env python

"""
Google weather lookup

Uses the undocumented Google API to fetch current weather data 
"""

from xml.dom import minidom
import urllib2
from lib.botconfig import config
from BotModule import BotModule

default_locale = config.get("weather", "default_locale")
weather_url = "http://www.google.com/ig/api?weather="



def weather(self, user, channel, args):
	"""Displayes weather data for given location."""

	location = args if args else default_locale
	
	try:
		weather_data = get_weather(location)
		self.msg(channel, "{location}: {temp}, {condition}".format(**weather_data))
	except InvalidLocale:
		self.msg(channel, "Invalid location")

def get_weather(location):
	if location == "":
		raise InvalidLocale
	weather_file = urllib2.urlopen(weather_url + urllib2.quote(location))
	wd = minidom.parse(weather_file)
	# if there is a node called problem_cause we have an error
	if [n for n in wd.firstChild.firstChild.childNodes
	               if n.nodeName == "problem_cause"] != []:
		raise InvalidLocale
	data = {}
	data["location"] = wd.getElementsByTagName("city")[0].attributes["data"].value
	data["temp"] = (wd.getElementsByTagName("current_conditions")[0].
	                   getElementsByTagName("temp_f")[0].attributes["data"].value)
	data["condition"] = (wd.getElementsByTagName("current_conditions")[0].
	                        getElementsByTagName("condition")[0].
	                        attributes["data"].value)
	
	return data
	
class InvalidLocale(Exception):
	pass


bot_modules = [BotModule({"weather": weather})]

