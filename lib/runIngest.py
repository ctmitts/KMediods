import pickle
import os
import ingest as ing
import re

nfile = input("\tFile name: ")

sub = re.sub('.txt', '',nfile)

path = "./" + sub

[sentences, N] = ing.parseSent(nfile)

sparsity = input("Sparsity control (Integer): ")

counts = ing.observe(sentences,sparsity)

distances = ing.calcDist(counts,N, 0)

mars = counts['marginals']
joints = counts['joints']

counts = {'marginals':mars, 'joints':joints, 'N':N}

if not os.path.exists(path):
    os.makedirs(path)
    os.chdir(path)
else:
    os.chdir(path)

countFile = 'counts_' + sub + '.pkl'
countOpen = open(countFile, 'wb')
pickle.dump(counts, countOpen)
countOpen.close()

distFile = 'dist_' + sub + '.pkl'
distOpen = open(distFile, 'wb')
pickle.dump(distances, distOpen)
distOpen.close()


