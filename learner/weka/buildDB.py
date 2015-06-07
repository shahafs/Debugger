from weka import docXml, source_Monitor

__author__ = 'Amir-pc'

import sqlite3
import git
import csv
import git.objects.tree
import os
import datetime
import checkReport
import blameParse
import commentedCodeDetector
import pathPackCsv
import unicodedata

def BugNum(stri):
    s = stri.lower().replace(":","").replace("#","").replace("-","").split()
    ans = ""
    for x in s:
        for i in list(x):
            if (i in list("1234567890")):
                ans = ans + i
        if(len(ans)<8 and len(ans)>4):
            return int(ans)
        ans=""
    return 0


def commTable(bugs,commits,j ,k ,max):
    commits_items = commits.items()
    all_commits=[]
    all_files=[]
    i=0
    for com in commits_items:
        i=i+1
        if (i == max):
            break
        comm=com[1]
        commit_id=int("".join(list(comm.hexsha)[:7]),16)
        commiter_date=  datetime.datetime.fromtimestamp(comm.committed_date).strftime('%Y-%m-%d %H:%M:%S')
        author_date=  datetime.datetime.fromtimestamp(comm.authored_date).strftime('%Y-%m-%d %H:%M:%S')
        #x = (comm.committer.name).encode('ascii').decode("ISO-8859-1")
        name=unicodedata.normalize('NFKD', comm.committer.name).encode('ascii','ignore')
        committer= str(name)
        author= str(comm.author.name.encode('ascii','ignore'))
        stats =comm.stats
        parent =0
        if(comm.parents!=() ):
            parent =int("".join(list(comm.parents[0].hexsha)[:7]),16)
        msg =comm.message
        size=comm.size
        reach =comm.count()
        tot= stats.total
        dels=tot["deletions"]
        lines=tot["lines"]
        insertions=tot["insertions"]
        files=tot["files"]
        fields = (commit_id, bugs[j], commiter_date,committer,author_date,author, lines, dels, insertions, files,size,parent,reach,msg)
        all_commits.append(fields)
        #c.execute("INSERT INTO commits VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)", fields)
        stas= stats.files
        if(j%1000==0):
            print "iteration: "+str(j)+ " file: "+str(k)
        for fileName in stas:
            tot=stas[fileName]
            dels=tot["deletions"]
            lines=tot["lines"]
            insertions=tot["insertions"]
            fileTuple = (fileName.replace("/","\\"), commit_id,commiter_date,lines, dels, insertions, bugs[j])
            all_files.append(fileTuple)
            #c.execute("INSERT INTO files VALUES (?,?,?,?,?,?,?)", fileTuple)
            k=k+1
        j=j+1
        #conn.commit()
    return (all_commits,all_files)

def commitsAndBugs(bugs, commits,repo,max):
    i = 0
    am=0
    for git_commit in repo.iter_commits():
        a = False
        summ = git_commit.summary
        for x in list(summ):
            if (x in list("1234567890")):
                num = BugNum(summ)
                a = (num > 9)
                break
        if (a):
            bugs[i] = num
        else:
            bugs[i] = 0
        commits[i] = git_commit
        i = i + 1
        am=am+1
        if(am==max):
            break


def bugsTable(BugsFile,max):
    # Create table
    all_bugs=[]
    reader = csv.reader(BugsFile)
    # creates the reader object
    am=0
    for row in reader:# iterates the rows of the file in orders
        am=am+1
        if(am==1):
            continue
        if(am==max):
            break
        r=[]
        for x in row:
            lst=x
            if(len(lst)>0 and  lst[0]=="="):
                lst=lst[2:(len(lst)-1)]
            r.append(str(lst))
        r[7]= datetime.datetime.strptime(r[7],"%d/%m/%Y %H:%M")
        r[16]= datetime.datetime.strptime(r[16],"%d/%m/%Y %H:%M")
        all_bugs.append(r)
    #conn.commit()
    return all_bugs

def allFiles(path,max):
    acc=[]
    i=0
    pathLen=len(path)+1 # one for the \
    for root, dirs, files in os.walk(path): # Walk directory tree
        if(i == max):
            break
        for f in files:
            i=i+1
            path_join = "".join(list(os.path.join(root, f))[pathLen:])
            acc=acc+[path_join]
    return acc


def BuildRepo(gitPath, bugsPath,max ):
    BugsFile = open(bugsPath, "r")
    repo = git.Repo(gitPath)
    commits = {}
    bugs = {}
    allBugs=bugsTable(BugsFile,max)
    print("finish bugs")
    commitsAndBugs(bugs, commits,repo,max)
    allCommits,allFilesCommits=commTable(bugs,commits, 0,0,max)
    retFiles=[]
    print("finish commits")
    return (allCommits,allFilesCommits,allBugs)


def createTables(c,add):
    c.execute(
    '''CREATE TABLE bugsFix (ID INT,Product text,Component text,Assigned_To text,Status text,Resolution text,Reporter text,Last_Modified DateTime ,Version text,Milestone text,Hardware text,OS text,Priority text,Severity text,Summary text,Keywords text,Submit_Date DateTime ,Blocks text,Depends_On text,Duplicate_Of INT,CC text)''')

    if( not add):
        c.execute(
            '''CREATE TABLE commits (ID INT, bugId INT, commiter_date DateTime , commiter text,author_date DateTime , author text  , lines INT,deletions INT,insertions INT,files INT,size INT, parentID INT,reachable_commits INT, message text )''')
        c.execute(
            '''CREATE TABLE Commitedfiles (id INT,name text, commitid INT, commiter_date DateTime,lines INT,deletions INT,insertions INT, bugId INT)''')
        c.execute('''CREATE TABLE files (id INT,name text)''')
        c.execute('''CREATE TABLE Complexyfiles (name text, complex INT)''')
        c.execute('''CREATE TABLE haelsTfiles (name text, Operators_count INT, Distinct_operators INT, Operands_count INT, Distinct_operands INT, Program_length INT, Program_vocabulary INT,Volume float, Difficulty INT, Effort float)''')
        c.execute(
            '''CREATE TABLE bugs (ID INT,Product text,Component text,Assigned_To text,Status text,Resolution text,Reporter text,Last_Modified DateTime ,Version text,Milestone text,Hardware text,OS text,Priority text,Severity text,Summary text,Keywords text,Submit_Date DateTime ,Blocks text,Depends_On text,Duplicate_Of INT,CC text)''')
        c.execute(
            '''CREATE TABLE JAVAfiles (name text,Lines INT,	Statements INT,	Percent_Branch_Statements INT,Method_Call_Statements INT,Percent_Lines_with_Comments INT,Classes_and_Interfaces INT,Methods_per_Class float,Average_Statements_per_Method float,Line_Number_of_Most_Complex_Method 	INT, Name_of_Most_Complex_Method 	text, Maximum_Complexity INT,Line_Number_of_Deepest_Block INT,Maximum_Block_Depth INT,Average_Block_Depth	float, Average_Complexity	float, Statements_at_block_level_0 INT,Statements_at_block_level_1 INT,Statements_at_block_level_2 INT,Statements_at_block_level_3 INT,Statements_at_block_level_4 INT,Statements_at_block_level_5 INT,Statements_at_block_level_6 INT,Statements_at_block_level_7 INT,Statements_at_block_level_8 INT,Statements_at_block_level_9 INT)''')
        c.execute(
            '''CREATE TABLE Sourcemethods (File_Name text, Method text ,Complexity	INT, Statements INT, 	Maximum_Depth	INT, Calls INT)''')
        c.execute(
            '''CREATE TABLE classes (Dirpath text,superClass text,exception text, name text,externalizable text ,abstract text ,path text ,error text   ,included text ,scope text   ,serializable text)''')
        c.execute(
            '''CREATE TABLE constructors (Dirpath text ,className text , name text , synchronized text, varArgs text,  classPath text ,static text, signature text, included text, scope text, final text,  native text,  Num_params text)''')
        c.execute(
            '''CREATE TABLE methods (Dirpath text,className text, name text , synchronized text, abstract text , varArgs text, classPath text , static text, signature text , included text , scope text  , final text  , native text   ,return text,Num_params text)''')
        c.execute(
            '''CREATE TABLE fields (Dirpath text,className text,static text, name text, classPath text, transient text,volatile text,scope text,    final text, type text)''')
        c.execute(
            '''CREATE TABLE checkStyle (name text,McCabe REAL,fanOut REAL,NPath REAL,FileLen INT, NCSS INT, outer INT, publicMethods INT, totalMethods INT,thorwsSTM INT,Coupling INT,Executables INT, depthFor INT,depthIf INT)''')
        #c.execute(
         #   '''CREATE TABLE blame (name text,diff_commits INT,diff_commits_lastver INT,groups INT ,committers INT,avg_date DateTime,median_date DateTime ,max_date DateTime,numBlobs INT, numPatchs INT,numCommits INT )''')
        c.execute('''CREATE TABLE comments (name text, commitid INT)''')
        c.execute('''CREATE TABLE blameExtends (name text,diff_commits INT,diff_commits_lastver INT,diff_commitsApproved INT,diff_commits_lastverApproved INT,numBlobs INT, numPatchs INT,numCommits INT,
                    len_times INT,mean_times DateTime,median_times DateTime,var_times float,max_times DateTime,min_times DateTime,p01_times  float,p02_times  float,p05_times  float,mx1_times  float, max_min_times INT,
                    ones_times float, twos_times float,less5_times float,less10_times float,
                    len_difftimes INT,mean_difftimes DateTime,median_difftimes DateTime,var_difftimes float,max_difftimes DateTime,min_difftimes DateTime,p01_difftimes float,p02_difftimes float,p05_difftimes float,mx1_difftimes  float, max_min_difftimes INT,
                    ones_difftimes float, twos_difftimes float,less5_difftimes float,less10_difftimes float,
                    len_committers INT,p01_committers  float,p02_committers  float,p05_committers  float,mx1_committers  float,
                    len_timesApproved INT,mean_timesApproved DateTime,median_timesApproved DateTime,var_timesApproved float,max_timesApproved DateTime,min_timesApproved DateTime,p01_timesApproved  float,p02_timesApproved  float,p05_timesApproved  float,mx1_timesApproved  float, max_min_timesApproved INT,
                    ones_timesApproved float, twos_timesApproved float,less5_timesApproved float,less10_timesApproved float,
                    len_difftimesApproved INT,mean_difftimesApproved DateTime,median_difftimesApproved DateTime,var_difftimesApproved float,max_difftimesApproved DateTime,min_difftimesApproved DateTime,p01_difftimesApproved float,p02_difftimesApproved float,p05_difftimesApproved float,mx1__difftimesApproved  float, max_min_difftimesApproved INT,
                    ones_difftimesApproved float, twos_difftimesApproved float,less5_difftimesApproved float,less10_difftimesApproved float,
                    len_committersApproved INT,p01_committersApproved  float,p02_committersApproved  float,p05_committersApproved  float,mx1_committersApproved  float,
                    len_groups INT,mean_groups float,median_groups float,var_groups float,max_groups float,min_groups float,p01_groups  float,p02_groups  float,p05_groups  float,mx1_groups  float,
                    len_groupsApproved INT,mean_groupsApproved float,median_groupsApproved float,var_groupsApproved float,max_groupsApproved float,min_groupsApproved float,p01_groupsApproved  float,p02_groupsApproved  float,p05_groupsApproved  float,mx1_groupsApproved  float)'''    )

        c.execute(
        '''CREATE TABLE checkStyleExtends (name text, NCSS INT,FileLen INT,sum_fors REAL,sum_ifs REAL,sum_tries REAL,
                    len_mccab REAL,sum_mccab REAL,mean_mccab REAL,median_mccab REAL,var_mccab REAL,max_mccab REAL,min_mccab REAL, oneElement_mccab text,
                    len_fanOut REAL,sum_fanOut REAL,mean_fanOut REAL,median_fanOut REAL,var_fanOut REAL,max_fanOut REAL,min_fanOut REAL, oneElement_fanOut text,
                    len_NPath REAL,sum_NPath REAL,mean_NPath REAL,median_NPath REAL,var_NPath REAL,max_NPath REAL,min_NPath REAL, oneElement_NPath text,
                    len_JavaNCSSmet REAL,sum_JavaNCSSmet REAL,mean_JavaNCSSmet REAL,median_JavaNCSSmet REAL,var_JavaNCSSmet REAL,max_JavaNCSSmet REAL,min_JavaNCSSmet REAL, oneElement_JavaNCSSmet text,
                    len_thorwsSTM REAL,sum_thorwsSTM REAL,mean_thorwsSTM REAL,median_thorwsSTM REAL,var_thorwsSTM REAL,max_thorwsSTM REAL,min_thorwsSTM REAL, oneElement_thorwsSTM text,
                    len_coupl REAL,sum_coupl REAL,mean_coupl REAL,median_coupl REAL,var_coupl REAL,max_coupl REAL,min_coupl REAL, oneElement_coupl text,
                    len_executables REAL,sum_executables REAL,mean_executables REAL,median_executables REAL,var_executables REAL,max_executables REAL,min_executables REAL, oneElement_executables text,
                    len_lens REAL,sum_lens REAL,mean_lens REAL,median_lens REAL,var_lens REAL,max_lens REAL,min_lens REAL, oneElement_lens text
                    )''')
        c.execute(
        '''CREATE TABLE JAVAfilesFix (name text,Lines INT,	Statements INT,	Percent_Branch_Statements INT,Method_Call_Statements INT,Percent_Lines_with_Comments INT,Classes_and_Interfaces INT,Methods_per_Class float,Average_Statements_per_Method float,Line_Number_of_Most_Complex_Method 	INT, Name_of_Most_Complex_Method 	text, Maximum_Complexity INT,Line_Number_of_Deepest_Block INT,Maximum_Block_Depth INT,Average_Block_Depth	float, Average_Complexity	float, Statements_at_block_level_0 INT,Statements_at_block_level_1 INT,Statements_at_block_level_2 INT,Statements_at_block_level_3 INT,Statements_at_block_level_4 INT,Statements_at_block_level_5 INT,Statements_at_block_level_6 INT,Statements_at_block_level_7 INT,Statements_at_block_level_8 INT,Statements_at_block_level_9 INT)''')
        c.execute(
            '''CREATE TABLE SourcemethodsFix (File_Name text, Method text ,Complexity	INT, Statements INT, 	Maximum_Depth	INT, Calls INT)''')




def basicBuild(bugsPath, c, checkStyle, conn, gitPath, max):
    files = allFiles(gitPath, max)
    # add files to table files
    i = 0
    for f in files:
        # print f
        c.execute("INSERT INTO files VALUES (?,?)", (i, f))
        i = i + 1
    conn.commit()
    commits, commitedFiles, bugs = BuildRepo(gitPath, bugsPath, max)
    for com in commits:
        c.execute("INSERT INTO commits VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)", com)
    # can add commits and bugs to table and commited
    conn.commit()
    for bug in bugs:
        c.execute("INSERT INTO bugs VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", bug)
    conn.commit()
    commited = []
    for file in commitedFiles:
        file_ = file[0]
        files_index = -1
        if (file_ in files):
            files_index = files.index(file_)
        t = files_index,
        commited.append(t + file)
    for comFile in commited:
        c.execute("INSERT INTO Commitedfiles VALUES (?,?,?,?,?,?,?,?)", comFile)
    conn.commit()
    hael=commentedCodeDetector.buildHael(gitPath,max)
    for h in hael:
        c.execute("INSERT INTO haelsTfiles VALUES (?, ?, ?, ?, ?, ?, ?,?, ?, ?)", h)
    conn.commit()


def basicBuildOneTimeCommits( c, conn, gitPath, max,commits, commitedFiles, bugs):
    files = allFiles(gitPath, max)
    # add files to table files
    i = 0
    for f in files:
        # print f
        c.execute("INSERT INTO files VALUES (?,?)", (i, f))
        i = i + 1
    conn.commit()
    #commits, commitedFiles, bugs = BuildRepo(gitPath, bugsPath, max)
    for com in commits:
        c.execute("INSERT INTO commits VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)", com)
    # can add commits and bugs to table and commited
    conn.commit()
    for bug in bugs:
        c.execute("INSERT INTO bugs VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", bug)
    conn.commit()
    commited = []
    for file in commitedFiles:
        file_ = file[0]
        files_index = -1
        if (file_ in files):
            files_index = files.index(file_)
        t = files_index,
        commited.append(t + file)
    for comFile in commited:
        c.execute("INSERT INTO Commitedfiles VALUES (?,?,?,?,?,?,?,?)", comFile)
    conn.commit()
    hael=commentedCodeDetector.buildHael(gitPath,max)
    for h in hael:
        c.execute("INSERT INTO haelsTfiles VALUES (?, ?, ?, ?, ?, ?, ?,?, ?, ?)", h)
    conn.commit()



def BuildAll(gitPath, dbPath,bugsPath ,JavaDocPath, sourceMonitorFiles,sourceMonitorMethods,checkStyle,blamePath,date,add, max,CodeDir):
    conn = sqlite3.connect(dbPath)
    conn.text_factory = str
    c = conn.cursor()
    createTables(c,add)
    BugsFile=open(bugsPath,"r")
    bugs=bugsTable(BugsFile,max)
    #for bug in bugs:
        #c.execute("INSERT INTO bugsFix VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", bug)
     #   conn.commit()
    if(not add):
        basicBuild(bugsPath, c, checkStyle, conn, gitPath, max)
        SourceFiles,SourceMethods= source_Monitor.build(sourceMonitorFiles,sourceMonitorMethods,max)
        for file in SourceFiles:
            c.execute("INSERT INTO JAVAfiles VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", file)
        conn.commit()
        for met in SourceMethods:
            if len(met)!=6:
                continue
            c.execute("INSERT INTO Sourcemethods VALUES (?,?,?,?,?,?)", met)
        # can add source and methods
        conn.commit()

        packPath=pathPackCsv.projectPathPacks(gitPath)
        docs= docXml.build(JavaDocPath,packPath,max)
        # can add all javadoc options
        for doc in docs:
            for clss in doc:
                vals,all_methods,all_fields,all_cons=clss
                c.execute("INSERT INTO classes VALUES (?,?,?,?,?,?,?,?,?,?,?)", vals)
                for method in all_methods:
                    c.execute("INSERT INTO methods VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", method)
                for field in all_fields:
                    c.execute("INSERT INTO fields VALUES (?,?,?,?,?,?,?,?,?,?)", field)
                for cons in all_cons:
                    c.execute("INSERT INTO constructors VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", cons)
        blames=blameParse.blameBuild(blamePath,date,max)
        for blame in blames:
             c.execute("INSERT INTO blameExtends VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", blame)
        conn.commit()
        #blames=blameParse.blameBuild(blamePath,date,max)
        #for blame in blames:
         #    c.execute("INSERT INTO blame VALUES (?,?,?,?,?,?,?,?,?,?,?)", blame)
        comp = checkReport.fileRead(checkStyle,max,False,CodeDir)
        for f in comp:
            c.execute("INSERT INTO checkStyleExtends VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",f)
        conn.commit()
        SourceFiles,SourceMethods= source_Monitor.build(sourceMonitorFiles,sourceMonitorMethods,max)
        for file in SourceFiles:
            c.execute("INSERT INTO JAVAfilesFix VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", file)
        conn.commit()
        for met in SourceMethods:
            if len(met)!=6:
                continue
            c.execute("INSERT INTO SourcemethodsFix VALUES (?,?,?,?,?,?)", met)
        conn.commit()
    conn.close()
#BuildAll("C:\Users\Amir-pc\Documents\GitHub\org.eclipse.cdt", "C:\Users\Amir-pc\Documents\GitHub\Aapart1.db","C:\Users\Amir-pc\Documents\GitHub\\CDT-MORE-DATA.csv","C:/Users/Amir-pc/Documents/GitHub/Jdoc/*.xml","C:\Users\Amir-pc\Documents\GitHub\\source1.csv","C:\Users\Amir-pc\Documents\GitHub\\source1_methods.csv",30)

def BuildAllOneTimeCommits(gitPath, dbPath,bugsPath ,JavaDocPath, sourceMonitorFiles,sourceMonitorMethods,checkStyle,blamePath,date,add, max,CodeDir,commits, commitedFiles, bugs):
    conn = sqlite3.connect(dbPath)
    conn.text_factory = str
    c = conn.cursor()
    createTables(c,add)
    BugsFile=open(bugsPath,"r")
    #bugs=bugsTable(BugsFile,max)
    #for bug in bugs:
        #c.execute("INSERT INTO bugsFix VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", bug)
     #   conn.commit()
    if(not add):
        basicBuildOneTimeCommits( c, conn, gitPath, max,commits, commitedFiles, bugs)
        SourceFiles,SourceMethods= source_Monitor.build(sourceMonitorFiles,sourceMonitorMethods,max)
        for file in SourceFiles:
            c.execute("INSERT INTO JAVAfiles VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", file)
        conn.commit()
        for met in SourceMethods:
            if len(met)!=6:
                continue
            c.execute("INSERT INTO Sourcemethods VALUES (?,?,?,?,?,?)", met)
        # can add source and methods
        conn.commit()

        packPath=pathPackCsv.projectPathPacks(gitPath)
        docs= docXml.build(JavaDocPath,packPath,max)
        # can add all javadoc options
        for doc in docs:
            for clss in doc:
                vals,all_methods,all_fields,all_cons=clss
                c.execute("INSERT INTO classes VALUES (?,?,?,?,?,?,?,?,?,?,?)", vals)
                for method in all_methods:
                    c.execute("INSERT INTO methods VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", method)
                for field in all_fields:
                    c.execute("INSERT INTO fields VALUES (?,?,?,?,?,?,?,?,?,?)", field)
                for cons in all_cons:
                    c.execute("INSERT INTO constructors VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", cons)
        blames=blameParse.blameBuild(blamePath,date,max)
        for blame in blames:
             c.execute("INSERT INTO blameExtends VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", blame)
        conn.commit()
        #blames=blameParse.blameBuild(blamePath,date,max)
        #for blame in blames:
         #    c.execute("INSERT INTO blame VALUES (?,?,?,?,?,?,?,?,?,?,?)", blame)
        comp = checkReport.fileRead(checkStyle,max,False,CodeDir)
        for f in comp:
            c.execute("INSERT INTO checkStyleExtends VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",f)
        conn.commit()
        SourceFiles,SourceMethods= source_Monitor.build(sourceMonitorFiles,sourceMonitorMethods,max)
        for file in SourceFiles:
            c.execute("INSERT INTO JAVAfilesFix VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", file)
        conn.commit()
        for met in SourceMethods:
            if len(met)!=6:
                continue
            c.execute("INSERT INTO SourcemethodsFix VALUES (?,?,?,?,?,?)", met)
        conn.commit()
    conn.close()
#BuildAll("C:\Users\Amir-pc\Documents\GitHub\org.eclipse.cdt", "C:\Users\Amir-pc\Documents\GitHub\Aapart1.db","C:\Users\Amir-pc\Documents\GitHub\\CDT-MORE-DATA.csv","C:/Users/Amir-pc/Documents/GitHub/Jdoc/*.xml","C:\Users\Amir-pc\Documents\GitHub\\source1.csv","C:\Users\Amir-pc\Documents\GitHub\\source1_methods.csv",30)

def createIndexes(dbPath):
    conn = sqlite3.connect(dbPath)
    conn.text_factory = str
    c = conn.cursor()
    index_createA=' CREATE INDEX IF NOT EXISTS commits_id ON commits (ID)'
    c.execute(index_createA)
    conn.commit()
    index_createA=' CREATE INDEX IF NOT EXISTS bugs_id ON bugs (ID)'
    c.execute(index_createA)
    conn.commit()
    index_createA=' CREATE INDEX IF NOT EXISTS bugsFix_id ON bugsFix (ID)'
    c.execute(index_createA)
    conn.commit()
    index_createB=' CREATE INDEX IF NOT EXISTS commitedFiles_Commitid ON commitedfiles (commitid)'
    c.execute(index_createB)
    conn.commit()
    index_createC='  CREATE INDEX IF NOT EXISTS commitedFiles_Name ON commitedfiles (name)'
    c.execute(index_createC)
    conn.commit()
    index_createD='  CREATE INDEX IF NOT EXISTS JAVAfiles_Name ON JAVAfiles (name)'
    c.execute(index_createD)
    conn.commit()
    index_createD='  CREATE INDEX IF NOT EXISTS Sourcemethods_fileName ON Sourcemethods (File_Name)'
    c.execute(index_createD)
    conn.commit()
    index_createD='  CREATE INDEX IF NOT EXISTS JAVAfilesFix_Name ON JAVAfilesFix (name)'
    c.execute(index_createD)
    conn.commit()
    index_createD='  CREATE INDEX IF NOT EXISTS SourcemethodsFix_fileName ON SourcemethodsFix (File_Name)'
    c.execute(index_createD)
    conn.commit()
    index_createD='  CREATE INDEX IF NOT EXISTS classes_Name ON classes (name)'
    c.execute(index_createD)
    conn.commit()
    index_createD='  CREATE INDEX IF NOT EXISTS constructors_className ON constructors (className)'
    c.execute(index_createD)
    conn.commit()
    index_createD='  CREATE INDEX IF NOT EXISTS methods_className ON methods (className)'
    c.execute(index_createD)
    conn.commit()
    index_createD='  CREATE INDEX IF NOT EXISTS fields_className ON fields (className)'
    c.execute(index_createD)
    conn.commit()
    index_createD='  CREATE INDEX IF NOT EXISTS checkStyle_name ON checkStyle (name)'
    c.execute(index_createD)
    conn.commit()
    index_createD='  CREATE INDEX IF NOT EXISTS checkStyleExtends_name ON checkStyleExtends (name)'
    c.execute(index_createD)
    conn.commit()
    #index_createD='  CREATE INDEX IF NOT EXISTS blame_name ON blame (name)'
    #c.execute(index_createD)
    index_createD='  CREATE INDEX IF NOT EXISTS blameExtends_name ON blameExtends (name)'
    c.execute(index_createD)
    conn.commit()
    conn.close()

def names_dates():
    return [ ('CDT_8_0_1', '2011-09-15'), ('CDT_8_0_2', '2012-02-11'), ('CDT_8_1_0', '2012-06-10'), ('CDT_8_1_1', '2012-09-17'), ('CDT_8_1_2', '2013-02-14'), ('CDT_8_2_0', '2013-06-12')]

def build(versPath,dbsPath,bugsPath,add,max,vers, CodeDir):

    #vers=('CDT_8_0_2', 'CDT_8_1_0','CDT_8_1_1','CDT_8_1_2' )
    #vers= ('CDT_3_0',  'CDT_4_0_0',  'CDT_5_0_0',  'CDT_6_0_0',  'CDT_7_0_0',  'CDT_8_0_0')
    #vers= (  'CDT_5_0_0',  'CDT_6_0_0',  'CDT_7_0_0',  'CDT_8_0_0')
    #commsSpaces.create(vers,versPath)
    dates =[i1[1] for i1 in names_dates()]
    for ver,date in zip(vers,dates):
        print ver
        Path=versPath+"\\"+ver
        gitPath=Path+"\\"+ CodeDir
        dbPath=dbsPath+"\\"+ver+".db"
        JavaDocPath=Path+"\\Jdoc2"
        sourceMonitorFiles=Path+"\\"+ver+".csv"
        sourceMonitorMethods=Path+"\\"+ver+"_methods.csv"
        print sourceMonitorMethods
        checkStyle=versPath+"\\checkAll\\"+ver+".xml"
        blamePath=Path+"\\blame"
        print( dbPath)
        BuildAll(gitPath, dbPath,bugsPath ,JavaDocPath, sourceMonitorFiles,sourceMonitorMethods,checkStyle,blamePath,date,add, max,CodeDir)
        createIndexes(dbPath)

def buildOneTimeCommits(versPath,dbsPath,bugsPath,add,max,vers, CodeDir):

    #vers=('CDT_8_0_2', 'CDT_8_1_0','CDT_8_1_1','CDT_8_1_2' )
    #vers= ('CDT_3_0',  'CDT_4_0_0',  'CDT_5_0_0',  'CDT_6_0_0',  'CDT_7_0_0',  'CDT_8_0_0')
    #vers= (  'CDT_5_0_0',  'CDT_6_0_0',  'CDT_7_0_0',  'CDT_8_0_0')
    #commsSpaces.create(vers,versPath)
    dates =[i1[1] for i1 in names_dates()]
    ver=vers[-1]
    Path=versPath+"\\"+ver
    gitPath=Path+"\\"+ CodeDir
    commits, commitedFiles, bugs = BuildRepo(gitPath, bugsPath, max)
    for ver,date in zip(vers,dates):
        print ver
        Path=versPath+"\\"+ver
        gitPath=Path+"\\"+ CodeDir
        dbPath=dbsPath+"\\"+ver+".db"
        JavaDocPath=Path+"\\Jdoc2"
        sourceMonitorFiles=Path+"\\"+ver+".csv"
        sourceMonitorMethods=Path+"\\"+ver+"_methods.csv"
        print sourceMonitorMethods
        checkStyle=versPath+"\\checkAll\\"+ver+".xml"
        blamePath=Path+"\\blame"
        print( dbPath)
        BuildAllOneTimeCommits(gitPath, dbPath,bugsPath ,JavaDocPath, sourceMonitorFiles,sourceMonitorMethods,checkStyle,blamePath,date,add, max,CodeDir,commits, commitedFiles, bugs)
        createIndexes(dbPath)

if __name__ == "__main__":

    vers=('CDT_8_0_1','CDT_8_0_2', 'CDT_8_1_0','CDT_8_1_1','CDT_8_1_2' )
    #build("C:\GitHub\\vers","C:\GitHub\\vers\\dbP","C:\GitHub\\CDT-MORE-DATA.csv",False,30,vers,"org.eclipse.cdt")
    #build("C:\GitHub\\vers","C:\GitHub\\vers\\dbAdd\\done2","C:\GitHub\\CDT-MORE-DATA.csv",True,-1,vers,"org.eclipse.cdt")
    vers=('TOMCAT_8_0_4','TOMCAT_8_0_5','TOMCAT_8_0_6','TOMCAT_8_0_7','TOMCAT_8_0_8' )
    #vers=['TOMCAT_8_0_4']#,'TOMCAT_8_0_5','TOMCAT_8_0_6','TOMCAT_8_0_7','TOMCAT_8_0_8' )
    build("C:\\tomcat\\code","C:\\tomcat\\code\\dbAdd","C:\\tomcat\\tomcat_bugs.csv",False,-1,[vers[0]],"tomcat8")








