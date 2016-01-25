#! /usr/bin/env python
# coding:utf-8

import decimal
import sqlite3

decimal.getcontext().prec = 4
decimal.getcontext().rounding = decimal.ROUND_HALF_UP

def mkcorpus(sentences):
    return [(es.split(), fs.split()) for (es, fs) in sentences]

def _train(corpus, loop_count=1000):
    f_keys = set()
    for (es, fs) in corpus:
        for f in fs:
            f_keys.add(f)

    uniformPro = 1.0/len(f_keys)    #uniform probability initialization
    db = sqlite3.connect('mydb.db')
    cursor = db.cursor()
    cursor.execute('''create table if not exists t(e text, f text, val real, primary key (e, f))''')

    cursor.execute('''create table if not exists count(e text, f text, val real, primary key (e, f))''')
    cursor.execute('''create table if not exists total(f text unique, val real)''')
    cursor.execute('''create table if not exists s_total(e text unique, val real)''')
    for (es, fs) in corpus:
        for e in es:
            s_total = 0.0
            for f in fs:
                c1=db.cursor()
                cursor.execute('''create index if not exists t_ef on t(e, f)''')
                c1.execute('''select val from t indexed by t_ef where e=? and f=?''',(e,f))
                l = list(c1)
                if l==[]:
                    t = uniformPro
                else:
                    t = l[0][0]
                s_total += t
            try:
                cursor.execute('''insert into s_total values(?, ?)''', (e, s_total))
            except:
                cursor.execute('''update s_total set val=? where e=?''', (s_total, e))
                    
        for e in es:
            cursor.execute('''create index if not exists st_e on s_total(e)''')
            cursor.execute('''select val from s_total indexed by st_e where e=?''', (e,))
            l = list(cursor)
            s_total = l[0][0]
            for f in fs:
                cursor.execute('''create index if not exists t_f on total(f)''')
                cursor.execute('''select val from total indexed by t_f where f=?''', (f,))
                l = list(cursor)
                if l==[]:
                    total = 0.0
                else:
                    total = l[0][0]
                cursor.execute('''create index if not exists c_ef on count(e, f)''')
                cursor.execute('''select val from count indexed by c_ef where e=? and f=?''', (e,f))
                l = list(cursor)
                if l==[]:
                    count = 0.0
                else:
                    count = l[0][0]
                cursor.execute('''select val from t indexed by t_ef where e=? and f=?''',(e,f))
                l = list(cursor)
                if l==[]:
                    t =uniformPro
                else:
                    t = l[0][0]
                        
                count += t / s_total
                total += t / s_total

                try:
                    cursor.execute('''insert into count values(?,?,?)''',(e, f, count))
                except:
                    cursor.execute('''update count set val=? where e=? and f=?''',(count, e, f))
                try:
                    cursor.execute('''insert into total values(?,?)''',(f, total))
                except:
                    cursor.execute('''update total set val=? where f=?''',(total, f))

    c1 = db.cursor()
    c1.execute('''select * from count''')
    for row in c1:
        cursor.execute('''select val from total indexed by t_f where f=?''',(row[1],))
        l1 = list(cursor)
        total = l1[0][0]
        try:
            cursor.execute('''insert into t values(?,?,?)''', (row[0], row[1], row[2]/total))
        except:
            cursor.execute('''update t set val = ? where e=? and f=?''', (row[0], row[1], row[2]/total))
                 
    cursor.execute('''create table if not exists myDict(englishWord text, persianWord text, val real)''')
    cursor.execute('''create index t_v on t(val)''')
    cursor.execute('''insert into myDict select * from t indexed by t_v where val>0.8 order by e asc, val desc''')
    cursor.execute('''drop table count''')
    cursor.execute('''drop table total''')
    cursor.execute('''drop table s_total''')
    cursor.execute('''drop table t''')
    
    cursor.execute('''select * from myDict limit 500''')
    
    for row in cursor:
        print("{} {}\t{}".format(row[0], row[1], row[2]))

#
#    cursor.execute('''drop table myDict''')
#    
    db.commit()
    db.close()
    
def train(bitext):
    corpus = mkcorpus(bitext)
    return _train(corpus)

if __name__ == '__main__':
    me = open("Clean_Mizan_En.txt")
    mf = open("Clean_Mizan_Fa.txt", encoding="utf8")
    bitext = list(zip(me, mf))
    train(bitext)    
