# author-name-disambiguation

1、先下载数据集，将数据集放在此文件夹里\
2、将word2vec.py前半部分的注释去掉，运行。（这一步将测试集和验证集的abstract,venue,keyword,org等信息存储到gene/all_text.txt中。然后再根据此文件训练word2vec）\
   训练word2vec的参数可调。*注意：如果调整了embedding size，需要同时改变save_relations.py的word_len.*\
3、再运行train_score.py,给出*训练集*上的测试结果。里面的参数都可调整，结果可以帮助调参。\
4、调好参数之后，将调好的参数运用于save_paper_feature.py，给出*验证集*上的结果。提交之。\




   
