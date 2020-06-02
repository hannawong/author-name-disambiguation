##########给出validation set的结果############
import json,re
import numpy as np
import pickle
from sklearn.cluster import DBSCAN
from gensim.models import word2vec
from save_relations import save_relation
from random_walk import MetaPathGenerator
from sklearn.metrics.pairwise import pairwise_distances
from paper_similarity import generate_pair
#//////////////////////// save all paper info for every author name/////////////////////////////

f1=open("./OAG-v2-track1/OAG-v2-track1/valid/sna_valid_pub.json","r",encoding="utf-8")
f2=open("./OAG-v2-track1/OAG-v2-track1/valid/sna_valid_author_raw.json","r",encoding="utf-8")
pubs_raw = json.load(f1)  #pub
name_pubs1 =json.load(f2)  #author_raw
result={}
for name in name_pubs1:
    papers = name_pubs1[name]
    name_pubs_raw = {}
    for pid in papers:
        name_pubs_raw[pid] = pubs_raw[pid]   ###该作者名下的所有论文信息
    #out=open('genename/'+name +'.json',"w",encoding="utf-8")
    #json.dump(name_pubs_raw, out,ensure_ascii=False, indent=4)
    save_relation(name+".json",name)  #存储该人名的语义信息，关联信息
    mpg = MetaPathGenerator()
    mpg.read_data() #构建图
    ##论文关系表征向量
    ###############################################################
    all_embs = []
    rw_num = 5    ###集成学习，参数可调
    cp = set()
    for k in range(rw_num):
        mpg.generate_WMRW("gene/RandomWalk.txt", 5, 20)  #numwalks，walklength,参数可调
        sentences = word2vec.Text8Corpus(r'gene/RandomWalk.txt')
        model = word2vec.Word2Vec(sentences, size=100, min_count=1,iter=10,negative=25, window=10)  ##表征关系的word2vec，参数可调
        embs = []
        for i, pid in enumerate(papers):
            if pid in model:
                embs.append(model[pid])
            else:
                cp.add(i)
                embs.append(np.zeros(100))
        all_embs.append(embs)
    all_embs = np.array(all_embs)
    print('relational outlier:', cp)
    ###############################################################

    ##论文文本表征向量
    ###############################################################
    f3=open("gene/ptext_embedding.pkl","rb")
    ptext_emb = pickle.load(f3)
    f4=open("gene/tcp.pkl","rb")
    tcp = pickle.load(f4)
    print('semantic outlier:', tcp)
    tembs = []
    for i, pid in enumerate(papers):
        tembs.append(ptext_emb[pid])
    ###############################################################
    ##离散点
    outlier = set()
    for i in cp:
        outlier.add(i)
    for i in tcp:
        outlier.add(i)

    ##网络嵌入向量距离
    sk_sim = np.zeros((len(papers), len(papers)))
    for k in range(rw_num):
        sk_sim = sk_sim + pairwise_distances(all_embs[k], metric="cosine")
    sk_sim = sk_sim / rw_num

    ##文本距离
    t_sim = pairwise_distances(tembs, metric="cosine")
    ##整体距离
    w = 1  ##文本距离和网络关系距离的权重分配，参数可调。
    sim = (np.array(sk_sim) + w * np.array(t_sim)) / (1 + w)
    ####cluster
    pre = DBSCAN(eps=0.25, min_samples=4, metric="precomputed").fit_predict(sim)  #参数可调。
    ##离群论文
    for i in range(len(pre)):
        if pre[i] == -1:
            outlier.add(i)
    for i in cp:
        outlier.add(i)
    for i in tcp:
        outlier.add(i)

    ##基于阈值的相似性匹配,阈值可调
    threshold=1.5
    paper_pair = generate_pair(papers, outlier)
    paper_pair1 = paper_pair.copy()
    K = len(set(pre))
    for i in range(len(pre)):
        if i not in outlier:
            continue
        j = np.argmax(paper_pair[i])
        while j in outlier:
            paper_pair[i][j] = -1
            j = np.argmax(paper_pair[i])
        if paper_pair[i][j] >= threshold:
            pre[i] = pre[j]
        else:
            pre[i] = K
            K = K + 1

    for ii, i in enumerate(outlier):
        for jj, j in enumerate(outlier):
            if jj <= ii:
                continue
            else:
                if paper_pair1[i][j] >= threshold:
                    pre[j] = pre[i]


    result[name] = []
    for i in set(pre):
        oneauthor = []
        for idx, j in enumerate(pre):
            if i == j:
                oneauthor.append(papers[idx])
        result[name].append(oneauthor)
out=open("result_test.json","w",encoding="utf-8")
json.dump(result,out,indent=4)