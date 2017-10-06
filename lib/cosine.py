import os
import math
import re
import operator
import numpy as np
import ingest as ing
import pickle

#path = input("\tSet Working Directory: ")

def ingArticles():
    stopOpen = open("stopWords.txt",'r')
    stopFile = stopOpen.read()
    stop = stopFile.split(",")
    path = input("\tSet Working Directory: ")
    os.chdir(path)
    subDirs = [dir[0] for dir in os.walk('./') if dir[0] != './']
    Articles = {}
    for dir in subDirs:
        os.chdir(dir)
        sub = dir.split('./')[1]
        articles = [ar for ar in os.listdir('./') if '.txt' in ar]
        #arName = [sub + '_' + ar.replace('.txt','') for ar in articles]	
        for ar in articles:
            arName = sub + '_' + ar.replace('.txt', '')
            arOpen = open(ar,'r')
            contents = arOpen.read()
            contents = contents.replace('\'', '')
            contents = contents.replace('\"', '')
            text = re.sub("\d+\.\d+","",contents) ## remove decimal #.#
            text = re.sub("\d+","",text)  	
            text = re.sub('\.\.\.', '',text) ### remove ...
            text = re.sub('\...\.' , '.',text)  ## initial at beginning of sentence 
            text = re.sub('[-+=<>*/]',' ',text)
            text = re.sub('[:;,@#$%^&~`]', '', text)
            text = text.decode('unicode_escape').encode('ascii','ignore')
            text = re.sub('[!?.]', ' ', text) ## replace "(!?)" with "."
            lines = text.split('\n')
            title = lines[0]; del lines[0]
            lines = [line for line in lines if not line in [' ', '']]
            text = ''.join( [ l1 for l1 in lines])
            words = re.findall(r"[\w']+", text)
            words = [ing.processWord(wrd.lower()) for wrd in words if not ing.processWord(wrd.lower()) in stop]
            words = [wrd for wrd in words if not wrd in [' ', '']]
            tWords = re.findall(r"[\w']+", title)
            tWords = [ing.processWord(wrd.lower()) for wrd in tWords if not ing.processWord(wrd.lower()) in stop]
            mars = {}; joints = {}
            for wrd in tWords:	
                #wrd = ing.processWord(wrd)
                if wrd in mars:
                    mars[wrd] = mars[wrd] + 2.0
                if not wrd in mars:
                    mars[wrd] = 2.0
            for i in range(len(tWords)-1):
                wrd1 = tWords[i]; wrd2 = tWords[i+1]
                pair = wrd1 + " " + wrd2
                if pair in joints:
                    joints[pair] = joints[pair] + 2.0
                if not pair in joints:
                    joints[pair] = 2.0
            for wrd in words:
                #wrd = ing.processWord(wrd)
                if wrd in mars:
                    mars[wrd] = mars[wrd] + 1.0	
                if not wrd in mars:
                    mars[wrd] = 1.0	
            for i in range(len(words)-1):
                wrd1 = words[i]; wrd2 = words[i+1]
                pair = wrd1 + " " + wrd2
                if pair in joints:
                    joints[pair] = joints[pair] + 1.0
                if not pair in joints:
                    joints[pair] = 1.0  
            Articles[arName] = {'title':title, 'words':mars, 'pairs':joints}
        os.chdir('../')
    return Articles


def dotProduct(doc1, doc2, jp = 0):  ## if jp == 1, consider pairs
    if jp == 0:
        counts1 = doc1['words']; objs1 = sorted(counts1.keys())
        counts2 = doc2['words']; objs2 = sorted(counts2.keys())
        ## create container of all unique words
    if jp == 1:
        counts1 = doc1['pairs']; objs1 = sorted(counts1.keys())
        counts2 = doc1['pairs']; objs2 = sorted(counts2.keys())
    container = objs1 + [wrd for wrd in objs2 if not wrd in objs1]
    N = len(container)
    vec1 = [0.0]*N; vec2 = [0.0]*N
    dp = 0.0
    for i, wrd in enumerate(container):
        if wrd in objs1:
            vec1[i] = counts1[wrd]
        if wrd in objs2:
            vec2[i] = counts2[wrd]
        dp += vec1[i] * vec2[i]
    n1 = sum( [ v1i**2 for v1i in vec1]); n2 = sum( [ v2i**2 for v2i in vec2])
    cos = dp / ( math.sqrt(n1) * math.sqrt(n2) )
    if cos > 1:
        cos = round(cos,1) 
    return cos

def cAngle(cos):
    angle = 1 - (2*math.acos(cos)/math.pi)  ## angular distance (0,1) 
    #dist = ( (math.acos(dot)/math.pi)*180) / 90
    return angle

def rDist(dot):
    dist = ( (math.acos(dot)/math.pi)*180) / 90
    return dist

def calcDist(Articles, jp = 0 ):  ## if jp = 1, consider pairs
    dots = {}; dist = {}
    sortArt = sorted(Articles)
    used = []
    for art1 in sortArt:
        doc1 = Articles[art1]; # n1 = doc1['n']
        used.append(art1); notUsed = [art for art in sortArt if not art in used]
        for art2 in notUsed:
            doc2 = Articles[art2]; # n2 = doc2['n']
            key = art1 + ":" + art2;# N = n1 + n2
            if doc1 == doc2:
                dots[key] = 1
                dist[key] = rDist(1)
            else:
                if jp == 0:
                    dots[key] = dotProduct(doc1, doc2)
                    dist[key] = rDist(dots[key])
                if jp == 1:
                    dots[key] = dotProduct(doc1, doc2, jp = 1)
                    dist[key] = rDist(dots[key])
    return {'dist':dist, 'dots':dots}

## calculate accuracy of clusters with provided labels
def accuracy(Clusters):
    mediods = Clusters.keys()
    types = ['business', 'tech', 'entertainment', 'sport', 'politics']
    clBreak = {};
    pAccurate = 0.0
    for mediod in mediods:
        [typeM, idM] = mediod.split('_')
        store = {}
        N = len(Clusters[mediod])
        for s_type in types:
            counter = 0.0
            for obj in Clusters[mediod]:
                [typeO, idi] = obj.split('_')
                if typeO == s_type:
                    counter += 1.0
            store[s_type] = round( (counter / N) * 100,2)
        clBreak[mediod] = store
        temp = sorted(store.items(), key = operator.itemgetter(1), reverse = True )
        print 'Cluster around mediod _ %s_:' % mediod
        print temp
        pAccurate += clBreak[mediod][typeM]
    pAccurate = round(pAccurate / len(mediods),2)
    print 'Total Accuracy: %s percent' %pAccurate
    return clBreak    



#def returnDist(dots):
#	dist = {}
#	for key, dp in dots.iteritems():
#		dist[key] = ( (np.arccos(dp)/math.pi)*180) / 90
#        dist = ( (np.arccos(dot)/math.pi)*180) / 90
#        return dist



#for x in os.walk('./')

#articles = [ar for ar in os.listdir(path) if '.txt' in ar]
#artName = [re.sub(




#for root, dirs, files in os.walk('./'):
#	print root
#	print dirs
#	print files

#os.listdir('./')

#bold = "\033[1m"
#reset = "\033[0;0m"
#print "I want " + bold + "this" + reset + " text to be bold."

