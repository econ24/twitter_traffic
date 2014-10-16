import twitter
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

class TwitterChecker:
    consumerKey = 'q9HMjIaasrJNmXLFhlA'
    consumerSecret = 'K6Qcd2rbjG9AsgUizzEOArrC84kk2kpa6FPZPZqPkk'
    accessTokenKey = '131531920-Ezb3aZoog24QJoFUmqDZmvxT35RVuKNj05CTRqmY'
    accessTokenSecret = 'VmfdvGbnZnW7LxCcyEEnMKbUQGf3OprZyJcOeTcLUcAsc'
    
    def __init__(self):
        self.__API = twitter.Api(consumer_key=self.consumerKey, \
                                 consumer_secret=self.consumerSecret, \
                                 access_token_key=self.accessTokenKey, \
                                 access_token_secret=self.accessTokenSecret)
        self.queries = []
        self.queries.append('(highway OR road OR street OR traffic OR 87 OR '+\
                            'lane OR 90 OR northway OR exit OR drive) AND '+\
                            '(slow OR "backed up" OR blocked OR congest OR '+\
                            'closed OR closure OR gridlock OR accident OR '+\
                            '"traffic jam" OR "bumper to bumper" OR incident)')
        self.queries.append('(car OR truck OR vehicle OR bus OR tractor) AND '+\
                            '(disabled OR wreck OR crash OR collide OR collision)')
        self.queries.append('traffic OR road OR vehicle')

        self.geo = ('42.6525', '-73.7572', '50mi')# City of Albany
    #end __init__

    def checkTwitter(self):
        tweetList = []

        for i in range(len(self.queries)):
            query = self.queries[i]
            maxID = None

            for i in range(2):
                try:
                    rawTweets = self.__API.GetSearch(term = query,
                                                     geocode = self.geo,
                                                     count = 100,
                                                     max_id = maxID,
                                                     result_type = 'recent')
                except twitter.TwitterError:
                    print "Error retrieving tweets"
                    break
                except Exception as e:
                    print "Unknown Twitter error"
                    print str(e)
                    break
                #end try

                if rawTweets:
                    maxID = rawTweets[-1].GetId()
                    tweetList.extend(rawTweets)
                #end if
                    
                #if len(tweetList) >= 400:
                #    break
            #end for
        #end for
                    
        return tweetList
    #end checkTwitter
#end TwitterChecker
