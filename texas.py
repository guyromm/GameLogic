#!/usr/bin/env python

import random,sys,json
from functools import cmp_to_key as c2k
def cmp(a, b):
    return (a > b) - (a < b)


class Card(object):
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
    
    colors = ['h','d','c','s']
    numbers = ['2','3','4','5','6','7','8','9','T']
    royalty = ['J','Q','K','A']
    jokers = ['O1','O2']

    def to_json(self):
        return self.__repr__()
    def next(self):
        cw = self.cardworths[self.rank]
        if cw+1 in self.worthcards:
            rt = self.worthcards[cw+1]
            return Card(rt,self.suit)
        else:
            return None
    
    def __init__(self,rank,suit):
        assert rank in self.numbers or rank in self.royalty,rank
        assert suit in self.colors,suit
        self.rank = rank
        self.suit = suit
    def __repr__(self):
        return self.rank+self.suit

    def __gt__(self,c2):
        return self.cardworths[self.rank] > self.cardworths[c2.rank]
    def __lt__(self,c2):
        return self.cardworths[self.rank] < self.cardworths[c2.rank]
    def __eq__(self,c2):
        return self.cardworths[self.rank] == self.cardworths[c2.rank]

    
class RuCard(Card):
    numbers=['6','7','8','9','T']    
    jokers=[]

class CardCollection(object):
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
    def to_json(self):
        return [c.to_json() for c in self.cards]
    @classmethod
    def from_json(cls,j):
        o = cls()
        o.cards=[]
        for c in [Card(i[0],i[1]) for i in j]:
            o.cards.append(c)
        return o
    def eval_pair(self,mode='pair'):
        hand = self
        agg={}
        for h in hand:
            denom = h.rank
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

        agg = list(filter(lambda x: x[1]>minf,agg.items()))
        agg.sort(key=c2k(lambda x,y: cmp(Card.cardworths[x[0]],Card.cardworths[y[0]])))
        if mode=='two_pair':
            if len(agg)>=2:
                rt= [(Card.cardworths[cw[0]]*cw[1],cw) for cw in agg]
                tworth = sum([r[0] for r in rt])
                return (tworth,rt)
        elif mode in ['pair','three_of_a_kind','four_of_a_kind']:
            if len(agg):
                return Card.cardworths[agg[-1][0]]*agg[-1][1],agg[-1]
        elif mode in ['high_card']:
            return Card.cardworths[agg[-1][0]],agg[-1]
        elif mode in ['full_house']:
            aggv = [v[1] for v in agg]
            if 2 in aggv and 3 in aggv:
                cworth = [Card.cardworths[cw[0]]*cw[1] for cw in agg]
                return sum(cworth),agg
        else:
            raise Exception('unknown mode %s'%mode)
        return False

    def eval_two_pair(self):
        return self.eval_pair(mode='two_pair')
    def eval_three_of_a_kind(self):
        return self.eval_pair(mode='three_of_a_kind')
    def eval_high_card(self):
        return self.eval_pair(mode='high_card')
    def eval_full_house(self):
        return self.eval_pair(mode='full_house')
    def eval_four_of_a_kind(self):
        return self.eval_pair(mode='four_of_a_kind')

    def eval_flush(self,royal=False,straight=False,flush=True):

        rt=False
        if flush: lim_colors = Card.colors
        else: lim_colors = ['_']
        for lim_color in lim_colors:
            if flush:
                hc = list(filter(lambda x: x.suit==lim_color,self))
                if not straight and not royal and len(hc)==5:
                    return (sum([Card.cardworths[h.rank] for h in hc]),hc)
            else:
                hc = self
            #print('sorting %s'%hc)
            hc.sort() #key=c2k(card_sort))
            sequential=0
            if royal and len(hc) and Card.cardworths[hc[0].rank]!=10: 
                continue
            for i in range(len(hc)):
                crd = hc[i]
                seq_nxt = crd.next()
                if not seq_nxt:
                    continue
                #print('%s != %s'%(seq_nxt)
                # if i+1 not in hc:
                #     break
                ni = i+1
                if len(hc)<ni+1:
                    break
                #print('getting index',ni,'in',hc,len(hc)<ni)
                real_nxt=hc[ni]
                if seq_nxt.rank==real_nxt.rank:
                    sequential+=1
                else:
                    break

                if sequential>=4:
                    rt=(sum([Card.cardworths[h.rank] for h in self]),self)
                    break
        return rt
    def eval_straight(self):
        return self.eval_flush(straight=True,flush=False,royal=False)
    def eval_straight_flush(self):
        return self.eval_flush(straight=True)

    def eval_royal_flush(self):
        return self.eval_flush(royal=True,straight=True)

    def eval(self):
        for hc in reversed(self.hand_combinations):
            ev = getattr(self,'eval_'+hc)()
            if ev:
                #print(hc.upper(),':',type(ev),ev)
                assert type(ev)==tuple
                return (True,hc,ev)
        return False,None,None
    
    def __init__(self,jokers=False,card=Card,shuffle=True):
        self.jokers=jokers
        self.card = card

    def __len__(self):
        return len(self.cards)

    def __getitem__(self,key):
        return self.cards[key]
    
    def __add__(self,c2):
        cc = CardCollection()
        cc.cards=self.cards+c2.cards
        return cc

    def __iter__(self):
        for c in self.cards:
            yield c

    def sort(self):
        self.cards.sort()
    
    def __repr__(self):
        return str(self.cards)
    
class Deck(CardCollection):

    def __init__(self,jokers=False,card=Card,shuffle=True):
        super().__init__(jokers=jokers,card=card,shuffle=shuffle)
        self.generate(shuffle=shuffle)

    def deal(self,qty=2):
        rt=[]
        for i in range(qty):
            rt.append(self.pop())
        return rt
        
    def generate(self,shuffle=True):
        numbers = self.card.numbers
        royalty = self.card.royalty

        deck=[]
        for s in self.card.colors:
            for r in self.card.numbers+self.card.royalty:
                c = self.card(r,s)
                deck.append(c)
        if self.jokers:
            for j in self.card.jokers:
                deck+=self.card(j) #.jokers #add two jokers
        self.cards = list(deck)
        if shuffle: random.shuffle(self.cards)

    def pop(self):
        return self.cards.pop()

class Hand(Deck):
    take_qty=2
    def generate(self,*args,**kwargs):
        self.cards = []
    def take(self,cards,qty=take_qty):
        assert len(cards)==qty,"%s != %s"%(cards,qty)
        self.cards+=cards

class House(Hand):
    take_qty=3
    pass

class Game(object):
    def __init__(self,participants=1):
        self.participants = participants
        self.deck = Deck()
        self.hands={} 
        self.house=House()
    
    @classmethod
    def load(cls,obj):
        g = Game(obj['participants'])
        g.deck = Deck.from_json(obj['deck'])

        for hid,h in obj['hands'].items():
            g.hands[hid]=Hand.from_json(h)
        g.house = House.from_json(obj['house'])
        return g
    
    def to_json(self):
        return json.dumps({'participants':self.participants,
                           'deck':self.deck.to_json(),
                           'hands':dict([(k,h.to_json()) for (k,h) in self.hands.items()]),
                           'house':self.house.to_json()
                          })
    

    def deal(self):
        #deal hands
        for pi in range(0,self.participants):
            self.hands[pi] = Hand()
            self.hands[pi].take(self.deck.deal())

        #deal house
        self.house.take(self.deck.deal(3),3)

        
    def play(self):
        rt={}

        self.deal()
        #print('dealt: [%s] %s'%(' '.join(house),', '.join([' '.join(h) for h in hands.values()])))
        #evaluate hands
        for pi in self.hands:
            iseval,ev,worth = (self.hands[pi]+self.house).eval()
            #print(worth,ev,hands[pi],house)
            if ev: 
                assert pi not in rt
                rt[pi]={'hand':self.hands[pi], # 0
                        'house':self.house,    # 1 
                        'ev':ev,          # 2
                        'worth':worth}    # 3
                #Print(house,hands[pi],ev,worth)
        rt = list(rt.items())
        types = set([type(trt) for trt in rt])
        assert len(types)==1
        for t in types: assert t==tuple,t
        self.winner = None

        if self.participants>1: #find the winner
            rt.sort() #key=c2k(hands_cmp))

            types = set([type(trt) for trt in rt])
            assert len(types)==1
            for t in types: assert t==tuple,t


            wworth = rt[-1][1]['worth'][0]
            pworth = rt[-2][1]['worth'][0]

            # assert type(wworth)==int,Exception(rt[-1][1]['worth'])
            # assert type(pworth)==int,Exception(rt[-2][1]['worth'])
            try:
                if wworth>pworth:
                    self.winner = rt[-1]
            except TypeError:
                print('wworth:',rt[-1][1]['worth'])
                print('pworth:',rt[-2][1]['worth'])
                raise


        return rt,self.winner
        #raise Exception(hands,house)

def test(lim=10000):
    random.seed(len(sys.argv)>1 and sys.argv[1] or None)
    cnt=0
    patterns={}
    try:        
        for i in range(lim):
            g = Game(participants=8)
            res,winner = g.play()
            print(winner)

            for pid,r in res:
                if r['ev'] not in patterns: patterns[r['ev']]=0
                patterns[r['ev']]+=1
            cnt+=1
    finally:
        print('hands played:',cnt)
        for k,v in sorted(patterns.items(),key=c2k(lambda x,y: cmp(x[1],y[1])),reverse=True):
            print(k,v,'%2.2f'%(float(v)/cnt*10)+'%')
    

    
if __name__=='__main__':
    if 'test' in sys.argv:
        test()

    if 'new' in sys.argv:
        g = Game(participants=8)
    elif 'load' in sys.argv:
        j = json.load(sys.stdin)
        g = Game.load(j)
    if 'deal' in sys.argv:
        g.deal()
    if 'save' in sys.argv:
        print(g.to_json())
