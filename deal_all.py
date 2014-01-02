from texas import gendeck
import copy
import itertools
from random import shuffle

cards = range(0,52)
deck = gendeck(jokers=False)

def pr(indexr):
    return ' '.join([deck[v] for v in indexr.values()])
def pri(idx):
    return ' '.join([deck[v] for v in idx])

def permute(cardsnum=9,checkdupes=False):
    combs=[]
    cnt=0 ; dupes=0

    for p in  itertools.permutations(cards):
        rev = p[::-1]
        pr= pri(rev[0:cardsnum])
        if checkdupes and pr in combs: 
            dupes+=1
            #print 'dupe ',dupes,'/',cnt
            continue
        combs.append(pr)
        cnt+=1
        yield pr
        
def randeal(cardsnum=9):
    while True:
        shuffle(cards)
        yield pri(cards[0:cardsnum])
    






