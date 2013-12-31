from texas import hands_cmp,playround
import copy

outcomes = ['W','L','T']

def perms_srt(x,y):
    return cmp(outcomes.index(x),outcomes.index(y))

def get_result_permutations(oponents=3):
    res=[]

    from random import choice

    oarr = {}
    for o in outcomes:
        for i in range(0,oponents+1):
            if o not in oarr: oarr[o]=[]
            oarr[o].append(o*i)


    for k in oarr:
        for j in oarr:
            for m in oarr:
                if k==j or j==m or m==k: continue
                #print 'computing',k,j,m
                for ke in oarr[k]:
                    for je in oarr[j]:
                        for me in oarr[m]:
                            if len(ke)+len(je)+len(me)!=oponents: continue
                            tok = list(ke+je+me)
                            tok.sort(perms_srt)

                            res.append(''.join(tok))
    # print res
    # print len(res)
    # print len(set(res))
    return set(res)
def extract_permutations(r):
    dct = {1:'W',
           0:'T',
           -1:'L'}
    ret = {}
    for h in r:
        op=[]
        rc = copy.copy(r)
        rc.remove(h)
        for oh in rc: #minl:
            if h==oh: 
                raise Exception('wtf')
            res = dct[hands_cmp(h,oh)]
            op.append(res)
        op.sort(perms_srt)
        ''.join(op)
        tok = ''.join(op)
        if tok not in ret: ret[tok]=[]
        prod = h
        housecards = (prod[1][1])
        myhand = prod[1][0]+[prod[1][2]]
        otherhands = ', '.join([' '.join(rcc[1][0])+' '+
                               ' '.join([rcc[1][2]]) for rcc in rc])

        state= (''.join(tok)+': '+
            '[%s]'%' '.join(housecards)+
            ' [%s]'%' '.join(myhand)+
            ' vs [%s]'%otherhands)

        ret[tok].append(state)
    #raise Exception([(k,len(v)) for k,v in ret.items()])
    return ret

import os

def write(gperms,oponents):
    opdir = os.path.join('permutations',str(oponents))
    if not os.path.exists(opdir): os.mkdir(opdir)
    for perm in gperms:
        permf = os.path.join(opdir,perm+'.txt')
        fp = open(permf,'a')
        for row in gperms[perm]:
            fp.write(row+'\n')
        fp.close()
        print 'wrote',permf

def extract():
    oponents=5
    perms = get_result_permutations(oponents) 
    gperms={}
    print len(perms),'permutations needed'
    cnt=0
    try:
        while len(perms-set(gperms.keys())):
            r = playround(oponents+1)[0]
            mp = extract_permutations(r)

            for perm in mp:
                if perm not in gperms:
                    gperms[perm]={}
                    missing = perms-set(gperms.keys())
                    print len(gperms.keys()),'attained;',cnt,'tot. ; missing:',missing


                for st in mp[perm]:
                    if st not in gperms[perm]: 

                        gperms[perm][st]=0
                        #print st
                    else:
                        pass
                        #print '+'
                    gperms[perm][st]+=1
                    cnt+=1
    finally:
        print 'WRITING'
        write(gperms,oponents)
                
    return gperms
if __name__=='__main__':
    extract()
