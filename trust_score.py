# Created by happygirlzt on 6 Nov
from pathlib import Path
import statistics
import pandas as pd
# from bugRanker import bugLocator
import os
import prettytable
from matplotlib import pyplot as plt
import math
from clustering import run_x_means
import numpy as np
import time
from itertools import combinations
import random


### Config
threshold_score=0.5

def get_sorted_scores(report_id, code_scores_list: str, is_store_csv=False):
    '''
    Give bug report id and code scores
    对score进行排序后存储在csv文件中
    并返回排序的结果
    '''
    code_scores_dict={}
    for code_scores in code_scores_list:
        code_id, score = code_scores.split(':')
        code_scores_dict[code_id] = float(score)

    sorted_code_scored_dict = {k: v for k, v in sorted(code_scores_dict.items(), key=lambda item: item[1], reverse=True)}
    if is_store_csv:
        df=pd.DataFrame(sorted_code_scored_dict, index=[0])
        df=df.transpose()
        df=df.reset_index()
        df.columns=['code_id', 'score']
        df.to_csv(sortedScorePath/'{}.csv'.format(report_id))
    
    all_scores = list(sorted_code_scored_dict.values())
    return all_scores

def computeStdev(all_scores, K=[5, 10, 20], verbose=False):
    '''
    计算前k in K的数的标准差
    '''
    stdevData = {}
    for k in K:
        k_std=statistics.stdev(all_scores[:k])
        if verbose:
            print('         top {} std is {}'.format(len(all_scores[:k]), k_std))
        stdevData[k] = k_std
    return stdevData

def computeMean(all_scores, K=[5, 10, 20], verbose=False):
    '''
    计算前k in K的数的平均值
    '''
    meanData = {}
    for k in K:
        k_std=statistics.mean(all_scores[:k])
        if verbose:
            print('         top {} mean is {}'.format(len(all_scores[:k]), k_std))
        meanData[k] = k_std
    return meanData

def computeMedian(all_scores, K=[5, 10, 20], verbose=False):
    '''
    计算前k in K的数的中位数
    '''
    medianData = {}
    for k in K:
        k_std=statistics.median(all_scores[:k])
        if verbose:
            print('         top {} median is {}'.format(len(all_scores[:k]), k_std))
        medianData[k] = k_std
    return medianData

def computeVariance(all_scores, K=[5, 10, 20], verbose=False):
    '''
    计算前k in K的数的方差
    '''
    medianVariance = {}
    for k in K:
        k_std=statistics.variance(all_scores[:k])
        if verbose:
            print('         top {} variance is {}'.format(len(all_scores[:k]), k_std))
        medianVariance[k] = k_std
    return medianVariance

def computeMode(all_scores, K=[5, 10, 20], verbose=False):
    '''
    计算前k in K的数的众数
    '''
    for k in K:
        k_std=statistics.mode(all_scores[:k])
        if verbose:
            print('         top {} mode is {}'.format(len(all_scores[:k]), k_std))

def computeGap(all_scores, K=[5, 10, 20], verbose=False):
    '''
    计算分数之间的差值，返回并打印最大和最小的数值
    '''
    gapData = {}
    for k in K:
        gapList = []
        for index, score in enumerate(all_scores[:k]):
            try:
                gapList.append(all_scores[index] - all_scores[index + 1])
            except IndexError as e:
                # 我们并未约束K值和all_score长度之间的关系，因此可能会报错
                continue
        if verbose:
            print('         max {} gap is {}'.format(len(all_scores[:k]), max(gapList)))
            print('         min {} gap is {}'.format(len(all_scores[:k]), min(gapList)))
        gapData[k] = [max(gapList), min(gapList)]
    return gapData

def computRD(all_scores, K=[5, 10, 20], verbose=False):
    '''
    compute relative difference
    RD1 = (R2 - R20) / (R1 - R20)
    '''
    R1 = all_scores[0]
    for k in K:
        RDList = []
        R_k = all_scores[k-1]
        for index in range(1,k-1):
            RDList.append((all_scores[index] - R_k) / (R1 - R_k))
    if verbose:
        print('          {} relatvie difference is {}'.format(len(all_scores[:k]), RDList))  

def plot_gap(final_score_lines,plot_range=30):   
    '''
    画出gap的前30的图
    '''
    for score_line in final_score_lines:
        report_id, code_scores = score_line.split(';')
        code_scores_list = code_scores.split(' ')
        all_scores = get_sorted_scores(report_id, code_scores_list)
        lag_scores = all_scores[1:]
        all_scores = all_scores[:-1]
        diff_scores = np.array(all_scores) - np.array(lag_scores)
        all_scores = diff_scores[0:plot_range]
        x_axis = range(len(all_scores))
        if first_position_dict[report_id] < 10:
            l1=plt.plot(x_axis,all_scores,'g--',label='type1')
        else:
            l1=plt.plot(x_axis,all_scores,'r--',label='type1')
            
def log_like(x):
    '''
    log transformation to change the score distribution
    '''
    return math.log(math.sqrt(math.sqrt(x))+1,2)

def showSummary(score_line):
    '''
    执行计算trust score的全过程
    '''
    report_id, code_scores = score_line.split(';')
    code_scores_list = code_scores.split(' ')
    print('Bug report {}, ground truth rank: '.format(report_id), end='')
    for rank in positions[report_id]:
        if rank < 10:
            print('\033[1;32m {} \033[0m'.format(rank), end='')
        else:
            print('\033[1;31m {} \033[0m'.format(rank), end='')
    print()
    all_scores = get_sorted_scores(report_id, code_scores_list)
    pt = prettytable.PrettyTable()
    pt.field_names = ["k value", "mean", "median", "stdev", "variance", "max gap", "min gap"]
    # pt.field_names = ["k value", "stdev", "variance", "mean", "median", "max gap", "min gap"]
    meanData = computeMean(all_scores, K)
    stdevData = computeStdev(all_scores, K) # 计算标准差
    medianData = computeMedian(all_scores, K)
    varianceData = computeVariance(all_scores, K)

    gapData = computeGap(all_scores, K)
    computRD(all_scores)
    for k in stdevData.keys():
        pt.add_row([k, round(meanData[k],4), 
            round(medianData[k],4), 
            round(stdevData[k],4), 
            round(varianceData[k], 4),
            round(gapData[k][0],4),
            round(gapData[k][1],4)])
    print(pt)

def checkH1_on_single_report(score_line, alpha=2, verbose=False):
    '''
    heuristic1: There is a substantial gap.
    substantial gap: gap > alpha * stdv
    '''
    report_id, code_scores = score_line.split(';')
    code_scores_list = code_scores.split(' ')
    all_scores = get_sorted_scores(report_id, code_scores_list)
    gapData = computeGap(all_scores, K=[10])
    stdevData = computeStdev(all_scores, K=[len(all_scores)]) # 计算标准差
    is_substantial_gap_exist = True if gapData[10][0] > alpha * stdevData[len(all_scores)] else False
    if verbose:
        if first_position_dict[report_id] < 10:
            print('\033[1;32m {} \033[0m'.format(first_position_dict[report_id]), end='')
        else:
            print('\033[1;31m {} \033[0m'.format(first_position_dict[report_id]), end='')
        print(is_substantial_gap_exist)
    return report_id, is_substantial_gap_exist

def checkH2_on_single_report(score_line, alpha = 1, verbose=False):
    '''
    heuristic2: max_gap - min_gap > alpha * stdv
    '''
    report_id, code_scores = score_line.split(';')
    code_scores_list = code_scores.split(' ')
    all_scores = get_sorted_scores(report_id, code_scores_list)
    gapData = computeGap(all_scores, K=[10])
    stdevData = computeStdev(all_scores, K=[len(all_scores)]) # 计算标准差
    is_satisfying_h = True if gapData[10][0] - gapData[10][1] > alpha * stdevData[len(all_scores)] else False
    if verbose:
        if first_position_dict[report_id] < 10:
            print('\033[1;32m {} \033[0m'.format(first_position_dict[report_id]), end='')
        else:
            print('\033[1;31m {} \033[0m'.format(first_position_dict[report_id]), end='')
        print(is_satisfying_h)
    return report_id, is_satisfying_h

def checkH3_on_single_report(score_line):
    '''
    heuristic3: trust_score = 1 / size(cluster_1) > threshold
    '''
    report_id, code_scores = score_line.split(';')
    code_scores_list = code_scores.split(' ')
    all_scores = get_sorted_scores(report_id, code_scores_list)
    all_scores.sort(reverse=True)
    #print(all_scores[:50])
    all_scores_list = []
    for score in all_scores:
        all_scores_list.append([float(score), 0])

    X = np.array(all_scores_list)
    trust_score_by_H3 = run_x_means(X)
    is_satisfying_h = trust_score_by_H3 > threshold_score
    return report_id, is_satisfying_h
    
def checkH4_on_single_report(score_line, position = 20, verbose=False):
    '''
    heuristics4: normalized_score[20] < 0.4
    '''
    report_id, code_scores = score_line.split(';')
    code_scores_list = code_scores.split(' ')
    all_scores = get_sorted_scores(report_id, code_scores_list)

    normalized_score = max_normalize(all_scores)
    score_at_position = normalized_score[position]
    is_satisfying_h = True if score_at_position < 0.4 else False
    return report_id, is_satisfying_h

def checkH5_on_single_report(score_line, position = 3, verbose=False):
    '''
    heuristics5: normalized_score[3] < 0.55
    '''
    report_id, code_scores = score_line.split(';')
    code_scores_list = code_scores.split(' ')
    all_scores = get_sorted_scores(report_id, code_scores_list)
    normalized_score = max_normalize(all_scores)
    score_at_position = normalized_score[position]
    is_satisfying_h = True if score_at_position < 0.55 else False
    return report_id, is_satisfying_h

def checkH6_on_single_report(score_line, position = 1, verbose=False):
    '''
    heuristics6: normalized_score[1] < 0.7
    '''
    report_id, code_scores = score_line.split(';')
    code_scores_list = code_scores.split(' ')
    all_scores = get_sorted_scores(report_id, code_scores_list)
    normalized_score = max_normalize(all_scores)
    score_at_position = normalized_score[position]
    is_satisfying_h = True if score_at_position < 0.7 else False
    return report_id, is_satisfying_h

def checkH7_on_single_report(score_line):
    '''
    heuristics7: 前5个gap，至少有两个值大与0.2
    '''
    def getNgap(all_scores,n):
        gaps = []
        for i, score in enumerate(all_scores):
            if i == n:
                assert n == len(gaps)
                return gaps
            gaps.append(all_scores[i] - all_scores[i + 1])

    report_id, code_scores = score_line.split(';')
    code_scores_list = code_scores.split(' ')
    all_scores = get_sorted_scores(report_id, code_scores_list)
    gaps = getNgap(all_scores, 5)
    # 判断是否至少有两个值大于1
    count = 0
    for gap in gaps:
        if gap > 0.2:
            count += 1
    is_satisfying_h = True if count >= 2 else False
    return report_id, is_satisfying_h

def checkH8_on_single_report(score_line, alpha = 1, verbose=False):
    '''
    heuristic8: the 2000th file have socre within(0.5,0.6)
    '''
    report_id, code_scores = score_line.split(';')
    code_scores_list = code_scores.split(' ')
    all_scores = get_sorted_scores(report_id, code_scores_list)
    all_scores = list(map(log_like,all_scores))
    s_array = np.array(all_scores)
    if (0.5<=s_array[2000]<=0.6):
        is_satisfying_h = 1
    else:
        is_satisfying_h  = 0
    
    if verbose:
        if first_position_dict[report_id] < 10:
            print('\033[1;32m {} \033[0m'.format(first_position_dict[report_id]), end='')
        else:
            print('\033[1;31m {} \033[0m'.format(first_position_dict[report_id]), end='')
        print(is_satisfying_h)
    return report_id, is_satisfying_h

def checkH9_on_single_report(score_line, alpha = 1, verbose=False):
    '''
    heuristic9: the 200th score below 0.7
    '''
    report_id, code_scores = score_line.split(';')
    code_scores_list = code_scores.split(' ')
    all_scores = get_sorted_scores(report_id, code_scores_list)
    all_scores = list(map(log_like,all_scores))
    s_array = np.array(all_scores)
    if ( s_array[200]<=0.7 ):
        is_satisfying_h = 1
    else:
        is_satisfying_h  = 0
    
    if verbose:
        if first_position_dict[report_id] < 10:
            print('\033[1;32m {} \033[0m'.format(first_position_dict[report_id]), end='')
        else:
            print('\033[1;31m {} \033[0m'.format(first_position_dict[report_id]), end='')
        print(is_satisfying_h)
    return report_id, is_satisfying_h

def checkH10_on_single_report(score_line, alpha = 1, verbose=False):
    '''
    heuristic10: the 200 score below 0.8
    '''
    report_id, code_scores = score_line.split(';')
    code_scores_list = code_scores.split(' ')
    all_scores = get_sorted_scores(report_id, code_scores_list)
    all_scores = list(map(log_like,all_scores))
    s_array = np.array(all_scores)
    if ( s_array[200]<=0.8):
        is_satisfying_h = 1
    else:
        is_satisfying_h  = 0
    
    if verbose:
        if first_position_dict[report_id] < 10:
            print('\033[1;32m {} \033[0m'.format(first_position_dict[report_id]), end='')
        else:
            print('\033[1;31m {} \033[0m'.format(first_position_dict[report_id]), end='')
        print(is_satisfying_h)
    return report_id, is_satisfying_h

def checkH11_on_single_report(score_line, alpha = 1, verbose=False):
    '''
    heuristic11: the 4000th score within (0.5,0.6)
    '''
    report_id, code_scores = score_line.split(';')
    code_scores_list = code_scores.split(' ')
    all_scores = get_sorted_scores(report_id, code_scores_list)
    all_scores = list(map(log_like,all_scores))
    s_array = np.array(all_scores)
    if (0.5<=s_array[2000]<=0.6):
        is_satisfying_h = 1
    else:
        is_satisfying_h  = 0
    
    if verbose:
        if first_position_dict[report_id] < 10:
            print('\033[1;32m {} \033[0m'.format(first_position_dict[report_id]), end='')
        else:
            print('\033[1;31m {} \033[0m'.format(first_position_dict[report_id]), end='')
        print(is_satisfying_h)
    return report_id, is_satisfying_h



def call_heristic_func_by_num(heuristic_num):
    '''
    根据指定的heuristic num，返回对应的checkHX_on_single_report函数
    '''
    return {'1': checkH1_on_single_report, 
            '2': checkH2_on_single_report, 
            '3': checkH3_on_single_report, 
            '4': checkH4_on_single_report, 
            '5': checkH5_on_single_report, 
            '6': checkH6_on_single_report,
            '7': checkH7_on_single_report,
            '8': checkH8_on_single_report,
            '9': checkH9_on_single_report,
            '10': checkH10_on_single_report,
            '11': checkH11_on_single_report}[str(heuristic_num)]

def apply_single_heuristic(final_score_lines, heuristic_num, verbose=True):
    '''
    根据指定的heuistic_num，输出apply前后的success rate
    '''
    if verbose:
        print(call_heristic_func_by_num(heuristic_num).__doc__)
    green_count = 0 # 在top10内找到的
    red_count = 0 # 在top内没找到的数量
    green_count_with_h = 0 # apply heuristic之后中成功的
    red_count_with_h = 0 # apply heuristic之后中失败的
    green_with_h_id = []
    red_with_h_id = []
    
    for line in final_score_lines:
        report_id, is_satisfying_h = call_heristic_func_by_num(heuristic_num)(line)

        if first_position_dict[report_id] < 10:
            green_count += 1
            if is_satisfying_h:
                green_count_with_h += 1
                green_with_h_id.append(report_id)
        else:
            red_count += 1
            if is_satisfying_h:
                red_count_with_h += 1
                red_with_h_id.append(report_id)

    pt = prettytable.PrettyTable()
    pt.field_names = [" ", "success rate", "No. (< top 10)", "No. (Total)"]
    pt.add_row(["before", 
                round(green_count * 1.0 / (green_count + red_count), 4), 
                green_count, 
                green_count + red_count])
    pt.add_row(["after", 
                round(green_count_with_h * 1.0 / (green_count_with_h + red_count_with_h), 4), 
                green_count_with_h, 
                green_count_with_h + red_count_with_h])
    if verbose:
        print(pt)

    assert len(green_with_h_id) == green_count_with_h
    assert len(red_with_h_id) == red_count_with_h
    return green_with_h_id, red_with_h_id


def max_normalize(raw):
    max_value = max(raw)
    norm = [float(i)/max_value for i in raw]
    return norm

def visulize_heuristics(final_score_lines,heuristic_num_list: list=[1,4,6]):
    assert len(heuristic_num_list) == 3
    from matplotlib_venn import venn2, venn2_circles, venn2_unweighted
    from matplotlib_venn import venn3, venn3_circles
    from matplotlib import pyplot as plt
    list_after_apply_heuristics = []
    for heuristic_num in heuristic_num_list:
        list_satisfying_heuristic = []
        for line in final_score_lines:
            report_id, is_satisfying_h = call_heristic_func_by_num(heuristic_num)(line)
            if is_satisfying_h:
                list_satisfying_heuristic.append(report_id)
        list_after_apply_heuristics.append(list_satisfying_heuristic)

    vd3=venn3([set(list_after_apply_heuristics[0]),set(list_after_apply_heuristics[1]), set(list_after_apply_heuristics[2])],
                set_labels=(str(heuristic_num_list[0]), str(heuristic_num_list[1]), str(heuristic_num_list[2])))
    plt.show()

def apply_multiple_heurstics(final_score_lines, heuristic_num_list: list, verbose=False):
    # TO-DO: refactoring
    pt = prettytable.PrettyTable()
    pt.field_names = [" ", "success rate", "No. (< top 10)", "No. (Total)"]
    results = {}
    current_report_set = set(fixLink_dict.keys())
    green_count = 0
    red_count = 1
    for report_id in fixLink_dict.keys():
        if first_position_dict[report_id] < 10:
            green_count += 1
        else:
            red_count += 1
    
    pt.add_row(["No heuristic", 
                round(green_count * 1.0 / (green_count + red_count), 4), 
                green_count, 
                green_count + red_count])
    # 得到所有的report
    for heuristic_num in heuristic_num_list:
        green_with_h_id, red_with_h_id = (apply_single_heuristic(final_score_lines, heuristic_num, verbose=False))
        pt.add_row(["Applying H" + str(heuristic_num), 
            round(len(green_with_h_id) * 1.0 / (len(green_with_h_id) + len(red_with_h_id)), 4), 
            len(green_with_h_id), 
            len(green_with_h_id) + len(red_with_h_id)])
        current_report_set = set(green_with_h_id + red_with_h_id) & current_report_set
    green_count_with_h = 0
    red_count_with_h = 0
    for report_id in current_report_set:
        if first_position_dict[report_id] < 10:
            green_count_with_h += 1
        else:
            red_count_with_h += 1
    
    pt.add_row(["Applying all", 
                round(green_count_with_h * 1.0 / (green_count_with_h + red_count_with_h), 4), 
                green_count_with_h, 
                green_count_with_h + red_count_with_h])
    if verbose:
        print(pt)
    return green_count_with_h, red_count_with_h
    
def get_trust_score_by_h(satisfying_list):
    # To-Do: Not implementing
    # 读取trust_data.npy文件，得到trust score
    # Example: 1,2,3,4,5;0,841

    with open('./trust_data.txt') as f:
        trust_score_by_h_list = {}
        trust_scores = f.readlines()
        for trust_score in trust_scores:
            heuristics_data = trust_score.split(';')[0]
            trust_score = trust_score.split(';')[1]
            heuristic_list = []
            for heuristic_num in heuristics_data.split(','):
                if heuristic_num == '':
                    continue
                heuristic_list.append(int(heuristic_num))
            if set(heuristic_list) == set(satisfying_list):
                return float(trust_score) / 100
    
    return 0.6

        



def get_satisified_heuristics(score_line, heuristic_num_list=[1,2,4,5,6,7]):
    '''返回满足的trust_score的列表'''
    satisfying_list = []
    for heuristic_num in heuristic_num_list:
        report_id, is_satisfying_h = call_heristic_func_by_num(heuristic_num)(score_line)
        if is_satisfying_h:
            satisfying_list.append(heuristic_num)

    return report_id, satisfying_list





if __name__ == '__main__':
    from bugRanker import bugLocator

    # 先运行这些代码，得到一些必要信息，比如fixLink, first_position等
    buglocator = bugLocator("no")
    buglocator.setPathToTmp(os.path.join(os.getcwd(), 'tmp'))
    # Show the summary
    buglocator.setRankResultFromTmp()
    buglocator.apply_single_heuristic(1, verbose = True)

