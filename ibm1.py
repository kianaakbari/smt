#! /usr/bin/env python
# coding:utf-8

import collections
import decimal
from decimal import Decimal as D
import sqlite3

# set deciaml context
decimal.getcontext().prec = 4
decimal.getcontext().rounding = decimal.ROUND_HALF_UP

def _constant_factory(value):
    '''define a local function for uniform probability initialization'''
    return lambda: value

def mkcorpus(sentences):
    return [(es.split(), fs.split()) for (es, fs) in sentences]

def _train(corpus, loop_count=1000):
    f_keys = set()
    for (es, fs) in corpus:
        for f in fs:
            f_keys.add(f)
    # default value provided as uniform probability)
    t = collections.defaultdict(_constant_factory(D(1/len(f_keys))))

    # loop
    for i in range(loop_count):
        count = collections.defaultdict(D)
        total = collections.defaultdict(D)
        s_total = collections.defaultdict(D)
        for (es, fs) in corpus:
            # compute normalization
            for e in es:
                s_total[e] = D()
                for f in fs:
                    s_total[e] += t[(e, f)]
            for e in es:
                for f in fs:
                    count[(e, f)] += t[(e, f)] / s_total[e]
                    total[f] += t[(e, f)] / s_total[e]
        # estimate probability
        for (e, f) in count.keys():
            t[(e, f)] = count[(e, f)] / total[f]

    return t

def train(bitext, loop_count=1000):
    corpus = mkcorpus(bitext)
    return _train(corpus, loop_count)

if __name__ == '__main__':
    import sys
    es = open(sys.argv[1]) if len(sys.argv) >= 3 else open("a.txt")
    fs = open(sys.argv[2], encoding="utf-8") if len(sys.argv) >= 3 else open("b.txt", encoding="utf8")
    bitext = list(zip(es, fs))

    db = sqlite3.connect('mydb.db')
    cursor = db.cursor()
    cursor.execute('''create table if not exists tmp(englishWord text, persianWord text, val real)''')
    
    t = train(bitext, loop_count=1)

    for (e, f), val in t.items():
        cursor.execute('''insert into tmp values(?, ?, ?)''', (e, f, float(val)))

    cursor.execute('''create table if not exists myDict(englishWord text, persianWord text, val real)''')
    cursor.execute('''insert into myDict select * from tmp order by englishWord asc, val desc''')
    cursor.execute('''select * from myDict limit 50''')

    print("training after one loop:")
    for row in cursor:
        print("{} {}\t{}".format(row[0], row[1], row[2]))
    print('\n')

    cursor.execute('''delete from tmp''')
    cursor.execute('''delete from myDict''')
    
    t = train(bitext, loop_count=3)

    for (e, f), val in t.items():
        cursor.execute('''insert into tmp values(?, ?, ?)''', (e, f, float(val)))
    
    cursor.execute('''insert into myDict select * from tmp order by englishWord asc, val desc''')
    cursor.execute('''drop table tmp''')
    cursor.execute('''select * from myDict limit 50''')
    print("training after 3 loops:")
    for row in cursor:
        print("{} {}\t{}".format(row[0], row[1], row[2]))
    print('\n')

#
#    cursor.execute('''drop table myDict''') 
#
    
    db.commit()
    db.close()
