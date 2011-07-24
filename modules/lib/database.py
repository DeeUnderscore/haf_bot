"""
Database connection for other modules to import as needed
"""
import pymongo
from botconfig import config

dbname = config.get("bot", "dbname")
# Connect to the DB
print "Connecting to database..."

connection = pymongo.Connection()
db = connection[dbname]
