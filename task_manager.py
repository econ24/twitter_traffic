# -*- coding: utf-8 -*-
"""
Created on Sun Mar 09 23:07:04 2014

@author: Eric Conklin
"""
import json, threading
import my_database, tweet_formatter, twitter_checker, tweet_processor

class TaskManager(threading.Thread):
    def __init__(self, server, DBname, taskEvent, cache):
        threading.Thread.__init__(self)
        self.__DB = my_database.MyDatabase(DBname)
        self.__API = twitter_checker.TwitterChecker()
        self.__formatter = tweet_formatter.TweetFormatter()
        self.__processor = tweet_processor.TweetClassifier2()#Processor()
        self.__cache = cache
        
        self.__working = True
        self.__shutDown = False
        
        self.__taskEvent = taskEvent
        
        self.__server = server
    # end __init__
        
    def isWorking(self):
        return self.__working
        
    def requestShutDown(self):
        print '<manager> shutdown signal received'
        self.__shutDown = True
        
    def run(self):
        print '<manager> Opening database connection'
        self.__DB.openConn()
        print '<manager> Initializing cache'
        self.__cache.refreshCache(self.__DB)
        
        while not self.__shutDown and self.__taskEvent.wait(60):
            self.__working = True
            print '<manager> Querying Twitter...'
            rawTweets = self.__crawlTwitter()
            print '<manager> Queried tweets=', len(rawTweets)
            if rawTweets:
                print '<manager> Formatting tweets'
                users, formattedTweets, rawTweets = self.__formatTweets(rawTweets)
                self.__storeRawTweets(rawTweets)
                self.__storeUsers(users)
                self.__storeFormattedTweets(formattedTweets)
                print '<manager> Processing tweets'
                processedTweets = self.__processTweets(formattedTweets)
                self.__storeProcessedTweets(processedTweets)
                
                print '<manager> Refreshing cache'
                self.__cache.refreshCache(self.__DB)

            if not self.__shutDown:
                print '<manager> Sleeping...'
                self.__taskEvent.clear()
            self.__working = False
            
        print '<manager> Closing database connection'
        self.__DB.closeConn()
        print '<manager> Exiting'
        
        self.__server.shutdown()
        
    def __crawlTwitter(self):
        ''' returns a list of twitter status objects
        '''
        return self.__API.checkTwitter()
            
    def __storeRawTweets(self, rawTweets):
        ''' calls DB function to store raw tweets
        '''
        self.__DB.storeRawTweets(rawTweets)
            
    def __formatTweets(self, rawTweets):
        ''' returns two lists:
                a list of user dicts
                a list of tweet dicts
        '''
        return self.__formatter.formatTweets(rawTweets)
    
    def __storeUsers(self, users):
        ''' calls DB function to store users
        '''
        self.__DB.storeUsers(users)
                
    def __storeFormattedTweets(self, formattedTweets):
        ''' calls DB function to store formatted tweets
        '''
        return self.__DB.storeFormattedTweets(formattedTweets)
    
    def __processTweets(self, formattedTweets):
        ''' returns a list of processed tweets
        '''
        return self.__processor.processTweets(formattedTweets)
    
    def __storeProcessedTweets(self, formattedTweets):
        ''' calls DB function to store processed tweets
        '''
        return self.__DB.storeProcessedTweets(formattedTweets)