import numpy as np
def tanimoto(p,q):
    c = [v for v in p if v in q]
    return float(len(c) / (len(p) + len(q) - len(c)))

def generate_pair(pubs, outlier):
#######论文相似度的计算：(pi,pj的共同作者数)*1.5+tanimoto(pi的venue,pj的venue)+
####### tanimoto(pi中待消歧人名的org,pj中待消歧人名的org)+(pi,pj中title共词数)/3
    paper_org = {}
    paper_conf = {}
    paper_author = {}
    paper_word = {}
    temp = set()
    with open("gene/paper_org.txt", encoding='utf-8') as pafile:
        for line in pafile:
            temp.add(line)
    for line in temp:
        toks = line.strip().split(" ")
        if len(toks) == 2:
            p, a = toks[0], toks[1]
            if p not in paper_org:
                paper_org[p] = []
            paper_org[p].append(a)
    temp.clear()

    with open("gene/paper_conf.txt", encoding='utf-8') as pafile:
        for line in pafile:
            temp.add(line)
    for line in temp:
        toks = line.strip().split(" ")
        if len(toks) == 2:
            p, a = toks[0], toks[1]
            if p not in paper_conf:
                paper_conf[p] = []
            paper_conf[p] = a
    temp.clear()

    with open("gene/paper_author.txt", encoding='utf-8') as pafile:
        for line in pafile:
            temp.add(line)
    for line in temp:
        toks = line.strip().split(" ")
        if len(toks) == 2:
            p, a = toks[0], toks[1]
            if p not in paper_author:
                paper_author[p] = []
            paper_author[p].append(a)
    temp.clear()

    with open("gene/paper_word.txt", encoding='utf-8') as pafile:
        for line in pafile:
            temp.add(line)
    for line in temp:
        toks = line.strip().split(" ")
        if len(toks) == 2:
            p, a = toks[0], toks[1]
            if p not in paper_word:
                paper_word[p] = []
            paper_word[p].append(a)
    temp.clear()

    paper_paper = np.zeros((len(pubs), len(pubs)))
    for i, pid in enumerate(pubs):
        if i not in outlier:
            continue
        for j, pjd in enumerate(pubs):
            if j == i:
                continue
            ca = 0
            cv = 0
            co = 0
            ct = 0
            if pid in paper_author and pjd in paper_author:
                ca = len(set(paper_author[pid]) & set(paper_author[pjd])) * 1.5
            if pid in paper_conf and pjd in paper_conf and 'null' not in paper_conf[pid]:
                cv = tanimoto(set(paper_conf[pid]), set(paper_conf[pjd]))
            if pid in paper_org and pjd in paper_org:
                co = tanimoto(set(paper_org[pid]), set(paper_org[pjd]))
            if pid in paper_word and pjd in paper_word:
                ct = len(set(paper_word[pid]) & set(paper_word[pjd])) / 3

            paper_paper[i][j] = ca + cv + co + ct

    return paper_paper