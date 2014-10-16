# -*- coding: utf-8 -*-
"""
Created on Sun Apr 13 00:24:01 2014

@author: Eric Conklin
"""

import re, json
from os.path import join
from liblinearutil import train, predict, evaluations, save_model, load_model
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

def lookup(myjson, k):
  # return myjson[k]
  if '.' in k:
    # jpath path
    ks = k.split('.')
    v = myjson
    for k in ks: v = v.get(k, {})
    return v or ""
  return myjson.get(k, "")

def tweets_2_X(vocab, tweets):
    X = []
    for tweet_id, tweet in enumerate(tweets):
        text = lookup(tweet, 'text')
        if text:
            features = features_to_vector(vocab, extract_features(text))
            X.append(features)
    return X

def tweets_2_XY(vocab, tweets):
    X = []
    Y = []
    for tweet_id, tweet in tweets.items():
        text = lookup(tweet, 'text').lower()
        if text:
            features = features_to_vector(vocab, extract_features(text))
            X.append(features)
        if tweet['label']:
            Y.append(1)
        else:
            Y.append(0)
    return Y, X

def remove_urls(text):
    for url in re.findall(r'(https?://[^\s]+)', text):
        text = text.replace(url, '')
    return text
        
def features_to_vector(vocab, features):
    vector = [0] * len(vocab)
    for feat, freq in features.items():
        if vocab.has_key(feat):
            vector[vocab[feat]] = freq
    return vector
    
def extract_features(text):
    terms = remove_stopwords(text.split())
    return extract_terms_features(terms)

def predict_labels(vocab, tweets, model):
    X = tweets_2_X(vocab, tweets)
    Y = []
    p_label, p_acc, p_val = predict(Y,X,model, '-q')
    return p_label
    
def svm_model_train(Y, X): 
    traces = []
    for c in range(1, 4):
        for w1 in range(1, 4):
            for w0 in range(w1*2, w1*3+1):
                acc = train(Y, X,'-v 10 -c {} -w1 {} -w0 {} -q '.format(c, w1, w0))
                traces.append([(c, w1, w0), acc])
                print 'c={} | w1={} | w0={}'.format(c, w1, w0), acc
    c, w1, w0 = max(traces, key=lambda item: item[1])[0]
    print 'final values: c={} | w1={} | w0={}'.format(c, w1, w0)
    model=train(Y, X,'-c {} -w1 {} -w0 {} -q '.format(c, w1, w0))
    p_label, p_acc, p_val = predict(Y,X,model)
    ACC, MSE, SCC = evaluations(Y, p_label)
    return model, (ACC, MSE, SCC)

def load_json_file(f):
    json_data = open(f, 'r')
    data = json.load(json_data, encoding='utf-8')
    return data

def save_to_json_file(f, data):
    f = open(f, "w")
    f.write(json.dumps(data))
    f.close()

"""
unigram, bigram, and trigram features
"""
def extract_terms_features(terms):
    vector = dict()
    for term in terms:
        if vector.has_key(term):
            vector[term] += 1
        else:
            vector[term] = 1
    for i in range(len(terms) - 2):
        cb2 = ' '.join(terms[i:i+1])
        cb3 = ' '.join(terms[i:i+2])
        if vector.has_key(cb2):
            vector[cb2] += 1
        else:
            vector[cb2] = 1
        if vector.has_key(cb3):
            vector[cb3] += 1
        else:
            vector[cb3] = 1
    cb2 = ' '.join(terms[len(terms)-2:len(terms)])
    if vector.has_key(cb2):
        vector[cb2] += 1
    else:
        vector[cb2] = 1
    return vector    

def load_traffic_tweets_labels(vocab, label_file, ref_tweets_file):
    labels = load_json_file(label_file)
    tweets = load_json_file(ref_tweets_file)
    tweets = {tweet['tweet_id']: tweet for tweet in tweets}
    ref_tweets = dict()
    negative_tweets = []
    positive_tweets = []
    for (tweet_id, label) in labels:
        if tweets.has_key(tweet_id):
            tweet = tweets[tweet_id]
            text = lookup(tweet, 'text').lower()
            if len(re.findall(r'(https?://[^\s]+)', text)) > 0:
                continue
            ref_tweets[tweet_id] = tweets[tweet_id]
            ref_tweets[tweet_id]['label'] = label
            if label:
                positive_tweets.append(tweet)
            else:
                negative_tweets.append(tweet)
    print "# positive tweets: {}; # negative tweets: {}".format(len(positive_tweets), len(negative_tweets))
    Y, X = tweets_2_XY(vocab, ref_tweets)
    return Y, X

"""
identify terms with frequencies greater than cutoff, and store in a dictionary. 
key is term, and value is an identifie. 
"""
def generate_vocab(tweets):
    term_freq = dict()
    for tweet in tweets:
        #tweet = json.loads(line)
        text = lookup(tweet, 'text')
        terms = extract_features(text.lower())
        for term in terms:
            if not term_freq.has_key(term):
                term_freq[term] = 0
            term_freq[term] += 1
    cutoff = 15
    vocab = dict()
    identifier = 0
    for term, freq in term_freq.items():
        if freq >= cutoff:
            vocab[term] = identifier
            identifier += 1
    print "total terms reserved: {}".format(len(term_freq))
    #print vocab
    return vocab


STOPWORDS = ['a','able','about','across','after','all','almost','also','am','among',
             'an','and','any','are','as','at','be','because','been','but','by','can',
             'cannot','could','dear','did','do','does','either','else','ever','every',
             'for','from','get','got','had','has','have','he','her','hers','him','his',
             'how','however','i','if','in','into','is','it','its','just','least','let',
             'like','likely','may','me','might','most','must','my','neither','no','nor',
           'not','of','off','often','on','only','or','other','our','own','rather','said',
             'say','says','she','should','since','so','some','than','that','the','their',
             'them','then','there','these','they','this','tis','to','too','twas','us',
             'wants','was','we','were','what','when','where','which','while','who',
             'whom','why','will','with','would','yet','you','your']

"""
Assume all words are in lower case
"""
def remove_stopwords(terms):
    ref_terms = []
    for term in terms:
        if term not in STOPWORDS:
            ref_terms.append(term)
    return ref_terms
                
def train_svm_classifier(db):
    print 'loading vocabulary'
    ref_tweets_file = join('data', 'ref_tweets.json')
    tweets = db.getFormattedTweets()
    vocab = generate_vocab(tweets)
    save_to_json_file('data/svm_vocab.json', vocab)
    
    print 'loading training data (tweets, and labels)'
    label_file = 'data/train_labels.txt'
    Y, X = load_traffic_tweets_labels(vocab, label_file, ref_tweets_file) 
    
    print 'training a svm classifier'
    model, (ACC, MSE, SCC) = svm_model_train(Y, X)
    
    print 'saving the trained svm classifier'
    save_model('data/svm_model', model)
    
def predict_new_tweets(tweets, model, vocab):
    Y = predict_labels(vocab, tweets, model)
    return Y
            
def main():
    import my_database
    db = my_database.MyDatabase('twitter_data.db')
    db.openConn()
    train_svm_classifier(db)
    db.closeConn()
    
if __name__ == '__main__':
    main()