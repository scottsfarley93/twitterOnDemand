__author__ = 'scottsfarley'
import cherrypy
import tweepy
from tweepy.streaming import StreamListener
from tweepy import Stream
import json
import Queue
import time
import datetime



## application-wide auth/setup
## happens once per server init
api_key = 	"s9XZr91SwqZbUpYbT9LNy0bJV"
api_secret = "E2eugOjfxUFJWa9T5rsIU6MChRMRxUD8Xi5IN4m4EKSB3W7NWv"


accessToken = "222614775-p921FcG0iwAnpIwYyKsHbVWyr3IqQ9TyeHZFc2wz"
accessSecret = "fCvBReHfOD67MO7urbDipnrYxDJsZDWTgw4CLoqZjm1xP"

auth = tweepy.OAuthHandler(api_key, api_secret)
auth.set_access_token(accessToken, accessSecret)
authStatus = True

api = tweepy.API(auth)
apiStatus = True

class analytics():
    def __init__(self):
        self.hashtags = {}
        self.languages = {}
        self.platforms = {}
        self.timezones = {}
        self.locations = {}
    def refreshHashtags(self, hashtagList):
        for entity in hashtagList:
            tag = entity['text']
            if tag not in self.hashtags:
                self.hashtags[tag] = 0
            self.hashtags[tag] += 1

    def refreshPlatforms(self, platform):
        if platform not in self.platforms:
            self.platforms[platform] = 0
        self.platforms[platform] += 1

    def refreshTimezones(self, timezone):
        if timezone not in self.timezones:
            self.timezones[timezone] = 0
        self.timezones[timezone] +=1

    def refreshLanguages(self, language):
        if language not in self.languages:
            self.languages[language] = 0
        self.languages[language] += 1








class tweetStream(StreamListener):
    def __init__(self, queue):
        print queue
        self.queue = queue

    def on_status(self, status):
        print status
        self.queue.put(status)
    def on_data(self, raw_data):
        print raw_data
        self.queue.put(raw_data)
    def on_error(self, status_code):
        print status_code
        self.queue.put("Error!!!")
        self.queue.put(status_code)
        return False
    def on_timeout(self):
        print "Timeout"
        self.queue.put("Timeout")


##each function is a page call
##executed for each user
class App():
    def __init__(self):
        self.stream = None
        self.on = False
        self.streaming = False
        self.trackTerm = ""
        self.initTime = None
        self.timeSinceInit = 0
        self.totalCollectedTweets = 0
        self.numOutput = 0
        self.numInQueue = 0
        self.sessionQueue = None
        self.analytics = analytics()

    @cherrypy.expose
    def start(self):
        try:
            if self.on == False:
                self.sessionQueue = Queue.Queue()
                self.stream = Stream(auth, tweetStream(self.sessionQueue))
                self.stream.new_session()
                self.on = True
                self.initTime = datetime.datetime.now()
                currentTime = datetime.datetime.now()
                self.timeSinceInit = currentTime - self.initTime
                # user sessions
                if 'count' not in cherrypy.session:
                    cherrypy.session['count'] = 0
                cherrypy.session['count'] += 1
                return json.dumps({"success": True, 'data': None, "message": "New stream session initialized."})
            else:
                return json.dumps({"Success" : True, 'data':None, "message" : "Stream already started."})

        except Exception as e:
            self.on = False
            return json.dumps({"success": True, 'data': None, "message": "New stream session not started because " + str(e)})

    @cherrypy.expose
    def close(self):
        try:
            if self.on:
                self.stream.disconnect()
                self.on = False
                self.streaming = False
                self.sessionQueue = None
                return json.dumps({"success":True, 'data':None, "message":'Stream session terminated.'})
            else:
                return json.dumps({"success" : True, 'data':None, "message" : "Streaming already closed."})
        except Exception as e:
            return json.dumps({"success":False, 'data':None, "message":'Stream session not terminated because ' + str(e)})

    @cherrypy.expose
    def invisibleStream(self, toTrack, *args, **kwargs):
        try:
            if not self.streaming:
                self.stream.filter(track=[toTrack], async=True)
                self.streaming = True
                self.trackTerm = toTrack
                currentTime = datetime.datetime.now()
                self.timeSinceInit = currentTime - self.initTime
                return json.dumps({'success' :True, "data":None, "Message":"Stream is streaming."})
        except Exception as e:
            return json.dumps({"success" : False, "data":None, "message" : "Track stream failed because " + str(e)})

    @cherrypy.expose
    def trueStream(self, *args, **kwards):
        ##streams the connection as continuous json
        if not self.streaming:
            return json.dumps({"success" : False, "data":None, "message" : "Track stream failed because the application is not streaming."})
        try:
            def getTweetsFromQueue():
                t = 0
                while True:
                    t += 1
                    yield str(self.sessionQueue.get())
                    self.numOutput += 1
                self.stream.disconnect()
            return getTweetsFromQueue()
        except Exception as e:
            return json.dumps({"success" : False, "data":None, "message" : "Track stream failed because " + str(e)})

    @cherrypy.expose
    def pollStream(self):
        ## publishes all items currently in the queue as a json object
        # if not self.streaming:
        #     self.invisibleStart(toTrack) ##start streaming if not already
        outArr = []
        q = 0
        queueCopy = self.sessionQueue
        # for i in range(0, 100):
        #     queueCopy.put(i)
        self.totalCollectedTweets = self.numInQueue + self.numOutput
        while queueCopy.qsize() > 0:
            a =  queueCopy.get()
            outArr.append(a) ##puts the tweets into the raw output
            obj = json.loads(a)
            hashes = obj['entities']['hashtags']
            self.analytics.refreshHashtags(hashes)
            self.analytics.refreshPlatforms(obj['source'])
            self.analytics.refreshTimezones(obj['user']['time_zone'])
            self.analytics.refreshLanguages(obj['lang'])
            q += 1
        self.numOutput += q

        out = {
            "success" :True,
            "data" : outArr,
            "timezones": sorted(self.analytics.timezones.items(), key=lambda x: x[1], reverse=True),
            "platforms" : sorted(self.analytics.platforms.items(), key=lambda x: x[1], reverse=True),
            "languages" : sorted(self.analytics.languages.items(), key=lambda x: x[1], reverse=True),
            'hashtags': sorted(self.analytics.hashtags.items(), key=lambda x: x[1], reverse=True),
            "status": {
                "timeSinceInit" : str(self.getTimeSinceInit()),
                "streaming" :str(self.streaming),
                "connected" : str(self.on),
                "streamStarted" : str(self.initTime),
                "inQueue" : str(self.sessionQueue.qsize()),
                "processed" :str(self.numOutput),
                "totalCollected" : str(self.totalCollectedTweets)
            },
            "message": "Request fulfilled successfully.  Data is still streaming."
        }
        return json.dumps(out)

    @cherrypy.expose
    def dashboard(self):
        return open("dashboard.html")





    @cherrypy.expose
    def returnStatus(self):
        self.numInQueue = self.sessionQueue.qsize()
        self.totalCollectedTweets = self.numInQueue + self.numOutput
        s = "Server State: " + str(cherrypy.engine.state) + "<br />"
        s += "Streaming Connected: " + str(self.on) + "<br />"
        s += "Currently Streaming? " + str(self.streaming) + "<br />"
        s += "Tracking Term: "+ str(self.trackTerm) + "<br />"
        s += "Start Time:  " + str(self.initTime) + "<br />"
        s += "Time since initialization: " + str(self.getTimeSinceInit()) + "<br />"
        s += "Queue size: " + str(self.sessionQueue.qsize()) + '<br />'
        s += "Printed tweets: " + str(self.numOutput) + "<br />"
        s += 'Total collected tweets: '  + str(self.totalCollectedTweets) + "<br />"
        return s

    def getTimeSinceInit(self):
        if self.on:
            currentTime = datetime.datetime.now()
            self.timeSinceInit = currentTime - self.initTime
            print self.timeSinceInit
        else:
            return 0

    @cherrypy.expose
    def getNumInQueue(self):
        return str(self.numInQueue)

    @cherrypy.expose
    def getNumPrinted(self):
        return str(self.numOutput)

    @cherrypy.expose
    def getTotalCollected(self):
        self.totalCollectedTweets = self.numInQueue + self.numOutput
        return str(self.totalCollectedTweets)
    @cherrypy.expose
    def getSession(self, key=None):
        if key is None:
            return str(cherrypy.session.__dict__)
        else:
            if key in cherrypy.session:
                return str(cherrypy.session[key])
            else:
                return str(None)


if __name__ == '__main__':
    config = {
        "/" :{
            "response.stream" : True,
            "tools.sessions.on" :True
        }
    }
    cherrypy.quickstart(App(), "/", config)


