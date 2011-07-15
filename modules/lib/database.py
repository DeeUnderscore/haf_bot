"""
Database connection for other modules to import as needed
"""

# Connect to the DB
print "Connecting to database..."
import pymongo
connection = pymongo.Connection()
db = connection.rnyc_irc
