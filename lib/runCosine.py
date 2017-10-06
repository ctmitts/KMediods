import pickle
import os
import cosine as cos
import cl as cl

Articles = cos.ingArticles()

parseFile = 'parsed_articles.pkl'
parseOpen = open(parseFile, 'wb')
pickle.dump(Articles, parseOpen)
parseOpen.close()

results = cos.calcDist(Articles)

dist = results['dist']; maxD = 1; sortArt = sorted(Articles)

distances = [dist, maxD, sortArt]

distFile = 'dist_articles.pkl'
distOpen = open(distFile, 'wb')
pickle.dump(distances, distOpen)
distOpen.close()

k  = input("Number of clusters (k): ")

iResults = cl.selObjs(distances, k)

iClFile = 'iClusters_articles.pkl'
iClOpen = open(iClFile, 'wb')
pickle.dump(iResults,iClOpen)
iClOpen.close()

fResults = cl.optimize(distances, iResults)

Clusters = fResults['Clusters']

Breaks = cos.accuracy(Clusters)

fClFile = 'fClusters_articles.pkl'
fClOpen = open(fClFile, 'wb')
pickle.dump(fResults, fClOpen)
fClOpen.close()

