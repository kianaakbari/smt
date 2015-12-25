
def clear(fo,fw):
    for f in fo:
        f=f.split()
        for i in f:
            #remove numbers
            if(i.isdigit()):
                f.remove(i)
            #remove punctuatuions
            l = list(i)
            s = ""
            for j in l:
                if((((j == '.') or (j == ',')) or ((j == ':') or (j == ';'))) or (((j == '،') or (j == '؛')) or (((j == '(') or (j == ')')) or ((j == '?') or (j == '!'))))):
                    l.remove(j)
                else:
                    s = s+ j
                    break
            if(s == ""):
                f.remove(i)

        t = ""
        #remove punc in words
        for i in range(len(f)):
            l = list(f[i])
            s = ""
            for j in l:
                if((((j == '.') or (j == ',')) or ((j == ':') or (j == ';'))) or (((j == '،') or (j == '؛')) or (((j == '(') or (j == ')')) or ((j == '?') or (j == '!'))))):
                    l.remove(j)
                else:
                    s = s+ j
            t += s
            t += " "

        f = t
        fw.write(f)
        fw.write('\n')
    
fo=open("a.txt",encoding = "utf8")
fw=open("b.txt", "w", encoding="utf8")
clear(fo,fw)
fw.close()
fo.close()

fo=open("c.txt",encoding = "utf8")
fw=open("d.txt", "w", encoding="utf8")
clear(fo,fw)
fw.close()
fo.close()
