"""classes and methods for IR-based bug localization tools."""
import numpy as np
import os
import sys
import prettytable as pt
from pathlib import Path
from trust_score import call_heristic_func_by_num, get_trust_score_by_h, get_satisified_heuristics
import prettytable


class bugRanker():
    """Base class for bug localization tools."""

    pass


class bugLocator(bugRanker):
    """Class for BugLocator."""

    def __init__(self, path_to_BugLocator, path_to_tmp, repo_name=''):
        """Only specifiy the path to BugLocator.jar executables."""
        self.path_to_BugLocator_executable = path_to_BugLocator
        self.repo_name = repo_name
        self.path_to_tmp = os.path.join(path_to_tmp)

    def setPathToTmp(self, path_to_tmp):
        self.path_to_tmp = path_to_tmp

    def setRankResultFromTmp(self):
        self.sorted_query_result = self.getSortedRankResult()
        self.fixLink_dict = self.getFixLink()
        self.first_position_dict = self.getFirstFilePosition(self.sorted_query_result, self.fixLink_dict)
        self.positions = self.getAllGroundTruthPosistion(self.sorted_query_result, self.fixLink_dict)
        self.final_score_lines = open(os.path.join(self.path_to_tmp, 'finalScore.txt'), "r").readlines()


    def runBugLocator(self, path_to_bugreport, path_to_codebase, verbose = False):
        """Given path to bugreport and codebase, run BugLocator."""
        self.path_to_bugreport = path_to_bugreport
        self.path_to_codebase = path_to_codebase
        # use BugLocator
        cmd = 'java -jar ' + self.path_to_BugLocator_executable + ' -b ' + \
            self.path_to_bugreport + ' -s ' + \
            self.path_to_codebase + ' -a 0.2 -o ' + \
            os.path.join(self.path_to_tmp, 'result.txt' + 
            ' -t ' + 'result' + '/' + self.repo_name + '_tmp')
        if verbose:
            print(cmd)
        os.system(cmd)

    def getSortedRankResult(self):
        """
        Get the rank result for each bug report query.

        return a dictionary:
        {bugid: {fileid: similarity}}. {fileid: similarity}
        is sorted by similarity.
        """
        path_to_VSMScore = os.path.join(self.path_to_tmp, "finalScore.txt")
        with open(path_to_VSMScore) as f:
            content = f.read()
            query_result_list = content.split('\n')[0:-1]
            # Remove the last empty line

            sorted_query_result = {}
            for single_qeury_result in query_result_list:
                bugid = single_qeury_result.split(';')[0]
                query_result_by_fileid = single_qeury_result.split(';')[1]
                # convert into a list
                query_result_by_fileid = query_result_by_fileid.split(' ')
                query_result_dict = {}

                for fileid_similarity in query_result_by_fileid:
                    fileid = fileid_similarity.split(':')[0]
                    similarity = fileid_similarity.split(':')[1]
                    # convert similarity from str to float
                    query_result_dict[fileid] = float(similarity)
                # sort by similarity
                query_result_dict_by_similarity = {k: v for k, v in sorted(query_result_dict.items(), key=lambda item: item[1], reverse=True)}
                sorted_query_result[bugid] = query_result_dict_by_similarity

        return sorted_query_result

    def getTopNResult(self, n):
        """Only return top N query result."""
        sorted_query_result = bugLocator.getSortedRankResult(self)
        top_n_result = {}
        for bugid in sorted_query_result.keys():
            tmp_result = {}
            for index, fileid in enumerate(sorted_query_result[bugid]):
                if index == n:
                    break
                tmp_result[fileid] = sorted_query_result[bugid][fileid]

            top_n_result[bugid] = tmp_result
        print(top_n_result)

    def getFixLink(self):
        """
        Get the related fileid for each bugid.

        {bugid: [fileid1, fileid2, ...], ...}.
        """
        path_to_FixLink = os.path.join(self.path_to_tmp, "FixLink.txt")
        path_to_ClassName = os.path.join(self.path_to_tmp, "ClassName.txt")
        with open(path_to_ClassName) as f:
            content = f.read()
            fileid_path_list = content.split('\n')[0:-1]

            path_fileid_dict = {}
            for fileid_path in fileid_path_list:
                fileid = fileid_path.split('\t')[0]
                path = fileid_path.split('\t')[1]
                path_fileid_dict[path] = fileid

        with open(path_to_FixLink) as f:
            content = f.read()
            fixLink = content.split('\n')[0:-1]
            # Remove the last empty line

            fixLink_dict = {}
            for item in fixLink:
                bugid = item.split('\t')[0]
                filepath = item.split('\t')[1]
                try:
                    fixLink_dict[bugid].append(path_fileid_dict[filepath])
                except KeyError:
                    fixLink_dict[bugid] = [path_fileid_dict[filepath]]

        return fixLink_dict

    def getFirstFilePosition(self, sorted_query_result, fixLink_dict):
        """Find the position where first related code file appears."""
        first_position = {}
        for bugid in sorted_query_result.keys():
            related_fileids = fixLink_dict[bugid]

            count = 0
            for fileid in sorted_query_result[bugid].keys():
                if fileid in related_fileids:
                    first_position[bugid] = count
                    break
                count += 1

        return first_position
    
    def getAllGroundTruthPosistion(self, sorted_query_result, fixLink_dict):
        '''
        一个bug report可能对应多个buggy file
        返回所有文件的位置
        '''
        positions = {}
        for bugid in sorted_query_result.keys():
            related_fileids = fixLink_dict[bugid]
            positions[bugid] = []

            count = 0
            for fileid in sorted_query_result[bugid].keys():
                if fileid in related_fileids:
                    positions[bugid].append(count)
                count += 1
        return positions

        
    def showSummary(self, first_position_dict):
        """Show summary about the ranking result."""
        table = pt.PrettyTable()
        table.field_names = ['BugID', 'Rank of first related file']
        for bugid in first_position_dict.keys():
            table.add_row([bugid, first_position_dict[bugid]])
        print(table)

    def get_ts_statistics(self, ts_table):
        '''
        ts_table：根据满足h的情况，返回trsut_score
        ts_table 需要计算得出
        '''
        pass

    def generate_report(self, mode, threshold=0.65):
        '''
        根据mode生成结果，两种mode: optimistic, conservative
        如果是optimistic, 则所有的都推荐
        如果是conservative，则是生成trust_score高的
        '''
        # To-do: 首先要判断有是否符合
        conservative_set = []
        total_set = []
        for line in self.final_score_lines:
            report_id, satisfying_list = get_satisified_heuristics(line)
            trust_score = get_trust_score_by_h(satisfying_list)
            total_set.append(report_id)
            if trust_score > threshold:
                conservative_set.append(report_id)
        
        # 统计conservative mode的结果
        conservative_green_set = []
        for report_id in conservative_set:
            if self.first_position_dict[report_id] < 10:
                conservative_green_set.append(report_id)


        # 统计optimistic mode的结果
        total_green_set = []
        for report_id in total_set:
            if self.first_position_dict[report_id] < 10:
                total_green_set.append(report_id)

        if mode == 'conservative':
            print("\tConservative filtering: We do recommendation for {} bug reports, and the success rate is {}%".format(len(conservative_set), 
                100 * round(len(conservative_green_set) * 1.0 / len(conservative_set),4)))
            print("\tTotal number of bug reports: {}".format(len(total_set)))
        if mode == 'optimistic':
            print("\tOptimistic   filtering: We do recommendation for {} bug reports, and the success rate is {}%".format(len(total_set), 
                100 * round(len(total_green_set) * 1.0 / len(total_set), 4)))
        if mode == 'all':
            print("\tConservative filtering: We do recommendation for {} bug reports, and the success rate is {}%".format(len(conservative_set), 
                100 * round(len(conservative_green_set) * 1.0 / len(conservative_set),4)))
            print("\tOptimistic   filtering: We do recommendation for {} bug reports, and the success rate is {}%".format(len(total_set), 
                100 * round(len(total_green_set) * 1.0 / len(total_set), 4)))


        
    def apply_single_heuristic(self, heuristic_num, verbose=True):
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
        
        for line in self.final_score_lines:
            report_id, is_satisfying_h = call_heristic_func_by_num(heuristic_num)(line)

            if self.first_position_dict[report_id] < 10:
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
        before_success_rate = round(green_count * 1.0 / (green_count + red_count), 4)
        pt.add_row(["before", 
                    before_success_rate, 
                    green_count, 
                    green_count + red_count])

        after_succes_rate = round(green_count_with_h * 1.0 / (green_count_with_h + red_count_with_h), 4)
        pt.add_row(["after", 
                    after_succes_rate, 
                    green_count_with_h, 
                    green_count_with_h + red_count_with_h])
        if verbose:
            print(pt)
            print("Absolute success rate boosted by {}%".format(round(after_succes_rate - before_success_rate, 4) * 100))
            print("Relatvie success rate boosted by {}%".format(
                round((after_succes_rate - before_success_rate) / before_success_rate, 4) * 100))


        assert len(green_with_h_id) == green_count_with_h
        assert len(red_with_h_id) == red_count_with_h
        return green_with_h_id, red_with_h_id

    def apply_multiple_heurstics(self, heuristic_num_list: list, verbose=False):
        # TO-DO: refactoring
        pt = prettytable.PrettyTable()
        pt.field_names = [" ", "success rate", "No. (< top 10)", "No. (Total)"]
        results = {}
        current_report_set = set(self.fixLink_dict.keys())
        green_count = 0
        red_count = 1
        for report_id in self.fixLink_dict.keys():
            if self.first_position_dict[report_id] < 10:
                green_count += 1
            else:
                red_count += 1
        
        pt.add_row(["No heuristic", 
                    round(green_count * 1.0 / (green_count + red_count), 4), 
                    green_count, 
                    green_count + red_count])
        # 得到所有的report
        for heuristic_num in heuristic_num_list:
            green_with_h_id, red_with_h_id = (self.apply_single_heuristic(heuristic_num, verbose=False))
            pt.add_row(["Applying H" + str(heuristic_num), 
                round(len(green_with_h_id) * 1.0 / (len(green_with_h_id) + len(red_with_h_id)), 4), 
                len(green_with_h_id), 
                len(green_with_h_id) + len(red_with_h_id)])
            current_report_set = set(green_with_h_id + red_with_h_id) & current_report_set
        green_count_with_h = 0
        red_count_with_h = 0
        for report_id in current_report_set:
            if self.first_position_dict[report_id] < 10:
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