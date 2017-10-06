import pickle
import cl as cl
import os
import re
import pickle

file = input("\tFile name: ")

sub = re.sub('.txt', '',file)

path = "./" + sub

os.chdir(path)

distFile = 'dist_' + sub + '.pkl'
distOpen = open(distFile,'rb')
distances = pickle.load(distOpen)
distOpen.close()

k  = input("Number of clusters (k): ")

iResults = cl.selObjs(distances,k)

iClFile = 'iClusters_' + sub + '.pkl'
iClopen = open(iClFile,'wb')
pickle.dump(iResults,iClopen)
iClopen.close()


TF  = input("Optimize Clusters (T/F): ")

if TF == 'T':
	print "Beginning to optimize clusters"
	fResults = cl.optimize(distances,iResults)
	fClFile = 'fClusters_' + sub + '.pkl'
	fclOpen = open('fClusters.pkl','wb')
	pickle.dump(fResults,fclOpen)
	fclOpen.close()



