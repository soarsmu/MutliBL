# Created by happygirlzt on 11 Nov 2020

from sklearn.cluster import KMeans, DBSCAN
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pyclustering.cluster import cluster_visualizer
from pyclustering.cluster.xmeans import xmeans
from pyclustering.cluster.center_initializer import kmeans_plusplus_initializer
from pyclustering.cluster.kmeans import kmeans, kmeans_visualizer
from pyclustering.cluster.elbow import elbow


RANDOM_SEED = 42


# 3. X-means
# Prepare initial centers - amount of initial centers defines amount of clusters from which X-Means will
# start analysis.

def run_x_means(data):
    amount_initial_centers = 1
    initial_centers = kmeans_plusplus_initializer(
        data,
        amount_initial_centers,
        random_state = RANDOM_SEED).initialize()

    # Create instance of X-Means algorithm. The algorithm will start analysis from 2 clusters, the maximum
    # number of clusters that can be allocated is 20.
    xmeans_instance = xmeans(data,
                             centers=initial_centers,
                             kmax=20,
                             random_state = RANDOM_SEED)
    xmeans_instance.process()

    # Extract clustering results: clusters and their centers
    clusters = xmeans_instance.get_clusters()
    clusters.sort()

    first_cluster_size = len(clusters[0])
    #print('first cluster size is {}'.format(first_cluster_size))
    trust_score = float(1.0 / first_cluster_size)
    return trust_score

# Visualize clustering results
def visualize_x_mean(xmeans_instance, data):
    centers = xmeans_instance.get_centers()
    clusters = xmeans_instance.get_clusters()
    
    visualizer = cluster_visualizer()
    visualizer.append_clusters(clusters, data)
    visualizer.append_cluster(centers, None, marker='*', markersize=10)
    visualizer.show()
    
# 4. Elbow
def run_elbow(data):
    # create instance of Elbow method using K value from 1 to 10.
    kmin, kmax = 1, 10
    elbow_instance = elbow(data, kmin, kmax)
    # process input data and obtain results of analysis
    elbow_instance.process()
    amount_clusters = elbow_instance.get_amount()

    # perform cluster analysis using K-Means algorithm
    centers = kmeans_plusplus_initializer(
        data, amount_clusters,
        amount_candidates=kmeans_plusplus_initializer.FARTHEST_CENTER_CANDIDATE).initialize()
    
    kmeans_instance = kmeans(data, centers)
    kmeans_instance.process()
    
    clusters = kmeans_instance.get_clusters()
    centers = kmeans_instance.get_centers()
    kmeans_visualizer.show_clusters(data, clusters, centers)

# Satisfying H2
def satisfying_h2(trust_score):
    return trust_score > threshold_score

def return_top_k_ids(original_dict):
    # Sort the code files by the similarity scores return top K
    sorted_code_scored_dict = {k: v for k, v in sorted(original_dict.items(), key=lambda item: item[1], reverse=True)}
    df=pd.DataFrame(sorted_code_scored_dict, index=[0])
    df=df.transpose()
    df=df.reset_index()
    df.columns=['code_id', 'score']
    return list(df[:K]['code_id'])
    

def cluster(test_all=True):    
    for line in final_score.readlines():
        code_scores_list=[]
        code_scores_dict={}
        report_id, code_scores = line.split(';')
        
        index=0
        for code_score in code_scores.split():
            code_id, score = code_score.split(':')
            code_scores_list.append([float(score), index])
            code_scores_dict[code_id]=float(score)
        
        if not test_all:            
            top_K_ids=return_top_k_ids(code_scores_dict)
            top_K_code_scores_list=[]
            for id in top_K_ids:
                top_K_code_scores_list.append([float(code_scores_dict[id]), index])

            X=np.array(top_K_code_scores_list)
            #print(X)
        else:
            #print(len(code_scores_list))
            #print(len(code_scores_dict))
            code_scores_list.sort(reverse=True)
            X=np.array(code_scores_list)
        
        #run_elbow(X)
        run_x_means(X)
        #y_pred=dbscan.fit_predict(X)
        #print(dbscan.labels_)
        
        #y_pred=kmeans.fit_predict(X)
        #print(kmeans.inertia_)
        #print('cluster_center: {}'.format(kmeans.cluster_centers_))
        #print('number of iteration: {}'.format(kmeans.n_iter_))
        #plt.scatter(X[:, 0], X[:, 1], c=y_pred)
        #plt.show()
        break
    
if __name__=='__main__':
    top_K = 50
    num_clusters=3
    threshold_score_1=0.1
    p=Path('./tmp/')
    final_score=open(p/'finalScore.txt', 'r')
    ################################
    # 1. K means
    # for each bug report, do K-means
    kmeans = KMeans(
        init='random',
        n_clusters=num_clusters, 
        n_init=10, 
        max_iter=300, 
        random_state=42)

    # 2. DBSCAN
    dbscan = DBSCAN() # all use default
    cluster(False)