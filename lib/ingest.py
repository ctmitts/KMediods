import os
import math
import re
import operator

def splitWords(pair):
        words = pair.split(":")
        wrd1 =  words[0]; wrd2 = words[1]
        return wrd1, wrd2


def sort_alpha(w1, w2):
        if (w1 < w2):
                return("%s:%s" % (w1,w2))
        else:
                return("%s:%s" % (w2,w1))

def parseSent(filename):
        opened  = open(filename,'r')
        contents = opened.read()
        contents = contents.replace('\n',' ')
        contents = contents.replace('\'', '')
        contents = contents.replace('\"', '')
        text = re.sub("\d+\.\d+","",contents) ## remove decimal points
        text = re.sub('[!?]', '.', text) ## replace "(!?)" with "."
        text = re.sub('\.\.\.', '',text) ### remove ...
        text = re.sub('\...\.' , '.',text)  ## initial at beginning of sentence
        #contents = text.replace('...','')
        sentences = text.split(".")
        sentences.remove('')

        krap = [' ', '']
        sentences = [sent for sent in sentences if (len(sent) > 2 and [ch in krap for ch in sent])]

        N = len(sentences)
        avgLength = sum([ len(sentence) for sentence in sentences])/ len(sentences)

        print "Total number of observations: %s sentences" % N
        print "Average length of sentence: %s characters" % avgLength
        return sentences, N

def processWord(word):
        vowels = "aeiou"
        endings = ["ch", "s","sh","x","z"]
        exceptions = ["ifes","christmas","lies","sachs","abacus","dies","ties","status","series","acehs","acts","airbus","alexis","alois","analysis","arthritis","asbestosis","various","unanimous","unambiguous","news","classics","means","economics","electronics","politics","davies","abbas","absas"]
        if not word in exceptions:
                    if ( word.endswith("s") and (not word[len(word)-2] in vowels) ):
                        word = word[0:(len(word)-1)]
                    if ( word.endswith("s") and (word[len(word)-2] in vowels) ):
                        if word.endswith("ies"):
                            word = word[0:(len(word)-3)] + "y"
                        if word.endswith("es"): #and (not word[len(word) - 3] in vowels):  ## for consonants
                            sub = word[0:(len(word) - 2)]
                            if any([sub.endswith(sfx) for sfx in endings]):
                                word = sub
                            else:
                                word = word[0:(len(word)-1)]
                    if (word.endswith("ae")):
                            word = word[0:(len(word) - 1)]
                    if (word.endswith("eaux")):
                            word = word[0:(len(word) -1)]
        return word

def observe(sentences, sparsity):
        stopOpen = open("stopWords.txt",'r')
        stopFile = stopOpen.read()
        stop = stopFile.split(",")

        marginals = {}; joints = {}; tris = {};  sentWords = {}

        for i, sentence in enumerate(sentences):
                sentence = re.sub('[:;,@#$%()-+=<>*&0123456789]', '', sentence)
                sentence = sentence.decode('unicode_escape').encode('ascii','ignore')
                words = re.findall(r"[\w']+", sentence)
                senStore = [] ## store words from sentence
                for word in words:
                        word = word.lower()
                        if not word in stop:
                                word = processWord(word)
                                #if not word in senStore:
                                senStore.append(word)  ## store all independent instances of each word
                                if word in marginals:
                                        marginals[word] = marginals[word] + 1.0
                                if not word in marginals:
                                        marginals[word] = 1.0
                sentWords[i] = senStore
                ## compute all of the joint counts
                pairs = []
                for i in range(len(senStore)-1):
                        wrd1 = senStore[i]
                        for j in range(i+1,len(senStore) ):
                                wrd2 = senStore[j];
                                pair = wrd1 + ":" + wrd2; # pairs.append(pair)
                                if wrd2 != wrd1 and not pair in pairs:
                                        if pair in joints:
                                                joints[pair] = joints[pair] + 1
                                        if not pair in joints:
                                                joints[pair] = 1
                                        pairs.append(pair)
                triples = []
                for k in range(len(senStore)-1):
                        wrd = senStore[k]; nextWrd = senStore[k+1]
                        relPairs = [ relPair for relPair in pairs if nextWrd == splitWords(relPair)[0]]
                        for pair in relPairs:
                                [obj1, obj2] = splitWords(pair); pObs = obj1 + " " + obj2
                                triPair = wrd + ":" + pObs
                                if (wrd != obj1) and (wrd != obj2) and (not triPair in triples):
                                        if triPair in tris:
                                                tris[triPair] = tris[triPair] + 1
                                        if not triPair in tris:
                                                tris[triPair] = 1
                                        triples.append(triPair)
        ## Control for sparsity
        words = {}
        for wrd, c in marginals.iteritems():
                if c >= sparsity:
                        words[wrd] = c
        pairs = {}
        for j, jC in joints.iteritems():
                [wrd1, wrd2] = j.split(":")
                if wrd1 in words and wrd2 in words:
                        pairs[j] = jC
        triples = {}
        for tri, triC in tris.iteritems():
                [wrd1, pObj] = splitWords(tri)
                [wrd2, wrd3] = pObj.split(" ");
                pair1 = wrd1 + ":" + wrd2; pair2 = wrd1 + ":" + wrd3
                if ( pair1 in pairs and wrd3 in words ) and ( pair2 in pairs and wrd2 in words ):
                        triples[tri] = triC

        return {'marginals':words, 'joints':pairs, 'triples':triples }

def cogDist(a,b,ab,N):
        num = max(math.log(a), math.log(b)) - math.log(ab)
        denom = math.log(N) - min( math.log(a), math.log(b) )
        cogDist = num / denom
        return cogDist

def conCd(xc,yc, xcyc, N):
        num = max( math.log(xc), math.log(yc) ) - math.log(xcyc)
        denom = math.log(N) - min( math.log(xc), math.log(yc) )
        conCd = num / denom
        return conCd

def splitWords(pair):
        words = pair.split(":")
        wrd1 =  words[0]; wrd2 = words[1]
        return wrd1, wrd2

def calcDist(counts, N, option):  ## if option = 0, no conditional CD
        mars = counts['marginals']
        joints = counts['joints']
        dist = {}
        mCount  = 0; progress = 0
        nJ = len(joints); nQj = nJ/4
        for pair, jC in joints.iteritems():
            mCount = mCount + 1
            if mCount % nQj == 0:
                progress = progress + 25
                print "Building dictionary: %s percent completed" % progress
            [wrd1, wrd2] = splitWords(pair) # split joint pair into words
            if (wrd1 != wrd2):
                m1 = mars[wrd1]; m2 = mars[wrd2]
                dist[pair] = cogDist(m1,m2,jC,N)
        print "Finished calculating distances"
        maxD = max(dist.values()) + .25 ## *4, make parameter
        if option == 0:
            sortObj = sorted(mars)
            return dist, maxD, sortObj
        ## calculate conditional cognitive distances
        else:
            print "Start calculating conditional distances"
            triples = counts['triples']
            conDist = {}; pairs = []
            tCount  = 0; progress = 0
            nJ = len(joints); nQj = nJ/4
            for tri, triC in triples.iteritems():
                tCount = tCount + 1
                if tCount % nQj == 0:
                    progress = progress + 25
                    print "Building dictionary: %s percent completed" % progress
                [wrd1, pObj] = splitWords(tri);
                [wrd2, wrd3] = pObj.split(" ");
                if not pObj in pairs:
                    pairs.append(pObj)
                    pair1 = wrd1 + ":" + wrd2; pair2 = wrd1 + ":" + wrd3
                    #[pObs, wrd3] = splitWords(tri)
                    #[wrd1, wrd2] = pObs.split(" "); pair1 = wrd1 + ":" + wrd3; pair2 = wrd2 + ":" + wrd3
                    xc = joints[pair1]; yc = joints[pair2];
                    conDist[tri] = conCd( xc, yc, triC, N)
            maxConD = max(conDist.values() ) + .25
            sortObj = sorted(mars)
            sortPairs = sorted(pairs)
            return dist, conDist, maxD, maxConD, sortObj, sortPairs			

