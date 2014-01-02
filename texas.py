import random
colors = ['h','d','c','s']
def gendeck(type='normal',jokers=True):
    if type=='russian':
        numbers=['6','7','8','9','T']
    else:
        numbers = ['2','3','4','5','6','7','8','9','T']
    royalty = ['J','Q','K','A']

    deck=[]
    for c in colors:
        deck+= map(lambda x: str(x)+c,numbers+royalty)
    if jokers: deck+=['O1','O2'] #add two jokers
    return list(deck)

hand_combinations = [
    'high_card',                
    'pair',
    'two_pair',
    'three_of_a_kind',
    'straight',
    'flush',                    
    'full_house',
    'four_of_a_kind',
    'straight_flush',
    'royal_flush'
]

cardworths = {
    '2':2,
    '3':3,
    '4':4,
    '5':5,
    '6':6,
    '7':7,
    '8':8,
    '9':9,
    'T':10,
    'J':11,
    'Q':12,
    'K':13,
    'A':14
    }
worthcards = dict(zip(cardworths.values(),cardworths.keys()))

def card_sort(c1,c2):

    return cmp(cardworths[c1[0:-1]],
               cardworths[c2[0:-1]])

def nextcard(c):
    cw = cardworths[c[0:-1]]
    if cw+1 in worthcards:
        rt = worthcards[cw+1]
        return rt+c[1]
    else:
        return None

def eval_pair(hand,mode='pair'):
    agg={}
    for h in hand:
        denom = h[0:-1]
        if denom not in agg:
            agg[denom]=0
        agg[denom]+=1
    if mode=='three_of_a_kind':
        minf=2
    elif mode=='four_of_a_kind':
        minf=3
    elif mode=='high_card':
        minf=0
    elif mode in ['full_house','two_pair','pair']:
        minf=1
    else: raise Exception('unknown mode %s'%mode)

    agg = filter(lambda x: x[1]>minf,agg.items())
    agg.sort(lambda x,y: cmp(cardworths[x[0]],cardworths[y[0]]))
    if mode=='two_pair':
        if len(agg)>=2:
            return [(cardworths[cw[0]]*cw[1],cw) for cw in agg]
    elif mode in ['pair','three_of_a_kind','four_of_a_kind']:
        if len(agg):
            return cardworths[agg[-1][0]]*agg[-1][1],agg[-1]
    elif mode in ['high_card']:
        return cardworths[agg[-1][0]],agg[-1]
    elif mode in ['full_house']:
        aggv = [v[1] for v in agg]
        if 2 in aggv and 3 in aggv:
            cworth = [cardworths[cw[0]]*cw[1] for cw in agg]
            return sum(cworth),agg
    else:
        raise Exception('unknown mode %s'%mode)
    return False

def eval_two_pair(hand):
    return eval_pair(hand,mode='two_pair')
def eval_three_of_a_kind(hand):
    return eval_pair(hand,mode='three_of_a_kind')
def eval_high_card(hand):
    return eval_pair(hand,mode='high_card')
def eval_full_house(hand):
    return eval_pair(hand,mode='full_house')
def eval_four_of_a_kind(hand):
    return eval_pair(hand,mode='four_of_a_kind')

def eval_flush(hand,royal=False,straight=False,flush=True):
    rt=False
    if flush: lim_colors = colors
    else: lim_colors = ['_']
    for lim_color in lim_colors:
        if flush:
            hc = filter(lambda x: x[1]==lim_color,hand)
            if not straight and not royal and len(hc)==5:
                return (sum([cardworths[h[0:-1]] for h in hc]),hc)
        else:
            hc = hand
        #print 'sorting %s'%hc
        hc.sort(card_sort)
        sequential=0
        if royal and len(hc) and cardworths[hc[0][0:-1]]!=10: 
            continue
        for i in range(len(hc)):
            crd = hc[i]
            seq_nxt = nextcard(crd)
            if not seq_nxt:
                continue
            #print '%s != %s'%(seq_nxt,
            # if i+1 not in hc:
            #     break
            ni = i+1
            if len(hc)<ni+1:
                break
            #print 'getting index',ni,'in',hc,len(hc)<ni
            real_nxt=hc[ni]
            if seq_nxt[0:-1]==real_nxt[0:-1]:
                sequential+=1
            else:
                break

            if sequential>=4:
                rt=(sum([cardworths[h[0:-1]] for h in hand]),hand)
                break
    return rt
def eval_straight(hand):
    return eval_flush(hand,straight=True,flush=False,royal=False)
def eval_straight_flush(hand):
    return eval_flush(hand,straight=True)

def eval_royal_flush(hand):
    return eval_flush(hand,royal=True,straight=True)

def eval_hand(hand):
    global hand_combinations
    for hc in reversed(hand_combinations):
        ev = eval('eval_'+hc)(hand)
        if ev:
            return (True,hc,ev)
    return False,None,None
def hands_cmp(h1,h2):
    c1 = hand_combinations.index(h1[1][2])
    c2 = hand_combinations.index(h2[1][2])
    rt= cmp(c1,c2)
    #FIXME: this is incorrect, we judge by the sum of card worths
    #rather than precisely by the rules.
    if rt==0:
        rt = cmp(h1[1][3][0],h2[1][3][0])
    return rt

def playround(participants=1):
    rt={}
    deck = gendeck(jokers=False)
    hands={} ; house=[]
    random.shuffle(deck)
    #deal hands
    for pi in range(0,participants):
        hands[pi]=[]
        for i in range(2):
            hands[pi].append(deck.pop())

    #deal house
    house.append(deck.pop())
    house.append(deck.pop())
    house.append(deck.pop())

    #print 'dealt: [%s] %s'%(' '.join(house),', '.join([' '.join(h) for h in hands.values()]))
    #evaluate hands
    for pi in hands:
        iseval,ev,worth = eval_hand(hands[pi]+house)
        #print worth,ev,hands[pi],house
        if ev: 
            assert pi not in rt
            rt[pi]=(hands[pi],house,ev,worth)
            #print house,hands[pi],ev,worth
    rt = rt.items()
    winner = None

    if participants>1: #find the winner
        rt.sort(hands_cmp)
        wworth = rt[-1][1][3][0]
        pworth  =rt[-2][1][3][0]
        if wworth>pworth:
            winner = rt[-1]


    return rt,winner
    #raise Exception(hands,house)

def test(lim=10000000):
    cnt=0
    patterns={}
    try:        
        for i in range(lim):
            res,winner = playround(participants=8)
            print winner
            for pid,r in res:
                if r[2] not in patterns: patterns[r[2]]=0
                patterns[r[2]]+=1
            cnt+=1
    finally:
        print 'hands played:',cnt
        for k,v in sorted(patterns.items(),lambda x,y: cmp(x[1],y[1]),reverse=True):
            print k,v,'%4.4f'%(float(v)/cnt*100)+'%'
    

    
if __name__=='__main__':
    test()
