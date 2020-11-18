# -*- coding: UTF-8 -*-
from xml.dom.minidom import parse
import xml.dom.minidom
import os
import copy
import javalang
import translator
from tqdm import tqdm

def findJavaFileInCodebase(codebasePath):
    '''
    遍历codebase，找到所有的java文件的package name
    应该和BugLocator发现的文件一样
    然后判断bug report的文件是否在其中，如果不在则删掉
    '''
    javaFileList = []
    dirInfo = os.walk(codebasePath)
    for fileInfo in tqdm(list(dirInfo)):
        directory = fileInfo[0]
        fileNames = fileInfo[2]
        for name in fileNames:
            path = os.path.join(directory, name)
            if path.split('.')[-1] == 'java':
                with open(os.path.join(path), 'r') as f:
                    try:
                        tree = javalang.parse.parse(f.read())
                        javaFileList.append(tree.package.name + '.' + os.path.basename(os.path.join(codebasePath,path)))
                    except Exception:
                        # 可能存在语法错误
                        continue

    return javaFileList

def bugReportParser(path, codebasePath):
    '''
    这个函数是用于处理eclipise那个数据集的
    '''
    javaFileList = findJavaFileInCodebase(codebasePath)

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
        # However, BugLocator only allows id as Integer
        bugdata['opendate'] = bugReport.getAttribute("opendate")
        bugdata['fixdate'] = bugReport.getAttribute("fixdate")

        summary = bugReport.getElementsByTagName("summary")
        try:
            summaryText = summary[0].childNodes[0].data # 得到summary信息
        except Exception as e:
            summary = bugReport.getElementsByTagName("title")
            summaryText = summary[0].childNodes[0].data # 得到summary信息
        # Bugzbook中不是用summary，而是title
        if len(summary[0].childNodes) > 0:
            summaryText = summary[0].childNodes[0].data # 得到summary信息
        else:
            summaryText = ''

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
            if fileName in javaFileList:
                bugdata['files'].append(fileName)
        if len(bugdata['files']) == 0:
            # 如果在codebase中找不到这个文件
            # print("Cannot Found files in the codebase, skip...")
            continue
        allBugData['bugReportData'][bugReport.getAttribute("id")] = bugdata
    
    return allBugData

def bugzbookParser(path):
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
        # However, BugLocator only allows id as Integer
        bugdata['opendate'] = bugReport.getAttribute("opendate")
        bugdata['fixdate'] = bugReport.getAttribute("fixdate")

        summary = bugReport.getElementsByTagName("summary")
        try:
            summaryText = summary[0].childNodes[0].data # 得到summary信息
        except Exception as e:
            summary = bugReport.getElementsByTagName("title")
            summaryText = summary[0].childNodes[0].data # 得到summary信息
        # Bugzbook中不是用summary，而是title
        if len(summary[0].childNodes) > 0:
            summaryText = summary[0].childNodes[0].data # 得到summary信息
        else:
            summaryText = ''

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


def createXMLFile(allBugData, path_to_store='./'):
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

        if bugReport['summary'] == None:
            bugReport['summary'] = ''
        summaryNode.appendChild(doc.createTextNode(bugReport['summary']))
        if bugReport['description'] == None:
            bugReport['description'] = ''
        descriptionNode.appendChild(doc.createTextNode(bugReport['description']))

        buginformationNode.appendChild(summaryNode)
        buginformationNode.appendChild(descriptionNode)
        bugNode.appendChild(buginformationNode)

        fixedFilesNode = doc.createElement('fixedFiles')
        for fixedFile in bugReport['files']:
            fileNode = doc.createElement('file')
            if fixedFile == None:
                fixedFile = 'clear'
            fileNode.appendChild(doc.createTextNode(fixedFile))
            fixedFilesNode.appendChild(fileNode)

        bugNode.appendChild(fixedFilesNode)


        root.appendChild(bugNode)

    bugReportXMLName = repositoryName + '.XML'
    with open(os.path.join(path_to_store, bugReportXMLName), 'w') as f:
        doc.writexml(f, indent='\t', addindent='\t', newl='\n', encoding="utf-8")
    return os.path.join(path_to_store, bugReportXMLName)

def converter(allBugData, codebasePath, isIgnoreNoGT=True, verbose=False):
    '''
    接受parse后的bug reports数据，以及codebase的路径
    '''
    convertedBugData = {"bugReportData": {}}
    repoName = allBugData["repositoryName"]
    convertedBugData["repositoryName"] = repoName

    # bugid需要换成数字，给每个bug report分配一个数字id
    for i, origialBugID in enumerate(allBugData["bugReportData"]):
        # 将bug id改为数字
        i = str(i)
        convertedBugData["bugReportData"][i] = copy.deepcopy(allBugData["bugReportData"][origialBugID])
        convertedBugData["bugReportData"][i]["id"] = i

        # 修改file
        for j, filePath in enumerate(convertedBugData["bugReportData"][i]["files"]):
            if os.path.exists(os.path.join(codebasePath,filePath)):
                if filePath.split('.')[-1] == 'java':
                    # 是一个java文件
                    with open(os.path.join(codebasePath,filePath), 'r') as f:
                        try:
                            tree = javalang.parse.parse(f.read())
                        except:
                            if verbose:
                                print(f'\033[1;35;47m{"Cannot parse "}\033[0m{"  "}' + filePath)
                            #忽略此数据
                            convertedBugData["bugReportData"].pop(i)
                            break
                        '''
                        使用如下的逻辑处理文件名是因为出现过这样的情况：
                        在Bug report中，指向同一个文件，但是文件名大小写写错了
                        而python在读取文件的时候不区分文件名大小写，因此导致了KeyError
                        '''
                        father_dir = os.path.join(codebasePath,filePath).split('/')[0:-1]
                        files_on_disk = os.listdir('/'.join(father_dir))
                        file_name_in_report = os.path.basename(os.path.join(codebasePath,filePath))
                        for original_file_name in files_on_disk:
                            if file_name_in_report.lower() == original_file_name.lower():
                                convertedBugData["bugReportData"][i]["files"][j] = tree.package.name + '.' + original_file_name
                                if verbose:
                                    print(convertedBugData["bugReportData"][i]["files"][j])
                                break
                        # 修改<file>buggy file name</file>的数据
                        continue
                else:
                    # 存在，但不是java文件，无法处理
                    if verbose:
                        print(f'\033[1;35;47m{"Not java file :"}\033[0m{"  "}' + filePath)
            else: 
                # 文件并不存在，无法处理
                if verbose:
                    print(f'\033[1;33;44m{"File not found:"}\033[0m{" "}' + filePath)
            convertedBugData["bugReportData"][i]["files"][j] = "no_ground_truth_found"
            if isIgnoreNoGT:
                # 直接移除这一条
                convertedBugData["bugReportData"].pop(i)
                break

    return convertedBugData




if __name__=="__main__":
    bugzbookFilePath = '/Users/smu/Downloads/Bugzbook/pdfbox/2.0.0.xml'
    codebasePath = '/Users/smu/Desktop/pdfbox'
    # allBugData = bugReportParser(bugzbookFilePath,codebasePath)
    
    allBugData = bugzbookParser(bugzbookFilePath)
    convertedBugData = converter(allBugData, codebasePath)
    createXMLFile(convertedBugData)