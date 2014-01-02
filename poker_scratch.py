import pokereval
import copy
import os,sys
from deal_all import permute,randeal

pe = pokereval.PokerEval()
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
    return set(res)

def extract_permutations(r,house):
    dct = {-1:'W',
           0:'T',
           1:'L'}
    ret = {}
    assert len(r)==len(set([el.__repr__() for el in r]))
    for h in r:
        op=[]
        rc = copy.copy(r)
        idx = [el.__repr__() for el in rc].index(h.__repr__())
        del rc[idx]
        rcrepr = [rca.__repr__() for rca in rc]
        
        for oh in rc: #minl:
            if h.__repr__()==oh.__repr__(): 
                raise Exception('wtf',h,oh,rc)
            myeval = pe.evaln(house+h)
            oheval = pe.evaln(oh+house)
            res = dct[cmp(myeval,oheval)]
            op.append(res)
        op.sort(perms_srt)
        ''.join(op)
        tok = ''.join(op)

        if tok not in ret: ret[tok]=[]
        state = [house,h,myeval,rc]
        ret[tok].append(state)
    #raise Exception([(k,len(v)) for k,v in ret.items()])
    return ret



def write(gperms,oponents):
    opdir = os.path.join('permutations',str(oponents))
    if not os.path.exists(opdir): os.mkdir(opdir)
    for perm in gperms:
        permf = os.path.join(opdir,perm+'.txt')
        fp = open(permf,'a')
        rcnt=0
        for row in gperms[perm]:
            fp.write(row+'\n')
            rcnt+=1
        fp.close()
        print 'wrote',rcnt,'lines into',permf

def extract():
    oponents=int(sys.argv[1])
    perms = get_result_permutations(oponents) 
    gperms={}
    print len(perms),'permutations needed'
    cnt=0 ; pcnt=0
    if sys.argv[2]=='randeal':
        it = randeal
    elif sys.argv[2]=='permute':
        it = permute
    try:
        for p in it(5+(oponents+1)*2):
            #print p
            pcnt+=1
            if pcnt % 10000 ==0: print 'pcnt',pcnt
            if pcnt>=10000000: break

            #continue
            cards = p.split(' ')
            house = cards[0:5]


            r=[]
            #print 'house',house
            for i in range(5,5+oponents+1):
                r.append([cards[i],cards[i+1]])

            mp = extract_permutations(r,house)


            for perm in mp:
                if perm not in gperms:
                    gperms[perm]={}
                    missing = perms-set(gperms.keys())
                    print (gperms.keys()),'attained;',cnt,'tot.',pcnt,'ptot ; missing:',missing


                for st in mp[perm]:
                    strep = ' '.join([sta.__repr__() for sta in st])
                    if strep not in gperms[perm]: 

                        gperms[perm][strep]=0
                    else:
                        pass
                    gperms[perm][strep]+=1
                    cnt+=1
            if not len(missing): break
    finally:
        print 'WRITING'
        write(gperms,oponents)
                
    return gperms

if __name__=='__main__':
    extract()

