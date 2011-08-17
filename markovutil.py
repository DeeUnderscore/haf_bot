# -*- coding: utf-8 -*-

# TODO: Relocate this file
# TODO: Ensure URLs and other misc chars properly stripped

"""
Utilities for populating the Markov chain database for the Markov module
"""

from modules.lib.database import db
import csv
import re 

def unescape(text):
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    text = text.replace('&amp;', "&")
    return text

def split_text(text):
    tokens = []
    token = ""
    type = ''
    last_type = ''
    
    # pre-processing here to clean it up
    
    # nix some characters for simplicity
    text = text.replace('"', '')
    text = text.replace('@', '')
    text = text.replace('#', '')
    
    
    # nabbed this from http://daringfireball.net/2010/07/improved_regex_for_matching_urls
    url_pattern = re.compile("""(?i)\b((?:[a-z][\w-]+:(?:/{1,3}|[a-z0-9%])|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?������]))""")
    
    # nix all URLs
    text = re.sub(url_pattern, '', text)
    
    
    # tokenizing here
    for char in text:
        if re.match('\s', char):
            last_type = type
            type = 's'
            if token != "":
                tokens.append(token)
                token = ""
            continue 
        elif re.match("[\w']", char):
            last_type = type
            type = 'l'  # letters
        elif char in ",!?.:":
            last_type = type
            type = 'p'  # punctuation chars
        else:
            # disregard everything else
            continue
            
        if last_type == type:
            token += char
        else:
            if token != "":
                tokens.append(token)
            token = char
    tokens.append(token)
    
    return tokens
    
    
def markovize(filename='twits.csv'):
    print "Opening file..."
    entries = csv.reader(open(filename, 'rb'), delimiter=':')
    
    col = db['markov']
    
    col.insert({"word": ".", "wordcount": 1, "following": [(None, 1, 1)] })
    col.insert({"word": "?", "wordcount": 1, "following": [(None, 1, 1)] })
    col.insert({"word": "!", "wordcount": 1, "following": [(None, 1, 1)] })
    print "Database initialized..."
    
    linecount = 0
                       
    for entry in entries:
        linecount += 1
        if linecount % 10 == 0:
            # this could be something prettier, like a progress bar maybe
            print linecount
        
        text = unescape(entry[1])
        text = unicode(text, 'utf8')

        tokens = split_text(text)
        tokens.append(None)
        prev = None
        
        for (i, token) in enumerate(tokens):                       
            if i > 0:
                prev = tokens[i-1]
                
            if prev and re.match("[.!?]", prev):
                # These are always treated as terminal characters
                prev = None
                
            if prev == None and token == None:
                continue
            
            
            record = col.find_one({"word": prev})
            
            if record:
                following = record["following"]
                total = record['wordcount'] + 1
                # following is an array of tuples. The tuples are as follows:
                # (word, freq)
                # We don't use a dictionary here so we can store this sorted
                matched = False
                for entry in following:
                    if entry[0] == token:
                        entry[1] += 1
                        matched = True
                if not matched:
                    # only reached if the word hasn't been entered in the array yet
                    following.append((token, 1))
                    
                following = sorted(following, key=lambda k: k[1], reverse=True)
                object = {"word": prev,
                          "wordcount": total,
                          "following": following}
                col.update({"word": prev}, object)
            else:
                object = {"word": prev,
                          "wordcount": 1,
                          "following": [(token, 1)]}
                col.insert(object)
                
            
        
if __name__ == "__main__":
    markovize()
        
        