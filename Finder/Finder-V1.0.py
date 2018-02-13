import os
import sys
import time
import xml.etree.ElementTree as ET

def finder(stringToSearch, stringToExclude, useExcludeFlag):
    numOfFoundJobs = 0
    stringToSearch = stringToSearch.lower()
    stringToExclude = stringToExclude.lower()
    path = '\\\\ntsrv1\\tohna\\Control-M_Project\\Full-Drafts-Prod'
    os.chdir(path)
    draftFiles = sorted(os.listdir(os.getcwd()), key=os.path.getmtime)
    lastDraftFile = draftFiles[-1]
    tree = ET.parse(lastDraftFile)
    root = tree.getroot()
    resultList = []
    for Table in root:
        tableName = str(Table.get('TABLE_NAME'))
        orderMethod = str(Table.get('TABLE_USERDAILY'))
        if (Table.tag == "SMART_TABLE"):
            tableList = []
            tableListRow = "\n**************************************\n\nSmart Table : " + tableName + " - UserDaily : " + orderMethod
            tableList.append(tableListRow)
            loopObjectResult = []
            if useExcludeFlag == True:
                loopObjectResult = loopObjectWithExclude(Table,stringToSearch,stringToExclude)
            else:
                loopObjectResult = loopObject(Table,stringToSearch)
            if loopObjectResult != False and loopObjectResult != None :
                for loopListRow in loopObjectResult:
                    tableList.append(loopListRow)
                numOfFoundJobs += 1
                resultList.append(tableList)
            for subTable in Table.iter('SUB_TABLE'):
                subTableName = str(subTable.get('JOBNAME'))
                subTableList = []
                subTableListRow = "\n**************************************\n\nSub Table : " + subTableName  + " - Under : " + tableName
                subTableList.append(subTableListRow)
                loopObjectResult = []
                if useExcludeFlag == True:
                    loopObjectResult = loopObjectWithExclude(subTable,stringToSearch,stringToExclude)
                else:
                    loopObjectResult = loopObject(subTable,stringToSearch)
                
                if loopObjectResult != False and loopObjectResult != None :
                    for loopListRow in loopObjectResult:
                        subTableList.append(loopListRow)
                    numOfFoundJobs += 1
                    resultList.append(subTableList)
        for job in Table.iter('JOB'):
            tempList = []
            listRow = "\n**************************************\n\nTable : " + tableName + " - UserDaily : " + orderMethod
            tempList.append(listRow)
            jobName = job.get('JOBNAME')
            nodeId = job.get('NODEID')
            if not nodeId:
                nodeId = "None"
            listRow = "-->> Job : " + jobName + " - Agent : " + nodeId
            tempList.append(listRow)    
            loopObjectResult = []
            if useExcludeFlag == True:
                loopObjectResult = loopObjectWithExclude(job,stringToSearch,stringToExclude)
            else:
                loopObjectResult = loopObject(job,stringToSearch)
            #print(loopObjectResult)
            if loopObjectResult != False and loopObjectResult != None :
                for loopListRow in loopObjectResult:
                    tempList.append(loopListRow)
                numOfFoundJobs += 1
                resultList.append(tempList)
    for subList in resultList:
        print("\n".join(subList))
    print("\n**************************************\nTotal number of jobs found : ", numOfFoundJobs)

def getVariableType(i_VarName):
    dict = {
    "%%FTP-LPATH1" : "File Trans Left Path",
    "%%FTP-LPATH2" : "File Trans Left Path",
    "%%FTP-LPATH3" : "File Trans Left Path",
    "%%FTP-LPATH4" : "File Trans Left Path",
    "%%FTP-LPATH5" : "File Trans Left Path",
    "%%FTP-RPATH1" : "File Trans Right Path",
    "%%FTP-RPATH2" : "File Trans Right Path",
    "%%FTP-RPATH3" : "File Trans Right Path",
    "%%FTP-RPATH4" : "File Trans Right Path",
    "%%FTP-RPATH5" : "File Trans Right Path",
    "%%FTP-RUSER" : "File Trans Left User" ,
    "%%FTP-RUSER" : "File Trans Right User",
    "%%FTP-ACCOUNT": "File Trans Account",
    "%%FTP-LHOST" : "File Trans Left Host",
    "%%FTP-RHOST" : "File Trans Right Host",
    "%%DB-STP_PACKAGE" : "DB PKG Name",
    "%%DB-STP_NAME" : "DB SP Name",
    "%%INF-WORKFLOW" : "INF WF Name"
    }
    if i_VarName in dict:
        return dict[i_VarName]
    else:
        return i_VarName

def loopObject(objectName,stringToSearch):
    tempList = []
    foundIndicator = False
    jobBasicAttribs = objectName.attrib
    lowerJobBasicAttribs = dict((k, v.lower()) for k,v in jobBasicAttribs.items())
    for valueIndex in lowerJobBasicAttribs:
        lowValue = lowerJobBasicAttribs[valueIndex]
        #print(lowValue)
        value = jobBasicAttribs[valueIndex]
        if stringToSearch in lowValue:
            foundIndicator = True
            listRow = "---->> " + valueIndex.upper() + " = " + value
            tempList.append(listRow)
    for subItem in objectName:
        parameterType = subItem.tag
        lowerDict = dict((k.lower(), v.lower()) for k,v in subItem.attrib.items())
        if parameterType == "VARIABLE":
            varName = subItem.attrib.get('NAME')
            varValue = str(subItem.attrib.get('VALUE'))
            lowerVarValue = varValue.lower()
            if stringToSearch in lowerVarValue:
                foundIndicator = True
                translatedFieldName = getVariableType(varName)
                listRow = "---->> " + translatedFieldName +  " = " + varValue
                tempList.append(listRow)
        elif parameterType == "QUANTITATIVE":
            initName = subItem.attrib.get('NAME')
            initValue = subItem.attrib.get('VALUE')
            lowerInitName = initName.lower()
            if stringToSearch in lowerInitName :
                foundIndicator = True
                listRow = "---->> INIT = " + initName
                tempList.append(listRow)
        elif parameterType == "INCOND" :
            condName = subItem.attrib.get('NAME')
            lowerCondName = condName.lower()
            condDate = subItem.attrib.get('ODATE')
            if stringToSearch in lowerCondName:
                foundIndicator = True
                listRow = "---->> IN Cond Name = " + condName +  " | Date = " + condDate
                tempList.append(listRow)
        elif parameterType == "OUTCOND" :
            condName = subItem.attrib.get('NAME')
            lowerCondName = condName.lower()
            condSign = subItem.attrib.get('SIGN')
            condDate = subItem.attrib.get('ODATE')
            if stringToSearch in lowerCondName:
                foundIndicator = True
                listRow = "---->> OUT Cond Name = " + condName + " | Sign = " + condSign + " | Date = " + condDate
                tempList.append(listRow)
        elif parameterType == "ON":
            onCode = subItem.attrib.get('CODE')
            onStmt = subItem.attrib.get('STMT')
            for doStatement in subItem.iter():
                doType = doStatement.tag
                if doType == "DOSHOUT":
                    destName = doStatement.attrib.get('DEST')
                    lowerDestName = destName.lower()
                    msgText = doStatement.attrib.get('MESSAGE')
                    lowerMsgText = msgText.lower()
                    if stringToSearch in lowerDestName or stringToSearch in lowerMsgText:
                        foundIndicator = True
                        listRow = "---->> On Code = " + onCode + " Stmt = " + onStmt + " | Shout Destination Name = " + destName + " | MSG = " + msgText
                        tempList.append(listRow)
                if doType == "DOCOND":
                    condName = doStatement.attrib.get('NAME')
                    lowerCondName = condName.lower()
                    condSign = doStatement.attrib.get('SIGN')
                    condDate = doStatement.attrib.get('ODATE')
                    if stringToSearch in lowerCondName:
                        foundIndicator = True
                        listRow = "---->> On Code = " + onCode + " OUT Cond Name = " + condName + " | Sign = " + condSign + " | Date = " + condDate
                        tempList.append(listRow)
                if doType == "DOMAIL":
                    mailDestination = doStatement.attrib.get('DEST')
                    lowerMailDest = mailDestination.lower()
                    mailMsg = doStatement.attrib.get('MESSAGE')
                    if mailMsg != None:
                        lowerMailMsg = mailMsg.lower()
                    else:
                        mailMsg = lowerMailMsg = "Empty Body"
                    mailSubject = doStatement.attrib.get('SUBJECT')
                    if mailSubject != None:
                        lowerMailSubject = mailSubject.lower()
                    else:
                        mailSubject = lowerMailSubject = "Empty Subject"
                    if stringToSearch in lowerMailDest or stringToSearch in lowerMailMsg or stringToSearch in lowerMailSubject:
                        foundIndicator = True
                        listRow = "---->> Mail Message:"  + "\n-------->> TO : " + mailDestination + "\n-------->> Subject : " + mailSubject + "\n-------->> Message : " + mailMsg
                        tempList.append(listRow)
        elif parameterType == "SHOUT":
            whenTime = subItem.attrib.get('TIME')
            destName = subItem.attrib.get('DEST')
            lowerDestName = destName.lower()
            msgText  = subItem.attrib.get('MESSAGE')
            lowerMsgText = msgText.lower()
            whenText = subItem.attrib.get('WHEN')
            if stringToSearch in lowerDestName or stringToSearch in lowerMsgText:
                foundIndicator = True
                if whenTime:
                    listRow = "---->> PostProc Shout Name = " + destName + " | MSG = " + msgText + " | WHEN = " + whenText + " " + whenTime
                    tempList.append(listRow)
                else:
                    listRow = "---->> PostProc Shout Name = " + destName + " | MSG = " + msgText + " | WHEN = " + whenText
                    tempList.append(listRow)
    if foundIndicator:
        return tempList
    else:
        return False




def loopObjectWithExclude(objectName,stringToSearch,stringToExclude):
    tempList = []
    foundIndicator = False
    jobBasicAttribs = objectName.attrib
    lowerJobBasicAttribs = dict((k, v.lower()) for k,v in jobBasicAttribs.items())
    for valueIndex in lowerJobBasicAttribs:
        lowValue = lowerJobBasicAttribs[valueIndex]
        #print(lowValue)
        value = jobBasicAttribs[valueIndex]
        if stringToSearch in lowValue and stringToExclude not in lowValue:
            foundIndicator = True
            listRow = "---->> " + valueIndex.upper() + " = " + value
            tempList.append(listRow)
    for subItem in objectName:
        parameterType = subItem.tag
        lowerDict = dict((k.lower(), v.lower()) for k,v in subItem.attrib.items())
        if parameterType == "AUTOEDIT2":
            varName = subItem.attrib.get('NAME')
            varValue = str(subItem.attrib.get('VALUE'))
            lowerVarValue = varValue.lower()
            if stringToSearch in lowerVarValue and stringToExclude not in lowerVarValue:
                foundIndicator = True
                translatedFieldName = getVariableType(varName)
                listRow = "---->> " + translatedFieldName +  " = " + varValue
                tempList.append(listRow)
        elif parameterType == "QUANTITATIVE":
            initName = subItem.attrib.get('NAME')
            initValue = subItem.attrib.get('VALUE')
            lowerInitName = initName.lower()
            if stringToSearch in lowerInitName and stringToExclude not in lowerInitName:
                foundIndicator = True
                listRow = "---->> INIT = " + initName
                tempList.append(listRow)
        elif parameterType == "INCOND" :
            condName = subItem.attrib.get('NAME')
            lowerCondName = condName.lower()
            condDate = subItem.attrib.get('ODATE')
            if stringToSearch in lowerCondName and stringToExclude not in lowerCondName:
                foundIndicator = True
                listRow = "---->> IN Cond Name = " + condName +  " | Date = " + condDate
                tempList.append(listRow)
        elif parameterType == "OUTCOND" :
            condName = subItem.attrib.get('NAME')
            lowerCondName = condName.lower()
            condSign = subItem.attrib.get('SIGN')
            condDate = subItem.attrib.get('ODATE')
            if stringToSearch in lowerCondName and stringToExclude not in lowerCondName:
                foundIndicator = True
                listRow = "---->> OUT Cond Name = " + condName + " | Sign = " + condSign + " | Date = " + condDate
                tempList.append(listRow)
        elif parameterType == "ON":
            onCode = subItem.attrib.get('CODE')
            onStmt = subItem.attrib.get('STMT')
            for doStatement in subItem.iter():
                doType = doStatement.tag
                if doType == "DOSHOUT":
                    destName = doStatement.attrib.get('DEST')
                    lowerDestName = destName.lower()
                    msgText = doStatement.attrib.get('MESSAGE')
                    lowerMsgText = msgText.lower()
                    if (stringToSearch in lowerDestName and stringToExclude not in lowerDestName) or (stringToSearch in lowerMsgText and stringToExclude not in lowerMsgText):
                        foundIndicator = True
                        listRow = "---->> On Code = " + onCode + " Stmt = " + onStmt + " | Shout Destination Name = " + destName + " | MSG = " + msgText
                        tempList.append(listRow)
                if doType == "DOCOND":
                    condName = doStatement.attrib.get('NAME')
                    lowerCondName = condName.lower()
                    condSign = doStatement.attrib.get('SIGN')
                    condDate = doStatement.attrib.get('ODATE')
                    if stringToSearch in lowerCondName and stringToExclude not in lowerCondName:
                        foundIndicator = True
                        listRow = "---->> On Code = " + onCode + " OUT Cond Name = " + condName + " | Sign = " + condSign + " | Date = " + condDate
                        tempList.append(listRow)

                if doType == "DOMAIL":
                    mailDestination = doStatement.attrib.get('DEST')
                    lowerMailDest = mailDestination.lower()
                    mailMsg = doStatement.attrib.get('MESSAGE')
                    if mailMsg != None:
                        lowerMailMsg = mailMsg.lower()
                    else:
                        mailMsg = lowerMailMsg = "Empty Body"
                    mailSubject = doStatement.attrib.get('SUBJECT')
                    if mailSubject != None:
                        lowerMailSubject = mailSubject.lower()
                    else:
                        mailSubject = lowerMailSubject = "Empty Subject"
                    if ( stringToSearch in lowerMailDest and stringToExclude not in  lowerMailDest ) or ( stringToSearch in lowerMailMsg and stringToExclude not in lowerMailMsg )or ( stringToSearch in lowerMailSubject
                                            and strinToExclude not in lowerMailSubject):
                        foundIndicator = True
                        listRow = "---->> Mail Message:"  + "\n-------->> TO : " + mailDestination + "\n-------->> Subject : " + mailSubject + "\n-------->> Message : " + mailMsg
                        tempList.append(listRow)
                        
        elif parameterType == "SHOUT":
            whenTime = subItem.attrib.get('TIME')
            destName = subItem.attrib.get('DEST')
            lowerDestName = destName.lower()
            msgText  = subItem.attrib.get('MESSAGE')
            lowerMsgText = msgText.lower()
            whenText = subItem.attrib.get('WHEN')
            if (stringToSearch in lowerDestName and stringToExclude not in lowerDestName) or (stringToSearch in lowerMsgText and stringToExclude not in lowerMsgText):
                foundIndicator = True
                if whenTime:
                    listRow = "---->> PostProc Shout Name = " + destName + " | MSG = " + msgText + " | WHEN = " + whenText + " " + whenTime
                else:
                    listRow = "---->> PostProc Shout Name = " + destName + " | MSG = " + msgText + " | WHEN = " + whenText
                    tempList.append(listRow)
    if foundIndicator:
        return tempList
    else:
        return False
                
yes = set(['YES','Y','YE'])
stringToSearch = ""
stringToExclude = ""
keepSearchingIndicator = True
useExcludeFlag = False
while keepSearchingIndicator:
    stringToSearch = ""
    while stringToSearch == "":
        stringToSearch = input('Enter the string to search : ')
    useExclude = input('Do you want to exclude something? (y/yes or any othter key continue) :')
    useExclude = useExclude.upper()
    if useExclude in yes:
        useExcludeFlag = True
        while stringToExclude == "" :
            stringToExclude = input('Enter the string to exclude from the results : ')
        stringToSearch = stringToSearch.strip()
        stringToExclude = stringToExclude.strip()
        finder(stringToSearch, stringToExclude, useExcludeFlag)
    else:
        useExcludeFlag = False
        stringToSearch = stringToSearch.strip()
        finder(stringToSearch, "None", useExcludeFlag)
    keepSearching = input('do you want to search another string ? (y/yes)')
    keepSearching = keepSearching.upper()
    if keepSearching not in yes:
        keepSearchingIndicator = False
    
input('Press any key to continue.... ')



    
