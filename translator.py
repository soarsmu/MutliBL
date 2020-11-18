# -*- coding: UTF-8 -*-

# 需要安装Google的SDK
# from google.cloud import translate_v2 as translate
from xml.dom.minidom import parse
import xml.dom.minidom
import copy
import os
from comment_parser import comment_parser
import magic
from tqdm import tqdm
import time
import traceback
import eventlet
import timeout_decorator

@timeout_decorator.timeout(5)
def get_comment(codeFilePath):
    commentList = comment_parser.extract_comments(codeFilePath, mime='text/x-java-source')
    return commentList





def bug_report_parser(path):
    '''
    用来parse XML文件，并返回一个包含所有信息的字典
    包含一些信息：
    * bug id opendate fixdate
    * buginformation
        * summary
        * description
    * fixedFiles
        * a series of files in the codebase
    '''
    allBugData = {} # 用于存储bug数据，包括repo名称，bugReport信息
    allBugData['bugReportData'] = {}

    DOMTree = parse(path) # 读取存储bug report的XML文件
    bugreports = DOMTree.documentElement
    bugrepositoryName = bugreports.getAttribute('name')
    allBugData['repositoryName'] = bugrepositoryName
    bugReportList = bugreports.getElementsByTagName("bug")
    
    for bugReport in bugReportList:
        bugdata = {}
        bugdata['id'] = bugReport.getAttribute("id")
        bugdata['opendate'] = bugReport.getAttribute("opendate")
        bugdata['fixdate'] = bugReport.getAttribute("fixdate")

        summary = bugReport.getElementsByTagName("summary")
        try:
            summaryText = summary[0].childNodes[0].data # 得到summary信息
        except Exception as e:
            summary = bugReport.getElementsByTagName("title")
            summaryText = summary[0].childNodes[0].data # 得到summary信息

        bugdata['summary'] = summaryText
        description = bugReport.getElementsByTagName("description")
        # 发现description有可能是空的，因此做此处理
        if len(description[0].childNodes) > 0:
            descriptionText = description[0].childNodes[0].data # 得到description信息
        else:
            descriptionText = ''
        bugdata['description'] = descriptionText
        fixedFiles = bugReport.getElementsByTagName("file")
        bugdata['files'] = []
        for file in fixedFiles:
            try:
                fileName = file.childNodes[0].data
            except:
                fileName = ""
            bugdata['files'].append(fileName)
        allBugData['bugReportData'][bugReport.getAttribute("id")] = bugdata
    
    return allBugData

def createXMLFile(allBugData):
    '''
    接受allBugData的字典
    解析字典，并且构建XML文件
    '''
    bugReportData = allBugData['bugReportData']
    repositoryName = allBugData['repositoryName']

    doc = xml.dom.minidom.Document()
    root = doc.createElement("bugrepository") 
    root.setAttribute('name', repositoryName) 
    doc.appendChild(root)

    for bugid in bugReportData:
        bugReport = bugReportData[bugid]
        bugNode = doc.createElement('bug')
        bugNode.setAttribute('id', bugid) 
        bugNode.setAttribute('opendate', bugReport['opendate']) 
        bugNode.setAttribute('fixdate', bugReport['fixdate']) 
        
        buginformationNode = doc.createElement('buginformation')
        summaryNode = doc.createElement('summary')
        descriptionNode = doc.createElement("description")

        summaryNode.appendChild(doc.createTextNode(bugReport['summary']))
        descriptionNode.appendChild(doc.createTextNode(bugReport['description']))

        buginformationNode.appendChild(summaryNode)
        buginformationNode.appendChild(descriptionNode)
        bugNode.appendChild(buginformationNode)

        fixedFilesNode = doc.createElement('fixedFiles')
        for fixedFile in bugReport['files']:
            fileNode = doc.createElement('file')
            fileNode.appendChild(doc.createTextNode(fixedFile))
            fixedFilesNode.appendChild(fileNode)

        bugNode.appendChild(fixedFilesNode)


        root.appendChild(bugNode)

    bugReportXMLName = repositoryName + '.XML'
    with open(os.path.join('./', bugReportXMLName), 'w') as f:
        doc.writexml(f, indent='\t', addindent='\t', newl='\n', encoding="utf-8")

def translator(text):
    '''Unimplemented!!! Implement this'''
    # summary_English = translate_client.translate(summaryText, 'en')['translatedText']
    # Return translated text!!!
    return text


def translateBugReport(allBugData):
    '''
    接受格式固定的bug data，将中文翻译为英文
    '''
    raw_allBugData = allBugData
    allBugData_English = copy.deepcopy(allBugData)
    
    repositoryName = allBugData['repositoryName'] 
    allBugData_English['repositoryName'] = repositoryName + '_English'
    # 修改名称

    bugReportData = allBugData['bugReportData'] # 有关bug report的原始数据
    for bugid in bugReportData:
        bugReport = bugReportData[bugid]
        # 得到summary和description的原始文本
        summaryText = bugReport['summary']
        descriptionText = bugReport['description']
        
        # Do translation
        summary_English = translator(summaryText)
        description_English = translator(descriptionText)
        
        # translation is done.

        # 现在用这些新的信息修改bug report
        allBugData_English['bugReportData'][bugid]['summary'] = summary_English
        # 修改summary
        allBugData_English['bugReportData'][bugid]['description'] = description_English
        # 修改description
    
    return raw_allBugData, allBugData_English


def translateCodeComment(codeFilePath):
    '''
    得到代码的路径，读取所有的comment
    然后翻译，并append到文件的末尾
    To-Do: 如果项目中多种编程语言混合怎么办？需要自动识别PL. 暂时只关注.java file
    '''
    # check whether it is a java file, if not, warning the users and skip.
    comment_to_append = ''
    if codeFilePath[-5:] != '.java':
        # 暂时我们只关注java文件，如果不是.java文件则跳过
        return ''
    try:
        commentList = get_comment(codeFilePath)
    except timeout_decorator.timeout_decorator.TimeoutError as e:
        return ''
    # 这里容易出问题，有些Java文件貌似无法被parse

    for comment in commentList:
        commentText = comment.text().replace('*', ' ')
        comment_English = translator(commentText)
        comment_to_append = comment_to_append + '\n /* ' + comment_English + '*/ \n'
    
    return comment_to_append


def translateCommentInRepo(pathToRepo, path_to_new_repo):
    '''
    接受一个repo的路径
    遍历得到其中所有的Java文件，并对其进行翻译
    '''
    assert os.path.exists(path_to_new_repo)
    dirInfo = os.walk(pathToRepo)
    for fileInfo in tqdm(list(dirInfo)):
        directory = fileInfo[0]
        fileNames = fileInfo[2]
        for name in fileNames:
            if name.split('.')[-1] != 'java':
                continue
            path = os.path.join(directory, name)
            comment_to_append = translateCodeComment(path)
            # 要创建文件夹，然后创建文件
            target_dir = path_to_new_repo + '/' + directory.split(pathToRepo)[1]
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)
            code_content = open(path,'r').read()
            with open(os.path.join(target_dir, name), 'w') as f:
                f.write(code_content)
                f.write("/* Translated Comments:  */ ")
                f.write(comment_to_append)
    return path_to_new_repo
                





def translateBugReportModule():
    bugReportPath = '/Users/smu/Desktop/ZXingBugRepository.xml'
    allBugData = bug_report_parser(bugReportPath)
    raw_allBugData, allBugData_English = translateBugReport(allBugData)
    createXMLFile(allBugData_English)

if __name__=='__main__':    
    translate_client = translate.Client()
    codeToRepo = '/Users/smu/Desktop/ZXing-1.6/core/'
    translateCommentInRepo(codeToRepo)
    
