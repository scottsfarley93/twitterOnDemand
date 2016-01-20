import tweepy
import json
import psycopg2
##twitter
api_key = 	"s9XZr91SwqZbUpYbT9LNy0bJV"
api_secret = "E2eugOjfxUFJWa9T5rsIU6MChRMRxUD8Xi5IN4m4EKSB3W7NWv"


accessToken = "222614775-p921FcG0iwAnpIwYyKsHbVWyr3IqQ9TyeHZFc2wz"
accessSecret = "fCvBReHfOD67MO7urbDipnrYxDJsZDWTgw4CLoqZjm1xP"

auth = tweepy.OAuthHandler(api_key, api_secret)
auth.set_access_token(accessToken, accessSecret)


##open an app-wide connection to the database
database = "twitterOnDemand"
username = "postgres"
hostname = "localhost"
password = "Sequoia93!"
connectString = "dbname='" + str(database) + "' user='" + str(username) + "' host='" + str(hostname) + "' password='" + str(password) + "'"
connection = psycopg2.connect(connectString)
dbCursor = connection.cursor()

api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
counter = 0
cursor = tweepy.Cursor(api.search, q='debate')
for i in cursor.items():
    try:
        text = i.text.replace("'", '"').encode('ascii','ignore')
        source = i.source.replace("'", '"').encode('ascii','ignore')
        entities = i.entities
        hashtagsEntities = entities[u'hashtags']
        hashtagsText = "{"
        for h in hashtagsEntities:
            hashtagsText += (str(h['text'].strip("'").replace("'", '"')).encode('ascii','ignore')) + ","
        if hashtagsText[-1] == ",":
            hashtagsText = hashtagsText[:-1]
        hashtagsText += "}"
        userDetails = i.user
        userName = str(userDetails.name)
        userName = userName.replace("'", '"').encode('ascii','ignore')
        userLocation = str(userDetails.location)
        userLocation = userLocation.replace("'", '"').encode('ascii','ignore')
        timezone = str(userDetails.time_zone)
        timezone = timezone.replace("'", '"').encode('ascii','ignore')
        timestamp = i.created_at
        lang = str(i.lang)
        j = str(i._json)
        j = j.strip("'")
        j = j.encode("ascii", "ignore")
        j = j.replace("'", '"')


        sql = '''INSERT INTO "Tweets"("recordID", "tweetText", "tweetPlatform", hashtags, "User", "Location", language, timezone, raw_response, "time") VALUES'''
        sql += "(Default, '" + str(text) + "','"  + str(source) + "','" + str(hashtagsText) + "', '" + str(userName) + "','" + str(userLocation) + "','" + str(lang) + "','" + str(timezone) + "','" + j + "', '" + str(timestamp) + "');"
        dbCursor.execute(sql)
        print counter
        counter += 1
        connection.commit()
    except Exception as e:
        print str(e)
connection.commit()
