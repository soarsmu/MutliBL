# -*- coding: UTF-8 -*-
import configparser
import os
import argparse
from convertBugzbook import createXMLFile, converter, bugzbookParser
from bugRanker import bugLocator
from translator import bug_report_parser, translateBugReport, translateCommentInRepo
import traceback
from sheet_converter import sheet_to_xml_converter

# TO-do: check包



def run():
    # Read configuration file
    config = configparser.ConfigParser()
    config_path = 'config.ini'
    config.read(config_path)

    # Convert sheet to xml files.
    print("\n\nStep 0. Convert sheet to xml files.")
    path_to_bug_report_sheet = config['bug_info']['path_to_bug_report_sheet']
    repo_name = config['bug_info']['repo_name']
    path_to_store_results = os.path.join('./result/', repo_name + '_tmp')
    if not os.path.exists(path_to_store_results):
        os.makedirs(path_to_store_results)
    path_to_store_bug_report_xml = sheet_to_xml_converter(path_to_bug_report_sheet, path_to_store_results, repo_name)
    print("\tThe bug report is store in {}".format(path_to_store_bug_report_xml))

    # path_to_store_bug_report_xml = config['bug_info']['path_to_store_bug_report_xml']
    path_to_original_codebase = config['bug_info']['path_to_original_codebase']
    

    path_to_codebase = path_to_original_codebase
    bug_report_path = path_to_store_bug_report_xml

    # Translate bug report and comments in codebase
    is_translation_required = config['translation_config']['is_translation_required']
    print("\n\nStep 1. Translating Chinese to English")
    if is_translation_required == 'True':
        print("\tYou've chosen to translated the bug reports and comments in the codebase.")
        print("\tWe are translating summary and description in bug reports....")
        all_bug_data = bugzbookParser(path_to_store_bug_report_xml)
        raw_allBugData, allBugData_English = translateBugReport(all_bug_data)
        bug_report_path = createXMLFile(allBugData_English, path_to_store_results)

        print("\tWe are translating the commments in codebase to English...")
        try:
            path_to_translated_repo = os.path.join(path_to_store_results, allBugData_English["repositoryName"])
            if not os.path.exists(path_to_translated_repo):
                os.mkdir(path_to_translated_repo)
            path_to_codebase = translateCommentInRepo(path_to_original_codebase, path_to_translated_repo)
            print("\tThe translation process is finished.")
            print("\tNew repo is stored in {}".format(path_to_codebase))
            print("\tNew bug report is stored in {}".format(bug_report_path))
        except:
            traceback.print_exc()
    else:
        print("\tThe user doesn't want to translate.")
        print("\tThe codebase is stored in {}".format(path_to_codebase))
        print("\tThe bug report is stored in {}".format(bug_report_path))
        all_bug_data = bug_report_parser(bug_report_path)

    # Preprocessing bug reports, ignore those without ground truth.
    print("\n\nStep 2. Preprocess bug report")

    print("\t{} bug reports recieved.".format(len(all_bug_data['bugReportData'])))
    print("\tIf a bug report doesn't have a linked file, or linked files are non-java or cannot be found in the codebase, we consider it's invalid.")
    coverted_bug_data = converter(all_bug_data, path_to_codebase, isIgnoreNoGT=True, verbose=False)
    print("\t{} bug reports are invalid, we drop them.".format(len(all_bug_data["bugReportData"]) - len(coverted_bug_data['bugReportData'])))
    print("\t{} bug reports are valid and being processed...".format(len(coverted_bug_data['bugReportData'])))
    bug_report_path = createXMLFile(coverted_bug_data, path_to_store_results)


    # Run bug localization tool
    print("\n\nStep 3. Localize Bugs")

    if not os.path.exists(path_to_store_results):
        print("The path to store results doesn't exist!")

    path_to_tool = config['execute_config']['path_to_bl_box']

    buglocator = bugLocator(path_to_tool, path_to_store_results, repo_name)
    buglocator.runBugLocator(bug_report_path, path_to_codebase)
    print("\tBug Localization finished")

    # Generate report
    print('\n\nStep 4. Generate summary')
    mode = config['execute_config']['mode']
    buglocator.setRankResultFromTmp()
    buglocator.generate_report(mode)



if __name__=='__main__':
    parser = argparse.ArgumentParser(description="Demo of Multi-Language Bug Localization Tool")
    args = parser.parse_args()

    run()