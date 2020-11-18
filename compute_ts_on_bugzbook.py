# -*- coding: UTF-8 -*-
import os
import copy
from convertBugzbook import bugzbookParser, converter, createXMLFile
from multiprocessing import Pool
from multiprocessing import Process, Queue

def merge_bug_data(bugdata_list: list) -> dict:
    assert len(bugdata_list) > 0
    mergedBugData = {}
    mergedBugData["bugReportData"] = {}
    mergedBugData["repositoryName"] = bugdata_list[0]["repositoryName"]
    bug_count = 0
    for bugdata in bugdata_list:
        for i, origialBugID in enumerate(bugdata["bugReportData"]):
            bug_count += 1
            bug_count_str = str(bug_count)
            mergedBugData["bugReportData"][bug_count_str] = copy.deepcopy(bugdata["bugReportData"][origialBugID])
            mergedBugData["bugReportData"][bug_count_str]["id"] = bug_count_str

    return mergedBugData


def merge_report(report_dir, codebase_dir, merged_report_path):
    if not (os.path.exists(report_dir) and os.path.exists(codebase_dir)):
        print(report_dir)
        print(codebase_dir)
    assert os.path.exists(report_dir)
    assert os.path.exists(codebase_dir)
    convertedBugData_list = []
    for report in os.listdir(os.path.join(report_dir)):
        if report == '.DS_Store':
            continue
        single_report_path = os.path.join(report_dir, report)
        allBugData = bugzbookParser(single_report_path)
        # convertedBugData = converter(allBugData, codebase_dir)
        convertedBugData_list.append(allBugData)
    mergedBugData = merge_bug_data(convertedBugData_list)
    createXMLFile(mergedBugData, merged_report_path)


def merge_bugzbook_report(path_to_report, path_to_codebase):
    '''
    --path_to_report:
        --project_1:
            --report1.xml
            -- ...
    --path_to_codebase:
        --project_1:
            ...code of project_1
    需要注意的是，两个目录下的文件夹名称需要相同
    '''
    for repo_name in os.listdir(path_to_report):
        if repo_name == '.DS_Store':
            # a special file on the Mac
            continue
        merge_report(os.path.join(path_to_report, repo_name), 
                    os.path.join(path_to_codebase, repo_name))

def run_buglocator(i):
    while True:
        repo_name = q.get()
        if repo_name == '.DS_Store':
            # a special file on the Mac
            continue
        command = 'java -jar {} -b {} -s {} -a 0.2 -o result.txt -t {}'.format(
            path_to_tool,
            os.path.join(merged_report_path, repo_name + '.xml'),
            os.path.join(path_to_codebase, repo_name),
            os.path.join(path_to_tmp, repo_name + "_tmp"))
        print(command)
        os.system(command)

if __name__=='__main__':
    path_to_codebase = './bugzbook_data/codebase_data'
    path_to_report = './bugzbook_data/bugreport_data'
    merged_report_path = './new_merged_report'
    path_to_tmp = './tmp_dir'
    path_to_tool = './tools/BL_tools.jar'

    for repo_name in os.listdir(path_to_report):
        if repo_name == '.DS_Store':
            continue
        report_dir = os.path.join(path_to_report, repo_name)
        codebase_dir = os.path.join(path_to_codebase, repo_name)
        merge_report(report_dir, codebase_dir, merged_report_path)
    exit()
    q = Queue()
    for repo_name in os.listdir(path_to_report):
        q.put(repo_name)

    p = Pool(4)
    for i in range(7):
        p.apply_async(run_buglocator, args=(1,))
    print('Waiting for all subprocesses done...')
    p.close()
    p.join()
    print('All subprocesses done.')



    
