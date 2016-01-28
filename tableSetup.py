import Queue

def createTable(host, username, pw, database, tableName):
    print "Started setup."
    import psycopg2
    connectString = "dbname='" + str(database) + "' user='" + str(username) + "' host='" + str(host) + "' password='" + str(pw) + "'"
    conn = psycopg2.connect(connectString)
    if not conn:
        print "Failed to connect to database."
    else:
        print "Connection to database: OKAY"
    sql = '''CREATE TABLE "''' + str(tableName) + '''" (
        recordID serial NOT NULL,
        tweetText text,
        tweetPlatform text,
        userScreenName text,
        userRealName text,
        userLocation text,
        tweetLatitude double precision,
        tweetLongitude double precision,
        language text,
        timezone text,
        hashtags text[],
        media text[],
        urls text[],
        userMentions text[],
        symbols text[],
        time time with time zone
        ) WITH (OIDS=FALSE);
        '''

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
        ## symbols // financial symbols starting with the $ sign
        ## time // time of response

    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()
    print "Created table: OKAY"
    cursor.execute('''ALTER TABLE "''' + str(tableName) + '''" OWNER TO ''' + str(username))
    print "Changed table ownership: OKAY"

#createTable("localhost", "postgres", "Sequoia93!", "twitterOnDemand", "Tweets3") ##set up the table to store all tweets from this event

