# -*- coding: utf-8 -*-
"""
Created on Sat Apr 12 17:50:42 2014

@author: Eric Conklin
"""

import my_database, json
from os.path import join
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

DBfile = 'twitter_data.db'
label_file = join('data', 'train_labels.txt')
ref_file = join('data', 'ref_tweets.json')
            
def main():
    DB = my_database.MyDatabase(DBfile)
    DB.openConn()
    
    tweets = DB.getFormattedTweets()
    
    DB.closeConn()
            
    labelledTweets = []
    try:
        f = open(label_file, 'r')
        labelledTweets = json.load(f)
    except Exception as e:
        print e
    f.close()
        
    tweetIDs = []
    for twt in labelledTweets:
        tweetIDs.append(twt[0])
    
    refTweets = []

    num = 1
    print 'total tweets=', len(tweets)
    print 'labelled tweets=', len(labelledTweets)
    print 'unlabelled tweets=', (len(tweets) - len(labelledTweets))
    for tweet in tweets:
        if tweet['tweet_id'] in tweetIDs:
            refTweets.append(tweet)
            continue
        
        print '**********'
        print 'tweet numer:', num
        num += 1
        print tweet['tweet_id'] + ':', tweet['text']
        print '**********'
        val = None
        while val != True and val != False:
            val = None
            val = raw_input('t/f? > ')
            
            if val.lower() == 't':
                val = True
                refTweets.append(tweet)
            elif val.lower() == 'f':
                val = False
                refTweets.append(tweet)
            elif val.lower() == 'q':
                val = None
                break

        if val is None:
            break
            
        twt = [tweet['tweet_id'], val]
        labelledTweets.append(twt)
        
    with open(ref_file, 'w') as f:
        json.dump(refTweets, f)
        
    with open(label_file, 'w') as f:
        json.dump(labelledTweets, f)
    
if __name__ == "__main__":
    main()