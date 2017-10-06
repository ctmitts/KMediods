import operator

def select(d2dict, mM):
    inverse = [(value, key) for key, value in d2dict.items()]
    if (mM == 0):
        selected = min(inverse)[1]  ## representative object ~ mediod
    if (mM == 1):
        selected = max(inverse)[1]   ## representative object
    if ( (mM != 0) and (mM != 1) ):
        selected = 'NA'
    return selected


def splitWords(pair):
        words = pair.split(":")	
        wrd1 =  words[0]; wrd2 = words[1]
        return wrd1, wrd2

def retValue(relPair,dist,maxD):
        [word1, word2] = splitWords(relPair)
        if (word1 == word2):
            value = 0
        else:
            inverse = word2 + ":" + word1
            if (relPair in dist):
                value = dist[relPair]
            if (inverse in dist):
                value = dist[inverse]
            if (not relPair in dist) and (not inverse in dist):
                value = maxD
        return value

def retValue2(relPair, dist, maxD, IO= 0):  ## IO = 0 for non-conditional, IO = 1 for conditional 
    [obj1, obj2] = splitWords(relPair)
    if IO == 0:
        if (obj1 == obj2):
            value = 0
        else:
            inverse = obj2 + ":" + obj1
            if (relPair in dist):
                value = dist[relPair]
            if (inverse in dist):
                value = dist[inverse]
            if (not relPair in dist) and (not inverse in dist):
                value = maxD
    else: ## conditional
        [wrd2, wrd3] = obj2.split(" ")
        if obj1 == wrd2 and obj1 == wrd3:
            value = 0
        else:
            inverse = obj1 + " " + wrd2 + ":" + wrd3
            if (relPair in dist):
                value = dist[relPair]
            if (inverse in dist):
                value = dist[inverse]
            if (not relPair in dist) and (not inverse in dist):
                value = maxD
    return value


def cluster(distances,repObj):
    dist = distances[0];
    maxD = distances[1];
    sortObj = distances[2]
    clusters = {}
    for rObj in repObj:
        clusters[rObj] = []; clusters[rObj].append(rObj)
    for obj in sortObj:
        if not obj in repObj:
            nearest = min([[rObj,retValue(obj + ":" + rObj, dist,maxD)] for rObj in repObj],key = lambda k:k[1])[0]
            clusters[nearest].append(obj)
    avgCds = {};
    for rObj, objs in clusters.iteritems():
        nObjs = len(objs)
        avgCds[rObj] = sum([retValue(rObj + ":" + obj,dist,maxD) for obj in objs])/nObjs
    avgDS = sum([avgCds[rObj] for rObj in repObj])/len(repObj)
    return {'Clusters':clusters,'Objective':avgDS,'ClAvgs':avgCds}

def calcSilo(distances, clusters):
    dist = distances[0];
    maxD = distances[1];
    sortObj = distances[2]
    repObj = clusters.keys()
    sis = {}; AvgSi = {};
    for rObjA,objsA in clusters.iteritems():
        ais = {}; cis = {}; bis = {};
        nObjsA = len(objsA)
        for objA in objsA:
            ais[objA] = sum( [retValue(objA + ":" + obj,dist,maxD) for obj in objsA if obj != objA]) / (nObjsA - 1)
            for rObjC, objsC in clusters.iteritems():
                if rObjC != rObjA:
                    nObjsC = len(objsC)
                    cis[objA + ":" + rObjC] = sum( [retValue(objA + ":" + objC, dist, maxD) for objC in objsC]) / nObjsC
            bis[objA] = min([cis[objA + ":" + rObjC] for rObjC in repObj if rObjC != rObjA])
            sis[objA] = (bis[objA] - ais[objA]) / max( ais[objA], bis[objA] )
        AvgSi[rObjA] = sum( [sis[obj] for obj in objsA]) / nObjsA
    tAvgSi = sum( [ val for obj, val in sis.iteritems()]) / len(sis)
    return {'Coeff':tAvgSi, 'clSilo':AvgSi}

def selObjs(distances,k):
    dist = distances[0]; 
    maxD = distances[1]; 
    sortObj = distances[2]; n = len(sortObj); nQ = n/4
    repObj = []; 
    r = 0
    while r < k:
        counter = 0; progress = 0
        cumDs = {} ## hold contributions
        if r == 0: ## find the first representative object
            for iObj in sortObj:
                counter = counter + 1
                if (counter % nQ == 0):
                    progress = progress + 25
                    #print "Looking for object %s: %s percent completed" % (r+1,progress)
                key = iObj + ":"
                Tcont = 0
                for jObj in sortObj: ## object j
                    contribution = retValue(key + jObj,dist,maxD) 
                    Tcont = Tcont + contribution
                cumDs[iObj] = Tcont
            selection = select(cumDs,0) ## select object with minimum cummulative distance
            repObj.append(selection)
            r = 1
        else:
            for iObj in sortObj: ## object i
                counter = counter + 1
                if (counter % nQ == 0):
                    progress = progress + 25
                    #print "Looking for object %s: %s percent completed" % (r+1, progress)
                key = iObj + ":"
                Tcont = 0
                for jObj in sortObj: ## object j
                    closest = min([retValue(rObj + ":" + jObj, dist, maxD) for rObj in repObj]) #for each object j find the most similar (closest) previously selected object
                    dij = retValue(key + jObj, dist, maxD) ## similarity of object j with object i
                    contribution = max(closest - dij, 0)
                    Tcont = Tcont + contribution
                cumDs[iObj] = Tcont
            selection = select(cumDs, 1) ## select objects with maximum contribution to unselected objects
            repObj.append(selection)
            r = r + 1 # r is incremented as representative objects are found
        print "Found object %s: %s" % (r, selection)
    print "Representative Objects: %s" % repObj
    clusterPack = cluster(distances,repObj); objI = clusterPack['Objective']; clAvgs = clusterPack['ClAvgs']
    print "Average dissimilarity among all clusters %s" % objI
    print "Average dissimilarity in each cluster %s:" % [(repObj[i], clAvgs[repObj[i]]) for i in range(len(repObj))]
    return {'Mediods':repObj, 'ClusterInfo':clusterPack}

def swap(distances, repObj):
    dist = distances[0];
    maxD = distances[1];
    sortObj = distances[2]; 
    n = len(sortObj); k = len(repObj)
    counter = 0; progress = 0
    cumDs = {}
    N = ( (n - k)**2) * k
    nD = N / 10
    for iObj in repObj: ## object i
        for hObj in sortObj: 
            if not hObj in repObj: ## object h
                #print "Consider to swap %s for %s" % (iObj, hObj)
                counter = counter + 1
                if counter % nD == 0:
                    progress = progress + 10
                    print "%s completed" % progress 
                swapPair = iObj + ":" + hObj
                repKey = iObj + ":"
                swapKey = hObj + ":"
                #rKey = swapR + ":"
                Tcont = 0
                for jObj in sortObj:
                    if (not jObj in repObj):
                        curSwap = retValue(swapKey + jObj, dist,maxD)
                        curR = retValue(repKey + jObj, dist,maxD)
                        othReps = sorted([retValue(rObj + ":" + jObj, dist,maxD) for rObj in repObj if rObj != iObj])  ## [D_j, E_j]
                        if any( curR > othR for othR in othReps) and any( curSwap > othR for othR in othReps): ## a
                            cont = 0
                        if all(curR <= othR for othR in othReps): ## b
                            if curSwap < othReps[0]: ## b1
                                cont = (curSwap - curR)
                            if curSwap >= othReps[0]: ## b2
                                cont = (othReps[0] - curR)
                        if any( curR > othR for othR in othReps) and all(curSwap < othR for othR in othReps) and curSwap < curR: ## c
                                cont = (curSwap - othReps[0])
                        Tcont = Tcont + cont
                cumDs[swapPair] = Tcont
    bestPair = select(cumDs,0)
    return {'Swap':bestPair, 'Contributions':cumDs}

def optimize(distances, iResults):
    repObj = iResults['Mediods']
    info = iResults['ClusterInfo']; obj = info['Objective']
    state = False
    counter = 0
    while state == False:
        nResults = swap(distances,repObj)
        bestPair = nResults['Swap']; cumDs = nResults['Contributions']
        if (cumDs[bestPair] < 0):
            [old, new] = splitWords(bestPair)
            temp = [rObj for rObj in repObj if rObj != old]
            temp.append(new)
            nInfo = cluster(distances,temp)
            objN = nInfo['Objective']
            if objN < obj:
                repObj.remove(old); repObj.append(new)
                obj = objN
                clAvgs = nInfo['ClAvgs']
                Clusters = nInfo['Clusters']
                print "Representative object %s was swapped out for %s" % (old,new)
            else:
                print "Optimal Clustering achieved"
                state = True
                nInfo = cluster(distances,repObj)
                clAvgs = nInfo['ClAvgs']
                Clusters = nInfo['Clusters']
                print "Average dissimilarity among all clusters %s" % obj
                print "Average dissimilarity in each cluster %s:" % [(repObj[i], clAvgs[repObj[i]]) for i in range(len(repObj))]
        else:
            print "No Swap"
            state = True
            clAvgs = info['ClAvgs']
            Clusters = info['Clusters']
            print "Average dissimilarity among all clusters %s" % obj
            print "Average dissimilarity in each cluster %s:" % [(repObj[i], clAvgs[repObj[i]]) for i in range(len(repObj))]
        counter = counter + 1
        print "Number %s swap completed" % counter
    return {'Mediods':repObj,'Objective':obj,'ClusterAverages':clAvgs,'Clusters':Clusters}



### UNFINISHED NEW APPROACH 

def fastPick(distances, IO = 0):  
    sortObj = distances[4];
    if IO == 0:
        dist = distances[0]
        maxD = distances[2]
    else:
        dist = distances[1] ## conDist
        maxD = distances[3]
        sortPairs = distances[5]
    n = len(sortObj); nD = n/10

    tDs = {}
    
    for iObj in sortObj:
        key = iObj + ":"
        tDs[iObj] = sum( [ retValue(key + lObj, dist, maxD) for lObj in sortObj])

    vJays = {}
    counter = 0; progress = 0
    for jObj in sortObj:
        vj = 0
        if (counter % nD == 0):
            progress = progress + 10
            print "Still Looking: %s percent completed" % progress
        for iObj in sortObj:
            pair = iObj + ":" + jObj
            iStore = retValue(pair, dist,maxD) / tDs[iObj]
            vj = vj + iStore
        vJays[jObj] = vj
        counter = counter + 1
    k = input("\tHow many objects would you like to select? ")
    repObj = sorted(vJays.items(), key = operator.itemgetter(1))[0:k] 
    for i in range(k):
        repObj[i] = repObj[i][0]
    return {'Mediods':repObj, 'AllComputed':vJays}


def newCluster(distances,repObj):
    dist = distances[0];
    maxD = distances[1];
    sortObj = distances[2]
    clusters = {}
    ## Initialize clusters to include the representative objects, mediods of each cluster
    for rObj in repObj:
        clusters[rObj] = []; clusters[rObj].append(rObj)
        ## Assign the remaining objects to the cluster with the most similar representative object
    for obj in sortObj:
        if not obj in repObj:
            nearest = min([[rObj,retValue(obj + ":" + rObj, dist,maxD)] for rObj in repObj],key = lambda k:k[1])[0]
            clusters[nearest].append(obj)
            Tds = {} ## sum of distances from each object in a particular cluster, to that cluster's representative object 
            ClAvgs = {}
    for rObj, clObjs in clusters.iteritems():
        key = rObj + ":"
        Tds[rObj] = sum([retValue(key + obj, dist, maxD) for obj in clObjs])
        ClAvgs[rObj] = Tds[rObj] / len(clObjs)
    obj = sum( [clAvg for clAvg in ClAvgs.values()]) / len(repObj)		

    return {'Clusters':clusters,'SumofDs':Tds, 'Objective':obj, 'ClAvgs':ClAvgs}


#def updCluster(distances, repObj):

#    dist = distances[0]
#    maxD = distances[1]
#    sortObj = distances[2]

#    iCls = newCluster(distances, repObj) ## calculate the sum of distances from all objects to their mediods
#    iClusters = iCls['Clusters'] 
#    Tds = iCls['SumofDs']  ## sum of distances
#    for rObj, clObjs in iClusters.iteritems():
#        obj = Tds[rObj]
#    for clObj in clObjs:
#        value = sum([retValue( clObj + ":" + Obj2, dist, maxD) for Obj2 in clObjs])
#        if value < obj:
#            obj = value
#    best = clObj
#    del Tds[rObj]
#        Tds[best] = obj

#        values = {}
#        for rObj, clObjs in iClusters.iteritems():
#            obj = Tds[rObj]
#            values = {}
#            for clObj in clObjs:
#                values[clObj] = sum( [retValue( clObj + ":" + Obj2, dist, maxD) for Obj2 in clObjs])
#                    best = min( values.items(), key = operator.itemgetter(1))
#                nMediod = best[0]; nObj = best[1]; 
#            if nObj < obj:
#                del Tds[rObj]
#                Tds[nMediod] = nObj

#    best = min( [clObj, sum([ retValue( clObj + ":" + Obj2, dist, maxD) for Obj2 in clObjs if Obj2 != clObj]) for clObj in clObjs], key = lamba k:k[0])[0]


#    best = min([ clObj, sum(cl.retValue( clObj + ":" + Obj2, dist, maxD) for Obj2 in clObjs for clObj in ClObjs
#    return {'Mediods':nRepObj}



