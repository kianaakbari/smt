#! /usr/bin/env python
# coding:utf-8

import os
import collections
import ibmmodel1
import utility
import decimal
from decimal import Decimal as D

# set deciaml context
decimal.getcontext().prec = 4
decimal.getcontext().rounding = decimal.ROUND_HALF_UP


class _keydefaultdict(collections.defaultdict):
    '''define a local function for uniform probability initialization'''
    def __missing__(self, key):
        if self.default_factory is None:
            raise KeyError(key)
        else:
            ret = self[key] = self.default_factory(key)
            return ret

def _train(corpus, loop_count=1000):
    #print(corpus)
    #print(loop_count)
    f_keys = set()
    for (es, fs) in corpus:
        for f in fs:
            f_keys.add(f)
    # initialize t
    t = ibmmodel1._train(corpus, loop_count)
    # default value provided as uniform probability)

    def key_fun(key):
        ''' default_factory function for keydefaultdict '''
        i, j, l_e, l_f = key
        return D("1") / D(l_f + 1)
    a = _keydefaultdict(key_fun)

    # loop
    for _i in range(loop_count):
        # variables for estimating t
        count = collections.defaultdict(D)
        total = collections.defaultdict(D)
        # variables for estimating a
        count_a = collections.defaultdict(D)
        total_a = collections.defaultdict(D)

        s_total = collections.defaultdict(D)
        for (es, fs) in corpus:
            l_e = len(es)
            l_f = len(fs)
            #l_e = os.stat(es).st_size
            #l_f = os.stat(fs).st_size
            
            # compute normalization
            for (j, e) in enumerate(es, 1):
                s_total[e] = 0
                for (i, f) in enumerate(fs, 1):
                    s_total[e] += t[(e, f)] * a[(i, j, l_e, l_f)]
            # collect counts
            for (j, e) in enumerate(es, 1):
                for (i, f) in enumerate(fs, 1):
                    c = t[(e, f)] * a[(i, j, l_e, l_f)] / s_total[e]
                    count[(e, f)] += c
                    total[f] += c
                    count_a[(i, j, l_e, l_f)] += c
                    total_a[(j, l_e, l_f)] += c

        #for k, v in total.items():
        #    if v == 0:
        #        print(k, v)
        # estimate probability
        for (e, f) in count.keys():
            try:
                t[(e, f)] = count[(e, f)] / total[f]
            except decimal.DivisionByZero:
                print(u"e: {e}, f: {f}, count[(e, f)]: {ef}, total[f]: \
                      {totalf}".format(e=e, f=f, ef=count[(e, f)],
                                       totalf=total[f]))
                raise
        for (i, j, l_e, l_f) in count_a.keys():
            a[(i, j, l_e, l_f)] = count_a[(i, j, l_e, l_f)] / \
                total_a[(j, l_e, l_f)]
    # output
    #for (e, f), val in t.items():
    #    print("{} {}\t{}".format(e, f, float(val)))
    #for (i, j, l_e, l_f), val in a.items():
    #    print("{} {} {} {}\t{}".format(i, j, l_e, l_f, float(val)))

    return (t, a)


def train(bitext, loop_count=1000):
    #for i, j in sentences:
    #    print(i, j)
    corpus = utility.mkcorpus(bitext)
    return _train(corpus, loop_count)


def viterbi_alignment(le, lf, t, a):
    '''
    return
        dictionary
            e in es -> f in fs
    '''
    max_a = collections.defaultdict(float)
    l_e = len(le)
    l_f = len(lf)
    #l_e = os.stat(es).st_size
    #l_f = os.stat(fs).st_size
    
    for (j, e) in enumerate(es, 1):
        current_max = (0, -1)
        for (i, f) in enumerate(fs, 1):
            val = t[(e, f)] * a[(i, j, l_e, l_f)]
            # select the first one among the maximum candidates
            if current_max[1] < val:
                current_max = (i, val)
        max_a[j] = current_max[0]
    return max_a


def show_matrix(le, lf, t, a):
    '''
    print matrix according to viterbi alignment like
          fs
     -------------
    e|           |
    s|           |
     |           |
     -------------
    >>> sentences = [("僕 は 男 です", "I am a man"),
                     ("私 は 女 です", "I am a girl"),
                     ("私 は 先生 です", "I am a teacher"),
                     ("彼女 は 先生 です", "She is a teacher"),
                     ("彼 は 先生 です", "He is a teacher"),
                     ]
    >>> t, a = train(sentences, loop_count=1000)
    >>> args = ("私 は 先生 です".split(), "I am a teacher".split(), t, a)
    |x| | | |
    | | |x| |
    | | | |x|
    | | |x| |
    '''
    max_a = viterbi_alignment(le, lf, t, a).items()
    m = len(le)
    n = len(lf)
    return utility.matrix(m, n, max_a, le, lf)



def test_viterbi_alignment():
    x = viterbi_alignment([1, 2, 1],
                          [2, 3, 2],
                          collections.defaultdict(int),
                          collections.defaultdict(int))
    # Viterbi_alignment selects the first token
    # if t or a doesn't contain the key.
    # This means it returns NULL token
    # in such a situation.
    ans = {1: 1, 2: 1, 3: 1}
    assert dict(x) == ans


if __name__ == '__main__':
    import sys

    es = open(sys.argv[1]) if len(sys.argv) >= 3 else open("a.txt")
    fs = open(sys.argv[2], encoding="utf-8") if len(sys.argv) >= 3 else open("b.txt", encoding="utf8")
    bitext = list(zip(es, fs))
    t, a = train(bitext, loop_count=3)

    #es = "私 は 先生 です".split()
    #fs = "I am a teacher".split()
#    le = list(es.read().split())
#    lf = list(es.read().split())
#    args = (le, lf, t, a)
#    print(show_matrix(*args))

    for (e, f), val in t.items():
        if(val>=0.8):
            print("{} {}\t{}".format(e, f, val))
