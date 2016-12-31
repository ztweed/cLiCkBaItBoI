## BOT FOR PARSING P4K TWEETS ##

## RUN EVERY FIVE MINUTES ##

## Prelims
from selenium import webdriver
from p4kRevs import p4kRevs
from lxml import etree
import os
import urllib3 as urllib
import xml.etree.ElementTree as ET
import tweepy, time, sys, requests, lxml, ast

# Handles REVIEWS
def p4kRevs(xmlTree, xmlText, dct):
    headline = dct['headline'].upper()
    metaList = xmlTree.findall('head/meta')

    for i in range(0, len(metaList)-1):
        if metaList[i].attrib['name'] == "og:description":
            ogDesc = metaList[i].attrib['content']

    ogDesc = ogDesc.upper()

    return headline + "\n" + ogDesc

# p4k stuff
acct = '@pitchfork'

# my api stuff
print("Authenticating API...")
CONSUMER_KEY = os.environ['CONSUMER_KEY']
CONSUMER_SECRET = os.environ['CONSUMER_SECRET']
ACCESS_KEY = os.environ['ACCESS_KEY']
ACCESS_SECRET = os.environ['ACCESS_SECRET']
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth)
print("Done!")

## Get link from last tweet!
print("Retrieving tweets...")
lrt     = api.user_timeline(acct, count = 20)
twtText = lrt[15].text
twtID   = lrt[15].id
delim   = 'http'
parsTwt = twtText.split(delim,2)
link    = delim + parsTwt[len(parsTwt)-1]
print("Done!")

## Get source XML from last tweet, find article type
print("Parsing XML...")
# Get link and determine where it sends us
page    = requests.get(link, headers={'User-Agent': 'Mozilla/5.0'}) #headers arg prevents 403 forbidden error
finDest = page.history[len(page.history)-1].url
host    = urllib.util.parse_url(finDest).host

# If the link brings us to p4k...
if host == "p4k.in":
    xmlText = page.text
    parser  = etree.XMLParser(recover=True) #ignores errors when parsing
    xmlTree = etree.fromstring(xmlText, parser=parser)
    script  = xmlTree.findtext("head/script") # get string of relevant attribs
    myDict  = ast.literal_eval(script)        # transform previous step into dictionary
    print("Done!")

    # Make Decisions Based on Article Type
    print("Writing tweet...")
    if myDict['articleSection'] == 'reviews':
        myTweet = p4kHelps(xmlTree, xmlText, myDict)
        print("Done!")
        print("Sending Tweet...")
        myTweetLen = 136 - len(acct)
        myTweet = acct + " " + myTweet[:myTweetLen] + "..."
        api.update_status(myTweet, twtID)
        print("Tweet sent!")
    else:
        print("Abort: This article is " + myDict['articleSection'] + "!")

else:
    print("Abort: Foreign Host!")
