#####将所有paper的语义表征向量存储在gene/ptext_embedding.pkl
#####将paper的关系存储在gene/paper_author.txt、gene/paper_conf.txt、gene/paper_word.txt、gene/paper_org.txt

import json,re
import numpy as np
import pickle
word_len=250
from gensim.models import word2vec
def save_relation(name_pubs_raw, name): # 保存论文的各种feature
    print(name)
    tcp=set()
    file=open("genename/"+name_pubs_raw,"r",encoding="utf-8")
    name_pubs_raw = json.load(file)
    ## trained by all text in the datasets. Training code is in the cells of "train word2vec"
    model_w = word2vec.Word2Vec.load("word2vec/word2vec.model")

    r = '[!“”"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~—～’]+'
    stopword = ['at', 'based', 'in', 'of', 'for', 'on', 'and', 'to', 'an', 'using', 'with', 'the', 'by', 'we', 'be',
                'is', 'are', 'can']
    stopword1 = ['university', 'univ', 'china', 'department', 'dept', 'laboratory', 'lab', 'school', 'al', 'et',
                 'institute', 'inst', 'college', 'chinese', 'beijing', 'journal', 'science', 'international']

    f1 = open('gene/paper_author.txt', 'w', encoding='utf-8') #paper_id->author
    f2 = open('gene/paper_conf.txt', 'w', encoding='utf-8')  #paper_id->venue
    f3 = open('gene/paper_word.txt', 'w', encoding='utf-8')  #paper_id->keyword
    f4 = open('gene/paper_org.txt', 'w', encoding='utf-8')  #paper->org
    taken = name.split("_")
    name = taken[0] + taken[1]
    name_reverse = taken[1] + taken[0]
    if len(taken) > 2:
        name = taken[0] + taken[1] + taken[2]
        name_reverse = taken[2] + taken[0] + taken[1]
    authorname_dict = {}
    ptext_emb = {}
    for i,paperid in enumerate(name_pubs_raw):
        paper = name_pubs_raw[paperid]
        # save authors
        org = ""
        for author in paper["authors"]:
            authorname = re.sub(r, '', author["name"]).lower()
            taken = authorname.split(" ")
            if len(taken) == 2:  ##检测目前作者名是否在作者词典中
                authorname = taken[0] + taken[1]
                authorname_reverse = taken[1] + taken[0]
                if authorname not in authorname_dict:
                    if authorname_reverse not in authorname_dict:
                        authorname_dict[authorname] = 1
                    else:
                        authorname = authorname_reverse
            else:
                authorname = authorname.replace(" ", "")
            if authorname != name and authorname != name_reverse:
                f1.write(paperid + ' ' + authorname + '\n')  #某篇文章的其他作者
            else:
                if "org" in author:
                    org = author["org"]  #待消歧作者的org
#save org 待消歧作者的机构名
        org_ = org.strip()
        org_ = org_.lower() #小写
        org_ = re.sub(r,' ', org_) #去除符号
        org_ = re.sub(r'\s{2,}', ' ', org_).strip() #去除多余空格
        org_ = org_.split(' ')
        org_ = [word for word in org_ if len(word)>1]
        org_= [word for word in org_ if word not in stopword1]
        org_ = [word for word in org_ if word not in stopword]
        org_=set(org_)
        for word in org_:
            f4.write(paperid + ' ' + word + '\n')
        # save venue
        pstr = paper["venue"].strip()
        pstr = pstr.lower()
        pstr = re.sub(r, ' ', pstr)
        pstr = re.sub(r'\s{2,}', ' ', pstr).strip()
        pstr = pstr.split(' ')
        pstr = [word for word in pstr if len(word) > 1]
        pstr = [word for word in pstr if word not in stopword1]
        pstr = [word for word in pstr if word not in stopword]
        for word in pstr:
            f2.write(paperid + ' ' + word + '\n')
        if len(pstr) == 0:
            f2.write(paperid + ' ' + 'null' + '\n')

        #save text
        text = ""
        keyword=""
        if "keywords" in paper:
            for word in paper["keywords"]:
                keyword=keyword+word+" "
        text = text + paper["title"]
        text=text.strip()
        text = text.lower()
        text = re.sub(r,' ', text)
        text = re.sub(r'\s{2,}', ' ', text).strip()
        text = text.split(' ')
        text = [word for word in text if len(word)>1]
        text = [word for word in text if word not in stopword]
        for word in text:
            f3.write(paperid + ' ' + word + '\n')
#save all words' embedding
        pstr = keyword + " " + paper["title"] + " " + paper["venue"] + " " + org
        if "year" in paper:
              pstr = pstr +  " " + str(paper["year"])
        pstr=pstr.strip()
        pstr = pstr.lower()
        pstr = re.sub(r,' ', pstr)
        pstr = re.sub(r'\s{2,}', ' ', pstr).strip()
        pstr = pstr.split(' ')
        pstr = [word for word in pstr if len(word)>2]
        pstr = [word for word in pstr if word not in stopword]
        pstr = [word for word in pstr if word not in stopword1]

        words_vec = []
        for word in pstr:
            if (word in model_w):
                words_vec.append(model_w[word])
        if len(words_vec) < 1:
            words_vec.append(np.zeros(word_len))
            tcp.add(i)
            print ('outlier:',paperid,pstr)
        ptext_emb[paperid] = np.mean(words_vec, 0)

    #  ptext_emb: key is paper id, and the value is the paper's text embedding
    out1=open("gene/ptext_embedding.pkl","wb")  #存储所有paper的向量(表征paper的语义关系)
    out2=open("gene/tcp.pkl","wb")  #离群paper的id
    pickle.dump(ptext_emb,out1)
    pickle.dump(tcp,out2)
