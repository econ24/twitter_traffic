import sqlite3
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

class MyDatabase:
    def __init__(self, name):
        self.DBfile = name
        self.__conn = False

    # private functions
    def __commitConn(self):
        try:
            self.__conn.commit()
        except Exception as e:
            print e
            raise DBException('Error opening a connection to database ' + self.DBfile)
            
    def __execute(self, cmd, *args):
        if not self.__conn:
            raise DBException('You must open a connection first')
        try:
            return self.__conn.execute(cmd, *args)
        except Exception as e:
            print e
            raise DBException('Error executing: ' + cmd)
            
    # public functions
    def openConn(self):
        try:
            self.__conn = sqlite3.connect(self.DBfile)
            self.__conn.row_factory = sqlite3.Row
        except Exception as e:
            print e
            raise DBException('Error opening a connection to database ' + self.DBfile)

    def closeConn(self):
        if not self.__conn:
            raise DBException('You must open a connection first')
        try:
            self.__conn.close()
        except Exception as e:
            print e
            raise DBException('Error closing the connection to database ' + self.DBfile)
            
    def storeRawTweets(self, rawTweets):
        rawTweetsTupleList = []
        for tweet in rawTweets:
            tTup = (str(tweet.GetId()), tweet.AsJsonString())
            rawTweetsTupleList.append(tTup)
            
        try:
            cmd = "INSERT OR IGNORE INTO raw_tweets VALUES (?, ?);"
            for tweet in rawTweetsTupleList:
                self.__execute(cmd, tweet)
            self.__commitConn()
        except DBException as dbe:
            print dbe
            
    def getRawTweets(self):
        query = 'SELECT * FROM raw_tweets;'
        try:
            #self.__conn.row_factory = sqlite3.Row
            results = self.__execute(query)

            tweetList = []
            for row in results:
                twt =  row['tweet_as_json']
                tweetList.append(twt)
            
        except DBException as dbe:
            print dbe
                   
        return tweetList
            
    def storeUsers(self, users):
        usersTupleList = []
        for user in users:
            uTup = (user['user_id'], user['screen_name'], user['location'])
            usersTupleList.append(uTup)
            
        try:
            for user in usersTupleList:
                self.__execute("INSERT OR REPLACE INTO users VALUES (?, ?, ?);", user)
            self.__commitConn()
        except DBException as dbe:
            print dbe
            
    def storeFormattedTweets(self, tweets):
        tweetsTupleList = []
        for tweet in tweets:
            tTup = (tweet['tweet_id'], tweet['created_at'], tweet['time_stamp'], \
                    tweet['text'], tweet['user_id'], tweet['retweet_count'], \
                    tweet['coordinates'], tweet['place_name'], tweet['location'])
            tweetsTupleList.append(tTup)
            
        try:
            for tweet in tweetsTupleList:
                self.__execute("INSERT OR IGNORE INTO formatted_tweets VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);", tweet)
            self.__commitConn()
        except DBException as dbe:
            print dbe
            
    def getFormattedTweets(self):
        query = 'SELECT * FROM formatted_tweets;'
        tweetList = []
        try:
            #self.__conn.row_factory = sqlite3.Row
            results = self.__execute(query)

            for row in results:
                twt = {'tweet_id': row['tweet_id'], \
                       'created_at': row['created_at'], \
                       'time_stamp': row['time_stamp'], \
                       'text': row['text'], \
                       'user_id': row['user_id'], \
                       'retweet_count': row['retweet_count'], \
                       'coordinates': row['coordinates'], \
                       'place_name': row['place_name'], \
                       'location': row['location']}
                tweetList.append(twt)
            
        except DBException as dbe:
            print dbe
                   
        return tweetList
            
    def storeProcessedTweets(self, tweets):
        tweetsTupleList = []
        for tweet in tweets:
            tTup = (tweet['tweet_id'], tweet['rating'])
            tweetsTupleList.append(tTup)
            
        try:
            for tweet in tweetsTupleList:
                self.__execute("INSERT OR REPLACE INTO processed_tweets VALUES (?, ?);", tweet)
            self.__commitConn()
        except DBException as dbe:
            print dbe
            
    def getProcessedTweets(self, delta):
        query = 'SELECT screen_name, created_at, text, rating, time_stamp ' +\
                'FROM processed_tweets NATURAL JOIN formatted_tweets, users ' +\
                'WHERE time_stamp >= ? ' +\
                'AND formatted_tweets.user_id = users.user_id ' +\
                'AND rating > 0.0 ' +\
                'ORDER BY time_stamp DESC;'
        try:
            #self.__conn.row_factory = sqlite3.Row
            results = self.__execute(query, (delta,))

            tweetList = []
            for row in results:
                twt = {'screen_name': row['screen_name'], \
                       'created_at': row['created_at'], \
                       'text': row['text'], \
                       'time_stamp': row['time_stamp'], \
                       'rating': row['rating']}
                tweetList.append(twt)
            
        except DBException as dbe:
            print dbe
                   
        return tweetList
        
    def storeLabelledTweets(self, tweets):
        tweetsTupleList = []
        for key, value in tweets.items():
            tTup = (key, value)
            tweetsTupleList.append(tTup)
            
        try:
            for tweet in tweetsTupleList:
                self.__execute("INSERT OR REPLACE INTO labelled_tweets VALUES (?, ?);", tweet)
            self.__commitConn()
        except DBException as dbe:
            print dbe
            
    def getLabelledTweets(self):
        query = 'SELECT screen_name, text, label ' +\
                'FROM labelled_tweets NATURAL JOIN formatted_tweets, users ' +\
                'WHERE formatted_tweets.user_id = users.user_id;'
        try:
            #self.__conn.row_factory = sqlite3.Row
            results = self.__execute(query)

            tweetList = []
            for row in results:
                twt = {'screen_name': row['screen_name'], \
                       'text': row['text'], \
                       'label': bool(row['label'])}
                tweetList.append(twt)
            
        except DBException as dbe:
            print dbe
                   
        return tweetList
        
    # special functions
    def wipeTable(self, table):
        cmd = 'DELETE FROM ' + table.split()[0] + ';'
        try:
            self.__execute(cmd)
            self.__commitConn()
        except DBException as dbe:
            print dbe
            
    def dropTable(self, table):
        cmd = 'DROP TABLE ' + table.split()[0] + ';'
        try:
            self.__execute(cmd)
            self.__commitConn()
        except DBException as dbe:
            print dbe

    # table creation functions
    def init(self):
        ''' function used to initialize database. '''
        
        c = self.__conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
        if not c.fetchone():
            self.__createUsersTable()
            self.__conn.commit()

        c = self.__conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='raw_tweets';")
        if not c.fetchone():
            self.__createRawTweetsTable()
            self.__conn.commit()

        c = self.__conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='formatted_tweets';")
        if not c.fetchone():
            self.__createFormattedTweetsTable()
            self.__conn.commit()

        c = self.__conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='processed_tweets';")
        if not c.fetchone():
            self.__createProcessedTweetsTable()
            self.__conn.commit()

        c = self.__conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='labelled_tweets';")
        if not c.fetchone():
            self.__createLabelledTweetsTable()
            self.__conn.commit()

    def __createUsersTable(self):
        qry = 'CREATE TABLE users ' +\
               '(user_id TEXT PRIMARY KEY, ' +\
                'screen_name TEXT, ' +\
                'location TEXT);'
        self.__execute(qry)

    def __createRawTweetsTable(self):
        qry = 'CREATE TABLE raw_tweets ' +\
               '(tweet_id TEXT PRIMARY KEY, ' +\
                'tweet_as_json TEXT);'
        self.__execute(qry)

    def __createFormattedTweetsTable(self):
        qry = 'CREATE TABLE formatted_tweets ' +\
               '(tweet_id TEXT PRIMARY KEY REFERENCES raw_tweets(tweet_id), ' +\
                'created_at TEXT, ' +\
                'time_stamp INT, ' +\
                'text TEXT, ' +\
                'user_id TEXT REFERENCES users(user_id), ' +\
                'retweet_count INT, ' +\
                'coordinates TEXT, ' +\
                'place_name TEXT, ' +\
                'location TEXT);'
        self.__execute(qry)

    def __createProcessedTweetsTable(self):
        qry = 'CREATE TABLE processed_tweets ' +\
               '(tweet_id TEXT PRIMARY KEY REFERENCES formatted_tweets(tweet_id), ' +\
                'rating INT);'
        self.__execute(qry)
        
    def __createLabelledTweetsTable(self):
        qry = 'CREATE TABLE labelled_tweets ' +\
               '(tweet_id TEXT PRIMARY KEY REFERENCES formatted_tweets(tweet_id), ' +\
                'label INTEGER);'
        self.__execute(qry)
        
#end MyDatabase

class DBException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
#end DBException
        
def main():
    db = MyDatabase('twitter_data.db')
    db.openConn()
    db.init()
    db.closeConn()

if __name__ == "__main__":
    main()
