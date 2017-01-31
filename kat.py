# kickass-api-wrapper
# https://github.com/auino/kickass-api-wrapper

#!/usr/bin/env python

import sys
import re
import urllib, urllib2
import requests
import cherrypy
import HTMLParser
from bs4 import BeautifulSoup
from xml.etree.ElementTree import Element, SubElement, Comment, tostring

###########################
###   BASIC SETTINGS    ###
###        BEGIN        ###
###########################

# limits returned results
LIMITRESULTS = None

# listening address used by the server (i.e. set it to "127.0.0.1" to only accept connections from localhost, "0.0.0.0" for a public service binding)
LISTENADDRESS="127.0.0.1"

# listening port of the server
LISTENPORT=8123

###########################
###   BASIC SETTINGS    ###
###         END         ###
###########################

###########################
###  ADVANCED SETTINGS  ###
###        BEGIN        ###
###########################

# user agent used to request HTML pages
USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.107 Safari/537.36'

# Sonarr search format
SONARRSEARCHFORMAT = '/usearch/'

# returned resource category type
CATEGORY = 'TV'

# returns detailed information for each found file
DETAILEDRESULTS = True

# used space separator for the query
SEPARATOR = '+'

# comparison string to identify verified torrents
VERIFIEDSTRING = 'Verified Torrent'

# extraction patterns

EXTRACTIONPATTERNS_GENERAL = patterns = [
	{'key': 'name', 'actions': [{'tag': 'a', 'filter': {'class': 'cellMainLink'}, 'field': 'CONTENT', 'index': 0}]},
	{'key': 'link', 'actions': [{'tag': 'a', 'filter': {'class': 'cellMainLink'}, 'field': 'href', 'index': 0}]},
	{'key': 'verified', 'actions': [{'tag': 'a', 'filter': {'class': 'icon16'}, 'field': 'title', 'index': 0}]},
	{'key': 'magnet', 'actions': [{'tag': 'a', 'filter': {'title': 'Torrent magnet link'}, 'field': 'href', 'index': 0}]},
	{'key': 'uploader', 'actions': [{'tag': 'span', 'filter': {'class': 'font11px'}, 'field': 'CONTENT', 'index': 0}]},
	{'key': 'size', 'actions': [{'tag': 'td', 'filter': {'class': 'nobr'}, 'field': 'CONTENT', 'index': 0}]}
]

EXTRACTIONPATTERNS_DETAIL = [
	{'key': 'seeders', 'actions': [{'tag': 'div', 'filter': {'class': 'seedBlock'}, 'field': None, 'index': 0}, {'tag': 'strong', 'filter': None, 'field': 'CONTENT', 'index': 0}]},
	{'key': 'leechers', 'actions': [{'tag': 'div', 'filter': {'class': 'leechBlock'}, 'field': None, 'index': 0}, {'tag': 'strong', 'filter': None, 'field': 'CONTENT', 'index': 0}]},
	{'key': 'updatetime', 'actions': [{'tag': 'time', 'filter': None, 'field': 'CONTENT', 'index': 0}]},
	{'key': 'infohash', 'actions': [{'tag': 'span', 'filter': {'class': 'font10px'}, 'field': 'CONTENT', 'index': 0}]},
	{'key': 'sizebytes', 'actions': [{'tag': 'span', 'filter': {'class': 'folderopen'}, 'field': 'CONTENT', 'index': 0}]}
]

def geturl(args): return 'http://kat.how/search.php?q=' + args

###########################
###  ADVANCED SETTINGS  ###
###         END         ###
###########################

def createxmlsubtreefromrecord(parent, fieldname, data):
	try:
		r = SubElement(parent, fieldname)
		if data != None: r.text = data
		return r
	except: return None

def convertrecordstoxml(records):
	xml = Element('rss', {'version': '2.0', 'xmlns:torrent': 'http://xmlns.ezrss.it/0.1/'})
	channel = SubElement(xml, 'channel')
	channel.title = 'kickass-api-wrapper'
	for r in records:
		top = createxmlsubtreefromrecord(channel, 'item', r.get('recordname'))
		title = createxmlsubtreefromrecord(top, 'title', r.get('name'))
		category = createxmlsubtreefromrecord(top, 'category', CATEGORY)
		author = createxmlsubtreefromrecord(top, 'author', r.get('uploader'))
		link = createxmlsubtreefromrecord(top, 'link', r.get('link'))
		guid = createxmlsubtreefromrecord(top, 'guid', r.get('link'))
		pubdate = createxmlsubtreefromrecord(top, 'pubDate', r.get('updatetime'))
		length = createxmlsubtreefromrecord(top, 'torrent:contentLenght', r.get('sizebytes'))
		infohash = createxmlsubtreefromrecord(top, 'torrent:infoHash', r.get('infohash'))
		uri = createxmlsubtreefromrecord(top, 'torrent:magnetURI', '<![CDATA['+r.get('magnet')+']]>')
		seeds = createxmlsubtreefromrecord(top, 'torrent:seeds', r.get('seeders'))
		peers = createxmlsubtreefromrecord(top, 'torrent:peers', r.get('peers'))
		verified = createxmlsubtreefromrecord(top, 'torrent:verified', ('1' if r.get('verified') else '0'))
		filename = createxmlsubtreefromrecord(top, 'torrent:fileName', r.get('name'))
		enclosure = SubElement(top, 'enclosure', {'url': r.get('link')})
	return HTMLParser.HTMLParser().unescape(tostring(xml))

# extracts data from a BeautifulSoup element using given patterns
def dataextractor(data, patterns):
	res = {}
	for el in patterns:
		try:
			v = data
			for action in el.get('actions'):
				v = v.find_all(action.get('tag'), action.get('filter'))[action.get('index')]
				if action.get('field') != None:
					if action.get('field') == 'CONTENT': v = v.getText()
					else: v = v.get(action.get('field'))
			res[el.get('key')] = v
		except: return None
	return res

def geturlcontent(url):
	# making the request
	r = requests.get(url, headers={'User-Agent':USER_AGENT,'Upgrade-Insecure-Requests': '1','x-runtime': '148ms'}, allow_redirects=True)
	# check for connection or HTTP error
	try: r.raise_for_status()
	except: return None
	# getting html content
	return r.content

def search(query, verified):
	records = []
	# searching all results
	url = geturl(query)
	print url
	result = geturlcontent(url)
	if result == None: return None
	# building html as a structure
	soup = BeautifulSoup(result, 'html.parser')
	count = 0
	# getting results, one by one
	for row in soup.find_all('tr')[1:]:
		# extracting data in function of the patterns
		rowdata = dataextractor(row, EXTRACTIONPATTERNS_GENERAL)
		# checking if something gone wrong
		if rowdata == None: continue
		# checking if magnet link is present
		if rowdata.get('magnet') == None: continue
		# retrieving right verified field
		if rowdata.get('verified') == None: verified = False
		else: rowdata['verified'] = rowdata.get('verified').lower() == VERIFIEDSTRING.lower()
		if verified and not rowdata.get('verified'): continue
		# retrieving right uploader field
		if rowdata.get('uploader') != None:
			rowdata['uploader'] = rowdata.get('uploader').replace('\n', ' ').split(' ')
			rowdata['uploader'] = [x for x in rowdata.get('uploader') if x][2]
		# retrieving detailed information, if needed
		if DETAILEDRESULTS and rowdata.get('link') != None:
			# getting further torrent information
			result = geturlcontent(rowdata.get('link'))
			if result == None: continue
			# building html as a structure
			soup = BeautifulSoup(result, 'html.parser')
			# extracting data in function of the patterns
			elementdata = dataextractor(soup, EXTRACTIONPATTERNS_DETAIL)
			# merging arrays
			rowdata.update(elementdata)
			# computing peers field
			rowdata['peers'] = str(int(rowdata.get('seeders')) + int(rowdata.get('leechers')))
			# retrieving right infohash field
			rowdata['infohash'] = rowdata.get('infohash').split(': ')[1]
			# retrieving right sizebytes field
			rowdata['sizebytes'] = re.sub('\D', '', str(re.findall('\((.*?)\)', rowdata.get('sizebytes')[rowdata.get('sizebytes').rindex('('):])))
		records.append(rowdata)
		# checking result limits
		count += 1
		if LIMITRESULTS > 0 and count >= LIMITRESULTS: break
	return convertrecordstoxml(records)

def getconvertedparameters(par):
	res = ''
	l = par.lower().split(' ')
	for el in l:
		if not ':' in el:
			if res != '': res += SEPARATOR
			res += el
		else:
			kv = el.split(':')
			if kv[0] == 'season':
				res += SEPARATOR+'s'
				if int(kv[1]) < 10: res += '0'
				res += kv[1]
			if kv[0] == 'episode':
				res += 'e'
				if int(kv[1]) < 10: res += '0'
				res += kv[1]
	return res

class KATService(object):
	@cherrypy.expose
	def default(self,*args,**kwargs):
		cherrypy.response.headers["Content-Type"] = "text/xml; charset=utf-8"
		par = ''
		url = cherrypy.url()
		if SONARRSEARCHFORMAT in url: par = getconvertedparameters(re.findall(SONARRSEARCHFORMAT+'(.*?)/', url)[0])
		verified = ('verified:1' in url.lower())
		r = search(par, verified)
		print r
		return r

if __name__ == u"__main__":
	cherrypy.server.socket_host = LISTENADDRESS
	cherrypy.config.update({'server.socket_port': LISTENPORT})
	cherrypy.quickstart(KATService())
