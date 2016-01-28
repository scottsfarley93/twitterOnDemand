##import
from twython import Twython
from twython import TwythonStreamer
import datetime
import requests.exceptions

##log file config
import logging
logging.basicConfig(filename='/users/scottsfarley/documents/twitter.log',level=logging.INFO, format='%(levelname)s: %(asctime)s  %(message)s ', datefmt='%m/%d/%Y %I:%M:%S %p')
logging.info("Program start.")
print "Logging configured."

database = "twitterOnDemand"
username = "postgres"
host = "localhost"
pw = "Sequoia93!"

##database connection
import psycopg2
connectString = "dbname='" + str(database) + "' user='" + str(username) + "' host='" + str(host) + "' password='" + str(pw) + "'"
conn = psycopg2.connect(connectString)
if not conn:
    logging.critical("Failed to connect to database.")
else:
    logging.info("Database connection successful.")
print "Database configured."

##twitter api authentication
api_key = 	"fQywb4rHpso30eOcczmKyuerD"
api_secret = "t751z3ONA81s8kFiVO6aLL3bWNBzHglhxwV8p3XGLj60IRKg1v"
accessToken = "222614775-p921FcG0iwAnpIwYyKsHbVWyr3IqQ9TyeHZFc2wz"
accessSecret = "fCvBReHfOD67MO7urbDipnrYxDJsZDWTgw4CLoqZjm1xP"

exTimes = []

class TweetListener(TwythonStreamer):
    def on_success(self, data):
        sendToDB(data)
        return True ## keep alive
    def on_error(self, status_code, data):
        print status_code, data
        logging.critical("Error %s, message %s", status_code, data)
        return True
    def on_timeout(self):
        print "Execution timed out"
        logging.error("Timeout.  Retrying operation.")
        return True



def sendToDB(i):
    try:
        start = datetime.datetime.now()
        print i
        text = i[u'text'].replace("'", '"').encode('ascii','replace') ##message body
        source = i[u'source'].replace("'", '"').encode('ascii','replace') ##source platform
        if i[u'coordinates'] != None:
            lat = i[u'coordinates'][u'coordinates'][0]
            lng = i[u'coordinates'][u'coordinates'][1]
        else:
            lat = 0
            lng = 0
        entities = i[u'entities'] ##hashtags/urls/etc
        ##assemble hashtag array
        hashtagsEntities = entities[u'hashtags']
        hashtagsText = "{"
        for h in hashtagsEntities:
            hashtagsText += (h['text'].strip("'").replace("'", '"').encode('ascii','replace')) + ","
        if hashtagsText[-1] == ",":
            hashtagsText = hashtagsText[:-1]
        hashtagsText += "}"
        ##assemble url array
        urlEntities = entities[u'urls']
        urlText = "{"
        for u in urlEntities:
            urlText += u['expanded_url'].encode("ascii", "replace") + ","
        if urlText[-1] == ",":
            urlText = urlText[:-1]
        urlText += "}"
        if u'media' in entities.keys():
            ##assemble media (photos) array
            mediaEntities = entities[u'media']
            mediaText = "{"
            for m in mediaEntities:
                mediaText += m['expanded_url'].encode("ascii", "replace") + ","
            if mediaText[-1] == ",":
                mediaText = mediaText[:-1]
            mediaText += "}"
        else:
            mediaText = "{}"
        ##assemble user_mentions array
        mentionEntities = entities[u'user_mentions']
        mentionText = "{"
        for m in mentionEntities:
            mentionText += m['screen_name'].encode("ascii", 'replace') + ","
        if mentionText[-1] == ",":
            mentionText = mentionText[:-1]
        mentionText += "}"

        ##symbol array is default
        symbolText = "{}"
        userDetails = i[u'user']
        userName = str(userDetails[u'name'].encode("ascii", 'replace'))
        userScreenName = str(userDetails[u'screen_name'])
        userName = userName.replace("'", '"').encode('ascii','replace')
        userScreenName.replace("'", "").encode("ascii", "ignore")
        userLocation = userDetails[u'location']
        if userLocation is not None:
            userLocation = userLocation.encode("ascii", "replace").replace("'", '"')
        else:
            userLocation = "None"
        timezone = str(userDetails[u'time_zone'])
        timezone = timezone.replace("'", '"').encode('ascii','replace')
        timestamp = i[u'created_at']
        now = datetime.datetime.now()
        lang = str(i[u'lang'])
        ##create the insert statement
        queryString = '''INSERT INTO "Tweets3" VALUES (Default, '''
        queryString += "'" + text + "',"
        queryString += "'" + source + "',"
        queryString += "'" + userScreenName + "',"
        queryString += "'" + userName + "',"
        queryString += "'" + userLocation + "',"
        queryString += str(lat) + "," + str(lng) + ","
        queryString += "'" + lang + "',"
        queryString += "'" + timezone + "',"
        queryString += "'" + hashtagsText + "',"
        # queryString += "'" + mediaText + "',"
        queryString += "'{}',"
        queryString += "'" + urlText + "',"
        queryString += "'" + mentionText + "',"
        queryString += "'" + symbolText + "',"
        queryString += "'" + str(now) + "');"
        cursor = conn.cursor()
        cursor.execute(queryString)
        conn.commit()

        ##Table structure
        ## recordID // can be used as a primary key
        ## tweetText // tweet body
        ## tweetPlatform // application used to report tweet *twitter for iPhone, twitter Online, tweetdeck, etc
        ## userScreenName // twitter handle of user
        ## userRealName // real name of person recording tweet
        ## userLocation // semantic description of user location
        ## tweetLatitude // actual geolocation of tweet
        ## tweetLongitude // actual geolocation of tweet
        ## language // language of tweet as reported by twitter
        ## timezone // timezone of user as used by twitter for advertising
        ## hashtags // array of hashtag text
        ## media // array of media (photo) URLs
        ## urls // array of external urls
        ## userMentions // array of twitterHandles mentioned in this tweet
        ## symbols // financial symbols starting with the $ sign --> does anyone even do this?
        ## time // time of response
        #queryString += t[]
        finish = datetime.datetime.now()
        delta = finish - start
        exTimes.append(delta.total_seconds())
        print exTimes
    except Exception as e:
        logging.warning("Failed to record tweet because %s", str(e))

##go!

def streaming():
    while True:
        try:
            stream = TweetListener(api_key, api_secret, accessToken, accessSecret)
            print "Stream configured.  Starting data return..."
            logging.info("Starting twitter stream client.")
            stream.statuses.filter(track='Syria,Immigration,same-sex marriage,education,taxes,gun control, gay marriage, economy, health care, foreign policy, climate change, refugees')
        except requests.exceptions.ChunkedEncodingError:
            logging.error("Streaming error.  Will retry immediately.")
        except Exception as e:
            logging.critical("Fatal error %s.  Will retry.", str(e))
            continue
streaming()