# -*- coding: utf-8 -*-
"""
Created on Fri Mar 28 21:00:21 2014

@author: Eric Conklin
"""

import threading, time, my_database

class CacheManager:
    def __init__(self):
        self.__cachedTweets = []
        
        self.__lock = threading.Lock()
        
    def requestTweets(self, sinceTime):
        delta = time.time() - (sinceTime * 60)
        
        self.__lock.acquire()
        
        twts = [twt for twt in self.__cachedTweets if twt['time_stamp'] >= delta]
        
        self.__lock.release()
        return twts
        
    def refreshCache(self, db):
        self.__lock.acquire()
        
        self.__cachedTweets = db.getProcessedTweets(1440)
        
        self.__lock.release()
        