#######在训练集上测试准确率
import json
import pickle
from pairwise_evaluate import pairwise_evaluate
from paper_similarity import generate_pair
from save_relations import save_relation
from random_walk import MetaPathGenerator
f1=open("./OAG-v2-track1/OAG-v2-track1/train_pub.json","r",encoding="utf-8")
pubs_raw = json.load(f1)
f2=open("./OAG-v2-track1/OAG-v2-track1/train_author.json","r",encoding="utf-8")
name_pubs = json.load(f2)
import re
from gensim.models import word2vec
from sklearn.cluster import DBSCAN

import numpy as np
from sklearn.metrics.pairwise import pairwise_distances

result = []
for n, name in enumerate(name_pubs):
    if(n>5):
        break
    ilabel = 0
    pubs = []  # all papers
    labels = []  # ground truth

    for author in name_pubs[name]:
        iauthor_pubs = name_pubs[name][author]
        for pub in iauthor_pubs:
            pubs.append(pub)
            labels.append(ilabel)
        ilabel += 1

    print(n, name, len(pubs))

    if len(pubs) == 0:
        result.append(0)
        continue

    ##保存关系
    ###############################################################
    name_pubs_raw = {}
    for i, pid in enumerate(pubs):
        try:
            name_pubs_raw[pid] = pubs_raw[pid]
        except:
            print("no")
    #f3=open("genename/"+name+".json","w",encoding="utf-8")
    #json.dump(name_pubs_raw, f3, indent=4)
    save_relation(name + '.json', name)
    ###############################################################

    ##元路径游走类
    ###############################################################r
    mpg = MetaPathGenerator()
    mpg.read_data()
    ###############################################################

    ##论文关系表征向量
    ###############################################################
    all_embs = []
    rw_num = 5
    cp = set()
    for k in range(rw_num):
        mpg.generate_WMRW("gene/RW.txt", 5, 20)  # 生成路径集
        sentences = word2vec.Text8Corpus(r'gene/RW.txt')
        model = word2vec.Word2Vec(sentences, size=100, min_count=1,iter=10,negative=25, window=10)
        embs = []
        for i, pid in enumerate(pubs):
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
    f4=open("gene/ptext_embedding.pkl","rb")
    ptext_emb =pickle.load(f4)
    f5=open("gene/tcp.pkl","rb")
    tcp = pickle.load(f5)
    print('semantic outlier:', tcp)
    tembs = []
    for i, pid in enumerate(pubs):
        tembs.append(ptext_emb[pid])
    ###############################################################

    ##离散点
    outlier = set()
    for i in cp:
        outlier.add(i)
    for i in tcp:
        outlier.add(i)

    ##网络嵌入向量相似度
    sk_sim = np.zeros((len(pubs), len(pubs)))
    for k in range(rw_num):
        sk_sim = sk_sim + pairwise_distances(all_embs[k], metric="cosine")
    sk_sim = sk_sim / rw_num

    ##文本相似度
    t_sim = pairwise_distances(tembs, metric="cosine")

    w = 1
    sim = (np.array(sk_sim) + w * np.array(t_sim)) / (1 + w)

    ##evaluate
    ###############################################################
    pre = DBSCAN(eps=0.25, min_samples=4, metric="precomputed").fit_predict(sim)

    for i in range(len(pre)):
        if pre[i] == -1:
            outlier.add(i)

    ## assign each outlier a label
    paper_pair = generate_pair(pubs, outlier)
    paper_pair1 = paper_pair.copy()
    K = len(set(pre))
    for i in range(len(pre)):
        if i not in outlier:
            continue
        j = np.argmax(paper_pair[i])
        while j in outlier:
            paper_pair[i][j] = -1
            j = np.argmax(paper_pair[i])
        if paper_pair[i][j] >= 1.5:
            pre[i] = pre[j]
        else:
            pre[i] = K
            K = K + 1

    ## find nodes in outlier is the same label or not
    for ii, i in enumerate(outlier):
        for jj, j in enumerate(outlier):
            if jj <= ii:
                continue
            else:
                if paper_pair1[i][j] >= 1.5:
                    pre[j] = pre[i]

    labels = np.array(labels)
    pre = np.array(pre)
    print(labels, len(set(labels)))
    print(pre, len(set(pre)))
    pairwise_precision, pairwise_recall, pairwise_f1 = pairwise_evaluate(labels, pre)
    print(pairwise_precision, pairwise_recall, pairwise_f1)
    result.append(pairwise_f1)

    print('avg_f1:', np.mean(result))
