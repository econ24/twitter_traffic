# -*- coding: utf-8 -*-
"""
Created on Thu May 15 23:17:10 2014

@author: Eric Conklin
"""

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

import json, re
from os.path import join
from liblinearutil import train, predict, evaluations, save_model, load_model
from nltk.corpus import stopwords as Stopwords
from nltk.stem.snowball import SnowballStemmer as Stemmer

DIRECTORY = 'data'
VOCAB_FILE = join(DIRECTORY, 'vocab.txt')
MODEL_FILE = join(DIRECTORY, 'model.dat')
    
def preprocessText(text):
    # convert text to all lower case
    text = text.lower()
    
    # collect all hash tags
    tags = re.findall('#[^\s#]+', text)
    # remove all hash tags
    text = re.sub('#[^\s]*', '', text)
    # remove all garbage from hash tags
    for i in range(len(tags)):
        tags[i] = re.sub('[^\w#]+', '', tags[i]).strip()
        
    # remove all mentions
    text = re.sub('@[^\s]*', '', text)
    
    # remove all links
    text = re.sub('https?://[^\s]+', '', text)
    
    # remove repeated characters, such as 'zzzzzzzz'
    text = re.sub(r'([a-z])\1{2,}', '\1', text)
    
    # save any dollar amounts
    dollars = ['$XXX'] * len(re.findall('\$[0-9]+,?[0-9]*', text))
    # replace dollars with place holder #
    text = re.sub('\$[0-9]+,?[0-9]*', '#', text)
    
    # save any percents
    percents = ['XXX%'] * len(re.findall('[0-9]+%', text))
    # replace percents with place holder @
    text = re.sub('[0-9]+%', '@', text)
    
    # remove all non-alphabetic characters except any # or @ placeholders
    text = re.sub('[^a-z#@]', ' ', text).strip()
    
    # replace dollars in previous positions
    for dollar in dollars:
        text = text.replace('#', dollar, 1)
    
    # replace percents in previous positions
    for percent in percents:
        text = text.replace('@', percent, 1)
    
    return text, tags
    
def extractNGrams(text):
    stemmer = Stemmer('english')
    stopwords = Stopwords.words('english')
    
    unigrams = [stemmer.stem(word) for word in re.split('\W+', text) \
            if len(word) > 2 and word not in stopwords]
            
    num = len(unigrams)
    bigrams = []
    trigrams = []
    for i in range(len(unigrams)):
        if i+2 <= num:
            bigrams.append(' '.join(unigrams[i : i+2]))
        
        if i+3 <= num:
            trigrams.append(' '.join(unigrams[i : i+3]))
    
    return unigrams, bigrams, trigrams
    
def generateVocab(tweets):
    corpus = {}
    
    for tweet in tweets:
        text, tags = preprocessText(tweet['text'])    
        
        for tag in tags:
            if tag not in corpus:
                corpus[tag] = {'type': 'tag', 'count': 0}
            corpus[tag]['count'] += 1
        
        unigrams, bigrams, trigrams = extractNGrams(text)
        
        for unigram in unigrams:
            if unigram not in corpus:
                corpus[unigram] = {'type': 'unigram', 'count': 0}
            corpus[unigram]['count'] += 1
        
        for bigram in bigrams:
            if bigram not in corpus:
                corpus[bigram] = {'type': 'bigram', 'count': 0}
            corpus[bigram]['count'] += 1
            
        for trigram in trigrams:
            if trigram not in corpus:
                corpus[trigram] = {'type': 'trigram', 'count': 0}
            corpus[trigram]['count'] += 1
    # end for
            
    vocab = {}
    index = 0
    for key, value in corpus.items():
        if value['type'] == 'tag' and value['count'] >= 20:
            vocab[key] = index
            index += 1
        elif value['type'] == 'unigram' and value['count'] >= 15:
            vocab[key] = index
            index += 1
        elif value['type'] == 'bigram' and value['count'] >= 10:
            vocab[key] = index
            index += 1
        elif value['type'] == 'trigram' and value['count'] >= 5:
            vocab[key] = index
            index += 1
            
    return vocab
    
def generateVectors(vocab, tweets):
    vectors = []
    
    for tweet in tweets:
        vector = [0] * len(vocab)
        
        text, tags = preprocessText(tweet['text'])
        
        for tag in tags:
            if tag in vocab:
                vector[vocab[tag]] += 1
        
        unigrams, bigrams, trigrams = extractNGrams(text)
        
        for unigram in unigrams:
            if unigram in vocab:
                vector[vocab[unigram]] += 1
                
        for bigram in bigrams:
            if bigram in vocab:
                vector[vocab[bigram]] += 1
            
        for trigram in trigrams:
            if trigram in vocab:
                vector[vocab[trigram]] += 1
            
        vectors.append(vector)
            
    return vectors
    
def trainModel(Y, X, numPos):
    numNeg = len(X) - numPos
    
    if numPos > numNeg:
        w0 = float(numPos) / float(numNeg)
        w1 = 1.0
    else:
        w1 = float(numPos) / float(numNeg)
        w0 = 1.0
    
    traces = []
    for c in range(1, 11):
        print 'calculating accuracy for c = {}...'.format(c)
        acc = train(Y, X,'-v 10 -c {} -w1 {} -w0 {} -q '.format(c, w1, w0))
        traces.append((c, acc))
        print ''
        
    c, acc = max(traces, key=lambda item: item[1])
    print 'highest value for c = {}\n'.format(c)
    
    model = train(Y, X,'-c {} -w1 {} -w0 {} -q '.format(c, w1, w0))
    
    print 'testing model...'
    p_label, p_acc, p_val = predict(Y,X,model)
    ACC, MSE, SCC = evaluations(Y, p_label)
    
    return model
    
def saveAsJSON(theStuff, theFile):
    with open(theFile, 'w') as outFile:
        json.dump(theStuff, outFile)
        
def loadFromJSON(theFile):
    with open(theFile) as inFile:
        data = json.load(inFile)
        
    return data
    
def generateVocabAndModel():
    import my_database
    
    db = my_database.MyDatabase('twitter_data.db')
    db.openConn()    
    labelledTweets = db.getLabelledTweets()
    db.closeConn()
    
    labels = []
    numPos = 0
    for tweet in labelledTweets:
        labels.append(tweet['label'])
        if bool(tweet['label']):
            numPos += 1
    
    print 'loading vocab...'
    vocab = generateVocab(labelledTweets)
    print len(vocab), 'vocab words loaded\n'
    
    print 'creating vectors...'
    vectors = generateVectors(vocab, labelledTweets)
    print len(vectors), 'vectors created\n'
    
    print 'training model...\n'
    model = trainModel(labels, vectors, numPos)
    
    saveAsJSON(vocab, VOCAB_FILE)
    save_model(MODEL_FILE, model)
        
def classifyTweets(tweets, model, vocab):
    allLabels = []
    chunkSize = 5000
    for i in range(0, len(tweets), chunkSize):
        vectors = generateVectors(vocab, tweets[i : min(len(tweets), i+chunkSize)])
        
        labels, p_acc, p_val = predict([], vectors, model, '-q')
        
        allLabels.extend(labels)
    
    return allLabels

def main():
    generateVocabAndModel()

if __name__ == '__main__':
    main()

