import paramiko
import base64
import os
import getpass
import sys
from datetime import datetime
from datetime import timedelta
from operator import itemgetter
import collections
from itertools import groupby

def is_empty(any_structure):
    if any_structure:
        #print('Structure is not empty.')
        return False
    else:
        #print('Structure is empty.')
        return True

def printTable(myDict, colList=None):
   """ Pretty print a list of dictionaries (myDict) as a dynamically sized table.
   If column names (colList) aren't specified, they will show in random order.
   Author: Thierry Husson - Use it as you want but don't blame me.
   """
   if not colList: colList = list(myDict[0].keys() if myDict else [])
   myList = [colList] # 1st row = header
   for item in myDict: myList.append([str(item[col] or '') for col in colList])
   colSize = [max(map(len,col)) for col in zip(*myList)]
   formatStr = ' | '.join(["{{:<{}}}".format(i) for i in colSize])
   myList.insert(1, ['-' * i for i in colSize]) # Seperating line
   for item in myList: print(formatStr.format(*item))

print("************************\nThis is Statistics Reporter, no need to order a job for statistics :)\n************************\n")
userName = "ctmuser"
encodedPassword = b'YzBudHJvbC1t'
#password = getpass.getpass("Enter Password for ctmuser : ")
keepSearching = True
decodedPassword = base64.b64decode(b'YzBudHJvbC1t')
decodedPassword = decodedPassword.decode('ascii')
yes = set(['YES','Y','YE'])

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
try:
    ssh.connect("pctmpapp", username=userName, password=decodedPassword)
except paramiko.ssh_exception:
    raise Exception('Failed To login! Please check the password again')
    input()

while(keepSearching):
    notFoundDataForJob = True
    while(notFoundDataForJob):
        commandToExucute = 'ctmruninf -list "*" -jobname '
        os.system('cls')
        jobNameTosearchFor = input('Enter Job Name or prefix (Key Sensitive!!!) : ')
        commandToExucute = commandToExucute + '"*' + jobNameTosearchFor + '*"'
        #print(commandToExucute)
        try:
            stdin, stdout, stderr = ssh.exec_command(commandToExucute)
            myList = stdout.read().splitlines()[2:-2]
            #print(myList)
            if is_empty(myList):
                input('No data for this job or prefix! enter any key to try again...')
            else:
                #input('All Good')
                notFoundDataForJob = False
        except paramiko.SSHException:
            #input('Shit')
            raise Exception('Faild to execute the command!')
    results = []
    for line in myList:
        line = line.decode('ascii').split()
        endDate = datetime.strptime(line[0], '%Y%m%d%H%M%S')
        runTime = round(float(line[-1]))
        delta = timedelta(seconds=runTime)
        startDate = endDate - delta
        m, s = divmod(runTime, 60)
        h, m = divmod(m, 60)
        runTime = "%d:%02d:%02d" % (h, m, s)
        jobName = line[1]
        memName = line[5]
        dict = collections.OrderedDict([
             ("Job Name", jobName),
             ("Mem Name", memName),
             ("Start Time", startDate),
             ("End Time", endDate),
            ("Elapsed Minutes", runTime)]
         )
        results.append(dict)
    sortedResults = sorted(results, key=itemgetter('Job Name','Mem Name'))

    groups = []
    uniquekeys = []
    for k, g in groupby(sortedResults, key=itemgetter('Job Name','Mem Name')):
        groups.append(list(g))
        uniquekeys.append(k)
    if (len(uniquekeys) > 1):
        print('There are ' + str(len(uniquekeys)) + ' Jobs :  ')
        for key in uniquekeys:
            print(key[0] + ' ||| ' + key[1])
        print("\n\n\n+++++++++++++++++++++++++++++")
    printTable(sortedResults)
    keepSearchingAnswer = input('Search for another job?... (Y/N)')
    keepSearchingAnswer = keepSearchingAnswer.upper()
    if keepSearchingAnswer not in yes:
        keepSearching = False