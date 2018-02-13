import os
import sys
import time
import xml.etree.ElementTree as ET


def finder(schemaName, resourceName):
    numOfFoundJobs = 0
    schemaName = schemaName.lower()
    resourceName = resourceName.lower()
    path = '\\\\ntsrv1\\tohna\\Control-M_Project\\Full-Drafts-Prod'
    os.chdir(path)
    draftFiles = sorted(os.listdir(os.getcwd()), key=os.path.getmtime)
    lastDraftFile = draftFiles[-1]
    tree = ET.parse(lastDraftFile)
    root = tree.getroot()
    resultList = []
    for Table in root:
        tableName = str(Table.get('FOLDER_NAME'))
        orderMethod = str(Table.get('FOLDER_ORDER_METHOD'))
        for job in Table.iter('JOB'):
            tempList = []
            listRow = "\n**************************************\n\nTable : " + tableName + " - UserDaily : " + orderMethod
            tempList.append(listRow)
            jobName = job.get('JOBNAME')
            nodeId = job.get('NODEID')
            applType = job.get('APPL_TYPE')
            if applType not in "DATABASE":
                continue
            if not nodeId:
                nodeId = "None"
            listRow = "-->> Job : " + jobName + " - Agent : " + nodeId
            tempList.append(listRow)
            loopObjectResult = []
            loopObjectResult = loopObject(job, schemaName, resourceName)
            if loopObjectResult != False and loopObjectResult != None:
                for loopListRow in loopObjectResult:
                    tempList.append(loopListRow)
                numOfFoundJobs += 1
                resultList.append(tempList)
    for subList in resultList:
        print("\n".join(subList))
    print("\n**************************************\nTotal number of jobs found : ", numOfFoundJobs)


def getVariableType(i_VarName):
    dict = {
        "%%FTP-LPATH1": "File Trans Left Path",
        "%%FTP-LPATH2": "File Trans Left Path",
        "%%FTP-LPATH3": "File Trans Left Path",
        "%%FTP-LPATH4": "File Trans Left Path",
        "%%FTP-LPATH5": "File Trans Left Path",
        "%%FTP-RPATH1": "File Trans Right Path",
        "%%FTP-RPATH2": "File Trans Right Path",
        "%%FTP-RPATH3": "File Trans Right Path",
        "%%FTP-RPATH4": "File Trans Right Path",
        "%%FTP-RPATH5": "File Trans Right Path",
        "%%FTP-RUSER": "File Trans Left User",
        "%%FTP-RUSER": "File Trans Right User",
        "%%FTP-ACCOUNT": "File Trans Account",
        "%%FTP-LHOST": "File Trans Left Host",
        "%%FTP-RHOST": "File Trans Right Host",
        "%%DB-STP_SCHEM" : "DB Schema",
        "%%DB-STP_PACKAGE": "DB PKG Name",
        "%%DB-STP_NAME": "DB SP Name",
        "%%INF-WORKFLOW": "INF WF Name"
    }
    if i_VarName in dict:
        return dict[i_VarName]
    else:
        return i_VarName


def loopObject(objectName, schemaName, resourceName):
    tempList = []
    foundJobIndicator = False
    foundQrIndicator = False
    jobBasicAttribs = objectName.attrib
    for subItem in objectName:
        parameterType = subItem.tag
        lowerDict = dict((k.lower(), v.lower()) for k, v in subItem.attrib.items())
        if parameterType == "VARIABLE":
            varName = subItem.attrib.get('NAME')
            varValue = str(subItem.attrib.get('VALUE'))
            lowerVarValue = varValue.lower()
            if schemaName in lowerVarValue and varName in "%%DB-STP_SCHEM":
                foundJobIndicator = True
                translatedFieldName = getVariableType(varName)
                listRow = "---->> " + translatedFieldName + " = " + varValue
                tempList.append(listRow)
                qRList = []
                for qResource in objectName.iter('QUANTITATIVE'):
                    qRName = str(qResource.get('NAME').lower())
                    qRList.append(qRName)
                if resourceName in qRList:
                    foundQrIndicator = True
                    break
                else:
                    listRow = "---->> QR : " + resourceName + " Not Found\n" + "-------->> QR List : " + str(qRList)
                    tempList.append(listRow)
                    break
            else:
                continue
        else:
            continue
    if ((foundJobIndicator) and (foundQrIndicator == False)):
        return tempList
    else:
        return False

yes = set(['YES', 'Y', 'YE'])
schemaName = ""
resourceName = ""
keepSearchingIndicator = True
useExcludeFlag = False
while keepSearchingIndicator:
    schemaNames = ""
    while schemaNames == "":
        schemaNames = input('Enter the name of the Oracle Schemna : ')
    schemasList = schemaNames.split(',')
    resourceName = input('Enter Resource Name :')
    resourceName = resourceName.upper()
    for schema in schemasList:
        finder(schema, resourceName)
    keepSearching = input('do you want to search another string ? (y/yes)')
    keepSearching = keepSearching.upper()
    if keepSearching not in yes:
        keepSearchingIndicator = False

input('Press any key to continue.... ')




