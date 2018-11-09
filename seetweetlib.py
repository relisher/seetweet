#!/usr/bin/python
# -*- coding: utf-8 -*-

#SeeTweet 2.2.0 splits the Python script into a library of useful functions (seetweetlib.py)
# that hopefully won't need customized, and the main script (seetweet220.py) that should be the locus of customization.

twitterfolder = './twitter-1.14.2/'


versionnum = '2.2.0'

import io
import sys
import re
import os
from time import localtime,strftime,sleep,time

#Add the Python twitter module
#Twitter package from http://pypi.python.org/pypi/twitter, under MIT License
#by Mike Verdone, http://mike.verdone.ca/twitter
if os.path.exists(twitterfolder):		#specify where to look for twitter if not already on path
	sys.path.append(twitterfolder)
from twitter import *


#Function to import city names, states, and coordinates from USGS Board on Geographic Names Gazetter
# obtained from http://geonames.usgs.gov/domestic/download_data.htm
def importcitylist(infile='NationalFile_20120204.txt.cities'):
	#Loading city data
	cities = {}
	rf = io.open(infile,'r', encoding="utf-8")
	for line in rf:
		splitline = line.split(',')
		state = splitline[1]
		if state not in cities:
			cities[state] = {}
		cities[state][splitline[0]] = [float(splitline[2]),float(splitline[3])]
	rf.close()
	return cities


#Function replaces full versions of states with their postal codes for USGS National File matching
#Note: may want to extend this with other abbreviations for the states
def replacestates(text):
	text = re.sub('uk(raine)?\Z','UA',text)
	text = re.sub('Укр(аина)?\Z','UA',text)
	text = re.sub('Україна\Z','UA',text)
	return text

def findcities(text):
	text =  u''.join(text).lower().encode('utf-8').strip()
	for city in cities['UA']:
		city = u''.join(city).lower().encode('utf-8').strip()
		if city in text:
			return [city,'unk',city,'UA']
	return None

def getlimits(tsearch):
	errors = 0
	maxerrors = 3
	while (errors < maxerrors):
		try:
			r = tsearch.application.rate_limit_status(resources='search')
			break
		except TwitterHTTPError as e:
			errors = errors + 1
			print "Twitter Error encountered. Retrying",MAXERRORS-errors,"more times."
			print "\n"+e.response_data
			sleep(5)
	if (errors==MAXERRORS):
		print "Repeated errors encountered, possibly due to rate limit."
		print "Will wait 15 minutes and try once more before quitting."
		sleep(900)
		try:
			r = tsearch.application.rate_limit_status(resources='search')
		except:
			raise Exception("Gave up because of repeated errors, sorry.")
	return r['resources']['search']['/search/tweets']

def parsetime(timestr):
	#Assumes Twitter is still reporting a tweet's time as, e.g.,:
	# "Wed Aug 27 13:08:45 +0000 2008"
	#Returns list of: day,year,month,date,hour,minute,second
	monthdict = {'Jan':'1','Feb':'2','Mar':'3','Apr':'4','May':'5','Jun':'6','Jul':'7','Aug':'8','Sep':'9','Oct':'10','Nov':'11','Dec':'12'}
	timesplit = re.split('[: ]',timestr)
	timelist = [timesplit[0],timesplit[7],monthdict[timesplit[1]]]
	timelist.extend(timesplit[2:6])
	return ','.join(timelist)

def extractinfo(res,wff=False):
	outputline = ''
	outcome = ''
	tid = res['id_str']
	tweettime = parsetime(res['created_at'])
	tweet = cleantweetre.sub(' ',res['text'])+'\n'
	try:
		uid = res['user']['id_str']
	except:
		tweetline = 'unk,unk,'+u''.join(tid).encode('utf-8').strip()+','+tweet
		return ['','nouserinfo',tid,tweetline]

	if res['geo']:
		test_str = 'GEO: '+str(res['geo']['coordinates'])+' '+u''.join(tweet.strip()).encode('utf-8').strip()
		print test_str
		outcome = 'geo'
		origloc = str(res['geo']['coordinates'][0])+','+str(res['geo']['coordinates'][1])
		outputline = outcome+','+'unk,unk,'+origloc+','+u''.join(uid).encode('utf-8').strip()+','+u''.join(tid).encode('utf-8').strip()+ ',' + u''.join(tweet.strip()).encode('utf-8').strip() + '\n'
	elif res['coordinates']:
		test_str = 'COORD: '+str(res['coordinates']['coordinates'])+' 'u''.join(tweet.strip()).encode('utf-8').strip()
		print u''.join(test_str).encode('utf-8').strip()
		outcome = 'coordinates'
		origloc = str(res['coordinates']['coordinates'][0])+','+str(res['coordinates']['coordinates'][1])
		outputline = outcome+','+'unk,unk,'+origloc+','+u''.join(uid).encode('utf-8').strip()+','+u''.join(tid).encode('utf-8').strip()+ ',' + u''.join(tweet.strip()).encode('utf-8').strip() + '\n'
	else:
		loc = res['user']['location'].lower().strip()
		print u''.join(loc).encode('utf-8').strip()
		origloc = loc.replace(',',' ')
		lr = utre.match(loc)
		if lr:
			test_str = 'UT: ['+lr.group(2)+','+lr.group(3)+'] 'u''.join(tweet.strip()).encode('utf-8').strip()
			print u''.join(test_str).encode('utf-8').strip()
			outcome = 'ut'
			outputline = outcome+','+'unk,unk,'+lr.group(2)+','+lr.group(3)+','+u''.join(uid).encode('utf-8').strip()+','+u''.join(tid).encode('utf-8').strip()+ ',' + u''.join(tweet.strip()).encode('utf-8').strip() + '\n'
			#return [outputline,outcome,tid]
		else:
			#print 'L: '+loc+' '+res['text']
			ll = llre.search(loc)
			if ll:
				test_str = 'LL: '+loc+' 'u''.join(tweet.strip()).encode('utf-8').strip()
				print u''.join(test_str).encode('utf-8').strip()
				outcome = 'llprofile'
				outputline = outcome+','+'unk,unk,'+ll.group(1)+','+ll.group(2)+','+u''.join(uid).encode('utf-8').strip()+','+u''.join(tid).encode('utf-8').strip() + ',' + u''.join(tweet.strip()).encode('utf-8').strip() + '\n'
				#return [outputline,outcome,tid]
			else:
				loc = loc.replace('.','')
				r = cityre.search(loc)
				if r:
					city = r.group(1).strip()
					state = r.group(2).replace('.','')
					if state in cities:
						if city in cities[state]:
							test_str = 'CS: '+city+','+state+' 'u''.join(tweet.strip()).encode('utf-8').strip()
							print u''.join(test_str).encode('utf-8').strip()
							outcome = 'citystate'
							outputline = outcome+','+city+','+state+','+str(cities[state][city][0])+','+str(cities[state][city][1])+','+u''.join(uid).encode('utf-8').strip()+','+u''.join(tid).encode('utf-8').strip()+ ',' + u''.join(tweet.strip()).encode('utf-8').strip() + '\n'
							tweetline = ','.join([origloc,uid,tid,tweet])
							return [','.join([tweettime,outputline]),outcome,tid,tweetline]	#skip the rest of the manual city list
				cityres = findcities(loc)
				if cityres:
					test_str = 'KC: '+ cityres[0] +' ' +  u''.join(tweet.strip()).encode('utf-8').strip()
					print test_str
					outcome = 'knowncity'
					test = outcome+ ','+ cityres[0]+ ','+cityres[1]+ ',' + ','+cityres[2]+ ','+cityres[3]+ ','+u''.join(uid).encode('utf-8').strip()+','
					outputline = outcome+ ','+ cityres[0]+ ','+cityres[1]+ ','+cityres[2]+ ','+cityres[3]+ ','+u''.join(uid).encode('utf-8').strip()+','+u''.join(tid).encode('utf-8').strip()+ ',' + u''.join(tweet.strip()).encode('utf-8').strip() + '\n'
				else:
					#print 'Unsuccessful loc: ',loc,' (from user ',uid,')\n'
					test_str = 'F: '+origloc+' '+uid
					test_str = u''.join(test_str).encode('utf-8').strip()
					print test_str +' ' +  u''.join(tweet.strip()).encode('utf-8').strip()
					outcome = 'failure'
					if wff:
						failline = origloc+'\n'
						wff.write(failline.encode('ascii','ignore'))
	csvloc = origloc.replace(',',';')						#Removing excess commas for storing tweet in a CSV
	tweetline = ','.join([csvloc,uid,tid,tweet])
	if outputline:
		outputline = ','.join([u''.join(tweettime).encode('utf-8').strip(),outputline])			#Adding time iff there is something to output
	return [outputline,outcome,tid,tweetline]

def balanceandprint(tl,mintids,maxtids,searchesleft,wf):
	maxoutcutoff = 2 			#A search is considered to have maxed out if this many searches left
	maximin = float("+inf")
	print "Balancing multi-location search results."
	#print searchesleft
	#print maxtids
	#print mintids
	ranges = [0]*len(maxtids)
	for locnum in range(0,len(maxtids)):
		ranges[locnum] = (maxtids[locnum]-mintids[locnum])
		if searchesleft[locnum] <= maxoutcutoff:
			maximin = min(maximin,ranges[locnum])	#maximin is the max min tid of searches that did max out
	#print ranges
	print "maximin:",maximin
	for locnum in range(0,len(tl)):
		cutoffs = 0
		#print "accept after", long(maxtids[locnum]-maximin), "for loc", locnum
		for resnum in range(0,len(tl[locnum])):
			#print "curr tweet: ", tl[locnum][resnum][2]
			#weight = str(maximin/ranges[locnum])			#Weights for a search location as relative rate to most productive search
			if maximin==float("+inf"):
				wf.write(tl[locnum][resnum][0][:-1]+",1\n")
			elif tl[locnum][resnum][2] >= (maxtids[locnum]-maximin):	#If current hit comes after the cutoff
				wf.write(tl[locnum][resnum][0][:-1]+",1\n")
			else:
				wf.write(tl[locnum][resnum][0][:-1]+",0\n")
				cutoffs = cutoffs + 1
		print cutoffs, "cutoffs for loc", locnum
	return

#Function to perform OAuth authorization
#	Imports existing OAuth credentials if these exist,
#	otherwise prompts user to authorize SeeTweet & stores credentials
def authorize(app_oauth_file = 'app.oauth',cons_oauth_file = 'cons.oauth'):
	constoken, conssecret = read_token_file(cons_oauth_file)				#SeeTweet's information
	if not os.path.exists(app_oauth_file):									#if user not authorized already
		oauth_dance("SeeTweet "+versionnum,constoken,conssecret,app_oauth_file)		#perform OAuth Dance
	apptoken, appsecret = read_token_file(app_oauth_file)					#import user credentials
	tsearch = Twitter(auth=OAuth(apptoken,appsecret,constoken,conssecret))	#create search command
	return tsearch


################################################################################
#
# Global variable definitions
#
################################################################################

cities = importcitylist()
cityre = re.compile(u'([a-z ]+)[, ]+([a-z]{2})\Z',flags=re.I)
utre = re.compile(u'(üt|iphone): ([0-9\.]+[0-9]),(-[0-9\.]+[0-9])',flags=re.I)
llre = re.compile(u'([0-9\.]+[0-9]),(-[0-9\.]+[0-9])',flags=re.I)
depunctre = re.compile(u'[^a-z ]',flags=re.I)
cleantweetre = re.compile(u'[\n,]',flags=re.I)
MAXERRORS = 3
