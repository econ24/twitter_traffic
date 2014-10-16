# -*- coding: utf-8 -*-
"""
Created on Mon Mar 10 00:18:30 2014

@author: Eric Conklin
"""
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

KEY_WORDS = ['highway', 'road', 'street', 'traffic', 'incident', \
            'northway', 'exit', 'lane', 'drive','slow', "backed up", \
            'blocked', 'congest', 'crash', 'wreck', 'closes', "gridlock", \
            'accident', 'car', 'truck', 'vehicle', 'bus', 'disabled', \
            "traffic jam", "bumper to bumper", 'closure', 'collide', \
            'collision']
            
LOCATIONS = set(['albany', 'troy', 'colonie', 'clifton park', 'rensselaer', 'watervliet'])

class TweetProcessor:
    def processTweets(self, formattedTweets):
        processedTweets = []
        ''' Process each formatted tweet.
        '''
        for tweet in formattedTweets:
            tweet['rating'] = self.__checkTweet(tweet, formattedTweets)
        
            if tweet['rating'] >= 4.0:
                tweet['rating'] = 1.0
            elif tweet['rating'] >= 0.0:
                tweet['rating'] = 0.0
            else:
                tweet['rating'] = -1.0
                
            processedTweets.append(tweet)
        return processedTweets
    # end processTweets
            
    def __checkTweet(self, tweet, tweets):
        ''' No need for retweets since already have main tweet.
        '''
        if tweet['text'].lower().count('rt @'):
            return 0.0
                    
        ''' Occurs when a textual duplicate, non-retweeted tweet appears.
        '''
        if 'rating' in tweet and tweet['rating'] == -1.0:
            return -1.0
            
        ''' Checks for textual duplicates, sums any retweet counts with most recent
        tweet's count, marks duplicate for later identification.
        Also increments most recent tweet's retweet count for every duplicate.
        '''
        for i in range(len(tweets)-1, -1, -1):
            if tweets[i] == tweet:
                break
            if tweets[i]['text'][0:len(tweets[i]['text'])//2] == tweet['text'][0:len(tweet['text'])//2]:
                if tweets[i]['time_stamp'] > tweet['time_stamp']:
                    tweets[i]['retweet_count'] = tweets[i]['retweet_count'] + tweet['retweet_count'] + 1
                    tweet['retweet_count'] = 0
                    return -1
                else:
                    tweet['retweet_count'] = tweets[i]['retweet_count'] + tweet['retweet_count'] + 1
                    tweets[i]['retweet_count'] = 0
                    tweets[i]['rating'] = -1.0
            
        ''' Simply count keywords.
        '''
        count = 0
        for word in KEY_WORDS:
            count += tweet['text'].lower().count(word)
        
        ''' Weight retweets with higher significance.
        '''
        count += (tweet['retweet_count'])*2.0
                    
        for location in LOCATIONS:
            if tweet['location'].lower().count(location):
                return count
            
        return 0.0
    # end __checkTweet
        
class Classifier:
    def processTweets(self, formattedTweets):
        processedTweets = []

        labels = self.classifier(formattedTweets, self.model, self.vocab)
        
        for index, label in enumerate(labels):
            tweet = formattedTweets[index]
            
            tweet['rating'] = self.__checkTweet(tweet, formattedTweets, label)
            
            processedTweets.append(tweet)
        
        return processedTweets
    # end processTweets
        
    def __checkTweet(self, tweet, tweets, label):
        ''' No need for retweets since already have main tweet.
        '''
        if tweet['text'].lower().count('rt @'):
            return 0.0
                    
        ''' Occurs when a textual duplicate, non-retweeted tweet appears.
        '''
        if 'rating' in tweet and tweet['rating'] == -1.0:
            return -1.0
            
        ''' Checks for textual duplicates, sums any retweet counts with most recent
        tweet's count, marks duplicate for later identification.
        Also increments most recent tweet's retweet count for every duplicate.
        '''
        for i in range(len(tweets)-1, -1, -1):
            if tweets[i] == tweet:
                break
                
            if 'rating' in tweets[i] and tweets[i]['rating'] == -1.0:
                continue
            
            if tweets[i]['text'] == tweet['text']:
                if tweets[i]['time_stamp'] > tweet['time_stamp']:
                    tweets[i]['retweet_count'] = tweets[i]['retweet_count'] + tweet['retweet_count'] + 1
                    tweet['retweet_count'] = 0
                    return -1.0
                else:
                    tweet['retweet_count'] = tweets[i]['retweet_count'] + tweet['retweet_count'] + 1
                    tweets[i]['retweet_count'] = 0
                    tweets[i]['rating'] = -1.0
                    
        for location in LOCATIONS:
            if tweet['location'].lower().count(location):
                return label
                
        return 0.0
    # end __checkTweet
        
class TweetClassifier(Classifier):
    def __init__(self):
        import tweet_classifier as classifier
        
        self.model = classifier.load_model('data/svm_model')
        self.vocab = classifier.load_json_file('data/svm_vocab.json')
        self.classifier = classifier.predict_new_tweets

class TweetClassifier2(Classifier):
    def __init__(self):
        import tweet_classifier_2 as classifier
        
        self.model = classifier.load_model('data/model.dat')
        self.vocab = classifier.loadFromJSON('data/vocab.txt')
        self.classifier = classifier.classifyTweets

def main():
    import my_database
    DBname = 'twitter_data.db'

    db = my_database.MyDatabase(DBname)
    db.openConn()
    proc = TweetClassifier2()
    
    try:
        db.dropTable('processed_tweets')
    finally:
        db.init()
    
    tweets = db.getFormattedTweets();
    processedTweets = proc.processTweets(tweets)
    db.storeProcessedTweets(processedTweets)
    db.closeConn()

if __name__ == '__main__':
    main()