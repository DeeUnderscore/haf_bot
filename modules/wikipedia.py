#!/usr/bin/env python
"""
wikipedia.py - Phenny Wikipedia Module
Copyright 2008-9, Sean B. Palmer, inamidst.com
Licensed under the Eiffel Forum License 2.

http://inamidst.com/phenny/
"""

import re, urllib, urllib2
import web
import json

wikiuri = 'http://en.wikipedia.org/wiki/%s'
wikisearch = 'http://en.wikipedia.org/wiki/Special:Search?' \
                    + 'search=%s&fulltext=Search'

r_tr = re.compile(r'(?ims)<tr[^>]*>.*?</tr>')
r_paragraph = re.compile(r'(?ims)<p[^>]*>.*?</p>|<li(?!n)[^>]*>.*?</li>')
r_tag = re.compile(r'<(?!!)[^>]+>')
r_whitespace = re.compile(r'[\t\r\n ]+')
r_redirect = re.compile(
   r'(?ims)class=.redirectText.>\s*<a\s*href=./wiki/([^"/]+)'
)

abbrs = ['etc', 'ca', 'cf', 'Co', 'Ltd', 'Inc', 'Mt', 'Mr', 'Mrs', 
         'Dr', 'Ms', 'Rev', 'Fr', 'St', 'Sgt', 'pron', 'approx', 'lit', 
         'syn', 'transl', 'sess', 'fl', 'Op', 'Dec'] \
   + list('ABCDEFGHIJKLMNOPQRSTUVWXYZ') \
   + list('abcdefghijklmnopqrstuvwxyz')
t_sentence = r'^.{5,}?(?<!\b%s)(?:\.(?=[\[ ][A-Z0-9]|\Z)|\Z)'
r_sentence = re.compile(t_sentence % r')(?<!\b'.join(abbrs))

def unescape(s): 
   s = s.replace('&gt;', '>')
   s = s.replace('&lt;', '<')
   s = s.replace('&amp;', '&')
   s = s.replace('&#160;', ' ')
   return s

def text(html): 
   html = r_tag.sub('', html)
   html = r_whitespace.sub(' ', html)
   return unescape(html).strip()

def search(term): 
   try: import search
   except ImportError, e: 
      print e
      return term

   if isinstance(term, unicode): 
      term = term.encode('utf-8')
   else: term = term.decode('utf-8')

   term = term.replace('_', ' ')
   try: uri = search.result('site:en.wikipedia.org %s' % term)
   except IndexError: return term
   if uri: 
      return uri[len('http://en.wikipedia.org/wiki/'):]
   else: return term

def wikipedia_lookup(term, last=False): 
   global wikiuri
   if not '%' in term: 
      if isinstance(term, unicode): 
         t = term.encode('utf-8')
      else: t = term
      q = urllib.quote(t)
      u = wikiuri % q
      bytes = web.get(u)
   else: bytes = web.get(wikiuri % term)
   bytes = r_tr.sub('', bytes)

   if not last: 
      r = r_redirect.search(bytes[:4096])
      if r: 
         term = urllib.unquote(r.group(1))
         return wikipedia_lookup(term, last=True)

   paragraphs = r_paragraph.findall(bytes)

   if not paragraphs: 
      if not last: 
         term = search(term)
         return wikipedia_lookup(term, last=True)
      return None

   # Pre-process
   paragraphs = [para for para in paragraphs 
                 if (para and 'technical limitations' not in para 
                          and 'window.showTocToggle' not in para 
                          and 'Deletion_policy' not in para 
                          and 'Template:AfD_footer' not in para 
                          and not (para.startswith('<p><i>') and 
                                   para.endswith('</i></p>'))
                          and not 'disambiguation)"' in para) 
                          and not '(images and media)' in para
                          and not 'This article contains a' in para 
                          and not 'id="coordinates"' in para
                          and not 'class="thumb' in para]
                          # and not 'style="display:none"' in para]

   for i, para in enumerate(paragraphs): 
      para = para.replace('<sup>', '|')
      para = para.replace('</sup>', '|')
      paragraphs[i] = text(para).strip()

   # Post-process
   paragraphs = [para for para in paragraphs if 
                 (para and not (para.endswith(':') and len(para) < 150))]

   para = text(paragraphs[0])
   m = r_sentence.match(para)

   if not m: 
      if not last: 
         term = search(term)
         return wikipedia_lookup(term, last=True)
      return None
   sentence = m.group(0)

   maxlength = 275
   if len(sentence) > maxlength: 
      sentence = sentence[:maxlength]
      words = sentence[:-5].split(' ')
      words.pop()
      sentence = ' '.join(words) + ' [...]'

   if (('using the Article Wizard if you wish' in sentence)
    or ('or add a request for it' in sentence)): 
      if not last: 
         term = search(term)
         return wikipedia_lookup(term, last=True)
      return None

   sentence = '"' + sentence.replace('"', "'") + '"'
   sentence = sentence.decode('utf-8').encode('utf-8')
   wikiuri = wikiuri.decode('utf-8').encode('utf-8')
   term = term.decode('utf-8').encode('utf-8')
   return sentence + ' - ' + (wikiuri % term)


#
# haf_bot module follows
# 

def wiki(self, user, channel, args): 
    if not args:
        self.msg(channel, "Usage !wiki <article>")
    else:
        origterm = args
        origterm = origterm.encode('utf-8')

        term = urllib2.unquote(origterm)
        term = term[0].upper() + term[1:]
        term = term.replace(' ', '_')

        try: result = wikipedia_lookup(term)
        except IOError: 
            error = "Can't connect to en.wikipedia.org (%s)" % (wikiuri % term)
            self.msg(channel, error)
            return

        if result is not None: 
            self.msg(channel, result)
        else: self.msg(channel, 'Can\'t find anything in Wikipedia for "%s".' % origterm)

# this uses wiktionary and not wikipedia, but it's tangentially related so it 
# might as well go here 
def define(self, user, channel, args):
    """ Defines a word using the Wiktionary API """
    if args:
        data = json.load(urllib2.urlopen(
            "http://en.wiktionary.org/w/api.php?format=json&action=query&prop=revisions&rvprop=content&titles=%s" % args))
        innerdata = data["query"]["pages"]
        if "-1" in innerdata:
            self.msg(channel, "No definition found.")
            return
        for key in innerdata:
            string = innerdata[key]["revisions"][0]["*"]
            result = re.findall(".*#.*", string)
            defs = len(result)
            formatted = re.sub("# ", "", re.sub("{.*}\s", "", result[0]))
            formatted = str(formatted.replace('[', '').replace(']', ''))
            self.msg(channel,
                     "%s - %s (Found %i definitions at http://en.wiktionary.org/wiki/%s)" % (
                     args, formatted, defs, args))        

from BotModule import BotModule      
wikipedia = BotModule({"wiki": wiki, "define": define})

