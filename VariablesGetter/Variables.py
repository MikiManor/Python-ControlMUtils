# uncompyle6 version 2.11.3
# Python bytecode 3.5 (3350)
# Decompiled from: Python 3.5.2 |Anaconda 4.1.1 (64-bit)| (default, Jul  5 2016, 11:41:13) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: Variables.py
import paramiko
import base64
import os
import collections
from operator import itemgetter

def is_empty(any_structure):
    if any_structure:
        return False
    return True


def printTable(myDict, colList=None):
    print('started')
    if not colList:
        colList = list(myDict[0].keys() if myDict else [])
    myList = [
     colList]
    for item in myDict:
        myList.append([str(item[col] or '') for col in colList])

    colSize = [max(map(len, col)) for col in zip(*)]
    myList.insert(1, ['-' * i for i in colSize])
    return myList


def serverConnectionEstablish(serverName, ssh):
    userName = 'ctmuser'
    decodedPassword = base64.b64decode(b'YzBudHJvbC1t')
    decodedPassword = decodedPassword.decode('ascii')
    try:
        ssh.connect(serverName, username=userName, password=decodedPassword)
    except paramiko.ssh_exception:
        raise Exception('Failed To login! Please check the password again')

    return ssh


def variablesPuller(ssh):
    commandToExucute = ' ctmvar -action list '
    os.system('cls')
    try:
        stdin, stdout, stderr = ssh.exec_command(commandToExucute)
        myList = stdout.read().splitlines()[2:-2]
        if is_empty(myList):
            return 'No Data Found... :-('
        notFoundDataForJob = False
    except paramiko.SSHException:
        raise Exception('Failed to execute the command!')

    results = []
    for line in myList:
        line = line.decode('ascii').split()
        varName = line[0]
        varExpr = line[1]
        dict = collections.OrderedDict([
         (
          'Variable Name', varName),
         (
          'Variable Expression', varExpr)])
        results.append(dict)

    sortedResults = sorted(results, key=itemgetter('Variable Name'))
    return printTable(sortedResults)


def main(serverName):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        sshConnection = serverConnectionEstablish(serverName, ssh)
    except:
        quit()

    try:
        return variablesPuller(sshConnection)
    except:
        quit()
# okay decompiling M:\Scripts\Python\CTM-Utils.exe_extracted\out00-PYZ.pyz_extracted\Variables.pyc
