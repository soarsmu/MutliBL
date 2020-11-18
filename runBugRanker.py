from bugRanker import bugLocator
import argparse
import os
from multiprocessing import Pool, Process, Queue
from time import sleep
from itertools import combinations

def run(heuristic_num_list):
    while True:
        if not q.empty():
            repo_name = q.get()
        else:
            return
        if repo_name == '.DS_Store':
            # a special file on the Mac
            continue
        buglocator = bugLocator("path_to_BugLocator")
        buglocator.setPathToTmp(os.path.join(path_to_tmp, repo_name+"_tmp"))

        # Show the summary
        buglocator.setRankResultFromTmp()
        for i in heuristic_num_list:
            green_count, red_count = buglocator.apply_single_heuristic(i)
        
def comput_trust_score(dummy):
    while True:
        if not q.empty():
            heuristic_num_list = q.get()
        else:
            return
        total_green_count = 0
        total_red_count = 0
        for repo_name in os.listdir(path_to_codebase):
            if repo_name == '.DS_Store':
                # a special file on the Mac
                continue
            buglocator = bugLocator("path_to_BugLocator")
            buglocator.setPathToTmp(os.path.join(path_to_tmp, repo_name+"_tmp"))
            buglocator.setRankResultFromTmp()
            try:
                green_count, red_count = buglocator.apply_multiple_heurstics(heuristic_num_list, verbose=False)
            except Exception as e:
                print(e)
            total_green_count += green_count
            total_red_count += red_count
        success_rate = round(total_green_count * 1.0 / ( total_green_count + total_red_count) * 100, 4)
        print("The trust score of heuristic {} is {}%".format(heuristic_num_list, success_rate))




if __name__ == '__main__':
    from trust_score import call_heristic_func_by_num
    bugzbook_data_path = '/media/zyang/bugzbook_data'
    path_to_codebase = os.path.join(bugzbook_data_path, "codebase_data")
    path_to_report = os.path.join(bugzbook_data_path, "bugreport_data")
    merged_report_path = os.path.join(bugzbook_data_path, "merged_report")
    path_to_tmp = os.path.join(bugzbook_data_path, "tmp_dir")
    path_to_tool = './tools/BL_tools.jar'

    # heuristic_num_list = range(1,10)
    # q = Queue()
    # for repo_name in os.listdir(path_to_codebase):
    #     q.put(repo_name)

    # print("hello")
    # for i in range(0,8):
    #     for heuristic_combination in list(combinations(range(1,8), i)):
    #         print(heuristic_combination)
    q = Queue(1000)
    for i in range(1,8):
        for heuristic_combination in list(combinations(range(1,8), i)):
            q.put(list(heuristic_combination))
    
    p = Pool(7)
    for i in range(7):
        p.apply_async(comput_trust_score, args=(1,))
    p.close()
    p.join()
    print('All subprocesses done.')

    # intialize buglocator

