# -*- coding: utf-8 -*-
"""
Created on Sun Mar 09 23:51:34 2014

@author: Eric Conklin
"""

import datetime, json, LocationResolver, re
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

UNIX_EPOCH = (1970, 1, 1)

class TweetFormatter:
    def __init__(self):
        self.locator = LocationResolver.LocationResolver()
    # end __init__
        
    def JSONizer(self, thing):
        return json.dumps(thing)
    # end JSONizer
            
    def formatTweets(self, rawTweets):
        # check for retweets
        for tweet in rawTweets:
            reTweet = tweet.GetRetweeted_status()
            if reTweet:
                rawTweets.append(reTweet)
        
        rawUsers = [tweet.GetUser() for tweet in rawTweets]
        
        userList = []
        for user in rawUsers:
            # extract user data
            uID = str(user.GetId())
            uSN = user.GetScreenName()
            uLOC = user.GetLocation() or None
            
            userDict = {'user_id': uID, 
                        'screen_name': uSN,
                        'location': uLOC}
            #print userDict
            
            userList.append(userDict)
            
        #print 'num users=', len(userList)
            
        tweetList = []
        for tweet in rawTweets:
            # convert twitter stamp into a form acceptable to datetime
            dtStr = tweet.GetCreatedAt().replace('+0000', 'UTC').strip()
            
            # create datetime object
            dt = datetime.datetime.strptime(dtStr, '%a %b %d %H:%M:%S %Z %Y')
            
            # get seconds from unix epoch from datetime object
            stamp = int((dt - datetime.datetime(*UNIX_EPOCH)).total_seconds())
            
            # extraxt tweet data
            tID = tweet.GetId()
            tCA = str(dt) + ' UTC'
            tSTMP = stamp
            tTXT = re.sub('https?://[^\s]+', '', tweet.GetText())
            tUID = str(tweet.GetUser().GetId())
            tRTC = tweet.GetRetweetCount() or 0
            
            tCOORDS = tweet.GetCoordinates() or None
            if tCOORDS: tCOORDS = json.dumps(tCOORDS)
            
            tPLC = tweet.GetPlace() or None
            if tPLC: tPLC = tPLC['name']
            
            loc = self.locator.resolveLocationFromTweet(tweet.AsDict())
            
            if loc:
                temp1 = loc.getCity() or "Unknown"
                temp2 = loc.getCounty() or "Unknown"
                tLOC = str(temp1) + ', ' + str(temp2)
            else:
                tLOC = "Unknown, Unknown"
            
            tweetDict = {'tweet_id': tID,
                         'created_at': tCA,
                         'time_stamp': tSTMP,
                         'text': tTXT,
                         'user_id': tUID,
                         'retweet_count': tRTC,
                         'coordinates': tCOORDS,
                         'place_name': tPLC,
                         'location': tLOC}
            
            tweetList.append(tweetDict)
        #end for loop
            
        return userList, tweetList, rawTweets
    # end formatTweets
        
    def createFeatureCollection(self, tweets):
        featureCollection = []
        for tweet in tweets:
            featureCollection.append(tweet)
        return featureCollection
    # end createFeatureCollection


def main():
    import my_database, twitter

    DBname = 'twitter_data.db'

    db = my_database.MyDatabase(DBname)
    db.openConn()
    form = TweetFormatter()
    
    try:
        db.dropTable('formatted_tweets')
    finally:
        db.init()
        
    tweets = db.getRawTweets()
    
    tweetList = []
    for tweet in tweets:
        twt = json.loads(tweet)
        tweetList.append(twitter.Status.NewFromJsonDict(twt))

    users, formattedTweets, rawTweets = form.formatTweets(tweetList)
    db.storeFormattedTweets(formattedTweets)
    db.closeConn()

if __name__ == '__main__':
    main()