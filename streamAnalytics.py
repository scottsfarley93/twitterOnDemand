__author__ = 'scottsfarley'
import twython
from twython import Twython
from twython import TwythonStreamer
import datetime
import requests.exceptions
import logging
from collections import Counter

import cherrypy


##twitter api authentication
api_key = 	"fQywb4rHpso30eOcczmKyuerD"
api_secret = "t751z3ONA81s8kFiVO6aLL3bWNBzHglhxwV8p3XGLj60IRKg1v"
accessToken = "222614775-p921FcG0iwAnpIwYyKsHbVWyr3IqQ9TyeHZFc2wz"
accessSecret = "fCvBReHfOD67MO7urbDipnrYxDJsZDWTgw4CLoqZjm1xP"


from math import sqrt

def zscore(obs, pop):
    # Size of population.
    number = float(len(pop))
    # Average population value.
    avg = sum(pop) / number
    # Standard deviation of population.
    std = sqrt(sum(((c - avg) ** 2) for c in pop) / number)
    # Zscore Calculation.
    return (obs - avg) / std



class Analytics:
    def __init__(self):
        self.allHashtags = [] ## list of all hashtags
        self.trending = []
        self.rate = 0
        self.n = 0
        self.allURLs = []
        self.allMentions = []
        self.allUsers = []
        self.allLocations = []
        self.allPlatforms = []
        self.allLanguages = []
        self.allTimezones = []
        self.rankedLanguages = Counter()
        self.rankedPlatforms = Counter()
        self.rankedLocations = Counter()
        self.rankedUsers = Counter()
        self.rankedTimezones = Counter()
        self.rankedMentions = Counter()
        self.rankedURLS = Counter()
        self.rankedHashtags = Counter()
        self.timestamps = []
        self.init = datetime.datetime.now()
        self.exTimes = []
        self.maxRate = -1
        self.minRate = 10000


    def addTweet(self, tweetJSON):
        try:
            entities = tweetJSON['entities']
            hashtags = entities['hashtags']
            ##add the hashtags
            for h in hashtags:
                self.allHashtags.append(h['text'])
            ##add the urls
            urls = entities['urls']
            for u in urls:
                self.allURLs.append(u['expanded_url'])
            ##add the userMentions
            mentions = entities['user_mentions']
            for m in mentions:
                self.allMentions.append(m['screen_name'])
            ##add the user locations
            loc = tweetJSON['user']['location']
            self.allLocations.append(loc)
            ##add the timezone
            tz = tweetJSON['user']['time_zone']
            self.allTimezones.append(tz)
            ## add the platform
            platform = tweetJSON['source']
            self.allPlatforms.append(platform)
            ## add the user
            username = tweetJSON['user']['screen_name']
            self.allUsers.append(username)
            ## add the language
            lang = tweetJSON['lang']
            self.allLanguages.append(lang)
            self.n += 1
            ## add the timestamp
            self.timestamps.append(datetime.datetime.now())
        except Exception as e:
            print str(e)

    def updateHashtags(self):
        self.rankedHashtags = Counter(self.allHashtags)
    def updateLanguages(self):
        self.rankedLanguages = Counter(self.allLanguages)
    def updateLocations(self):
        self.rankedLocations = Counter(self.allLocations)
    def updateURLs(self):
        self.rankedURLS = Counter(self.allURLs)
    def updatePlatforms(self):
        self.rankedPlatforms = Counter(self.allPlatforms)
    def updateUsers(self):
        self.rankedUsers = Counter(self.allUsers)
    def updateMentions(self):
        self.rankedMentions = Counter(self.allMentions)
    def updateTimezones(self):
        self.rankedTimezones = Counter(self.allTimezones)

    def returnAnalytics(self, p=5):
        out = {
            "numTweets" : self.n,
            "topHashtags" : self.rankedHashtags.most_common(p),
            "topLocations" : self.rankedLocations.most_common(p),
            "topMentions": self.rankedMentions.most_common(p),
            "topTimezones":self.rankedTimezones.most_common(p),
            "topUsers":self.rankedUsers.most_common(p),
            "topPlatforms":self.rankedPlatforms.most_common(p),
            "topURLS":self.rankedURLS.most_common(p),
            "topLanguages":self.rankedLanguages.most_common(p),
            "timestamp" :str(datetime.datetime.now()),
            "avgRate" : self.longTermAverage(),
            "executionTime" : self.avgExTime(),
            "currentRate" : self.currentRate(),
            "minRate" : self.minRate,
            "maxRate" : self.maxRate,
        }
        print out
        return out

    def longTermAverage(self):
        now = datetime.datetime.now()
        td = now - self.init
        secs = td.total_seconds()
        avg = self.n / secs
        return avg

    def avgExTime(self):
        a = 0
        for i in self.exTimes:
            a += i.total_seconds()
        return a / self.n

    def currentRate(self, seconds=10):
        ago = datetime.datetime.now() - datetime.timedelta(seconds=seconds)
        num = 0
        for ts in self.timestamps:
            if ts > ago:
                num += 1
        avg = num / float(seconds)
        if avg > self.maxRate:
            self.maxRate = avg
        if avg < self.minRate:
            self.minRate = avg





    def onTweet(self, tweet):
        exStart = datetime.datetime.now()
        self.addTweet(tweet)
        self.updateHashtags()
        self.updateLanguages()
        self.updateLocations()
        self.updateMentions()
        self.updatePlatforms()
        self.updateTimezones()
        self.updateURLs()
        self.updateUsers()
        self.returnAnalytics()
        exEnd = datetime.datetime.now()
        exTime = exEnd - exStart
        self.exTimes.append(exTime)



A = Analytics()


class TweetListener(TwythonStreamer):
    def on_success(self, data):
        A.onTweet(data)
        return True ## keep alive
    def on_error(self, status_code, data):
        print status_code, data
        return True
    def on_timeout(self):
        return True


stream = TweetListener(api_key, api_secret, accessToken, accessSecret)
stream.statuses.filter(track='syria, election')


