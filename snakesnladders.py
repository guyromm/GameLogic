from random import randrange

start_spots = range(0,100)
ladders = {4:14,
           9:31,
           1:38,
           28:84,
           40:42,
           36:44,
           51:67,
           80:100,
           71:91}
snakes = {16:6,
          49:11,
          47:26,
          69:19,
          56:53,
          64:60,
          87:24,
          93:73,
          95:75,
          98:78}

dicerange=[1,7]

def getmove(r):
        if r in ladders:
            fr = ladders[r]
            annotated='%s^%s'%(r,ladders[r])
        elif r in snakes:
            fr=snakes[r]
            annotated='%s~%s'%(r,snakes[r])
        else:
            fr=r
            annotated='%s'%r
        return fr,annotated

        return fr

def testboxes():
    for s in start_spots:
        print s
        for d in range(*dicerange):
            r = s+d
            fr,annotated = getmove(r)
            print s,d,r,annotated

def throwdice():
    return (randrange(*dicerange))

def playgame():
    i=0 ; cnt=0
    a=[]
    while i<100:
        i=i+throwdice()
        i,annotated=getmove(i)
        a.append(annotated)
        cnt+=1
    seq=' '.join(a)
    return cnt,seq

def test():
    l=[] ; seqs={}
    toplay=10000000
    for i in range(toplay):
        turns,seq = playgame()
        l.append(turns)
        if seq not in seqs: seqs[seq]=0
        seqs[seq]+=1
    print toplay,'plays'
    print 'average:',float(sum(l))/len(l) if len(l) > 0 else float('nan')
    print '%s seqs'%len(seqs)
test()

           

