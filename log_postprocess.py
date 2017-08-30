#!nusr/bin/python
#coding:utf-8
 

import subprocess
import sys
import os
import time
import platform
import re
import shutil
import zipfile
import gzip
import xml.etree.ElementTree as et
import datetime
import getopt
import struct
import StringIO
import string
from optparse import OptionParser
import re
import pexpect
global vmlinux_f
global sysdump_p
global ylog_p
global serial_num
global devbitinfo
num64 = "sp9850"
num642 = "sp9860"
num643 = "sp9832"

crash = None
savepath = None
#product_name_regex = re.compile(r'ro.product.name')
#product_name_get_regex = re.compile(r'(\w+)')
#build_host_regex = re.compile(r'ro.build.host')
#hw_version_regex = re.compile(r'ro.product.hardware')
#build_finger_regex = re.compile(r'ro.build.fingerprint')

def isLinux():
    sysstr = platform.system()
    if(sysstr == "Windows"):
        return False
    elif(sysstr == "Linux"):
        return True
    else:
        return False
#############################################################################
###########folderparser################ 
class FolderParser(object):
    '''
    classdocs
    '''

    def __init__(self, logfolder, devnum):
        '''
        Constructor
        '''
        # store the real path to a file
        self.storefile = "/home/likewise-open/SPREADTRUM/erin.liu/log_postprocess/log"
        self.devnum = devnum
        # static defined variable
        self.dateinternal = "DATE_INTERNAL";
        self.dateinternal_lastlog = "DATEINTERNAL_LASTLOG";
        self.dateexternal = "DATE_EXTERNAL";
        self.dateexternal_lastlog = "DATEEXTERNAL_LASTLOG";
        # store the fade and real path map
        self.mapfadereal = {}
        self.initdata()
        self.logfolder = logfolder
        if self.logfolder == None or self.logfolder == "":
            self.logfolder = self.getLogPath()
        print "logfolder " +str(self.logfolder)
        self.fullfilepaths = []
        self.fullfolderpaths = []
        self.cp = ConfigParser("configs/config.xml")
        self.workpath()
        
        
    def initdata(self):
        self.mapfadereal[self.dateinternal] = ""
        self.mapfadereal[self.dateinternal_lastlog] = []
        self.mapfadereal[self.dateexternal] = ""
        self.mapfadereal[self.dateexternal_lastlog] = []
        pass

    def printData(self):
        print "internal"
        print self.mapfadereal[self.dateinternal]
        print "internal_last"
        print self.mapfadereal[self.dateinternal_lastlog]
        print "external"
        print self.mapfadereal[self.dateexternal]
        print "external_last"
        print self.mapfadereal[self.dateexternal_lastlog]

    # return the log path if no basepath passed
    def getLogPath(self):
        if self.logfolder == None or self.logfolder == "":
            f = open(self.storefile, "r")
            path = f.readline()
            # get current path
            return path.strip()
        else:
            return self.logfolder
    
    # return report folder
    def getReportPath(self):
        pass
    def workpath(self):
        for parent, dirnames, filenames in os.walk(self.logfolder):  
            for dirname in  dirnames:  
                # print "parent is:" + parent
                # check if endwith external_storage
                # check if endwith external_storage
                # print  "dirname is" + dirname
                # internal_storage
                # internal_storage/last_log
                # internal_storage/2014-06-03-19-27-04
		'''
		if dirname.find("-") != -1 and parent.find("last_log") != -1 and parent.find("internal_log") != -1:
		    if isLinux():
		        interlast_external_date = parent.split("/")[-2]
		    else:
			interlast_external_date = parent.split("\\")[-2]
		    self.mapfadereal[self.dateinternal_lastlog].append((interlast_external_date,dirname))
		elif dirname.find("-") != -1 and parent.find("last_log") != -1:
		    self.mapfadereal[self.dateexternal_lastlog].append(dirname)
		if  dirname.find("-") != -1 and parent.endswith("external_storage"):
		    self.mapfadereal[self.dateexternal] = dirname
		if  dirname.find("-") != -1 and parent.endswith("internal_storage"):
		    self.mapfadereal[self.dateinternal] = dirname
                self.fullfolderpaths.append(os.path.join(parent, dirname))
		'''	
                if dirname.find("ylog") != -1 and parent.endswith("last_ylog") and parent.find("external_storage") != -1:
                    print "last_ext"
                    print dirname
                    print parent
                    self.mapfadereal[self.dateexternal_lastlog].append(dirname)
                if  dirname.find("ylog") != -1 and dirname.find("last_ylog") < 0 and parent.endswith("external_storage"):
                    print "ext"
                    print dirname
                    print parent
                    self.mapfadereal[self.dateexternal] = dirname
                if  dirname.find("ylog") != -1 and dirname.find("last") < 0 and parent.endswith("internal_storage"):
                    print "inter"
                    print dirname
                    print parent
                    self.mapfadereal[self.dateinternal] = dirname
                if  dirname.find("last_ylog") != -1 and parent.endswith("internal_storage"):
                    print "last_inter"
                    print dirname
                    print parent
                    self.mapfadereal[self.dateinternal_lastlog] = dirname
                self.fullfolderpaths.append(os.path.join(parent, dirname))
	
            #self.printData()
            for filename in filenames: 
                # print "parent is"+ parent
                # print "filename is:" + filename
                # print "the full name of the file is:" + os.path.join(parent,filename)
                self.fullfilepaths.append(os.path.join(parent, filename))
        #print "*****************self.mapfadereal*************"
  	#print self.mapfadereal
    def getmap(self):
        return self.mapfadereal
    
    def getfiles(self):
        return self.fullfilepaths
    
    def getfilesToStr(self):
        return ",".join(self.fullfilepaths)
      
    def getfolder(self):
        return self.fullfolderpaths
    
    def getfolderToStr(self):
        return ",".join(self.fullfolderpaths)
    
    def printmap(self):
        print self.mapfadereal
        
    def printfiles(self):
        print self.fullfilepaths
        
    def printdirs(self):
        print self.fullfolderpaths
        
    def getFileCount(self):
        return len(self.fullfilepaths)
    
    def getFolderCount(self):
        return len(self.fullfolderpaths)
        pass
    
    def getAnrFiles(self):
        typename = "anr"
        self.getFilesBy(typename)
        pass
    
    # return the string list of files with "," split
    def getFilesBy(self, typeName):
        files = self.cp.getProblemFiles(typeName)
        print typeName
        for f in files:
            f.toStr()
		#print f
        print typeName
        tmprefiles = []
	#count_num = 0
	#print files
        # get all path meeted files
        for i in self.fullfilepaths:
	#    count_num += 1
	#   print "--------------print count_num----------------"
       	#    print str(count_num)
	#    print "------------print i----------------"
	#    print i
            for f in files:
	        #print "xx"+f.getPath()
                #print "yy"+self.getRealPath(f.getPath())
                #print "0000000000f in files0000000000"
		#print f
                pp=""
                if not isLinux():
                    pp=f.getPath().replace("/","\\")
                else:
                    pp=f.getPath().replace("\\","/")
		    #print "tototoototototototot"
		    #f.toStr()
		#print "--------------print pp----------------"
		#print pp
                #print self.getRealPath(pp)
		#print i
                pp_list = self.getRealPath(pp)
		#print "plplplplplplplplplplplplplp"
		#for pl in pp_list:
		#    print pl
		#for ppl in pp_list:
                for jn in range(len(pp_list)):
                    if i.find(pp_list[jn]) >= 0:
                    # check items
                        chk = f.getCheckitem()
		    #print "chk" + str(chk)
                        if chk == "" or chk == None:
                            tmprefiles.append(i)
                        else:
                            for ii in chk.split(","):
                                if os.path.basename(i).find(ii) >= 0:
                                    tmprefiles.append(i)
                                    break
#break
        print "tmprefile " +str(tmprefiles)
        tmprefiles = list(set(tmprefiles))
        return ",".join(tmprefiles)
        pass
    
    def __checkComplete(self, f):
        i = 0
        while i < len(f):
            realPath = f[i]
	    
	    #print realPath
            i += 1
        return  f
        #return os.path.join(self.logfolder, realPath)
     
    # return null if file path is not exist
    def getRealPath(self, fadepath):
        result = fadepath
        if result == "" or result == None:
            return ""
        results = []
	#print "---------self.mapfadereal.item------"
	#print self.mapfadereal.items
        for (k, v) in self.mapfadereal.items():
            if result.find(k) != -1:
		
                #print "************print k v**************88"
	        #print k,v
                if v == "" or v == []:
                    results.append(result.replace(k, "nofolderfound"))
                else:
                    if isinstance(v, list):
                        for i in range(len(v)):
			    #print "list"
			    #print v[i]
                            vv = v[i]
                            if isinstance(vv,tuple):	
                                results.append(result.replace(k,vv[1]).replace("DATEEXTERNAL_LASTLOG",vv[0]))
                            else:
                                results.append(result.replace(k, vv))
                    else:
                        results.append(result.replace(k, v))
			
            # print result
            else:
                results.append(result)
        results = list(set(results))
		
        return self.__checkComplete(results)
        pass

#############################################################
############configparser##################

class ConfigParser:
    
    def __init__(self,configfile):
        self.configfile=configfile
        self.root=et.parse(configfile).getroot()
        pass
    
    # get text value in tree view 
    def parserSingle(self,item):
        nodes=item.split("/")
        length = len(nodes)
        self.node=self.root
        for i in range(length):
            self.node=self.node.find(nodes[i])
        return self.node.text
        pass
    # get checkItems
    def getCheckItems(self):
        checkfileNode=self.root.find("checkfile")
        files=checkfileNode.findall("file")
        fArr=[]
        # stype="file",ismust=0,checkitem="",condition="",path=""
        for f in files:
            #print f.get("type"),f.get("ismust"),f.get("checkitem"),f.get("condition"),f.text
            ff=FileItem(f.get("type"),f.get("ismust"),f.get("checkitem"),f.get("condition"),f.text)
            fArr.append(ff)
            pass
        return fArr
    
    def getProblemneededfiles(self,problemtype):
        return self.getProblemFiles(problemtype)
        pass
    
    def getProblemFiles(self,problemtype):
        problems=self.getProblems()
        files=[]
        ffs=None
        for p in problems:
            if p.get("type") == problemtype:
                # here get all file list
                ffs=p.findall("file")
                break
        if ffs !=None:
            for x in ffs:
                ff=FileItem(x.get("type"),"",x.get("checkitem"),"",x.text)
                ff.toStr()
                files.append(ff)
            pass
        return files
        pass
    def getProblems(self):
        problemneedfilenode=self.root.find("problemneededfile")
        return problemneedfilenode.findall("problem")
        
########################################################################
#########fileitem################################
class FileItem(object):
    '''
    used for file complition check
    '''


    def __init__(self,stype="file",ismust=0,checkitem="",condition="",path="",checktype="default"):
        '''
        Constructor
        '''
        self.stype=stype
        self.ismust=ismust
        self.checkitem=checkitem
        self.condition=condition
        self.path=path
        self.checktype=checktype
        self.checkresult=""
        pass
    
    def setCheckresult(self,checkresult):
        self.checkresult=checkresult
        
    def getCheckresult(self):
        return self.checkresult
        
    def setChecktype(self,checktype):
        self.checktype=checktype
    
    def getChecktype(self):
        return self.checktype
            
    def setStype(self,stype):
        self.stype=stype
    
    def getStype(self):
        return self.stype
    
    def setIsmust(self,ismust):
        self.ismust=ismust
        
    def getIsmust(self):
        return self.ismust
    
    def setCheckitem(self,checkitem):
        self.checkitem=checkitem
        
    def getCheckitem(self):
        return self.checkitem
    
    def setCondition(self,condition):
        self.condition=condition
    
    def getCondition(self):
        return self.condition
    
    def doCondition(self,pre):
        return eval(str(pre)+self.condition)
    
    def getPath(self):
        return self.path
    
    def setPath(self,path):
        self.path=path
        
    def getCheckItemNum(self):
        if self.checkitem=="exist":
            return 0
        if self.checkitem=="hassubfiles":
            return 1
        if self.checkitem=="subfilescount":
            return 2
        if self.checkitem=="foldersize":
            return 3


        
    def checkPath(self,realPath):
        result="check path is " + realPath
        # check if file exist
        if realPath=="":
            return 
        return 
    
    def toStr(self):
        print str(self.stype) + str(self.ismust) + str(self.checkitem) + str(self.condition)+str(self.path)


def printstr(str):
    #if debug:
    if True:
        print str

############################################################################
#########kernel_panic  main############################
    
class Main:
    def __init__(self, vmlinuxPath, sysdumpPath=None, slogPath=None, devbitInfo=None,devNum=None):
    #def __init__(self, sysdumpPath=None, slogPath=None, devNum=None):
        self.vmlinuxPath = vmlinuxPath
        self.sysdumpPath = sysdumpPath
        self.slogPath = slogPath
        self.devbitInfo = devbitInfo
        self.devnum = devNum
        self.report_title = "kernel_panic"
        self.report_content = ""
        self.sysdump_check_report_tag = "------ sysdump file check result ------"
        self.slog_check_report_tag = "------ slog comlete check result ------"
        self.startmode_report_tag = "------ start mode result ------"
        self.kernel_log_report_tag = "------ kernel log result ------"
        self.last_reg_access_report_tag = "------ last reg access result ------"
        self.kernel_log_sysdump_report_tag = "------ kernel log from sysdump result ------"
        self.text_segment_compare_report_tag = "------ .text statement compare result ------"
        self.oops_log_report_tag="------ Oops log result ------"
        self.kernel_log_keys = ["scheduling while atomic", "unbalanced enable/disable operation", "NFO:", "avc", ]
        self.filesmap = {}
        self.fzs = []
        if self.sysdumpPath != None:
            self.initData()
        if platform.system() == "Linux":
            location = self.slogPath.rfind("/")
        else:
            location = self.slogPath.rfind("\\")
        self.slogBasePath = self.slogPath[0:location]
        self.savePath = self.slogBasePath + os.path.sep + "post_process_report" + os.path.sep +"kernel_panic" + os.path.sep + "kernel_panic" + ".txt"
        self.savePath_dir = self.slogBasePath + os.path.sep + "post_process_report" + os.path.sep + "kernel_panic" + os.path.sep
		
        if not os.path.isdir(self.savePath_dir):
            os.makedirs(self.savePath_dir)
        print "savepath " +str(self.savePath)
        pass
    
    def initData(self):
        # check folder
        houzui = self.sysdumpPath[len(self.sysdumpPath) - 1:len(self.sysdumpPath)]
        if houzui == os.path.sep:
            self.sysdumpPath = self.sysdumpPath[0:len(self.sysdumpPath) - 1]
        self.fzs = os.listdir(self.sysdumpPath)
        self.fzs.sort()

    def getfile(self, key):
        for fz in self.fzs:
            print fz
            if str(fz).find(key) >= 0:
                return self.sysdumpPath + os.path.sep + str(fz)
        return None
        pass
    
    def run(self):
        #printstr("begin run")
        #self.report_content += self.getSlogCheckReport() + "\n"
        #self.report_content += self.getAndroidKernelLogkReport() + "\n"
        self.report_content += str(self.getAndroidRebootMode()) + "\n"
        #self.report_content += self.getCheckSysdumpReport() + "\n"
        #self.report_content += self.getLastRegAccess() + "\n"
        self.report_content += self.getSysdumpKernelLog() + "\n"
        #self.report_content += self.getTextSegmentCompareResult() + "\n"
        pass
    
    '''
        if sysdumppath exist deal with files here
        if not deal with files under slogpath/sysdump/
    '''
    def getLastRegAccess(self):
        global devbitinfo
        result = self.last_reg_access_report_tag + "\n"
	#if (cmp(self.devbitInfo,num64) == 0) or (cmp(self.devbitInfo,num642) == 0):
        if (self.devbitInfo.find(num64) != -1) or (self.devbitInfo.find(num642) != -1) or (self.devbitInfo.find(num643) != -1):
            print "******************64 bit**************"
            gr = GetRegAccess64(self.vmlinuxPath, self.sysdumpPath)
	#if (cmp(bit_t,num32) == 0):
        else:
            print "*******************32 bit*************"
            gr = GetRegAccess(self.vmlinuxPath, self.sysdumpPath)
        gr.parser()
        result += gr.getResult() + "\n"
        result += "cpu count " + str(gr.getCpucount())
        return result
        pass
    
    def checkKernelLog(self,keyw):
        fp = open(self.slogBasePath + os.path.sep + "post_process_report" + os.path.sep + "kernel_panic" + os.path.sep + "kernel_log.log")
        line = fp.readline()
        while line:
            fc = False
	    #if line.find("Kernel panic") != -1: 
            for kk in keyw:
                if line.find(kk) != -1:
                    fl = False 
                    for char in line:
                        if char in string.printable:
                            continue
                        else:
                            fl = True
                            break
                    if not fl:
                        fc = True
                        break
 
            if fc:
                print "find OK"
                return 1
            line = fp.readline()
        return 0

    def getSysdumpKernelLog(self):
        global bit_t
        result = self.kernel_log_sysdump_report_tag + "\n"
        sysdumpfile = self.getfile("01_0x80000000-0x87ffffff")
        if sysdumpfile == None:
            sysdumpfile = self.getfile("01_0x80000000-0xbfffffff")
        if sysdumpfile == None:
            sysdumpfile = self.getfile("sysdump.core.01")
        print sysdumpfile
        klp = KernelLogParser(self.vmlinuxPath, sysdumpfile, self.devbitInfo, self.slogBasePath + os.path.sep + "post_process_report" + os.path.sep + "kernel_panic" + os.path.sep)
        
        res = klp.parser()

        result +="kernel log location:\n"+res[0] +"\n"+ res[1]
        print result
        # write Oops log to logreport
        result += self.oops_log_report_tag+"\n"
        if os.path.exists(res[1]):
            f= open(res[1])
            result+=f.read()
            f.close()
            pass
        else:
            result +="No Oops log"
        
        return result
        if sysdumpfile.find("dumpall") != -1:
            os.remove(sysdumpfile)
        pass
    
    '''
        vmlinux and sysdump files contains 01_0x80000000-0x87ffffff
    '''
    def getTextSegmentCompareResult(self):
        global bit_t
        sysdumpfile = self.getfile("01_0x80000000-0x87ffffff")
        if sysdumpfile == None:
            sysdumpfile = self.getfile("01_0x80000000-0xbfffffff")
        if sysdumpfile == None:
            sysdumpfile = self.getfile("sysdump.core.01_")
#	print "*************sysdumpfile 01....-0x...."
        print sysdumpfile
        result = self.text_segment_compare_report_tag + "\n"
        if sysdumpfile == None:
            result += "no 01_0x80000000-0x87ffffff file find,skip compare .text segment"
            return result
	#if (cmp(self.devbitInfo,num64) == 0) or (cmp(self.devbitInfo,num642) == 0):
        if (self.devbitInfo.find(num64) != -1) or (self.devbitInfo.find(num642) != -1) or (self.devbitInfo.find(num643) != -1):
            #print "*******************64 bit********************"
            ct = Compare_textset64(self.vmlinuxPath, sysdumpfile)
        else:
            #print "********************32 bit*************************"
            ct = Compare_textset(self.vmlinuxPath, sysdumpfile)
        result += ".Text segment compare result is " + str(ct.run())
        return result
        pass
    
    
    def getAndroidRebootMode(self):
        # get cmdline.log path
        '''
        import os
        path=last_log_path+"*/misc/cmdline.log"
        result = os.popen("ls " + path).read()
        print result
        '''
        fp = FolderParser(self.slogPath,self.devnum)
        files_cmdline = fp.getFilesBy("sysinfo")
        ss_cmd = files_cmdline.split(",")
        for f in ss_cmd:
            if os.path.exists(f):
                fp = open(f.strip())
                content = fp.read()
                fp.close()
                # print "aa"
                # print str(content).strip()
                # print "bb"
                # get the cmdline.log field androidboot.mode
	        # TODO wait for geng.ren androidboot.mode
                rebootmodeindex = str(content).find("androidboot.mode")
                if rebootmodeindex == -1:
                    return  self.startmode_report_tag + "\n" + "no androidboot.mode"
                    # return "norebootmode"
                else:
                    subresult = str(content)[rebootmodeindex:len(content)]
                    subresult = subresult.split(" ")[0]
                    subresult = subresult.split("=")[1]
                    return  self.startmode_report_tag + "\n" + subresult
                    # return subresult
            else:
                print "file  " + f + " is not exist"
                return self.startmode_report_tag + "\n" + "no cmdline.log file"
        pass
    
        '''
            get all content from kernel log contains log keys
        '''
    def getAndroidKernelLogkReport(self):
        result = self.kernel_log_report_tag + "\n";
        fp = FolderParser(self.slogPath,self.devnum)
        print "-----------print get full path-----------"
        fp.printdirs()
        print "-----------print get full files-----------"
        fp.printfiles()
        files_kernel = fp.getFilesBy("kernel")
        print "------------------files_kernel-------------"
        print files_kernel        
        # return "" if not exist problem type
        # files_none = fp.getFilesBy("none")
        # print files_none == ""
        # splite by ","
        ss_kernel = files_kernel.split(",")
        for f in ss_kernel:
            print f
            tl = TextLogparser(self.kernel_log_keys, str(f))
            tl.parser()
            result += tl.getExceptionToString()
            pass
        return result
        
        

    
    def getCheckSysdumpReport(self):
        import os
	#global bit_t
        top_path = self.slogPath
        result = self.sysdump_check_report_tag + "\n"
        # print "log path is " + top_path
        # TODO check if sysdump is download complete
        if platform.system() == "Linux":
            sysdumpfilepath = top_path + "/sysdump/"
        else:
            sysdumpfilepath = top_path + "\\sysdump\\"
        
        res = os.listdir(sysdumpfilepath)
        #print str(res)
        # result = os.popen("ls " + sysdumpfilepath).read()
        # print result
        result += sysdumpfilepath + "\n"
        if len(res) == 0:
            result += "no  sysdump file under " + sysdumpfilepath
        else:
            # print "exist files"
            if len(res) > 3:
                result + str(res)
            else:
                result + str(res)
        if self.sysdumpPath != None:
            res = os.listdir(self.sysdumpPath)
            # result = os.popen("ls " + sysdumpfilepath).read()
            # print result
            result += self.sysdumpPath + "\n"
            if len(res) == 0:
                result += "no  sysdump file under " + self.sysdumpPath
            else:
                # print "exist files"
                if len(res) > 3:
                    result += str(res)
                else:
                    result += str(res)
        return result
        pass
    
    def getSlogCheckReport(self):
        result = self.slog_check_report_tag + "\n";
        lc = LogCheck(self.slogPath,self.devnum)
        result_tmp = lc.check()
        result += "check result " + str(result_tmp[0]) + "\n"
        result += "check detail " + str(result_tmp[1]) + "\n"
        return result;
        pass
    
    def genReport(self):
        printstr("generate report")
        printstr("detail pls refer to the report")
        f = open(self.savePath,'w')
        f.write(self.report_content)
        f.close()
        print "report store in  file " + self.savePath
        pass
###############################################################
##########kernel_panic textlogparser###################
class TextLogparser:
    def __init__(self,keys,log_path,before=5,after=5,checkFirst=False):
        self.keys=keys
        self.kernel_log_path=log_path
        self.exceptionLog={}
        self.checkFirst=checkFirst
        self.before=before
        self.after=after
        self.sp="------------------------------------------------------\n"
	pass
        
    '''
        lines: current line number:record lines before:back to line number end:forward to line number
    '''
    def readScope(self,lines,number=8,before=4,end=4):
        f=open(self.kernel_log_path)
        content=""
        for linenum, line in enumerate(f):
            if linenum >= lines-before and linenum<lines-end+number:
                content+=line
        f.close()
        return content
    
    '''
        add a exception to error store
    '''
    def addException(self,key,value):
        result = self.__getValue(key)
        if result == None:
            result=[]
            #print "first add"
            result.append(value)
            pass
        elif self.checkFirst:
            #print "second add"
            pass
        else:
            #print "normal add"
            result.append(value)
        self.exceptionLog[key]=result
        
    '''
        get key value
    '''
    def __getValue(self,name):
        result = None
        try:
            result = self.exceptionLog[name]
        except:
            #result = []
            #print "no data in self.exceptionLog"
            pass
        return result
        
    def getExceptionToString(self):
        content=""
        for key,value in self.exceptionLog.items():
            content += str(key)+":\n"
            tmpValue=""
            for v in value:
                tmpValue+=self.sp+v+"\n"
            content+=tmpValue
        return content
        pass
        
    
    def getException(self):
        return self.exceptionLog
                
    def parser(self):
        self.f=open(self.kernel_log_path,'r')
        line=0
        while 1:
            text = self.f.readline()
            if( text == '' ):
                #print 'finish'
                break
            elif( text == '\n'):
                #print 'enter'
                pass
            else:
                text = text.strip()
                for key in self.keys:
                    if( text.find(str(key)+"") >= 0):
                        #print "@@@@@@@@@@@@@@@@@@@@@@@@@@@@print kernel_keys*************"
		        #print key
                        #print text
                        #print "here is line " + str(line)
                        result=self.readScope(line,16,4,4)
                        #print result
                        #if self.checkFirst:
                        #self.exceptionLog('key')=result
                        self.addException(key,result)
                        # here record the result to a dict
            line+=1
        print "---------result read--------------"
	#print result
        self.f.close()
            
        pass
##########################################################################
#########kernel_panic getregaccess#####################

class GetRegAccess:

    def __init__(self,vmpath,sysdumpfolder):
        self.sysdumpfolder=sysdumpfolder
        self.vmlinux=vmpath
        self.key_setup_max_cpus=" setup_max_cpus"
        self.setup_max_cpus=""
        self.key_sprd_debug_last_regs_acce="sprd_debug_last_regs_acce"
        self.sprd_debug_last_regs_acce=""
        self.cpucount=1
        self.filesmap={}
        self.fzs=[]
        self.initData()
        self.result=""
        
    def initData(self):
        # check folder
        houzui=self.sysdumpfolder[len(self.sysdumpfolder)-1:len(self.sysdumpfolder)]
        if houzui=="/":
            self.sysdumpfolder=self.sysdumpfolder[0:len(self.sysdumpfolder)-1]
        self.fzs=os.listdir(self.sysdumpfolder)
        # sysdump files
        self.fzs.sort()
        for fz in self.fzs:
            if len(fz)>len('sysdump.core.00')+1 and fz.find("sysdump.core.") != -1:
                self.filesmap[fz]=(fz[fz.find("_")+1:fz.find("-")],fz[fz.find("-")+1:fz.find("_d")])
        print self.filesmap
        pass
        
    def parser(self):
        print "parsering..."+self.vmlinux
        # read symbol table from vmlinux
        try:
            result=os.popen("python readelf.py -s "+self.vmlinux)
        except:
            print "Please install pyelf tool!!!!!!!!!!!!!!!!"
            sys.exit(1)
        # get keys
        for p in result:
            #133213: c09aae30     4 OBJECT  GLOBAL DEFAULT   22 setup_max_cpus
            if str(p).find(" setup_max_cpus")>=0:
                self.setup_max_cpus=str(p)
                print "debug1 "+p
            #130443: c09fdd00     4 OBJECT  GLOBAL DEFAULT   23 sprd_debug_last_regs_acce
            elif str(p).find("sprd_debug_last_regs_acce")>=0:
                self.sprd_debug_last_regs_acce=str(p)
                print "debug2 "+p
        print "parver cpus over"
        if self.setup_max_cpus!="":
            # parser setup_max_cpus and sprd_debug_last_regs_acce
            print "setup_max_cpus" + str(self.setup_max_cpus)
            self.setup_max_cpus=self.setup_max_cpus.strip().split(" ")
            print self.setup_max_cpus
            self.setup_max_cpus_address=self.setup_max_cpus[1][2:len(self.setup_max_cpus[1])]
            self.setup_max_cpus_records=int(self.setup_max_cpus[6])
            
            print "setup_max_cpus_address "+str(self.setup_max_cpus_address)+"\n"+"setup_max_cpus_records "+str(self.setup_max_cpus_records)
        else:
            print "cannot find setup_max_cpus,exit."
            return
	    #sys.exit(1) 
        if self.sprd_debug_last_regs_acce!="":
            print "sprd_debug_last_regs_acce " + str(self.sprd_debug_last_regs_acce)
            self.sprd_debug_last_regs_acce=self.sprd_debug_last_regs_acce.strip().split(" ")
            print self.sprd_debug_last_regs_acce
            self.sprd_debug_last_regs_acce_address=self.sprd_debug_last_regs_acce[1][2:len(self.sprd_debug_last_regs_acce[1])]
            self.sprd_debug_last_regs_acce_records=int(self.sprd_debug_last_regs_acce[6])
            print "sprd_debug_last_regs_acce_address "+str(self.sprd_debug_last_regs_acce_address)+"\n"+"sprd_debug_last_regs_acce_records "+str(self.sprd_debug_last_regs_acce_records)
        else:
            print "cannot find sprd_debug_lase_regs_acce,exit"
            return
	    #sys.exit(1) 
        # get cpus and  sprd_debug_last_regs_acce_address base address
        # get first file
        #fi="sysdump.core.01_0x80000000-0x87ffffff_dump.lst"
        for (ke,v) in self.filesmap.items():
            if ke.find("sysdump.core.01_0x")>=0:
                fi=ke
                break
        fi = self.sysdumpfolder+ os.path.sep + fi
        print fi
        f= open(fi,'rb')
        # get cpu buf
        if self.setup_max_cpus!="":
            print "get setup_max_cpus buf"
            lines=int(self.setup_max_cpus_address,16)
            number=self.setup_max_cpus_records
            print "start addr == " + str(lines)
            print "getlines point == " + str(number)
            f.seek(lines)
            setup_max_cpus_buf=f.read(number)
            # get cpu sprd_debug_last_regs_acce
            print "parser setup_max_cpus"
            s1 = StringIO.StringIO(setup_max_cpus_buf)
            # time stamp
            a1 = struct.unpack("I", s1.read(4))
            print "CPU count=="+str(a1[0])
            self.cpucount=a1[0]
            
        print "parser sprd_debug_last_regs_acce get base address"
        print "get sprd_debug_last_regs_acce buf"
        lines=int(self.sprd_debug_last_regs_acce_address,16)
        number=self.sprd_debug_last_regs_acce_records
        print "start addr == " + str(lines)
        print "getlines point == " + str(number)
        f.seek(lines)
        sprd_debug_last_regs_acce_buf=f.read(number)
        print "buff length is " + str(sprd_debug_last_regs_acce_buf)
        s1 = StringIO.StringIO(sprd_debug_last_regs_acce_buf)
        #print "val=="+s1.getvalue()
        # time stamp update
        a1 = struct.unpack("I", s1.read(4))
        x=a1[0]
        if x == 0:
            print "Address D1 is wrong, exit"
            return	
        print "D1=="+str(hex(x))
        d1=x
        newaddress=0x80004000+(d1>>20)*4
        node=self.getfile(newaddress)
        print "new address in file d1 " + str(node)
        f=open(self.sysdumpfolder+"/"+node[0],'rb')
        try:
            newaddress=newaddress-long(eval(node[1][0]))
        except:
            print "Address D2 is wrong,exit."
            return
	    #sys.exit(1) 
        f.seek(newaddress)
        s1 = StringIO.StringIO(f.read(4))
        # update
        a1 = struct.unpack("I", s1.read(4))
        print "PGD D2=="+hex(a1[0])
        d2=a1[0]
        # read d3
        newaddress=(d2&0xfffff000)+((d1>>12)&0x1ff)*4
        print "new address d3 "+str(hex(newaddress))
        
        node=self.getfile(newaddress)
        print "new address in file d3 " + str(node)
        try:
            newaddress=newaddress-long(eval(node[1][0]))
        except:
            print "Address D3 is wrong,exit."
            return
	    #sys.exit(1)
        f=open(self.sysdumpfolder+"/"+node[0],'rb')
        f.seek(newaddress)
        s1 = StringIO.StringIO(f.read(4))
        a1 = struct.unpack("I", s1.read(4))
        print "PTE d3==" + hex(a1[0])
        d3=a1[0]
        # last steps
        newaddress=(d3&0xfffff000)+(d1&0xfff)
        print "newaddress d4 "+str(hex(newaddress))
        node=self.getfile(newaddress)
        print "new address in file d4 " + str(node)
        try:
            newaddress=newaddress-long(eval(node[1][0]))
        except:
            print "Address D4 is wrong,exit."
            return
	    #sys.exit(1)
        f=open(self.sysdumpfolder+"/"+node[0],'rb')
        f.seek(newaddress)
        s1 = StringIO.StringIO(f.read(24*self.cpucount))
        count=0
        while count<self.cpucount:
            #print "reg index:"+str(count)
            self.result+="reg index:"+str(count) + "\n"
            a1 = struct.unpack("I", s1.read(4))
            self.result+=hex(a1[0])+ "\n"
            #print hex(a1[0])
            a1 = struct.unpack("I", s1.read(4))
            self.result+=hex(a1[0])+ "\n"
            #print hex(a1[0])
            a1 = struct.unpack("I", s1.read(4))
            self.result+=hex(a1[0])+ "\n"
            #print hex(a1[0])
            a1 = struct.unpack("I", s1.read(4))
            self.result+=hex(a1[0])+ "\n"
            #print hex(a1[0])
            a1 = struct.unpack("I", s1.read(4))
            self.result+=hex(a1[0])+ "\n"
            #print hex(a1[0])
            a1 = struct.unpack("I", s1.read(4))
            self.result+=hex(a1[0])+ "\n"
            #print hex(a1[0])
            count+=1
            
    def getResult(self):
        return self.result
        
    def getCpucount(self): 
        return self.cpucount
        
    def getfile(self,address):
        print "search address is " + str(address)
        for (k,v) in self.filesmap.items():
            #print k,v,address
            if hex(address)>v[0] and hex(address)<v[1]:
                #print k
                return (k,v)
        return None

class GetRegAccess64:

    def __init__(self,vmpath,sysdumpfolder):
        self.sysdumpfolder=sysdumpfolder
        self.vmlinux=vmpath
        self.key_setup_max_cpus=" setup_max_cpus"
        self.setup_max_cpus=""
        self.key_sprd_debug_last_regs_acce="sprd_debug_last_regs_acce"
        self.sprd_debug_last_regs_acce=""
        self.cpucount=1
        self.filesmap={}
        self.fzs=[]
        self.initData()
        self.result=""
        
    def initData(self):
        # check folder
        houzui=self.sysdumpfolder[len(self.sysdumpfolder)-1:len(self.sysdumpfolder)-1]
        if houzui=="/":
            self.sysdumpfolder=self.sysdumpfolder[0:len(self.sysdumpfolder)-1]
        self.fzs=os.listdir(self.sysdumpfolder)
        # sysdump files
        self.fzs.sort()
        for fz in self.fzs:
            if len(fz)>len('sysdump.core.00')+1 and fz.find("sysdump.core.") != -1:
                self.filesmap[fz]=(fz[fz.find("_")+1:fz.find("-")],fz[fz.find("-")+1:fz.find("_d")])
        print self.filesmap
        pass
        
    def parser(self):
        print "parsering..."+self.vmlinux
        # read symbol table from vmlinux
        try:
            result=os.popen("python readelf.py -s "+self.vmlinux)
        except:
            print "Please install pyelf tool!!!!!!!!!!!!!!!!"
            sys.exit(1)
        
        print type(result)
        # get keys
        for p in result:
            #133213: c09aae30     4 OBJECT  GLOBAL DEFAULT   22 setup_max_cpus
            if p.find(" setup_max_cpus") >=0:
                self.setup_max_cpus=str(p)
                print "debug1 "+p
            #130443: c09fdd00     4 OBJECT  GLOBAL DEFAULT   23 sprd_debug_last_regs_acce
            elif str(p).find(" sprd_debug_last_regs_acce")>=0:
                self.sprd_debug_last_regs_acce=str(p)
                print "debug2 "+p
        print "parver cpus over"
	#os.system("tools/aarch64-linux-android-nm" +  self.ivmlinux | "grep -E "\<sprd_debug_last_regs_access\>"")




        if self.setup_max_cpus!="":
            # parser setup_max_cpus and sprd_debug_last_regs_acce
            print "setup_max_cpus" + str(self.setup_max_cpus)
            self.setup_max_cpus=self.setup_max_cpus.strip().split(" ")
            print self.setup_max_cpus
            self.setup_max_cpus_address=self.setup_max_cpus[1][10:len(self.setup_max_cpus[1])]
            #self.setup_max_cpus_records=int(self.setup_max_cpus[6])
            
            print "setup_max_cpus_address "+str(self.setup_max_cpus_address)
#	    +"\n"+"setup_max_cpus_records "+str(self.setup_max_cpus_records)
        else:
            print "cannot find setup_max_cpus,exit."
            return

        if self.sprd_debug_last_regs_acce!="":
            print "sprd_debug_last_regs_acce " + str(self.sprd_debug_last_regs_acce)
            self.sprd_debug_last_regs_acce=self.sprd_debug_last_regs_acce.strip().split(" ")
            print self.sprd_debug_last_regs_acce
            self.sprd_debug_last_regs_acce_address=self.sprd_debug_last_regs_acce[1][10:len(self.sprd_debug_last_regs_acce[1])]
#      	    self.sprd_debug_last_regs_acce_address=hex(self.sprd_debug_last_regs_acce_address)&(0xffffffff)
            #self.sprd_debug_last_regs_acce_records=int(self.sprd_debug_last_regs_acce[6])
            print "sprd_debug_last_regs_acce_address "+str(self.sprd_debug_last_regs_acce_address)
#	    +"\n"+"sprd_debug_last_regs_acce_records "+str(self.sprd_debug_last_regs_acce_records)
        else:
            print "cannot find sprd_debug_lase_regs_acce,exit"
            return    
        # get cpus and  sprd_debug_last_regs_acce_address base address
        # get first file
        fi="sysdump.core.01_0x80000000-0x87ffffff_dump.lst"
        for (ke,v) in self.filesmap.items():
            if ke.find("sysdump.core.01_0x")>=0:
                fi=ke
                break
        # 
        fi = self.sysdumpfolder+"/"+fi
        print fi
        f= open(fi,'rb')
        # get cpu buf
        if self.setup_max_cpus!="":
            print "get setup_max_cpus buf"
            lines=int(self.setup_max_cpus_address,16)
            #number=self.setup_max_cpus_records
            print "start addr == " + str(lines)
            #print "getlines point == " + str(number)
            f.seek(lines)
            setup_max_cpus_buf=f.read(4)
            # get cpu sprd_debug_last_regs_acce
            print "parser setup_max_cpus"
            s1 = StringIO.StringIO(setup_max_cpus_buf)
            # time stamp
            a1 = struct.unpack("I", s1.read(4))
            print "CPU count=="+str(a1[0])
            self.cpucount=a1[0]
            i = 0
            
        print "parser sprd_debug_last_regs_acce get base address"
        print "get sprd_debug_last_regs_acce buf"
        print type(self.sprd_debug_last_regs_acce_address)
#	self.sprd_debug_last_regs_acce_address=self.sprd_debug_last_regs_acce_address&ffffffff
#       print "sprd_debug_last_regs_acce_address "+str(self.sprd_debug_last_regs_acce_address)
        lines=int(self.sprd_debug_last_regs_acce_address,16)
#        number=self.sprd_debug_last_regs_acce_records
        print "start addr == " + str(lines)
#        print "getlines point == " + str(number)
        f.seek(lines)
        sprd_debug_last_regs_acce_buf=f.read(8)
        print "buff length is " + str(sprd_debug_last_regs_acce_buf)
        s1 = StringIO.StringIO(sprd_debug_last_regs_acce_buf)
        #print "val=="+s1.getvalue()
        # time stamp update
        a1 = struct.unpack("Q", s1.read(8))
        x=a1[0]
        x=x&0xffffffff
        if x == 0:
            print "Address D1 is wrong, exit"
            return	
        print "D1=="+str(x)
        actualaddr=(0x80000000&0xffffffff)+x
        print actualaddr
        node=self.getfile(actualaddr)
        print "node" +str(node)
        try:
            addr2=actualaddr-long(eval(node[1][0]))
        except:
            print "Address is wrong,exit."
            return
	    #sys.exit(1)
	#print addr2
        f=open(self.sysdumpfolder+"/"+node[0],'rb')
#	lines=int(addr2,16)
#	print "************read addr*******" +str(lines)
        f.seek(0,2)
        f_tell=f.tell()
        f.seek(addr2)
        f_tell=f.tell()
	#self.cpucount=8
        s1 = StringIO.StringIO(f.read(40*self.cpucount))
	#s1 = StringIO.StringIO(f.read(40*8))
        count=0
        while count<self.cpucount:
            #print "reg index:"+str(count)
            self.result+="reg index:"+str(count) + "\n"
            a1 = struct.unpack("Q", s1.read(8))
            self.result+=hex(a1[0])+ "\n"
            print hex(a1[0])
            a1 = struct.unpack("Q", s1.read(8))
            self.result+=hex(a1[0])+ "\n"
            #print hex(a1[0])
            a1 = struct.unpack("Q", s1.read(8))
            self.result+=hex(a1[0])+ "\n"
            #print hex(a1[0])
            a1 = struct.unpack("Q", s1.read(8))
            self.result+=hex(a1[0])+ "\n"
            #print hex(a1[0])
            a1 = struct.unpack("I", s1.read(4))
            self.result+=hex(a1[0])+ "\n"
            #print hex(a1[0])
            a1 = struct.unpack("I", s1.read(4))
            self.result+=hex(a1[0])+ "\n"
            #print hex(a1[0])
            count+=1
            
    def getResult(self):
        return self.result
        
    def getCpucount(self): 
        return self.cpucount
        
    def getfile(self,address):
        print "search address is " + str(address)
        for (k,v) in self.filesmap.items():
            #print k,v,address
            if hex(address)>v[0] and hex(address)<v[1]:
                #print k
                return (k,v)
        return None
        
##############################################################3
###########kernel_panic kernelparser###################3
class KernelLogParser:
    def __init__(self,vmpath,dumppath,devbit,savelocation):
        self.vmpath=vmpath
        self.dumppath=os.path.dirname(dumppath)
        self.dumpfile = self.dumppath + os.path.sep + "dump"
        self.devbit = devbit
        self.savelocation=savelocation
        if not os.path.isdir(self.savelocation):
            os.makedirs(self.savelocation)
        pass
        if (self.devbit.find("9850") != -1 or self.devbit.find("9860") != -1) and self.devbit.find("9850ka") < 0:
	    self.tool = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(self.vmpath)))))) + os.path.sep + "tools" + os.path.sep + "crash64"
        elif self.devbit.find("9861") != -1:
	    self.tool = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(self.vmpath)))))) + os.path.sep + "tools" + os.path.sep + "crash64_2"
        else:
            self.tool = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(self.vmpath)))))) + os.path.sep + "tools" + os.path.sep + "crash32"
        print self.vmpath
        print self.tool
    def parser(self):
        overw_flag = False
        os.system("cat %s/sysdump.core.0* >%s" %(self.dumppath,self.dumpfile))	
        print "parser vmlinux"
        if (self.devbit.find("9850") != -1 or self.devbit.find("9860") != -1) and self.devbit.find("9850ka") < 0:
            cmd = "%s -m phys_offset=0x80000000 %s %s" %(self.tool,self.dumpfile,self.vmpath)
        elif self.devbit.find("9861") != -1:
            cmd = "%s -m phys_base=0x34200000 %s %s --cpus 8" %(self.tool,self.dumpfile,self.vmpath)
        else:
            cmd = "%s -m phys_base=0x80000000 %s %s" %(self.tool,self.dumpfile,self.vmpath)
        print cmd 
        child = pexpect.spawn(cmd)
        if (self.devbit.find("9850") != -1 or self.devbit.find("9860") != -1) and self.devbit.find("9850ka") < 0:
            child.expect("crash64>")
        elif self.devbit.find("9861") != -1:
            child.expect("crash64_2>")
        else:
            child.expect("crash32>")
        #crash = child.expect('erin')
        #child.expect(cmdline)
        print "crashhhhhhhhhhhhhhhhhhhhhh"
        #print crash
        #fout = open (self.savelocation + "kernel_log.log", "w")
        kernel_log = self.savelocation + "kernel_log.log"
        #########time.sleep(30)
        #cmd1 = "log >%s" %kernel_log
        cmd1 = "log > %s" %kernel_log
        print cmd1 
        #child.sendline("log > kernel_log.txt")
        child.sendline(cmd1)
        child.sendline("q")
        time.sleep(2)
        child.close(force=True)
        print self.dumpfile
        os.system("rm %s" %self.dumpfile)
        kernelpath=self.savelocation+'kernel_log.log'
        oopspath=self.savelocation+'kernel_Oops.log'
        
        return kernelpath,oopspath
        

###########################################################       
#########kernel_panic compare_text#################
class Compare_textset:
    def __init__(self, vmpath, sysdump):
        self.vmpath = vmpath
        self.systemdump = sysdump
        self.hasdiff = False
        self.diffcontent = ""
        self.skipcount = 0
        
    def run(self):
        if isLinux():
            os.system("tools/arm-linux-gnueabihf-objcopy --only-section .text " + self.vmpath + " -O binary vmlinux_text.bin")
        else:
            os.system("tools\\arm-elf-objcopy.exe  --only-section .text " + self.vmpath + " -O binary vmlinux_text.bin")
        print "extract .text from vmlinx over"
        try:
            result = os.popen("python readelf.py -S " + self.vmpath)
        except:
            print "Please install pyelf tool!!!!!!!!!!!!!!!!!!"
            sys.exit(1)
        startaddress = None
        readsize = None
        for p in result:
            if p.find(" .text") >= 0:
                print ".text segment " + p
                i = p.find("PROGBITS")
                re = p[i:len(p)].split(" ")
                startaddress = '0x' + re[9]
                readsize = '0x' + re[10]
                break
        result.close()
        print "parser skipaddress"
        result = os.popen("python readelf.py -s " + self.vmpath)
        skipaddress = None
        for p in result:
            if p.find("__v7_setup_stack") >= 0:
                print p
                tt = p.strip().split(" ")[1]
                if tt.find("c") == 0:
                    skipaddress = '0x' + tt[1:len(p) - 1]
                else:
                    skipaddress = '0x' + tt
                skipaddress = eval(skipaddress) - eval(startaddress)
                '''
                i=p.find("v7_setup_stack")
                re=p[i:len(p)].split(" ")
                startaddress='0x'+re[9]
                readsize='0x'+re[10]
                break
                '''
        print "startaddress  readsize  skipaddress"
        print startaddress, readsize, skipaddress
        skipaddress = str(hex(skipaddress))
        f = open(self.systemdump, 'rb')
        f.seek(eval(startaddress))
        buf = f.read(eval(readsize))
        f.close()
        f = open('textfromsystemdump', 'wb')
        f.write(buf)
        f.close()
        # check the if size is the same 
        totalsize = 0
        # compare file size 
        if os.path.getsize('vmlinux_text.bin') == os.path.getsize('textfromsystemdump'):
            print "size is the same ,size==" + str(os.path.getsize('vmlinux_text.bin'))
            totalsize = os.path.getsize('vmlinux_text.bin')

        # rewrite file and filter
        fvm = open('vmlinux_text.bin', 'rb')
        fsys = open('textfromsystemdump', 'rb')
        # 0xE8BD4000
        # store final common seg
        fvmfile = open("fvmfile.bin", 'wb')
        fsysfile = open("fsysfile.bin", 'wb')
        skipaddressstatic = 0xE8BD4000
        
        buf1 = fvm.read(eval(skipaddress))
        fvm.read(44)
        buf2 = fvm.read(eval(readsize) - eval(skipaddress) - 44)
        fvm.close()
        
        fvm_new = open('vmlinux_text_new.bin', 'wb')
        fvm_new.write(buf1)
        fvm_new.write(buf2)
        fvm_new.close()
        
        fsys_new = open('textfromsystemdump_new.bin', 'wb')
        buf1 = fsys.read(eval(skipaddress))
        fsys.read(44)
        buf2 = fsys.read(eval(readsize) - eval(skipaddress) - 44)
        fsys_new.write(buf1)
        fsys_new.write(buf2)
        fsys_new.close()
        fsys.close()
        fsys_new = open('textfromsystemdump_new.bin', 'rb')
        fvm_new = open('vmlinux_text_new.bin', 'rb')           
        # compare
        count = 0
        passcount = 0
        return_result = "diffexist\n"
        while count < totalsize - 44:
        
            buf1 = fvm_new.read(4)
            a1 = struct.unpack("I", buf1)
            # print a1[0]
            # fvm.read(4)
            buf2 = fsys_new.read(4)
            a2 = struct.unpack("I", buf2)
            # skip if
            if skipaddressstatic == a1[0] or a2[0] == skipaddressstatic:
                pass
            else:
                fvmfile.write(buf1)
                fsysfile.write(buf2)
                if a1 == a2:
                    # print "same"
                    passcount += 1
                    pass
                else:
                    self.hasdiff = True
                    diffcontent = hex(a1[0]) + ":" + hex(a2[0])
                    print "diffexist", hex(a1[0]), hex(a2[0])
                    return_result += str(diffcontent)
                    return_result += "\n"
            count += 4
                
        fsys_new.close()
        fvm_new.close()
        fvmfile.close()
        fsysfile.close()

        # print "passcount==" + str(passcount)
        # juest write a report
        if not self.hasdiff:
            # print ".text sagment is the same"
            return True
            pass
            
        else:
            return return_result
            pass


class Compare_textset64:
    def __init__(self, vmpath, sysdump):
        self.vmpath = vmpath
        self.systemdump = sysdump
        self.hasdiff = False
        self.diffcontent = ""
        self.skipcount = 0
        
    def run(self):
        if isLinux():
#           os.system("tools/arm-linux-gnueabihf-objcopy --only-section .text " + self.vmpath + " -O binary vmlinux_text.bin")
            os.system("tools/aarch64-linux-gnu-objcopy --only-section .text " + self.vmpath + " -O binary vmlinux_text.bin")

        else:
            os.system("tools\\aarch64-linux-gnu-objcopy.exe --only-section .text " + self.vmpath + " -O binary vmlinux_text.bin")
        print "extract .text from vmlinx over"
        result = os.popen("python readelf.py -S " + self.vmpath)
        startaddress = None
        readsize = None
        for p in result:
            if p.find(".text") >= 0:
                print ".text segment " + p
                i = p.find("PROGBITS")
                print i
                re = p[i:len(p)].split(" ")
                print re
                startaddress = '0x' + re[9][8:len(re)]
                readsize = '0x' + re[11]
                break
            if str(p).find(" setup_max_cpus")>=0:
                print "parser is OK"
        result.close()
                # strip().split(" ")
        # get skip seg
        # in vmlinux search symbol:__v7_setup_stack
        #  c06516b0     0 NOTYPE  LOCAL  DEFAULT    2 __v7_setup_stack
        # python readelf.py -s vmlinux | grep v7_setup_stack
        print "parser skipaddress"
#        result = os.popen("tools/aarch64-linux-gnu-nm " + self.vmpath)
        result = os.popen("python readelf.py -s " + self.vmpath)
        skipaddress = None
        for p in result:
#           if p.find("__v7_setup_stack") >= 0:
            if p.find("handle_arch_irq") >= 0:
                print p
                tt = p.strip().split(" ")[1]
                if tt.find("c") != 0:
                    skipaddress = '0x' + tt[8:len(p)]
                else:
                    skipaddress = '0x' + tt
                print "skipaddress" +str(skipaddress)
                skipaddress = eval(skipaddress) - eval(startaddress)
                '''
                i=p.find("v7_setup_stack")
                re=p[i:len(p)].split(" ")
                startaddress='0x'+re[9]
                readsize='0x'+re[10]
                break
                '''
        print "startaddress  readsize  skipaddress"
        print startaddress, readsize, skipaddress
        skipaddress = str(hex(skipaddress))
        f = open(self.systemdump, 'rb')
        f.seek(eval(startaddress))
        buf = f.read(eval(readsize))
        f.close()
        f = open('textfromsystemdump', 'wb')
        f.write(buf)
        f.close()
        # check the if size is the same 
        totalsize = 0
        # compare file size 
        if os.path.getsize('vmlinux_text.bin') == os.path.getsize('textfromsystemdump'):
            print "size is the same ,size==" + str(os.path.getsize('vmlinux_text.bin'))
            totalsize = os.path.getsize('vmlinux_text.bin')

        # rewrite file and filter
        fvm = open('vmlinux_text.bin', 'rb')
        fsys = open('textfromsystemdump', 'rb')
        # 0xE8BD4000
        # store final common seg
        fvmfile = open("fvmfile.bin", 'wb')
        fsysfile = open("fsysfile.bin", 'wb')
#	32 64bit is different	
#       skipaddressstatic = 0xE8BD4000
        skipaddressstatic = 0xD503201F
        
        buf1 = fvm.read(eval(skipaddress))
        fvm.read(64)
        buf2 = fvm.read(eval(readsize) - eval(skipaddress) - 64)
        fvm.close()
        
        fvm_new = open('vmlinux_text_new.bin', 'wb')
        fvm_new.write(buf1)
        fvm_new.write(buf2)
        fvm_new.close()
        
        fsys_new = open('textfromsystemdump_new.bin', 'wb')
        buf1 = fsys.read(eval(skipaddress))
        fsys.read(64)
        buf2 = fsys.read(eval(readsize) - eval(skipaddress) - 64)
        fsys_new.write(buf1)
        fsys_new.write(buf2)
        fsys_new.close()
        fsys.close()
        fsys_new = open('textfromsystemdump_new.bin', 'rb')
        fvm_new = open('vmlinux_text_new.bin', 'rb')           
        # compare
        count = 0
        passcount = 0
        return_result = "diffexist\n"
        while count < totalsize - 64:
        
            buf1 = fvm_new.read(4)
            a1 = struct.unpack("I", buf1)
            # print a1[0]
            # fvm.read(4)
            buf2 = fsys_new.read(4)
            a2 = struct.unpack("I", buf2)
            # skip if
            if skipaddressstatic == a1[0] or a2[0] == skipaddressstatic:
                pass
            else:
                fvmfile.write(buf1)
                fsysfile.write(buf2)
                if a1 == a2:
                    # print "same"
                    passcount += 1
                    pass
                else:
                    self.hasdiff = True
                    diffcontent = hex(a1[0]) + ":" + hex(a2[0])
                    print "diffexist", hex(a1[0]), hex(a2[0])
                    return_result += str(diffcontent)
                    return_result += "\n"
            count += 4
                
        fsys_new.close()
        fvm_new.close()
        fvmfile.close()
        fsysfile.close()

        # print "passcount==" + str(passcount)
        # juest write a report
        if not self.hasdiff:
            # print ".text sagment is the same"
            return True
            pass
            
        else:
            return False
            pass

###############################################################
#####filesort#########################

class FileSort(object):

    def __init__(self,filelist):
	
        self.filelist = filelist
        self.filelist_date = []
        self.filelist_last = []
        self.filelist_inter = []

    def fsort(self):
	
        for ff in self.filelist:
            if ff.find("internal_storage") != -1:
                self.filelist_inter.append(ff)
            elif ff.find("last_ylog") != -1:
                self.filelist_last.append(ff)
            else:
                self.filelist_date.append(ff)

        self.filelist_date.sort()
        self.filelist_last.sort()
        self.filelist_inter.sort()

        filelist_sort = []	
        for ff in self.filelist_date:
            print ff
            filelist_sort.append(ff)
        for ff in self.filelist_inter:	
            print ff
            filelist_sort.append(ff)
        for ff in self.filelist_last:
            print ff
            filelist_sort.append(ff)
        filelist_sort.reverse()
        return filelist_sort

####################################################################
'''
java_crash_regex = re.compile(r'java_crash_log')
native_crash_time_get_regex = re.compile(r'native_crash_occur_time:\s*(.*)')
native_crash_module_get_regex = re.compile(r'native_crash_module:\s*(.*)')
native_crash_process_get_regex = re.compile(r'native_crash_process:\s*(.*)')
watchdog_crash_time_get_regex = re.compile(r'watchdog_crash_occur_time:\s*(.*)')
watchdog_crash_module_get_regex = re.compile(r'watchdog_crash_module:\s*(.*)')
java_crash_time_get_regex = re.compile(r'java_crash_occur_time:\s*(.*)')
java_crash_module_get_regex = re.compile(r'java_crash_module:\s*(.*)')
java_crash_thread_get_regex = re.compile(r'java_crash_thread:\s*(.*)')
kernel_crash_regex = re.compile(r'PC is at\s*(\w+)')
kernel_crash_time_regex = re.compile(r'\s*(\d+)')
debug = True
'''
##################################################################################
###########generate_final_report_related###########################

'''
def slog_begin_time(slog_p):
    
    begin_time = 0    
    fp = FolderParser(slog_p,"111")
    inputfile = fp.getFilesBy('begin')
    inputfile = inputfile.split(",") 
    sp = FileSort(inputfile)
    inputfile = sp.fsort()
    firstfile = inputfile[0]
    ff = open(firstfile)
    line = ff.readline()
    while line:
        if line[0] >= '0' and line[0] <= '9':
	    line = line.split(" ")
	    begin_time = line[0] + "_" + line[1].split(".")[0]
	    break
	line = ff.readline()
    return begin_time
'''	

def get_product(devf):
    product = get_build_host()
    try:
        product = product.split('/')[5]
        return product
    except:
        pass
    
    #product:sprdroid5.1_trunk_SharkLT8

def get_base_version(fingf):

    build_finger_regex = re.compile(r'ro.build.fingerprint')
    dev_file = None
    b_version = None
    if fingf:
        fd = open(fingf)
        line = fd.readline()
        while line:
            if build_finger_regex.search(line):
                pattern = r"(\[.*?\])"
                line = re.findall(pattern,line,re.M)
                if (len(line)>1):
                    line = line[1]
                    b_version = line.replace('[','').replace(']','')
                    location = b_version.find('/')
                    b_version = b_version[location+1:-1]
                break
            line = fd.readline()
    if b_version:
        #print b_version
        return b_version
    #sp9838aea_oversea/scx35l64_sp9838aea_5mod:5.1/LMY47D-W15.24.2-01:userdebug/test-key

def get_hw_version(dev_file):

    hw_version_regex = re.compile(r'ro.product.hardware')
    b_version = None
    hw_version = None
    if dev_file:
        fd = open(dev_file)
        line = fd.readline()
        while line:
            if hw_version_regex.search(line):
                pattern = r"(\[.*?\])"
                line = re.findall(pattern,line,re.M)
                if (len(line)>1):
                    line = line[1]
                    hw_version = line.replace('[','').replace(']','')
                break
            line = fd.readline()
    if hw_version:
        #print hw_version
        return hw_version
    #pass
    #[ro.product.hardware]: [SP9838A-1_V1.0.0(5M)]


def get_version_pac(devicef,fingerf):
    #b_host = get_build_host(devicef)
    b_host = ""
    b_host = get_build_host()
    b_host = b_host + "artifact/PAC/"
    d_mode = ""
    d_mode = get_device_mode()
    ss= get_base_version(fingerf)
    location = ss.rfind(':')
    ss = ss[location+1:]
    ss = ss.split('/')[0]
    pac = b_host + d_mode + "_" + ss + "-native"
    #print pac
    return pac


def get_logcheck(logpath,pp):
    checkresult = os.path.dirname(logpath) + os.path.sep + "checklogresult.txt"
    if os.path.exists(checkresult):
        try:
            ckp = open(checkresult)
        except:
            print "open checkresult error."
            return 0
        line = ckp.readline()
        flage = False
        while line:
            if line.find("skiped") != -1:
                flage = True
                pp.write(line)
            line = ckp.readline()
        if not flage:
            pp.write("Log check PASS.\n\n")
        else:
            pp.write("\n")
        ckp.close() 
                
           
def get_serverp(logpath,pp):
    baset = logpath.split(os.path.sep)
    base = baset[-2] + os.path.sep + baset[-1]
    serverp = "erin.liu@10.0.64.46:~/log_postprocess/log_postprocess_5.0.5/logs/" + base
    pp.write("Log path in server: %s\n" %serverp)
    pp.write("Password:PSD#sciuser\n")



def get_basic_info(logpath,pp):
    deviceinfo = logpath + os.path.sep + "sysprop.txt"
    fingerinfo = logpath + os.path.sep + "ro.build.fingerprint.txt"
    product = ""
    base_version = ""
    hardware_version = ""
    version_pac = ""

    if os.path.exists(deviceinfo):
        product = get_product(deviceinfo)
        pp.write("Product name: %s\n" %product)
        hardware_version = get_hw_version(deviceinfo)
        pp.write("Hardware version: %s\n" %hardware_version)
    if os.path.exists(fingerinfo):
        base_version = get_base_version(fingerinfo)
        pp.write("Base version: %s\n" %base_version)
    
    if os.path.exists(deviceinfo) and os.path.exists(fingerinfo):
        version_pac = get_version_pac(deviceinfo,fingerinfo)	
        pp.write("Version pac: %s\n\n" %version_pac)

def walkpath(log_path):
    global kernel_panic
    kernel_panic = False
    
    problem_file = []
    for p,d,f in os.walk(log_path):
        for file_list in f:
            if file_list.find("kernel_log.log") != -1:
                problem_file.append(os.path.join(p,file_list))
                kernel_panic = True
		#break
            if file_list.find("watchdog_list.txt") != -1:
                problem_file.append(os.path.join(p,file_list))
            if file_list.find("java_crash_list.txt") != -1:
                problem_file.append(os.path.join(p,file_list))
            if file_list.find("native_crash_list.txt") != -1:
                problem_file.append(os.path.join(p,file_list))
            if file_list.find("lowpower_list.txt") != -1:
                problem_file.append(os.path.join(p,file_list))
            if file_list.find("kmemleak_list.txt") != -1:
                problem_file.append(os.path.join(p,file_list))
            if file_list.find("anrpidlist.txt") != -1:
                problem_file.append(os.path.join(p,file_list))
        for dir_list in d:
            dirlist = None
            dirlist = os.listdir(os.path.join(p,dir_list))
            if dirlist:
                pass
            else:
                shutil.rmtree(os.path.join(p,dir_list))
    return problem_file

def get_probleminfo(ll,pro):
    for pp in pro.keys():
	
        if isinstance(pp,tuple):
            if ll.find(pp[0]) != -1 and ll.find(pp[1]) != -1:
                return (pp,pro[pp])
        else:
            if ll.find(pp) != -1:
                return (pp,pro[pp])
    return 0

def generate_final_report(finalf,plist,repol):

    javacrash_regex = re.compile("am_crash")
    nativecrash_regex = re.compile(r'pid: [0-9]+, tid: [0-9]+,\s*name:\s*(.*)\s*>>>\s*(.*)\s*<<<')
    watchdog1_regex = re.compile("WATCHDOG KILLING SYSTEM PROCESS")
    watchdog2_regex = re.compile("Subject:")
    pl = open(repol)
    line = pl.readline()
    while line:
        next_flag = False
        length = False
        if line.find("file: ") != -1:
            linefile = line
            print linefile
            line = pl.readline()
            print line
            if line.find("file: ") != -1 or line.find("--------------") != -1:
                continue
            while line:
                next_p = False 
                if len(plist) >0:
                    flag = get_probleminfo(line,plist)
                    if flag != 0:
			#plist.remove(flag)	
                        del plist[flag[0]]	
                        finalf.write("\n")
                        if isinstance(flag[0],tuple):
                            finalf.write(str(flag[0][0]) + " " + str(flag[0][1]) + " crash " + str(flag[1]) + " times.\n")
                        else:
                            finalf.write(str(flag[0].strip()) + " " + " crash " + str(flag[1]) + " times.\n")
                        finalf.write(linefile)
                        while line:
                            finalf.write(line)
                            line = pl.readline()
                            if line.find("file: ") != -1 or line.find("--------------") != -1:
                                next_flag = True
                                break
			    #if line.find("am_crash") != -1 or line.find("pid:") != -1 or line.find("Subject:") != -1:
                            if javacrash_regex.search(line) or nativecrash_regex.search(line) or watchdog1_regex.search(line) or watchdog2_regex.search(line):
                                next_p = True
                                break
                    else:
                        line = pl.readline()
                        if line.find("file: ") != -1 or line.find("--------------") != -1:
                            next_flag = True
                        if line.find("am_crash") != -1 or line.find("pid:") != -1 or line.find("Subject:") != -1:
                            next_p = True
                    if next_p:
                        continue
                    if next_flag:
                        break
                else:
                    length = True
                    break
		    
        if next_flag:
            continue
        if length:
            break
        line = pl.readline()
    pl.close()

def generate_final_report2(finalf,plist,repol):

    
    watchdog3_regex = re.compile("tid=")
    watchdog_crash1_regex = re.compile(r'waiting')
    watchdog_crash_get_regex = re.compile(r'\((.*?)\)')
    pl = open(repol)
    line = pl.readline()
    while line:
	#next_flag = False
        length = False
        if line.find("file: ") != -1:
            linefile = line
            tmp_p = pl.tell()
            line = pl.readline()
            if line.find("file: ") != -1 or line.find("--------------") != -1:
                continue
            while line:
                next_flag = False
                if watchdog3_regex.search(line):
                    pp = tmp_p
                    line = pl.readline()
                    while line:
                        next_p = False
                        if watchdog_crash1_regex.search(line):
                            tmp = watchdog_crash_get_regex.search(line)
                            if tmp:
                                tmp = tmp.groups()[0].split('.')[-1] 
                                if len(plist) >0:
                                    flag = get_probleminfo(tmp,plist)
                                    if flag != 0:
                                        del plist[flag[0]]	
                                        finalf.write("\n")
                                        finalf.write(str(flag[0].strip()) + " " + " crash " + str(flag[1]) + " times.\n")
                                        finalf.write(linefile)
                                        pl.seek(pp)
                                        line = pl.readline()
                                        while line:
                                            finalf.write(line)
                                            line = pl.readline()
                                            if line.find("file: ") != -1 or line.find("--------------") != -1:
                                                next_flag = True
                                                break
                                            if watchdog3_regex.search(line):
                                                next_p = True
                                                break
                        if line.find("file: ") != -1 or line.find("--------------") != -1:
                            next_flag = True
                            break
                        if line.find("tid=") != -1:
                            next_p = True
                            break
                        line = pl.readline()
                    if next_p:
                        continue
                if next_flag:
                    break
                tmp_p = pl.tell()
                line = pl.readline()   
        line = pl.readline() 
    pl.close()


			
		    
def convert(sec):
    try:
        sec = sec.split('.')[0]
        sec = int(sec)
        hours = sec/3600
        minutes = sec/60 - sec/3600*60
        seconds = sec - sec/60*60
        time = str(hours) + ":" +str(minutes) + ":" +str(seconds)
        return time
    except:
        pass


def kernel_panic_abstr(kernel_t,fp_out):

    kernel_panic_regex = re.compile(r'PC is at')
    kernel_bug_regex = re.compile(r'BUG:\s+failure at')
    kernel_panic_IO_regex = re.compile(r'last reg access result')
    kernel_panic_IO_end_regex = re.compile(r'cpu count')
    kernel_panic_compare_regex = re.compile(r'text statement compare result')
    kernel_panic_reg_regex = re.compile(r'reg index:')
    kernel_warning_regex = re.compile(r'WARNING:')
    kernel_panic_Panic_regex = re.compile(r'Kernel Panic')
    kernel_panic_panic_regex = re.compile(r'Kernel panic')
    kernel_panic_oops_regex = re.compile(r'Kernel Oops')
    kernel_panic_bug_regex = re.compile(r'Kernel BUG')
    kernel_emmc_regex = re.compile(r'REGISTER DUMP')
    fp = open(kernel_t,'r')
    line = fp.readline()
    warningf = os.path.dirname(kernel_t) + os.path.sep + "warning.txt"
    emmcf = os.path.dirname(kernel_t) + os.path.sep + "emmc.txt"
    fp_out.write("Kernel crash:\n")
    kernel_crash_time = None
    kernel_crash_module = None
    while line:
        if kernel_panic_regex.search(line) or kernel_bug_regex.search(line):
        #if kernel_panic_regex.search(line):
            line_ori = line
            kernel_crash_module = line.split(' ')[-1].strip()
            pattern = r"(\[.*?\])"
            line = re.findall(pattern,line,re.M)
            if (len(line)>0):
                line = line[0]
                kernel_crash_time = line.replace('[','').replace(']','').replace(' ','')
                kernel_crash_time = convert(kernel_crash_time)
                break
        line = fp.readline()
    fp_out.write("Kernel crash module: %s\n" % kernel_crash_module)
    fp_out.write("kernel crash time: %s\n" % kernel_crash_time)
    #fp_out.write("***********************kernel_panic_log*******************\n")
    #fp_out.write("Kernel crash log:\n")
    fp.seek(0)
    line = fp.readline()
    f_flag = False
    pc_flag = False
    while line:
        if line.find(" cut here ") != -1:
            cut_line = line
	    #fp_out.write(line)
            line = fp.readline()
            while line:
                if kernel_warning_regex.search(line):
                    wp = open(warningf,'a+')	
                    wp.write("file: %s\n" %kernel_t)
                    wp.write(cut_line)
                    i = 0
                    while line and i < 30:
			#fp_out.write(line)
                        wp.write(line)
                        i += 1
                        line = fp.readline()
                        if line.find(" end trace ") != -1:
			    #fp_out.write(line)
                            wp.write(line)
                            wp.write("\n")
                            break
                    wp.close()
                if kernel_panic_Panic_regex.search(line) or kernel_panic_panic_regex.search(line) or kernel_panic_oops_regex.search(line) or kernel_panic_bug_regex.search(line):
                    i = 0
                    f_flag = True
                    print line
                    while line and i < 30:
                        if kernel_panic_regex.search(line):
                            pc_flag = True
                        fp_out.write(line)
                        i += 1
                        line = fp.readline()
                        if line.find(" end trace ") != -1:
                            fp_out.write(line)
                            break
                    break
                if line.find(" end trace ") != -1:
                    break
                line = fp.readline()	

        line = fp.readline()
    if not f_flag:
        fp.seek(0)
        line = fp.readline()
        while line:
            if kernel_panic_Panic_regex.search(line) or kernel_panic_panic_regex.search(line) or kernel_panic_oops_regex.search(line) or kernel_panic_bug_regex.search(line) or line.find("Unable to handle kernel") != -1 or line.find("Modules linked in") != -1:
                print line
                f_flag = True
                i = 0
                while line and i < 30:
                    if kernel_panic_regex.search(line):
                        pc_flag = True
                    fp_out.write(line)
                    i += 1
                    line = fp.readline()
                break
            if kernel_warning_regex.search(line):
                wp = open(warningf,'a+')	
                wp.write("file: %s\n" %kernel_t)
                i = 0
                wp.write("\n")
                while line and i < 30:
	            #fp_out.write(line)
                    wp.write(line)
                    i += 1
                    line = fp.readline()
                    if line.find(" end trace ") != -1:
		        #fp_out.write(line)
                        wp.write(line)
                        wp.write("\n")
                        break
                wp.close()
		    
            line = fp.readline()

    if not f_flag:
        fp.seek(0)
        line = fp.readline()
        while line:
            if kernel_panic_panic_regex.search(line) or kernel_panic_oops_regex.search(line) or kernel_panic_bug_regex.search(line):
                print line
                f_flag = True
                i = 0
                while line and i < 30:
                    if kernel_panic_regex.search(line):
                        pc_flag = True
                    fp_out.write(line)
                    i += 1
                    line = fp.readline()
                break
            line = fp.readline()

    if not f_flag:
        fp.seek(0)
        line = fp.readline()
        while line:
            if line.find("Internal error") != -1 or line.find("Modules linked") != -1:
                print line
                f_flag = True
                i = 0
                while line and i < 30:
                    if kernel_panic_regex.search(line):
                        pc_flag = True
                    fp_out.write(line)
                    i += 1
                    line = fp.readline()
                break
            line = fp.readline()
		
    if not pc_flag:
        fp.seek(0)
        line = fp.readline()
        while line:
            if kernel_panic_regex.search(line):
                f_flag = True
                i = 0
                while line and i < 30:
                    fp_out.write(line)
                    i += 1
                    line = fp.readline()
                break
            line = fp.readline()

    if not pc_flag:
        fp.seek(0)
        tmptp = fp.tell()
        line = fp.readline()
        tracep = []
        while line:
            if line.find("Call trace") != -1:
                tracep.append(tmptp)
            line = fp.readline()
            tmptp = fp.tell()
        print tracep
        try:
            fp.seek(tracep[-3])    
            line = fp.readline()
            i = 0
            while line and i < 30:
                fp_out.write(line)
                i += 1
                line = fp.readline()
            pc_flag = true
        except:
            pass

    if not pc_flag:
        fp_out.write("please refer to %s" %kernel_t)

    fp.seek(0)
    line = fp.readline()

    ef = open(emmcf,"a+")
  
    while line:
        next_e = False
        if kernel_emmc_regex.search(line):
            ef.write(line)
            line = fp.readline()
            while line:
                if line.find("=================") != -1:
                    break
                if kernel_emmc_regex.search(line):
                    next_e = True
                    break
                ef.write(line)
                line = fp.readline()
        if next_e:
            continue
        line = fp.readline()
    ef.close()
    fp.close()


def generate_list(slog_base_p):


    javacrash_regex = re.compile("am_crash")
    nativecrash_regex = re.compile(r'pid: [0-9]+, tid: [0-9]+,\s*name:\s*(.*)\s*>>>\s*(.*)\s*<<<')
    nativecrash_system_server_regex = re.compile(r'pid: [0-9]+, tid: [0-9]+,\s*name:\s*(.*)\s*>>>\s*system_server\s*<<<')
    nativecrash_signal_regex = re.compile(r'signal\s*\d+')
    watchdog1_regex = re.compile("WATCHDOG KILLING SYSTEM PROCESS")
    watchdog2_regex = re.compile("Subject:")
    watchdog3_regex = re.compile("tid=")
    watchdog1_module_regex = re.compile("\s*Blocked in monitor\s*(.*) on")
    watchdog_crash1_regex = re.compile(r'waiting')
    watchdog_crash_get_regex = re.compile(r'\((.*?)\)')
    anr_regex = re.compile("happend anr")
    crash_time_regex = re.compile(r'\s*crash\s*\w+\s*times')
    kernel_warning_regex = re.compile(r'WARNING:')
    kernel_BUG_regex = re.compile(r'BUG:')
    kernel_Error_regex = re.compile(r'\s*Error\s*')
    kernel_emmc_regex = re.compile(r'REGISTER DUMP')
    kernel_dmcmpu_regex = re.compile(r'Warning! DMC MPU detected violated transaction')

    #slog_base_p = sys.argv[1]
    crash_file = None
    log_dir = slog_base_p + os.path.sep + "post_process_report"
    #warning_file = log_dir + os.path.sep + "warning_file"
    pproblem_list = log_dir + os.path.sep + "problem_list.txt"
    final_report = log_dir + os.path.sep + "final_report.txt"
    pidlist = log_dir + os.path.sep + "anr" + os.path.sep + "anrpidlist.txt"
    if os.path.exists(pproblem_list):
    	os.remove(pproblem_list)
    if os.path.exists(final_report):
        os.remove(final_report)


    fp = open(pproblem_list,"w+")
    #fr = open(final_report,"w+")
    get_serverp(slog_base_p,fp)
 
    for dd in os.listdir(slog_base_p):
        if dd.find("log_") != -1:
            slogp = os.path.join(slog_base_p,dd)
            get_logcheck(slogp,fp)
            get_basic_info(slogp,fp) 
            break
    #kernel_panic = False
    problem_list = walkpath(log_dir)
    num_java = 0
    num_native = 0
    num_watchdog = 0 
    num_anr = 0


    if kernel_panic:
        fr = open(final_report,"w+")
        kernel_log = log_dir + os.path.sep + "kernel_panic" + os.path.sep + "kernel_log.log" 
	#ff = open(final_report,"w")
        kernel_panic_abstr(kernel_log,fr)
	#ff.close()
        fr.close()
        fr = open(final_report)
        line = fr.readline()
        while line:
            fp.write(line)
            line = fr.readline()
        fr.close()

    warningf = log_dir + os.path.sep + "kernel_panic" + os.path.sep + "warning.txt"
    bugf = log_dir + os.path.sep + "kernel_panic" + os.path.sep + "bug.txt"
    errorf = log_dir + os.path.sep + "kernel_panic" + os.path.sep + "error.txt"
    emmcf = log_dir + os.path.sep + "kernel_panic" + os.path.sep + "emmc.txt"
    dmcmpuf = log_dir + os.path.sep + "kernel_panic" + os.path.sep + "dmcmpu.txt"
    modemf = log_dir + os.path.sep + "kernel_panic" + os.path.sep + "modem.txt"
    wcnf = log_dir + os.path.sep + "kernel_panic" + os.path.sep + "wcn.txt"
    if os.path.exists(warningf):
        wf = open(warningf)
        line = wf.readline()
        i = 0
        while line:
            if kernel_warning_regex.search(line):
                i += 1
            line = wf.readline()
        wf.close()
        if i > 0:
            fp.write("\nThere is warning error in kernel log: total %s times.\n" %str(i))
            fp.write("Please refer to %s\n" %warningf)
        else:
            os.remove(warningf)
	    
    if os.path.exists(bugf):
        bf = open(bugf)
        line = bf.readline()
        i = 0
        while line:
            if kernel_BUG_regex.search(line):
                i += 1
            line = bf.readline()
        bf.close()
        if i > 0:
            fp.write("\nThere is BUG error in kernel log: total %s times.\n" %str(i))
            fp.write("Please refer to %s\n" %bugf)
        else:
            os.remove(bugf)
	    
    if os.path.exists(errorf):
        erf = open(errorf)
        line =erf.readline()
        i = 0
        while line:
            if kernel_Error_regex.search(line):
                i += 1
            line = erf.readline()
        erf.close()
        if i > 0:
            fp.write("\nThere is Error in kernel log: total %s times.\n" %str(i))
            fp.write("Please refer to %s\n" %errorf)
        else:
            os.remove(errorf)
	    
    if os.path.exists(emmcf):
        ef = open(emmcf)
        line = ef.readline()
        i = 0
        while line:
            if kernel_emmc_regex.search(line):
                i += 1
            line = ef.readline()
        ef.close()
        if i > 0:
            fp.write("\nThere is emmc error in kernel log: total %s times.\n" %str(i))
            fp.write("Please refer to %s\n" %emmcf)
        else:
            os.remove(emmcf)
	    
    if os.path.exists(dmcmpuf):
        mf = open(dmcmpuf)
        line = mf.readline()
        i = 0
        while line:
            if kernel_dmcmpu_regex.search(line):
                i += 1
            line = mf.readline()
        mf.close()
        if i > 0:
            fp.write("\nThere is DMC MPU error in kernel log: total %s times.\n" %str(i))
            fp.write("Please refer to %s\n" %dmcmpuf)
        else:
            os.remove(dmcmpuf)
	    
    if os.path.exists(modemf):
        mof = open(modemf)
        line = mof.readline()
        i = 0
        while line:
            if line.find(" Modem ") != -1:
                i += 1
            line = mof.readline()
        mof.close()
        if i > 0:
            fp.write("\nThere is modem assert: total %s times.\n" %str(i))
            fp.write("Please refer to %s\n" %modemf)
        else:
            os.remove(modemf)
	    
	    
    if os.path.exists(wcnf):
        wwf = open(wcnf)
        line = wwf.readline()
        i = 0
        while line:
            if line.find(" Wcn ") != -1:
                i += 1
            line = wwf.readline()
        wwf.close()
        if i > 0:
            fp.write("\nThere is wcn assert: total %s times.\n" %str(i))
            fp.write("Please refer to %s\n" %wcnf)
        else:
            os.remove(wcnf)
	    

    if len(problem_list) < 1:
        #fp.write("No crash java/native/wt crash issue found.")
        pass
    else:
        for pp in problem_list:
            print pp
            d_flag = False
            fd = open(pp)
            line = fd.readline()
            while line:
                if line.find("file: ") != -1:
                    line = fd.readline()
                    if line.find("file: ") != -1 or line.find("-------------") != -1:
                        print line
                        continue
                    else:
                        if line:
                            d_flag = True
                line = fd.readline()
            fd.close()
            if pp.find("kernel_log.log") != -1:
                d_flag = True
            if not d_flag:
                d_dir = os.path.dirname(pp)
                if os.path.exists(d_dir):
                    shutil.rmtree(d_dir)
 
        problem_list = walkpath(log_dir)
        fr = open(final_report,"a")
        for pp in problem_list:
            if pp.find("lowpower_list.txt") != -1:
                fd = open(pp)
                line = fd.readline() 
                while line:
                    if line.find("file: ") != -1 or line.find("-----------") != -1 or line.find("Last temprature values and last cap value will be written") != -1:
                        pass
                    else:
                        fp.write("\nPowerdown & charging:\n")
                        fr.write("-----------------lowpower charger--------------------\n")
                        break
                    line = fd.readline()
                fd.seek(0) 
                line = fd.readline()
                while line:
                    if line.find("file: ") != -1 or line.find("Last temprature values and last cap value will be written") != -1:
                        pass
                    else:
                        fp.write(line)
                    fr.write(line)
                    line = fd.readline()
                fd.close()

            if pp.find("java_crash_list.txt")!= -1:
                ######find all java crash
                fr.write("--------------------java crash--------------------------\n")
                report = os.path.dirname(pp) + os.path.sep + "java_crash_report.txt"
                problemlist = []
                problemnum = {}
                fd = open(pp)
                line = fd.readline()
                while line:
                    next_f = False
                    if line.find("file: ") != -1:
                        line = fd.readline()
                        while line:
                            if javacrash_regex.search(line):
                                pattern = r"(\[.*?\])"
                                tmp = re.findall(pattern,line,re.M)[0].split(",")
                                javacrashmodule = tmp[2]
                                javacrashp = tmp[4]
				#problemlist[javacrashmodule] = javacrashp
                                problemlist.append((javacrashmodule,javacrashp))
                            if line.find("file: ") != -1 or line.find("-------------") != -1:
                                next_f = True
                                break
                            line = fd.readline()
                    if next_f:
                        continue
                    line = fd.readline()
                num_java = len(problemlist)
                for k in range(len(problemlist)):
                    if problemnum.has_key(problemlist[k]):
                        problemnum[problemlist[k]] += 1
                    else:
                        problemnum[problemlist[k]] = 1
		#print "Java crash: Total %s." %(num_java)
                problemlist = list(set(problemlist))
                pnum = problemnum.copy()
                for k in problemlist:
                    print k
                fd.close()
	        #generate_final_report(fr,problemlist,pp)
                ######write to final_report
                generate_final_report(fr,problemnum,pp)
                #####write to problem_list
                reportp = open(report)
		###java crash list
                while line:
                    next_flag = False
                    length = False
                    if line.find("file: ") != -1:
                        linefile = line
                        line = reportp.readline()
                        if line.find("file: ") != -1 or line.find("--------------") != -1: 
                            continue
                        while line:
                            next_p = False
                            if len(pnum) > 0:
                                flag = get_probleminfo(line,pnum)
                                if flag != 0 and (line.find("IN SYSTEM PROCESS") != -1 or line.find("system_server") != -1):
                                    del pnum[flag[0]]
                                    javacrash_module = None
                                    javacrash_time = None
                                    if isinstance(flag[0],tuple):
                                        javacrash_module = flag[0][0]
                                    else:
                                        javacrash_module = flag[0]
                                    if line[0] >= "0" and line[0] <= "9":
                                        javacrash_time = line.split(" ")
                                        javacrash_time = javacrash_time[0] + "_" + javacrash_time[1]
                                    fp.write("\nJava crash:\n")   
                                    fp.write("Java crash module: %s\n" %javacrash_module)
                                    fp.write("Java crash time: %s\n" %javacrash_time)
			            fp.write(linefile) 
                                    while line:
                                        fp.write(line)
                                        line = reportp.readline()
                                        if line.find("file ") != -1 or line.find("--------------") != -1:
                                            next_flag = True
                                            break
                                else:
                                    line = reportp.readline()
                                    if line.find("file: ") != -1 or line.find("--------------") != -1:
                                        next_flag = True
                                    if line.find("am_crash") != -1:
                                        next_p = True
                                if next_p:
                                    continue
                                if next_flag:
                                    break
                            else:
                                length = True
                                break
                    if next_flag:     
                        continue
                    if length:
                        break 
		    line = reportp.readline()
                reportp.close()												


 
            if pp.find("native_crash_list.txt")!= -1:
                fr.write("--------------------native crash--------------------------\n")
                #####fina all native crash
                report = os.path.dirname(pp) + os.path.sep + "native_crash_report.txt"
                problemlist = []
                problemnum = {}
                fd = open(pp)
                line = fd.readline()
                while line:
                    next_f = False
                    if line.find("file: ") != -1:
                        line = fd.readline()
                        while line:
                            if nativecrash_regex.search(line):
                                nativecrasht = nativecrash_regex.search(line).group(1)
                                nativecrashp = nativecrash_regex.search(line).group(2)
                                problemlist.append((nativecrasht,nativecrashp))
                            if line.find("file: ") != -1 or line.find("-------------") != -1:
                                next_f = True
                                break
                            line = fd.readline()
                    if next_f:
                        continue
                    line = fd.readline()
                num_native = len(problemlist)
                for k in range(len(problemlist)):
                    if problemnum.has_key(problemlist[k]):
                        problemnum[problemlist[k]] += 1
                    else:
                        problemnum[problemlist[k]] = 1
                print "Native crash: Total %s." %(num_native)
                problemlist = list(set(problemlist))
                pnum = problemnum.copy()
                for k in problemlist:
                    print k
                fd.close()
	        ########write to final_report	
                generate_final_report(fr,problemnum,report)
                reportp = open(report)
                line = reportp.readline()
                while line:
                    next_flag = False
                    length = False
                    if line.find("file: ") != -1:
                        linefile = line
                        line = reportp.readline()
                        if line.find("file: ") != -1 or line.find("--------------") != -1: 
                            continue
                        while line:
                            next_p = False
                            if len(pnum) > 0:
                                flag = get_probleminfo(line,pnum)
                                if flag != 0 and nativecrash_system_server_regex.search(line):
                                    del pnum[flag[0]]
                                    nativecrash_module = None
                                    nativecrash_time = None
                                    if isinstance(flag[0],tuple):
                                        nativecrash_module = flag[0][0]
                                    else:
                                        nativecrash_module = flag[0]
                                    if line[0] >= "0" and line[0] <= "9":
                                        nativecrash_time = line.split(" ")
                                        nativecrash_time = nativecrash_time[0] + "_" + nativecrash_time[1]
                                    fp.write("\nNative crash:\n")   
                                    fp.write("Native crash module: %s\n" %nativecrash_module)
                                    fp.write("Native crash time: %s\n" %nativecrash_time)
			            fp.write(linefile) 
                                    while line:
                                        fp.write(line)
                                        line = reportp.readline()
                                        if line.find("file ") != -1 or line.find("--------------") != -1:
                                            next_flag = True
                                            break
                                        if nativecrash_regex.search(line):
                                            next_p = True
                                            break
                                else:
                                    line = reportp.readline()
                                    if line.find("file: ") != -1 or line.find("--------------") != -1:
                                        next_flag = True
                                    if line.find("pid:") != -1 or line.find("stack") != -1:
                                        next_p = True
                                if next_p:
                                    continue
                                if next_flag:
                                    break
                            else:
                                length = True
                                break
                    if next_flag:     
                        continue
                    if length:
                        break 
		    line = reportp.readline()
                reportp.close()												



            
            if pp.find("watchdog_list.txt")!= -1:
                fr.write("-------------------- watchdog timeout--------------------------\n")
                ######find all wt crash
                report = os.path.dirname(pp) + os.path.sep + "watchdog_report.txt"
                problemlist = []
                problemnum = {}
                fd = open(pp)
                line = fd.readline()
                while line:
                    next_f = False
                    if line.find("file: ") != -1:
                        line = fd.readline()
                        while line:
                            if watchdog1_regex.search(line) or watchdog2_regex.search(line):
                                tmp = line.split(":")[-1]
                                problemlist.append(tmp)
			    
                            if line.find("file: ") != -1 or line.find("-------------") != -1:
                                next_f = True
                                break
                            line = fd.readline()
                    if next_f:
                        continue
                    line = fd.readline()
                num_watchdog = len(problemlist)
                for k in range(len(problemlist)):
                    if problemnum.has_key(problemlist[k]):
                        problemnum[problemlist[k]] += 1
                    else:
                        problemnum[problemlist[k]] = 1
                print "Watchdog timeout: Total %s." %(num_watchdog)
                problemlist = list(set(problemlist))
                pnum = problemnum.copy()
                generate_final_report(fr,problemnum,report)
                fd.close()
                reportp = open(report)
                line = reportp.readline()
                while line:
                    next_flag = False
                    length = False
                    if line.find("file: ") != -1:
                        linefile = line
                        line = reportp.readline()
                        if line.find("file: ") != -1 or line.find("--------------") != -1: 
                            continue
                        while line:
                            next_p = False
                            if len(pnum) > 0:
                                flag = get_probleminfo(line,pnum)
                                if flag != 0:
                                    del pnum[flag[0]]
                                    wtcrash_module = None
                                    wtcrash_time = None
                                    if isinstance(flag[0],tuple):
                                        wtcrash_module = flag[0][0]
                                    else:
                                        wtcrash_module = flag[0]
                                    if line[0] >= "0" and line[0] <= "9":
                                        wtcrash_time = line.split(" ")
                                        wtcrash_time = wtcrash_time[0] + "_" + wtcrash_time[1]
                                    fp.write("\nWatchdog timeout crash:\n")   
                                    fp.write("Watchdog timeout crash module: %s\n" %wtcrash_module)
                                    fp.write("Watchdog timeout crash time: %s\n" %wtcrash_time)
			            fp.write(linefile) 
                                    while line:
                                        fp.write(line)
                                        line = reportp.readline()
                                        if line.find("file ") != -1 or line.find("--------------") != -1:
                                            next_flag = True
                                            break
                                        if watchdog1_regex.search(line) or watchdog2_regex.search(line):
                                            next_p = True
                                            break
                                else:
                                    line = reportp.readline()
                                    if line.find("file: ") != -1 or line.find("--------------") != -1:
                                        next_flag = True
                                    if line.find("Subject: ") != -1:
                                        next_p = True
                                if next_p:
                                    continue
                                if next_flag:
                                    break
                            else:
                                length = True
                                break
                    if next_flag:     
                        continue
                    if length:
                        break 
		    line = reportp.readline()
                reportp.close()												


                if num_watchdog == 0:
                    reportpp = open(report)
                    ll = reportpp.readline()
                    while ll:
                        if watchdog3_regex.search(ll):
                            while ll:
                                if watchdog_crash1_regex.search(ll):
                                    tmp = watchdog_crash_get_regex.search(ll)
                                    if tmp:
                                        tmp = tmp.groups()[0].split('.')[-1]  
                                        problemlist.append(tmp)
                                if ll.strip() == "":
                                    break
                                ll = reportpp.readline()
                        if ll.find("file: ") != -1 or ll.find("-------------") != -1:
                            ll = reportpp.readline()
                            continue
                        ll = reportpp.readline()
		    
                    num_watchdog = len(problemlist)
                    for k in range(len(problemlist)):
                        if problemnum.has_key(problemlist[k]):
                            problemnum[problemlist[k]] += 1
                        else:
                            problemnum[problemlist[k]] = 1
                    problemlist = list(set(problemlist))
                    print "Watchdog timeout: Total %s." %(num_watchdog)
                    generate_final_report2(fr,problemnum,report)
                    reportpp.close()
                    
                    reportp = open(report)
                    line = reportp.readline()
                    wtcrash_module = None
                    wtcrash_time = None
                    while line:
                        
                        next_flag = False
                        if line.find("file: ") != -1:
                            linefile = line
                            line = reportp.readline()
                            tmp_p = reportp.tell()
                            while line:
                                
                                if watchdog3_regex.search(line):
                                    pp = tmp_p
                                    fp.write("\nWatchdog timeout crash:\n")
                                    wtline = fd.readline()
                                    while wtline:
                                        
				    #if watchdog1_regex.search(wtline) or watchdog2_regex.search(wtline):
                                        if watchdog_crash1_regex.search(wtline):
                                            wtcrash_module = watchdog_crash_get_regex.search(wtline)
                                            if wtcrash_module:
                                                wtcrash_module = wtcrash_module.groups()[0].split('.')[-1]  
                                                break
                                        wtline = reportp.readline()
                                    fp.write("Watchdog timeout crash module: %s\n" %wtcrash_module)
                                    fp.write("Watchdog timeout crash time: %s\n" %wtcrash_time)

                                    reportp.seek(pp)				    
                                    line = reportp.readline()
                                    while line:
                                        
                                        fp.write(line)
                                        line = reportp.readline()    
                                        if line.find("file: ") != -1:
                                            next_flag = True
                                            break
                                if line.find("file: ") != -1:
                                    next_flag = True
                                    break
                                tmp_p = reportp.tell()
                                line = reportp.readline()
                        if next_flag:
                            continue

                        line = reportp.readline()
                fd.close()
    
        if os.path.exists(pidlist):
            fr.write("--------------------------ANR list--------------------------\n")
            pl = open(pidlist)
            line = pl.readline()
            while line:
                if anr_regex.search(line):
                    num_anr += 1
                    fr.write(line)
                line = pl.readline()
            pl.close()
        fr.close()


        fp.write("\n\nALL ISSUE ABSTRACT:\n")
        fr = open(final_report)
        line = fr.readline()
        fp.write("\nJava crash:Total %s times.\n" %num_java)
        fp.write("Critical list:\n")
        while line:
            tt = False
            if line.find("---java crash---") != -1:
                line = fr.readline()
                while line:
                    if crash_time_regex.search(line):
                        fp.write(line) 
                    if javacrash_regex.search(line):
                        fp.write(line)
                    if line.find("--------------") != -1:
                        tt = True
                        break
                    line = fr.readline()
            if tt:
                break	
            line = fr.readline()
        fr.seek(0)
        line = fr.readline()
        fp.write("\nNative crash:Total %s times.\n" %num_native)
        fp.write("Critical list:\n")
        while line:
            tt = False
            if line.find("---native crash---") != -1:
                line = fr.readline()
                while line:
                    if crash_time_regex.search(line):
                        fp.write(line) 
                    if nativecrash_regex.search(line):
                        fp.write(line)
                    if nativecrash_signal_regex.search(line):
                        fp.write(line)
                    if line.find("--------------") != -1:
                        tt = True
                        break
                    line = fr.readline()
            if tt:
                break	
            line = fr.readline()
        fr.seek(0)
        line = fr.readline()
        fp.write("\nWatchdog timeout:Total %s times.\n" %num_watchdog)
        fp.write("Critical list:\n")
        while line:
            tt = False
            if line.find("---- watchdog timeout----") != -1:
                line = fr.readline()
                while line:
                    if crash_time_regex.search(line):
                        fp.write(line)
                    if watchdog1_regex.search(line) or watchdog2_regex.search(line):
                        fp.write(line)
                    if line.find("----------") != -1:
                        tt = True
                        break
                    line = fr.readline()
            if tt:
                break
            line = fr.readline()
        fr.seek(0)
        fp.write("\nANR:Total %s times.\n" %num_anr)
        fp.write("First anr:\n")
        line = fr.readline()
        while line:
            if anr_regex.search(line):
                fp.write(line)
                break
            line = fr.readline()
        fr.close()

    mempath = log_dir + os.path.sep + "memory"
    memfile = mempath + os.path.sep + "memory_report.txt"
    if os.path.exists(memfile):
        fp.write("\nThere is enhanced meminfo from kernel log.\n")
    else:
        try:
            shutil.rmtree(mempath)
        except:
            pass
    fp.close()

#############################get run time####################################
def getKernelLogPaths(fparser,TYPE):
    logstr = fparser.getFilesBy(TYPE)
    if logstr:
        return logstr.split(',')
    return None

def get_time(line):
    if line == "":
        return None
    d = [datetime.datetime.now().year,string.atoi(line[5:7]),string.atoi(line[8:10]), string.atoi(line[11:13]), string.atoi(line[14:16]), string.atoi(line[17:19])]
    Time = datetime.datetime(d[0],d[1],d[2],d[3],d[4],d[5])
    return Time
        
def get_start_end_time(filep):
    print filep
    fd = open(filep)
    line = fd.readline()
    start_time = get_time(line) 
    tmp_time = start_time
    while line != "":
        next_time = get_time(line)
        if next_time == None:
            break
        line = fd.readline()
        tmp_time = get_time(line)
        if tmp_time == None:
            break
        line = fd.readline()
        time_lenth = tmp_time - next_time
        if time_lenth.seconds > 300: #如果超过5分钟就判断reboot测试出现问题，就判定end time 是出现问题出现之前的时间
            fd.close()
            return (start_time,next_time)
    fd.seek(0)
    line = fd.readline()
    while line:
        tmpline = line
        line = fd.readline()
    fd.close()
    next_time = get_time(tmpline)
    return (start_time,next_time)

def get_start_end_time_msr(filep):
    rtime = 0
    time_line_regex = re.compile(r'\d\d:\d\d:\d\d GMT ')
    dated = {'Sun':'1','Mon':'2','Tue':'3','Wed':'4','Thu':'5','Fri':'6','Sat':'7'}
    fd = open(filep)
    line = fd.readline()
    while line:
        if line.find("/data/pid.txt exist") != -1:
            line = fd.readline()
            if time_line_regex.search(line):
                tmp_time = line.split(" ")
                day = dated[tmp_time[1]]
                (h,m,s) = tmp_time[5].split(":")
                print h,m,s
                d = [datetime.datetime.now().year,datetime.datetime.now().month,string.atoi(str(day)),string.atoi(str(h)),string.atoi(str(m)),string.atoi(str(s))]
                start_time = datetime.datetime(d[0],d[1],d[2],d[3],d[4],d[5])
                break
        line = fd.readline()
    print start_time
    days = 0
    while line:
        while line:
            if line.find("/data/pid.txt exist") != -1:
                line = fd.readline()
                if time_line_regex.search(line):
                    tmp_time = line.split(" ")
                    day = dated[tmp_time[1]]
                    (h,m,s) = tmp_time[5].split(":")
                    d = [datetime.datetime.now().year,datetime.datetime.now().month,string.atoi(str(day)),string.atoi(str(h)),string.atoi(str(m)),string.atoi(str(s))]
                    first_time = datetime.datetime(d[0],d[1],d[2],d[3],d[4],d[5])
                    break
            line = fd.readline()
        #if (first_time - start_time).seconds > 259200:
        if (first_time - start_time).days > 4:
            rtime += end_time - start_time
            start_time = first_time
            continue
        line = fd.readline()
        while line:
            if line.find("/data/pid.txt exist") != -1:
                line = fd.readline()
                if time_line_regex.search(line):
                    tmp_time = line.split(" ")
                    day = dated[tmp_time[1]]
                    (h,m,s) = tmp_time[5].split(":")
                    d = [datetime.datetime.now().year,datetime.datetime.now().month,string.atoi(str(day)),string.atoi(str(h)),string.atoi(str(m)),string.atoi(str(s))]
                    end_time = datetime.datetime(d[0],d[1],d[2],d[3],d[4],d[5])
                    break
            line = fd.readline()
        if (end_time - start_time).days > 4:
            rtime += first_time - start_time
            start_time = end_time
            continue
        if (end_time - first_time).seconds > 600:
            end_time = first_time
            break 
        line = fd.readline() 
    print end_time
    if rtime:
        return(end_time - start_time + rtime)
    else:
        return (end_time - start_time)

class runTime(object):

    def __init__(self, logfile):
        self.logfile = logfile

    def find_test_start_time(self):
        ret = False
        start_time = 0
        dp = open(self.logfile)
		
        line = dp.readline()
        while line:
            if line[1] >= '0' and line[1] <= '9':
                ret = True
                break
            line = dp.readline()
        dp.close()
        if ret == False:
            return False
        #d = [datetime.datetime.now().year, string.atoi(line[0:2]), string.atoi(line[3:5]), string.atoi(line[6:8]),string.atoi(line[9:11]), string.atoi(line[12:14])]
        d = [datetime.datetime.now().year, string.atoi(line[1:3]), string.atoi(line[4:6]), string.atoi(line[7:9]),string.atoi(line[10:12]), string.atoi(line[13:15])]
        start_time = datetime.datetime(d[0],d[1],d[2],d[3],d[4],d[5])
        print start_time
        dp.close()
        return start_time

    def find_test_end_time(self,keyword):
        count = 0
        if not keyword:
            fd = open(self.logfile)
            line = fd.readline()
            while line:
                if line[1] >= '0' and line[1] <= '9':
                    count += 1
                line = fd.readline()
            fd.seek(0)
            line = fd.readline()
            while line:
                if line[1] >= '0' and line[1] <= '9' :
                    count -= 1
                    if count == 0:
                        break
                line = fd.readline()
            fd.close()
            d = [datetime.datetime.now().year, string.atoi(line[1:3]), string.atoi(line[4:6]),string.atoi(line[7:9]), string.atoi(line[10:12]), string.atoi(line[13:15])]
            end_time = datetime.datetime(d[0],d[1],d[2],d[3],d[4],d[5])
            print end_time
            fd.close()
            return end_time
        else:
            fd = open(self.logfile)
            line = fd.readline()
            keyword_regex = re.compile(keyword)
            while line:
                if keyword_regex.search(line):
                    while line:
                        if line[1] >= '0' and line[1] <= '9' :
                            break
                        line = fd.readline()
                    print line
                    try:	
                        d = [datetime.datetime.now().year, string.atoi(line[1:3]), string.atoi(line[4:6]),string.atoi(line[7:9]), string.atoi(line[10:12]), string.atoi(line[13:15])]
                    except:
                        d = [datetime.datetime.now().year, string.atoi(line[0:2]), string.atoi(line[3:5]),string.atoi(line[6:8]), string.atoi(line[9:11]), string.atoi(line[12:14])]
                    end_time = datetime.datetime(d[0],d[1],d[2],d[3],d[4],d[5])

                    print end_time
                    fd.close()
                    return end_time

                line = fd.readline()

            fd.close()
            return False#如果没有找到返回false

def sd_last_kernel_get_time(line):
    if line[1] < '0' or line[1] > '9':
        return False
    d = [datetime.datetime.now().year,string.atoi(line[1:3]),string.atoi(line[4:6]), string.atoi(line[7:9]), string.atoi(line[10:12]), string.atoi(line[13:15])]
    Time = datetime.datetime(d[0],d[1],d[2],d[3],d[4],d[5])
    return Time
            
#def sd_last_kernel_start_end_time(filep1, filep2):
def sd_last_kernel_start_end_time(filep2):
    '''
    fd = open(filep1)
    line = fd.readline()
    while line:
        ret = sd_last_kernel_get_time(line)
        if ret:
            start_time = ret
            break
        line = fd.readline()
    fd.close()
    if not ret:
        return ret
    '''
    fd = open(filep2)
    line = fd.readline()
    while line:
        tmpline = line
        line = fd.readline()
    fd.close()
    ret = sd_last_kernel_get_time(tmpline)
    if ret:
        end_time = ret
        print end_time
        #time_lenth = end_time - start_time
        #return time_lenth
        return end_time
    return ret
            


def run_time(log_p,folderparser):

    calendar_time_regex = re.compile("(calendar_time):([0-9]+)")
    Monkey_Start_Calendar_Time = re.compile(r"( Monkey Start Calendar Time ):( [0-9]+)")
    log_base_p = os.path.dirname(log_p)
    log_dir = log_base_p + os.path.sep + "post_process_report"
    test_time_file = log_dir + os.path.sep + "test_time_report.txt"
    #test_time_list = log_dir + os.path.sep + "test_time_list.txt"
    preport = open(test_time_file,"w+")

    #######calculate all ylog runtime#############
    ylogpath = log_p + os.path.sep + "external_storage" + os.path.sep + "last_ylog" + os.path.sep + "ylog"
    for i in range(1,6): 
        ylog = ylogpath + str(i) + os.path.sep + "kernel" + os.path.sep + "kernel.log"
        if os.path.exists(ylog):
            print ylog
            runtimec = runTime(ylog)
            start_time = runtimec.find_test_start_time()
            end_time = runtimec.find_test_end_time(None)
            test_time = end_time - start_time
            preport.write("last_ylog/ylog%s runtime is %s\n" %(i,test_time))
    current_ylog = log_p + os.path.sep + "external_storage" + os.path.sep + "ylog" + os.path.sep + "kernel" + os.path.sep + "kernel.log"
    if os.path.exists(current_ylog):
        print current_ylog
        runtimec = runTime(current_ylog)
        start_time = runtimec.find_test_start_time()
        end_time = runtimec.find_test_end_time(None)
        test_time = end_time - start_time
        preport.write("current ylog runtime is %s\n\n" %test_time)
    
    
    sd_file_flag = False
    #logPath = getKernelLogPaths(folderparser,"runtime")
    logPath = getKernelLogPaths(folderparser,'runtime')
    if logPath:
        sd_file_flag = True
        sp = FileSort(logPath)
        logPath = sp.fsort()
        
    sd_last_kernel = []
    sd_monkey = []
    sd_cmdline = None
    sd_kernel_file_exist_flag = False
    sd_monkey_flag = False
    sd_cmdline_flag = False

    if sd_file_flag:
        for f in logPath:
            if f.find("kernel") != -1:
                sd_kernel_file_exist_flag = True
                sd_last_kernel.append(f)
                continue
            if f.find("monkey") != -1:
                sd_monkey_flag = True
                sd_monkey = f
                continue
    '''
    data_last_path = log_p + os.path.sep + "internal_storage" + os.path.sep + "last_ylog"
    if os.path.exists(data_last_path):
        for p,d,f in os.walk(data_last_path):
            for filename in f:
                if filename.find("cmdline") != -1:
                    sd_cmdline_flag = True
                    sd_cmdline = filename
                    sd_cmdline = os.path.join(p,filename)
                    print sd_cmdline
                    break
    '''
    if not sd_kernel_file_exist_flag:
        preport.write("no sd last kernel log\n")
        
    if not sd_monkey_flag :
        preport.write("no sd monkey log\n")
    '''
    if not sd_cmdline_flag:
        preport.write("no sd cmdline log\n")
    '''    

                
    sd_last_kernel.sort()
    print sd_last_kernel 
    print sd_monkey


    sd_path = log_p + os.path.sep + "external_storage" 
    problem_list_txt = log_dir + os.path.sep + "problem_list.txt"
    lowpower_path = log_dir + os.path.sep + "low_power"

    #reboot_test = False
    if not os.path.exists(sd_path + os.path.sep + 'rebootlog.log'):#reboot_test:
        preport.write("there is no \"rebootlog.log\"\n")
    if not os.path.exists(sd_path + os.path.sep + 'MSR.log'):#reboot_test:
        preport.write("there is no \"MSR.log\"\n")
    if os.path.exists(sd_path + os.path.sep + 'rebootlog.log'):#reboot_test:
		#统计sdcard last log kernel log 的时间差
        filep = sd_path + os.path.sep + 'rebootlog.log'
        start_time, end_time = get_start_end_time(filep)
                
        preport.write("This result from \"rebootlog.log\" \n")
        print start_time
        print end_time
        runtime = (end_time - start_time)
        start_time = "start time: %s\n"%start_time
        end_time = "end time: %s\n"%end_time
        preport.write(start_time)
        preport.write(end_time)
        print runtime.seconds
        #formate_str = "How long test time1: [%s]\n"%runtime
        formate_str = "\nReboot Run Time: [%s]\n"%runtime
        preport.write(formate_str)
    if os.path.exists(sd_path + os.path.sep + 'MSR.log'):#reboot_test:
		#统计sdcard last log kernel log 的时间差
        filep = sd_path + os.path.sep + 'MSR.log'
        runtime = get_start_end_time_msr(filep)
                
        preport.write("This result from \"MSR.log\" \n")
        #runtime = (end_time.split(" ")[-1] - start_time.split(" ")[-1])
        #start_time = "start time: %s\n"%start_time
        #end_time = "end time: %s\n"%end_time
        #preport.write(start_time)
        #preport.write(end_time)
        #print runtime.seconds
        #formate_str = "How long test time1: [%s]\n"%runtime
        formate_str = "\nMSR Run Time: [%s]\n"%runtime
        preport.write(formate_str)
    elif sd_kernel_file_exist_flag:
		#通过关键字分析problem_list文件 并找到结束时间
        result_flag = False
        rtf = runTime(sd_last_kernel[0])
        st = rtf.find_test_start_time()
        start_time = st
        file_name = "start time from file:%s\n"%sd_last_kernel[0]
        preport.write(file_name)
        st = "start time %s\n"%st
        preport.write(st)
        print st

        filep = problem_list_txt
        rtf = runTime(filep)
        keyword_list  = ['WATCHDOG KILLING SYSTEM PROCESS','>>> system_server <<<','FATAL EXCEPTION IN SYSTEM PROCESS']
        for keyword in keyword_list:
            et = rtf.find_test_end_time(keyword)
            if et:
                end_time_file = "end time from file:%s\n"%filep 
                tmp_et = "end_time:%s\n"%et
                preport.write(end_time_file)
                preport.write(tmp_et)
                runtime = (et - start_time)
                preport.write("\nRun Time: %s" %runtime)
                result_flag = True
                break
        '''
        if result_flag == False:
            preport.write("did'not find key word in the proplem.list\n")
            rtf = runtime(sd_last_kernel[0])
            et = rtf.find_test_end_time(none)
            end_time = et
            file_name = "end time from file:%s\n"%sd_last_kernel[0]
            preport.write(file_name)
            et = "end time %s\n"%et
            preport.write(et)
            runtime = (end_time - start_time)
            result_flag = true
        '''
        #if result_flag == False and sd_cmdline_flag == True:
        if result_flag == False and os.path.exists(lowpower_path):
            '''	
            charger_flag = False
            fd = open(sd_cmdline)
            line = fd.readline()
            while line:
                if line.find("androidboot.mode=charger") != -1:
                    charger_flag = True
                    break
                line = fd.readline()
            if not charger_flag :
                preport.write("no find mode = charge!\n")
                fd.close()
            '''
            if sd_kernel_file_exist_flag == True:
                #ret = sd_last_kernel_start_end_time(sd_last_kernel[-1], sd_last_kernel[0])
                ret = sd_last_kernel_start_end_time(sd_last_kernel[0])
                if ret:
                    #start_time_file = "start time from file:%s\n"%sd_last_kernel[-1] 
                    #preport.write(start_time_file)
                    end_time = ret
                    end_time_file = "end time from file:%s\n"%sd_last_kernel[0] 
                    preport.write(end_time_file)
                    st = "end time %s\n"%end_time
                    preport.write(st)
                    time_lenth = end_time - start_time
                    result_flag = True
                    st = "\nRun Time: %s\n" %time_lenth
                    preport.write(st)
                    #runtime = ret
                    #print runtime

        if result_flag == False:
            preport.write("did'not find key word in the proplem.list\n")
            rtf = runTime(sd_last_kernel[0])
            et = rtf.find_test_end_time(None)
            end_time = et
            file_name = "end time from file:%s\n"%sd_last_kernel[0]
            preport.write(file_name)
            et = "end time %s\n"%et
            preport.write(et)
            runtime = (end_time - start_time)
            preport.write("\nRun Time %s\n" %runtime)


        if sd_monkey_flag:
            rtime = 0	
            fd = open(sd_monkey)
            line = fd.readline()
            while line:
                if Monkey_Start_Calendar_Time.search(line):#line.find('Monkey Start Calendar Time'):
                    #d = [datetime.datetime.now().year,string.atoi(line[65:67]),string.atoi(line[68:70]), string.atoi(line[71:73]), string.atoi(line[74:76]), string.atoi(line[77:79])]
                    ttime = line.split(" ")[-3:-1]
                    print "ttt"
                    print ttime
                    print ttime[0]
                    print ttime[1]
                    d = [string.atoi(ttime[0][0:4]),string.atoi(ttime[0][5:7]),string.atoi(ttime[0][8:10]),string.atoi(ttime[1][0:2]),string.atoi(ttime[1][3:5]),string.atoi(ttime[1][6:8]),]
                    start_time = datetime.datetime(d[0],d[1],d[2],d[3],d[4],d[5])
                    print start_time
                    break
                line = fd.readline()
            count_time = 0
            while line:
                while line:
                    if calendar_time_regex.search(line):#line.find("calendar_time"):
                        ttime = line.split("calendar_time:")[-1].split(" ")
                        #print ttime[0]
                        #print ttime[1]
                        d = [string.atoi(ttime[0][0:4]),string.atoi(ttime[0][5:7]),string.atoi(ttime[0][8:10]),string.atoi(ttime[1][0:2]),string.atoi(ttime[1][3:5]),string.atoi(ttime[1][6:8]),]
                        first_time = datetime.datetime(d[0],d[1],d[2],d[3],d[4],d[5])
                        break
                    line = fd.readline()
                #print first_time - start_time
                #print (first_time - start_time).days
                if (first_time - start_time).days > 4:
                    #print first_time
                    if rtime == 0:
                        rtime = end_time - start_time
                    else:
                        rtime += end_time - start_time
                    start_time = first_time
                    #print rtime
                    continue
                line = fd.readline()
                while line:
                    if calendar_time_regex.search(line):#line.find("calendar_time"):
                        ttime = line.split("calendar_time:")[-1].split(" ")
                        #print ttime[0]
                        #print ttime[1]
                        d = [string.atoi(ttime[0][0:4]),string.atoi(ttime[0][5:7]),string.atoi(ttime[0][8:10]),string.atoi(ttime[1][0:2]),string.atoi(ttime[1][3:5]),string.atoi(ttime[1][6:8]),]
                        end_time = datetime.datetime(d[0],d[1],d[2],d[3],d[4],d[5])
                        break
                    line = fd.readline()
                #print end_time - start_time
                #print (end_time - start_time).days
                if (end_time - start_time).days > 4:
                    #print end_time
                    if rtime == 0:
                        rtime = first_time - start_time
                    else:
                        rtime += first_time - start_time
                    start_time = end_time
                    continue

                line = fd.readline()
						
            fd.close()
            if rtime:
                runtime = end_time - start_time + rtime
            else:
                runtime = end_time - start_time
            result_flag = True
            print runtime
            #formate_str = "How long test time3: [%d]\n"%runtime.seconds
            formate_str = "\nMonkey Run Time: %s\n"%runtime
            preport.write(formate_str)
				
################################################################################################
###############parse_kernel,anr,java.native,wt###################

def run_kernel_panic(devbit):
    print "***********kernel_panic begin************"
        
    m = Main(vmlinux_f,sysdump_p, ylog_p, devbit,serial_num)
    m.run()
    m.genReport()
    #arg_kernel = ['python','main.py',vmlinux_f,sysdump_p,slog_p,devbit,serial_num]
    #result_kernel = subprocess.Popen(arg_kernel,stdout=subprocess.PIPE,shell=False).stdout.readlines()


def run_anr():
    print "***********anr begin************"
    parse_anr(ylog_p,serial_num)
    #arg_anr = ['python','parse_anr.py','--log-dir',slog_p,'--serial-num',serial_num]

def run_native_crash():
    print "***********native_crash begin************"
    parse_native_crash(ylog_p,serial_num)
    #arg_native = ['python','parse_native_crash.py','--symbols-dir',vmlinux_f,'--log-dir',slog_p,'--serial-num',serial_num]

def run_java_crash():
    print "***********java_crash begin************"
    parse_java_crash(ylog_p,serial_num)
    #arg_java = ['python','parse_java_crash.py','--log-dir',slog_p,'--serial-num',serial_num]

def run_watchdog_crash():
    print "***********watchdog_crash begin************"
    parse_watchdog_crash(ylog_p,serial_num)
    #arg_watchdog = ['python','parse_watchdog_crash.py','--log-dir',slog_p,'--serial-num',serial_num]

def run_lowpower():
    print "***********lowpower begin************"
    parse_lowpower(ylog_p,serial_num)

def run_kmemleak():
    print "***********kmemleak begin************"
    parse_kmemleak(ylog_p, serial_num)

def run_mm():
    print "*************enhanced mem begin************"
    parse_mm(ylog_p,"last_time",serial_num)
####################################################################
##############parse_java_crash################################
def getReportDir_java(folderParser):
     
    if platform.system() == "Linux":
        location = folderParser.rfind("/")
    else:
        location = folderParser.rfind("\\")
    slogBasePath = folderParser[0:location]
    reportDir = slogBasePath + os.path.sep + "post_process_report" + os.path.sep + "java_crash" 
    if not os.path.exists(reportDir):
        os.makedirs(reportDir)
    reportdir_g = reportDir
    return reportDir

def getReportFile_java(folderParser):
    reportDir = getReportDir_java(folderParser)
    reportFile = os.path.join(reportDir, 'java_crash_report.txt')
    return reportFile

def getProblemList_java(folderParser):
    reportDir = getReportDir_java(folderParser)
    reportFile = os.path.join(reportDir, 'java_crash_list.txt')
    return reportFile

def clearReportDir_java(folderParser):
    reportDir = getReportDir_java(folderParser) 
    shutil.rmtree(reportDir)

def getSystemLogPaths(folderParser,PARSE_TYPE):
    logstr = folderParser.getFilesBy(PARSE_TYPE)
    if logstr:
        return logstr.split(',')
    return None

def getEventLogs(folderParser,PARSE_TYPE):
    logstr = folderParser.getFilesBy(PARSE_TYPE)
    if logstr:
        return logstr.split(',')
    return None

def getDropboxLogs(folderParser,PARSE_TYPE):
    logstr = folderParser.getFilesBy(PARSE_TYPE)
    if logstr:
        return logstr.split(',')
    return None

def getCrashEvent(efile,pfile,rf,fpp):

    java_crash_pattern = r'\sFATAL EXCEPTION:'
    java_crash_regex = re.compile(java_crash_pattern)
    java_crash_line_pattern = r'\sAndroidRuntime:\s'
    java_crash_line_regex = re.compile(java_crash_line_pattern)
    basedir = os.path.dirname(efile)
    print basedir
    ####get crash log
    sysfiles = None
    sysfiles = getSystemLogPaths(fpp,"javacrash")
    print sysfiles
    if sysfiles:
        sp = FileSort(sysfiles)
        sysfiles = sp.fsort()
        print sysfiles
    if os.path.exists(efile):
        fd = open(efile)
    else:
	#print "Open event file error,return"
        print "No event file for javacrash"
        return 0
    pfile.write("file: " + efile + "\n")
    #rf.write("------------------------------------------------------------\n")
    #rf.write("file: " + efile + "\n")
    line = fd.readline()
    while line:
	######find am_crash from event file
        if line.find("am_crash") != -1 and line.find("java") != -1:
            pfile.write(line)
	    #rf.write(line) 
            line = line.strip().split(" ")
            crashtime = line[0] + " " + line[1].split(".")[0]
            print crashtime
            ct = line[0] + "-" + line[1]
            d = [datetime.datetime.now().year,string.atoi(ct[0:2]),string.atoi(ct[3:5]),string.atoi(ct[6:8]),string.atoi(ct[9:11]),string.atoi(ct[12:14])]
            ct = datetime.datetime(d[0],d[1],d[2],d[3],d[4],d[5])
            if sysfiles:
                for ffs in sysfiles:
                    ff = False
                    fs = open(ffs)
                    ll = fs.readline()
                    while ll:
		    ######find according system info(timer and FATAL EXCEPTION)
                        if ll.find(crashtime) != -1 and java_crash_regex.search(ll):
			#if java_crash_regex.search(ll):
                            rf.write("----------------------------------------\n")
                            rf.write("file: " + ffs + "\n")
                            ff = True
                            while ll:
                                if java_crash_line_regex.search(ll):
                                    rf.write(ll)
                                else:
                                    break
                                ll = fs.readline()
                        if ff:
                            break
                        ll = fs.readline()
                    if ff:
                        fs.close()
                        break
                    fs.close()
				
        line= fd.readline()
    fd.close()		
 

def parseNext(fd):
    '''return a list contains the matched lines associate one java crash.'''

    java_crash_pattern = r'\sFATAL EXCEPTION:'
    java_crash_regex = re.compile(java_crash_pattern)
    java_crash_line_pattern = r'\sAndroidRuntime:\s'
    java_crash_line_regex = re.compile(java_crash_line_pattern)
    lines = []
    crash_begin = False

    line = fd.readline()
    while line:
        if not crash_begin:
            ## match "AndroidRuntime: FATAL EXCEPTION"
            if java_crash_regex.search(line):
                line = line.strip()
                lines.append(line)
                crash_begin = True
        else:
            ## match "AndroidRuntime:
            if java_crash_line_regex.search(line):
                line = line.strip()
                lines.append(line)
            else:
                ## java crash finished
                break
        line = fd.readline()

    return lines

def parse(input_file, output_file=None):
    try:
        fd = open(input_file, 'r')
    except:
        print 'Try to open input file error, input file:', input_file
        return

    if output_file:
        try:
            fd_out = open(output_file, 'a')
            fd_out.write("Parse log path: %s\n" % input_file)
        except:
            print 'Try to open output file error, output file:', output_file
            output_file = None

    lines = parseNext(fd)

    if output_file:
        while lines:
            fd_out.write("********************    Begin    ****************************\n")
            for line in lines:
                fd_out.write(line+'\n')
            fd_out.write("********************     End     ****************************\n")

            lines = parseNext(fd)
    else:
        while lines:
            print "********************    Begin    ****************************"
            for line in lines:
                print line
            print "********************     End     ****************************"

            lines = parseNext(fd)

    fd.close()
    if output_file:
        fd_out.close()


def getSystemCrashFileinfo(crash_file,pf,pl):


    java_crash_pattern = r'\sFATAL EXCEPTION:'
    java_crash_regex = re.compile(java_crash_pattern)
    if os.path.exists(crash_file):
        dfp = open(crash_file)
    else:
	#print "Cannot open system_server_crash@ file,return."
        print "No system_server_crash@ file."
        return 0
    pf.write("file: " + crash_file + "\n")
    pl.write("file: " + crash_file + "\n")
    line = dfp.readline()
    #lline = []
    t_flag = False
    while line:
        if java_crash_regex.search(line):
            t_flag = True
	    #get java_crash timer for memory analyse
	    #ll = line.split(" ") 
	    #java_timer_for_mm = ll[0] + " " + ll[1]
	    #print "java_timer_for_mm:**********************************************"
            pl.write(line)
            pf.write(line)
            for i in range(10):
		#lline.append(line)
		#tfp_p.write(line)
	        #line = dfp.readline()
                line = dfp.readline()
                pf.write(line)
		    #break
	    #break
        line = dfp.readline()
    #if there is no "FATAL EXCEPTION IN SYSTEM PROCESS:" info,then copy all system_server_crash@ content to tmp_report
    if not t_flag:
        dfp.seek(0)
        line = dfp.readline()
        while line:
            if line.find("Build:") != -1:
                pass
            else:
                pl.write(line)
                pf.write(line)
            line = dfp.readline()
    dfp.close()

def compare_slog_dropbox_java(report_p,list_p,tmpr_p,tmpl_p):
    reportp = open(report_p)
    listp = open(list_p)
    tmprp = open(tmpr_p)
    tmplp = open(tmpl_p)
    
    line1 = listp.readlines()
    line2 = reportp.readlines()
    listp.close()
    reportp.close()
	
    line = tmplp.readline()
    while line:
        if line.find("file: ") != -1:
            file_line = line
            line = tmplp.readline()
            while line and len(line) < 2:
                line = tmplp.readline()
            tmpline = line
            crash_time = tmpline.split(" ")
            try:
                crash_time = crash_time[0] + " " + crash_time[1]
            except:
                crash_time = crash_time[0]
            find_flag = False
            for ll in line1:
                if ll.find(crash_time) != -1:
                    find_flag = True
            if find_flag:
                pass
            else:
                listp = open(list_p,"a+")
	#	listp.write("-------------------------------------\n")
                listp.write(file_line)
                listp.write(line) 
                listp.close()
                tmprp.seek(0)
                mm = tmprp.readline()
                while mm:
                    if mm.find(crash_time) != -1:
                        reportp = open(report_p,"a+")
                        reportp.write("--------------------------------------------\n")
                        reportp.write(file_line)
                        reportp.write(mm)
                        mm = tmprp.readline()
                        while mm:
                            if mm.find("file: ") != -1:
                                break
                            reportp.write(mm)
                            mm = tmprp.readline()
                        reportp.close()
                    mm = tmprp.readline()
                break
		
        line = tmplp.readline()
			    
    tmprp.close()
    tmplp.close()			    


def usage():
    print 'Usage:', '[-h | --help] [--version] [[-i <File>] [-o <File>] | [--log-dir <Path>]] [--verbose]' 
    print
    print '       -h or --help, to show this usage infomations.'
    print '       -i, specify the input file for parsing, this is a mandatory.'
    print '       -o, specify the output file store the parse result, this is an option. if this option is not given, the parse result will output to standard output.'
    print '       --log-dir, specify the log directory used by FolderParser to get log paths and repoter path. Note: if this option is given, then the -i/-o option will be ignored.'
    print '       --verbose, output all parse result to standard output as welll as report file.'
    print '       --version, print version information to standard output.'

def getProblemList(folderParser):
    reportDir = getReportDir_java(folderParser)
    reportFile = os.path.join(reportDir, 'java_crash_list.txt')
    return reportFile


def parse_java_crash(input_dir,devnum):


    #script_file = sys.argv[0]
    #global java_time_for_mm
    tmpfile = os.path.abspath('.') + os.path.sep + "logs" + os.path.sep + "javacrash_file_tmp.txt"
    tmplist = os.path.abspath('.') + os.path.sep + "logs" + os.path.sep + "javacrash_list_tmp.txt"
    eventlogs = None
    dropboxlogs = None
    systemLogPaths = None
    if input_dir:
        fp = FolderParser(input_dir,devnum)

        clearReportDir_java(input_dir)
        reportFile = getReportFile_java(input_dir)
        problemlist = getProblemList(input_dir)
        ## get crash log file
        systemLogPaths = getSystemLogPaths(fp,"javacrash")
        if systemLogPaths:
            sp = FileSort(systemLogPaths)
            systemLogPaths = sp.fsort()
        print systemLogPaths
        eventlogs = getEventLogs(fp,"javacrashevent")
        if eventlogs:
            sp = FileSort(eventlogs)
            eventlogs = sp.fsort()
        dropboxlogs = getDropboxLogs(fp,"javacrashdropbox")
        if dropboxlogs:
            sp = FileSort(dropboxlogs)
            Dropboxlogs = sp.fsort()
        if eventlogs:
            plist = open(problemlist,"w+")
            rfile = open(reportFile,"w+")
            for eventfile in eventlogs:
                getCrashEvent(eventfile,plist,rfile,fp) 
        #systemLogPaths.sort()
	##get system log content
            plist.close()
            rfile.close()	
        elif systemLogPaths:
            for systemLog in systemLogPaths:
                parse(systemLog, reportFile)
        else:
            ## no system log to parse java crash
            print 'No system and event log file to parse.'
	    #rfile.wtite("\nNo system and event log file to parse")
        if dropboxlogs:
            tmpfile_p = open(tmpfile,"w")
            tmplist_p = open(tmplist,"w")
            for dropboxlog in dropboxlogs:
                getSystemCrashFileinfo(dropboxlog,tmpfile_p,tmplist_p)
		
            tmpfile_p.close()
            tmplist_p.close()	
            if os.path.exists(tmplist): 
                compare_slog_dropbox_java(reportFile,problemlist,tmpfile,tmplist)
	#java_timer_for_mm = java_timer_for_mm.replace(" ","_")
	#os.system("python parse_mm.py " + "--log-dir " + input_dir + " --serial-num " + devnum + " --timer " + "last_time")
    else:
        ## no input file, just return
        usage()
        #sys.exit(1)
	return 0
    if os.path.exists(tmpfile):
        os.remove(tmpfile)
    if os.path.exists(tmplist):
        os.remove(tmplist)
################################################################################################
############parse_native_crash##############################
def compare_slog_dropbox_native(report_p,list_p,tmpr_p,tmpl_p):

    native_crash_module_get_regex = re.compile(r'\s*name: (\w+)')
    reportp = open(report_p)
    listp = open(list_p)
    tmprp = open(tmpr_p)
    tmplp = open(tmpl_p)
    
    line1 = listp.readlines()
    line2 = reportp.readlines()
    listp.close()
    reportp.close()
	
    line = tmplp.readline()
    corelist = []
    while line:
        if line.find("file: ") != -1:
            print line
            file_line = line
            line = tmplp.readline()
            while line and len(line) < 2:
                line = tmplp.readline()
            tmpline = line
            find_flag = False
            for ll in line1:
                if ll.find(tmpline) != -1:
                    find_flag = True
            if find_flag:
                pass
            else:
                try:
                    name = native_crash_module_get_regex.search(line).group(1)
                    corelist.append(name)
                    listp = open(list_p,"a+")
	#	    listp.write("-------------------------------------\n")
                    listp.write(file_line)
                    listp.write(line) 
                    listp.close()
                    tmprp.seek(0)
                    mm = tmprp.readline()
                    while mm:
                        if mm.find(tmpline) != -1:
                            reportp = open(report_p,"a+")
                            reportp.write("--------------------------------------------\n")
                            reportp.write(file_line)
                            reportp.write(mm)
                            mm = tmprp.readline()
                            while mm:
                                if mm.find("file: ") != -1:
                                    break
                                reportp.write(mm)
                                mm = tmprp.readline()
                            reportp.close()
                        mm = tmprp.readline()
                    break
		except:
                    pass
        line = tmplp.readline()
    tmprp.close()
    tmplp.close()
    if len(corelist) >0:
        return corelist
    else:
        return 0			    

def get_tombstonefile_info(tombstonef,np,ft):

    native_crash_regex = re.compile(r'pid: [0-9]+, tid: [0-9]+,\s*name:\s*.*\s*>>>\s*.*\s*<<<')
    D_LINE_new = re.compile("stack:")
    end_line = re.compile("(--- --- --- --- --- --- --- )")
    flag = False
    if os.path.exists(tombstonef):
        tsp = open(tombstonef)
    else:
	#print "Cannot open SYSTEM TOMBSTONE@, return"
        print "No SYSTEM TOMBSTONE@."
        return 0
    np.write("file: " + tombstonef + "\n")
    ft.write("file: " + tombstonef + "\n")
    line = tsp.readline()
	#########write to tmp_log and native_crash_file.txt
    while line:
        if native_crash_regex.search(line):
	    #r_line = line
            flag = True
            ft.write(line)
            np.write(line)
            line = tsp.readline()
            while line:
                if D_LINE_new.search(line):
                    break
                else:
                    np.write(line)
                    line = tsp.readline()
            break
        line = tsp.readline()
	#np.write(line)
	#########write more info to native_crash_file.txt
    while line:
        if end_line.search(line):
		#np.close()
            break
        else:
            np.write(line)
        line = tsp.readline()	
    tsp.close()

def getTombstoneFile(folderparser):

    tombstonefiles = folderparser.getFilesBy('nativecrashdropbox')
    tombstonefiles = tombstonefiles.split(',')
    sp = FileSort(tombstonefiles)
    tombstonefiles = sp.fsort()
    tombstonefile = []
    for ts in tombstonefiles:
        if ts.find(".gz") != -1:
            dstfile = ts[:-3]
            ffp = gzip.GzipFile(ts,"r")
            outfile = open(dstfile,"w")
            outfile.write(ffp.read())
            outfile.close()
            tombstonefile.append(dstfile)
        else:
            tombstonefile.append(ts) 
    tombstonefile.sort()
    tombstonefile = list(set(tombstonefile))
    print tombstonefile
    return tombstonefile

def check_corefile(folderparser,native_p,corelist,parsetype):
    
    corefiles = folderparser.getFilesBy(parsetype)
    corefiles = corefiles.split(",")
    tmp_core = []
    for corefile in corefiles:
        for core in corelist:
            if corefile.find(core) != -1:
                tmp_core.append(corefile)

    print "tmp core" + str(tmp_core)
    for cc in tmp_core:
        if cc.find(" ") != -1:
            cct = cc
            cc_new = cct.replace(" ","-").replace("!","-")
            try:
                os.rename(cc,cc_new)
            except:
                pass
            cc = cc_new
        #print "native core file " + str(cc)
        result=os.popen("python readelf.py -l "+cc)
        line = ""
        for p in result:
            line = p
        line = line.strip().split(' ')
        print line
        try:
            size = int(line[-5],16) + int(line[-8],16)
            size_r = os.path.getsize(cc)
            print size_r
	
        #if real_size/gdb_excepted_size >0.85,then copy corefile to postprocess_report folder
            if size_r/size > float(0.85):
                dstfile = native_p + os.path.sep + os.path.basename(cc)
                shutil.copyfile(cc,dstfile)
            else:
                print "corefile size is incorrect."
        except:
            print "cannot get size of corefile"
            dstfile = native_p + os.path.sep + os.path.basename(cc)
            shutil.copyfile(cc,dstfile)
	 
def get_snapshot_file(folderparser,snap_f,native_pp,item):
 
    snapshotfiles = folderparser.getFilesBy(item)
    snapshotfiles = snapshotfiles.split(',')
    dstf = []
    for snapshotfile in snapshotfiles:
        for ss in snap_f:
            if snapshotfile.find(ss) != -1:
                tmp_dstf = native_pp + os.path.sep + os.path.basename(snapshotfile)
                dstf.append(tmp_dstf)
                shutil.copyfile(snapshotfile,tmp_dstf)
    if len(dstf) > 0:
        return dstf
    else:
        return 0

def get_nativecrash_info(tombsf,pl,pr):
    tombstone_regex = re.compile(r'ylog.tombstone 000') 
    native_crash_line_regex = re.compile(r'Fatal signal')
    native_crash_regex = re.compile(r'pid: [0-9]+, tid: [0-9]+,\s*name:\s*.*\s*>>>\s*.*\s*<<<')
    native_crash_module_get_regex = re.compile(r'\s*name: (.\w+)')
    D_LINE_new = re.compile("stack:")
    #D_LINE_new = re.compile("Tombstone written to")
    if os.path.exists(tombsf):
        fd = open(tombsf)
    else:
	#print "Open main file error,return."
        print "No tombstone file for nativecrash"
        return 0
    line = fd.readline()
    nativec = False
    while line:
        if tombstone_regex.search(line):
            pattern = r"(\[.*?\])"
            tmp_time = re.findall(pattern,line,re.M)[-1]
            pr.write("-----------------------------------------------------------------\n")
            pr.write("file: " + tombsf + "\n")
            pl.write("file: " + tombsf + "\n")
            next_native = False
            line = fd.readline()
            while line: 
                if native_crash_regex.search(line):
                    pl.write(tmp_time + " " + line)
                    location_t = line.find("pid: ")
                    native_f = line.strip()[location_t:-1]
                    core_list = native_crash_module_get_regex.search(line).group(1)
                            #time_list.append(tmp_time.replace(":","-"))
                if line.find("signal") != -1:
                    pl.write(line)
                if D_LINE_new.search(line):
                    next_native = True
                    break
                if native_crash_line_regex.search(line):
                    next_native = True
                pr.write(line)
                line = fd.readline()
            '''  
            if ft and native_f:
                #ft.seek(0)
                tline = ft.readline()
                while tline:
                    new_f = False
                    if tline.find(native_f) != -1:
                        pl.write("file: " + traces_file + "\n")
                        while tline:
                            pr.write(tline)
                            if D_LINE_new.search(tline):
                                new_f = True
                                break
                            tline = ft.readline()
                    if new_f:
                        break
                    tline = ft.readline()      
            '''  
        if nativec:
            break 
        line = fd.readline()
    fd.close()
    try:
        return (core_list,tmp_time)
    except:
        return 0 
	      
def parse_native_crash(logdir,devnum):

  native_crash_regex = re.compile(r'pid: [0-9]+, tid: [0-9]+,\s*name:\s*.*\s*>>>\s*.*\s*<<<')
  native_crash_module_get_regex = re.compile(r'\s*name: (.\w+)')
  tombstonefile = []
  flag = False
  result = "No snapshot file."

  if platform.system() == "Linux":
    location = logdir.rfind("/")
  else:
    location = logdir.rfind("\\")
  slogBasePath = logdir[0:location]
  
  if logdir == None:
    print "log directory is needed!"
    #sys.exit(0)
    return 0
  else:
    fp = FolderParser(logdir,devnum)
    reportpath = slogBasePath + os.path.sep + "post_process_report"
    if reportpath == '' or reportpath == None:
      print "get report path failed!"
      print "exit!"
      #sys.exit(0)
      return 0
    print reportpath
    nativepath = reportpath + os.path.sep + "native_crash"
    if os.path.exists(nativepath):
        shutil.rmtree(nativepath)
    if not os.path.exists(nativepath):
        os.makedirs(nativepath)
    #write pid...---ip lines to tmp_core_file, write pid and backtrace lines to native_crash_file and stored in report folder
    native_crash_file = nativepath + os.path.sep + "native_crash_report.txt"
    native_crash_list = nativepath + os.path.sep + "native_crash_list.txt"
    preport = open(native_crash_file,"w+")
    plist = open(native_crash_list,"w+")
    core_list = []
    trace_log = None
    trace_log = fp.getFilesBy("nativecrashtraces")
    trace_log = trace_log.split(",")
    sp = FileSort(trace_log)
    trace_log = sp.fsort()  
    if trace_log:
        for tracefile in trace_log:
            crash_list = get_nativecrash_info(tracefile,plist,preport)
            if crash_list != 0:
                core_list.append(crash_list[0])
	###there,,,ft_p will be written temporarily, just fit function of get_tombstonefile_info 
	###if there is snapshot file, it will be written by snapshot content
        #native_crash_line = get_tombstonefile_info(main_log,np_p,ft_p)
    preport.close()
    plist.close()
    
    ''' 
    plist = open(native_crash_list)
    line = plist.readline()
    time_list = []
    core_list = []
    while line:
        c_flag = False
        if line.find("file: ") != -1:
            line = plist.readline()
            while line:
                if native_crash_regex.search(line):
                    core_list.append(native_crash_module_get_regex.search(line).group(1))
                    tmp_line = line.strip().split(" ")
                    tmp_time = tmp_line[0] + "-" + tmp_line[1].split(".")[0]
                    time_list.append(tmp_time.replace(":","-"))
                if line.find("file: ") != -1:
                    c_flag = True
                    break
                line = plist.readline()
        if c_flag:
            continue
        line = plist.readline()
    '''
    '''
    if len(time_list) > 0:
	dd = get_snapshot_file(fp,time_list,nativepath,"nativecrashsnap")
    '''
    if len(core_list) > 0:
        core_list = set(list(core_list))
        check_corefile(fp,nativepath,core_list,"nativecrashcore")	
    plist.close()	

    dropboxlogs = getTombstoneFile(fp)	    
    tmpfile = os.path.abspath('.') + os.path.sep + "logs" + os.path.sep + "nativecrash_file_tmp.txt"
    tmplist = os.path.abspath('.') + os.path.sep + "logs" + os.path.sep + "nativecrash_list_tmp.txt"
    if len(dropboxlogs) > 0:
	  
        tmpfile_p = open(tmpfile,"w")
        tmplist_p = open(tmplist,"w")
        for dropboxlog in dropboxlogs:
            get_tombstonefile_info(dropboxlog,tmpfile_p,tmplist_p)
		
        tmpfile_p.close()
        tmplist_p.close()	
	
    if os.path.exists(tmplist):
        dropcore = compare_slog_dropbox_native(native_crash_file,native_crash_list,tmpfile,tmplist)
    if dropcore != 0:
        check_corefile(fp,nativepath,dropcore,"nativecrashcore")	
	
    #native_timer_for_mm = native_timer_for_mm.replace(" ","_")
    #print native_timer_for_mm
    #os.system("python parse_mm.py " + "--log-dir " + logdir + " --serial-num " + devnum + " --timer " + "last_time") 


    if os.path.exists(tmpfile):
        os.remove(tmpfile)
    if os.path.exists(tmplist):
        os.remove(tmplist)

##################################################################################################
############parse_watchdog_crash#######################

def get_snapshot_file_info(sfiles,watchdog_file,listfile):
    thread_id_regex = re.compile(r'\s*held by thread\s*(\d+)')
    thread_id_line_regex = re.compile(r'\s*tid=(\d+)')
    tfp = open(watchdog_file,'a+')
    lfp = open(listfile,'a+')
    tid_list = []
    for snap_f in sfiles:
	#print "ss" + snap_f
        try:
            dfp = open(snap_f)
        except:
            print "Cannot open snapshot file, exit."
            tfp.close()
            lfp.close()
            return 0
	#tmp_p = dfp.tell()
        line = dfp.readline()
        tid = None
        main_t = False
        while line:
            if line.find(" tid=1 ") != -1 and line.find("Blocked") != -1:
                pp = tmp_p
		#line_tid = line
                line = dfp.readline()
                while line:
                    if thread_id_regex.search(line):
                        tid = thread_id_regex.search(line).group(1)
                        print tid
                        if tid in tid_list:
                            pass
                        else:
                            tid_list.append(tid)
                            main_t = True
                        break 
                    if line.strip() == "":
                        break
                    line = dfp.readline()
            tmp_p = dfp.tell()
            line = dfp.readline()

        if main_t:
            
            dfp.seek(pp)
            tfp.write("\nfile: " + snap_f + "\n")
            lfp.write("file: " + snap_f + "\n")
            lfp.write(line)
            line = dfp.readline()
            lfp.write(line)
            while line:
                if line.strip() == "":
                    break
                tfp.write(line)
                line = dfp.readline()
            dfp.seek(0)
            tfp.write("\n")
            line = dfp.readline()
            while line:
                if thread_id_line_regex.search(line) and thread_id_line_regex.search(line).group(1) == str(tid):
                    while line:
                        if line.strip() == "":
                            break
                        tfp.write(line)
                        line = dfp.readline()
                    break
                line = dfp.readline()
	    #break
        dfp.close() 
    tfp.close()
    lfp.close()

def compare_slog_dropbox_wt(report_p,list_p,tmpr_p,tmpl_p):

    watchdog_thread_subject = re.compile(r'Subject:\s*(.*)')
    reportp = open(report_p)
    listp = open(list_p)
    tmprp = open(tmpr_p)
    tmplp = open(tmpl_p)
    
    line1 = listp.readlines()
    line2 = reportp.readlines()
    listp.close()
    reportp.close()
	
    line = tmplp.readline()
    corelist = []
    while line:
        if line.find("file: ") != -1:
            file_line = line
            line = tmplp.readline()
            while line and len(line) < 2:
                line = tmplp.readline()
            if watchdog_thread_subject.search(line):
                tmpline = watchdog_thread_subject.search(line).group(1)
            else:
                return 0
            find_flag = False
            for ll in line1:
                if ll.find(tmpline) != -1:
                    find_flag = True
            if find_flag:
		#pass
                tmprp.seek(0)
                mm = tmprp.readline()
                while mm:
                    if mm.find(tmpline) != -1:
                        reportp = open(report_p,"a+")
		        #reportp.write("--------------------------------------------\n")
		        #reportp.write(file_line)
                        reportp.write(mm)
                        mm = tmprp.readline()
                        while mm:
                            if mm.find("file: ") != -1:
                                break
                            reportp.write(mm)
                            mm = tmprp.readline()
                        reportp.close()
                    mm = tmprp.readline()
            else:
	        #name = native_crash_module_get_regex.search(line).group(1)
	        #corelist.append(name)
                listp = open(list_p,"a+")
	#	listp.write("-------------------------------------\n")
                listp.write(file_line)
                listp.write(line) 
                listp.close()
                tmprp.seek(0)
                mm = tmprp.readline()
                while mm:
                    if mm.find(tmpline) != -1:
                        reportp = open(report_p,"a+")
                        reportp.write("--------------------------------------------\n")
                        reportp.write(file_line)
                        reportp.write(mm)
                        mm = tmprp.readline()
                        while mm:
                            if mm.find("file: ") != -1:
                                break
                            reportp.write(mm)
                            mm = tmprp.readline()
                        reportp.close()
                    mm = tmprp.readline()
                break
		
        line = tmplp.readline()
    tmprp.close()
    tmplp.close()


def get_watchdog_file_info(watchdog,np,ft):
    watchdog_regex = re.compile(r'Blocked in handler on')
    watchdog_regex2 = re.compile(r'Blocked in')
    watchdog_thread_regex = re.compile(r'\((.*?)\)',re.I|re.X)
    #tfp = open(watchdog_file,'w')
    enter = False
    watchdog_traces = []
    #try:
    if os.path.exists(watchdog):
        dfp = open(watchdog)
    #except:
    else:
	#print "Cannot open system_server_watchdog@."
        print "No system_server_watchdog@."
        return 0
    np.write("file: " + watchdog + "\n")
    ft.write("file: " + watchdog + "\n")
    line = dfp.readline()
    while line:
        if watchdog_regex.search(line) or watchdog_regex2.search(line):
            enter = True
            ft.write(line)
            np.write(line)
            w_flag = True
            #tfp.write(line)
	#	posi = dfp.tell()
            watchdog_threads = watchdog_thread_regex.findall(line)
            for watchdog_thread in watchdog_threads:
                watchdog_traces.append('"' + watchdog_thread + '"' + ' ' + 'prio=')
            print watchdog_threads
            for watchdog_trace in watchdog_traces: 
                findf = False
                next_cmd = False
                dfp.seek(0)
                line = dfp.readline()
                i = 0
		    ###find Cmd line: system_server && watchdog_trace.
                while line:
                    if line.find("Cmd line: system_server") != -1:
                        line = dfp.readline()
                        while line:
                            if line.find(watchdog_trace) != -1:
                                np.write(line)
                                findf = True
                                line = dfp.readline()
                                while line:
			    		##until next "trace_thread"
                                    if re.match(r'^(\")',line):
                                        break
                                    else:
                                        np.write(line)
                                        line = dfp.readline()
                                break
                            if line.find("Cmd line: ") != -1:
                                next_cmd = True
                                break
                            line = dfp.readline()
			    ###if didn't find log for current thread trace, and 
			    ###if encounter next cmd line
                        if (not findf) and next_cmd:
                            continue
			    ###if find watchdog_trace or not, quit
                        br = True
                        break
                    line = dfp.readline()
	    ###if thread is ahead of blocked in, the enter can devoid of while 1
        if enter:
            break
        line = dfp.readline()
    dfp.close()

def get_watchdog_crash_file(folderparser):
    global dele
    dele = False
    watchdog_file = []
    watchdog_files = folderparser.getFilesBy("watchdogdropbox")
    watchdog_files = watchdog_files.split(',')
    for wf in watchdog_files:
        if wf.find(".gz") != -1:
            dele = True
            dstfile = wf[:-3]
            dfp = gzip.GzipFile(wf,"r")
            outfile = open(dstfile,"w")
            outfile.write(dfp.read())
            outfile.close()
            watchdog_file.append(dstfile)
        else:
            watchdog_file.append(wf)
    #watchdog_file.sort()
    watchdog_file = list(set(watchdog_file))
    sp = FileSort(watchdog_file)
    watchdog_file = sp.fsort()
    return watchdog_file


def get_snapshot_file_wt(folderparser,t_list,reportpath,parsetype):
    snap_time_regex = re.compile(r'pid\s*\d+\s*at\s*\d+-(\d+)-(\d+)\s*\d+:\d+:\d+')
    snapshot_files =  folderparser.getFilesBy(parsetype)
    snapshot_files = snapshot_files.split(',')
    sp = FileSort(snapshot_files)
    snapshot_files = sp.fsort()
    snapshot_files.reverse() 
    snapfile = []
    for tt in t_list:
        tt = tt.replace("-","")
        if len(snapshot_files) >0:
            aa = open(snapshot_files[-1])
            line = aa.readline()
            while line:
                if snap_time_regex.search(line):
                    tdate = snap_time_regex.search(line).group(1) + snap_time_regex.search(line).group(2) 
                    break
                line = aa.readline()
            aa.close()
            times = tdate+snapshot_files[-1].split("_")[-1].split(".")[0].replace("-","")
            if times < tt:
                if len(snapshot_files) > 1:
                    snapfile.append(snapshot_files[-2])
                    snapfile.append(snapshot_files[-1])
                else:
                    snapfile.append(snapshot_files[-1])
            else:
                i = 0
                for i in range(len(snapshot_files)):
                    aa = open(snapshot_files[i])
                    line = aa.readline()
                    while line:
                        if snap_time_regex.search(line):
                            tdate = snap_time_regex.search(line).group(1) + snap_time_regex.search(line).group(2) 
                            break
                        line = aa.readline()
                    aa.close()
                    times = tdate+snapshot_files[i].split('_')[-1].split('.')[0].replace('-','')
                    if times > tt:
                        if i > 1:
                            snapfile.append(snapshot_files[i-2])
                            snapfile.append(snapshot_files[i-1])
                        else:
                            snapfile.append(snapshot_files[i-1])
                        break

		
    if len(snapfile) != 0:
        for ff in snapfile:
            dstname = reportpath + os.path.sep + os.path.basename(ff)
            shutil.copyfile(ff,dstname)

def get_watchdogcrash_info(sysf,pr,pl):

    watchdog_is_going_to_kill_system_regex = re.compile(r'WATCHDOG IS GOING TO KILL SYSTEM')
    watchdog_killing_system_process_regex = re.compile(r'WATCHDOG KILLING SYSTEM PROCESS')
    pr.write("-------------------------------------------------------------\n")
    pr.write("file: " + sysf + "\n")
    pl.write("file: " + sysf + "\n")
    if os.path.exists(sysf):
        fd = open(sysf)
    else:
        print "No system file for watchdog timeout"
        return 0
    line = fd.readline()
    g_flag = False
    while line:
        c_flag = False
        if watchdog_is_going_to_kill_system_regex.search(line):
            pr.write(line)
            pl.write(line)
            line = fd.readline()
            while line:
                if watchdog_killing_system_process_regex.search(line):
                    g_flag = True
                    pr.write(line)
                    pl.write(line)
                    line = fd.readline()
                if line.find("Watchdog:") != -1:
                    pr.write(line)
                if line.find("Watchdog:") != -1 and line.find("GOODBYE!") != -1:
                    break
                if watchdog_is_going_to_kill_system_regex.search(line):
                    c_flag = True
                    break 
                line = fd.readline()
        if c_flag:
            continue
        line = fd.readline()
    if not g_flag:
        fd.seek(0)
        line = fd.readline()
        while line:
            if watchdog_killing_system_process_regex.search(line):
                g_flag = True
                pr.write(line)
                pl.write(line)
                line = fd.readline()
                while line:
                    if line.find("Watchdog:") != -1:
                        pr.write(line)
                    if line.find("Watchdog:") != -1 and line.find("GOODBYE!") != -1:
                        break
                    line = fd.readline()
	    line = fd.readline()
    fd.close()	      
    if g_flag:
        return g_flag
    else:
        return 0

def getReportDir_wt(folderParser):
     
    if platform.system() == "Linux":
        location = folderParser.rfind("/")
    else:
        location = folderParser.rfind("\\")
    slogBasePath = folderParser[0:location]
    reportDir = slogBasePath + os.path.sep + "post_process_report" + os.path.sep + "watchdog_timeout" 
    if not os.path.exists(reportDir):
        os.makedirs(reportDir)
    reportdir_g = reportDir
    return reportDir

def getReportFile_wt(folderParser):
    reportDir = getReportDir_wt(folderParser)
    reportFile = os.path.join(reportDir, 'watchdog_report.txt')
    return reportFile

def clearReportDir_wt(folderParser):
    reportDir = getReportDir_wt(folderParser) 
    shutil.rmtree(reportDir)

def parse_watchdog_crash(slog_path,devnum):

    watchdog_killing_system_process_regex = re.compile(r'WATCHDOG KILLING SYSTEM PROCESS')
    wat_flag = None
    sys_flag = None
    if slog_path:
        fp = FolderParser(slog_path,devnum)

        clearReportDir_wt(slog_path)
        reportFile = getReportFile_wt(slog_path)
        reportDir = getReportDir_wt(slog_path)
        tmp_watchdog_file = os.path.abspath('.') + os.path.sep + "logs" +os.path.sep + "tmp_watchdog_file.txt"
        watchdog_list = reportDir + os.path.sep + "watchdog_list.txt"
        preport = open(reportFile,"w+")
        plist = open(watchdog_list,"w+")
	####parse info from dropbox/file
        systemfiles = None
        systemfiles = fp.getFilesBy("watchdogcrash")
        systemfiles = systemfiles.split(",")
        sp = FileSort(systemfiles)
        systemfiles = sp.fsort()
        if systemfiles:
	    #tmp_result = get_system_watchdog(systemfiles,tmp_watchdog_file)
            for systemfile in systemfiles: 
                sys_flag = get_watchdogcrash_info(systemfile,preport,plist)
        preport.close()
        plist.close()

    
        plist = open(watchdog_list)
        line = plist.readline()
        time_list = []
        while line:
            c_flag = False
            if line.find("file: ") != -1:
                line = plist.readline()
                while line:
                    if watchdog_killing_system_process_regex.search(line):
                        ll = line.strip().split(" ")
                        tmp_time = ll[0] + "-" + ll[1].split(".")[0]
                        time_list.append(tmp_time.replace(":","-"))
                    if line.find("file: ") != -1:
                        c_flag = True
                        break
                    line = plist.readline()
            if c_flag:
                continue
            line = plist.readline()
        '''
        if len(time_list) > 0:
            get_snapshot_file_wt(fp,time_list,reportDir,"watchdogsnap")
        '''
        plist.close()


        dropboxlogs = get_watchdog_crash_file(fp)	    
        tmpfile = os.path.abspath('.') + os.path.sep + "logs" + os.path.sep + "watchdogcrash_file_tmp.txt"
        tmplist = os.path.abspath('.') + os.path.sep + "logs" + os.path.sep + "watchdogcrash_list_tmp.txt"
    if dropboxlogs:
	  
        tmpfile_p = open(tmpfile,"w")
        tmplist_p = open(tmplist,"w")
        for dropboxlog in dropboxlogs:
            wat_flag = get_watchdog_file_info(dropboxlog,tmpfile_p,tmplist_p)
		
        tmpfile_p.close()
        tmplist_p.close()	
    if os.path.exists(tmplist):
        dropcore = compare_slog_dropbox_wt(reportFile,watchdog_list,tmpfile,tmplist)
		
    if os.path.exists(tmpfile):
        os.remove(tmpfile)
    if os.path.exists(tmplist):
        os.remove(tmplist)
    if (wat_flag and wat_flag != 0) or (sys_flag and sys_flag != 0):
        pass
    else:
	
        snapfiles = fp.getFilesBy("watchdogsnap")
        snapfiles = snapfiles.split(",") 
        sp = FileSort(snapfiles)
        snapfiles = sp.fsort()
        print snapfiles
        get_snapshot_file_info(snapfiles,reportFile,watchdog_list)		
    
#####################################################################################################
################parse_lowpower###############


def get_files(filep,TYPE):
    files = filep.getFilesBy(TYPE)
    print files
    if files:
        return files.split(',')
    return None

def data_last_kernel_find_cap0(filep,preport,plist):
    low_power_regex = re.compile(r'cap:0')
    fd = open(filep)
    line = fd.readline()
    while line:
        if low_power_regex.search(line):
            tmp = "file:%s\n"%filep
            plist.write(tmp)
            plist.write(tmp)
            preport.write(line)
            preport.write(line)
            return True
        line = fd.readline()
    return False

def fileAnalyst(file_param,preport,plist):
    low_power_regex = re.compile(r'cap:0')
    tempreture_regex = re.compile(r'tempreture \d+ is Critical')
    current_regex = re.compile(r'current:(.\d+).*')
    vbat_regex = re.compile(r'vbat:(.\d+).*')
    state_regex = re.compile(r'state:(\d+)')
    ret = False
    cap0_flag = False
    line_count = 0
    last_info = 0

    print file_param
    fd = open(file_param)
    line = fd.readline()
    while line:
        if low_power_regex.search(line) :
            ret = True
        if low_power_regex.search(line) and current_regex.search(line) and vbat_regex.search(line):
            line_count += 1
        line = fd.readline()
    if ret == False:
        return ret
    if line_count == 0:
        return ret
    fd.seek(0)
    line = fd.readline()

    while line:
        if low_power_regex.search(line) and current_regex.search(line) and vbat_regex.search(line):
            if line_count > 3:
                line_count -= 1
                line = fd.readline()
                continue
            current = current_regex.search(line).group(1) 
            vbat = vbat_regex.search(line).group(1) 

            preport.write("\n************Power consumption***************\n")
            preport.write("\nfile: %s\n"%file_param)
            preport.write(line)
            plist.write("\nfile: %s\n"%file_param)
            plist.write(line)
            for i in range(0,4):
                line = fd.readline()
                preport.write(line)
                if state_regex.search(line):
                    state = state_regex.search(line).group(1)
                    state = int(state)
                    if state == 3 and current < 0 :
                        preport.write("*****Phone is charging but the power concume is too soon********\n")
                    break
            try:
                current = int(current)
                vbat = int(vbat)

		#print "dong:current:%d vbat:%d state %d\n"%(current ,vbat ,state)
                if current < 0 and vbat < 3200 and vbat > 0:
                    plist.write("Result : low power !!!!!!!!!!!!!!!!!!!!\n")
                    preport.write("Result : low power !!!!!!!!!!!!!!!!!!!!\n")
            except ValueError:
                pass
        line = fd.readline()

    return ret

def cacular_time(data_file, sd_file,preport,plist):
    ret = False
    data_start = 0
    sd_end = 0
    dp = open(data_file)
    line = dp.readline()
    while line:
        if line.find("cap:") != -1:
            for i in range(0,4):
                preport.write(line)
                break
            break
        line = dp.readline()

    dp.seek(0)
    line = dp.readline()
    while line:
        if line[0] >= '0' and line[0] <= '9':
		#data_start = line.split(" ")
		#data_start = data_start[0] + "-" + data_start[1]
            break
        line = dp.readline()
    dp.close()
    d = [datetime.datetime.now().year, string.atoi(line[0:2]), string.atoi(line[3:5]), 
    string.atoi(line[6:8]), string.atoi(line[9:11]), string.atoi(line[12:14])]
    data_start = datetime.datetime(d[0],d[1],d[2],d[3],d[4],d[5])
    print data_start

    sp = open(sd_file)
    sp_count = 0
    line = sp.readline()
    while line:
        if line.find("cap:") != -1:
            sp_count += 1
        line = sp.readline()
         
    sp.seek(0)
    line = sp.readline()
    while line:
        if sp_count == 1:
            for i in range(0,4):
                preport.write(line)
                line = sp.readline()
            break
        line = sp.readline()

    sp.seek(0)
    tmpline = sp.readline()
    while tmpline:
        if tmpline[0] >= '0' and tmpline[0] <= '9':
            line = tmpline
            break
        tmpline = sp.readline()
    sp.close()
	#sd_end = tmpline.split(" ")
	#sd_end = sd_end[0] + "-" + sd_end[1]
    d = [datetime.datetime.now().year, string.atoi(line[0:2]), string.atoi(line[3:5]), 
         string.atoi(line[6:8]), string.atoi(line[9:11]), string.atoi(line[12:14])]
    sd_end = datetime.datetime(d[0],d[1],d[2],d[3],d[4],d[5])
    print sd_end
			
   # if (data_start - sd_end).seconds > 3600:
    time12 = (data_start + 8 - sd_end).seconds
    ret = True
    if time12 > 3600:#
        plist.write("file:")
        plist.write(sd_file)
        plist.write("file:")
        plist.write(data_file)
        plist.write('***************Maybe freeze screen and lowpower charger********************\n')
        plist.write("The data's log' time to the sdcard log's time is: %d seconds\n" %time12)
        preport.write('***************Maybe freeze screen and lowpower charger********************\n')
        preport.write("The data's log' time to the sdcard log's time is: %d seconds\n\n" %time12)
        print "Freeze screen and lowpower charger"
    else:
        plist.write('***************Maybe not freeze screen and lowpower charger********************\n')
        preport.write('***************Maybe not freeze screen and lowpower charger********************\n')
        print "Charger error,please check usb device."	

    return ret

def find_android_key_word(filep,preport,plist):
    battery_meter_view_regex = re.compile(r'BatteryMeterView')
    level_regex = re.compile(r'level')
    try:
        fd = open(filep)
    except:
        print "find android_key_word\n"
        return 
    count = 0
    line = fd.readline()
    while line:
        if battery_meter_view_regex.search(line) and level_regex.search(line):
            count += 1
        line = fd.readline()
            
    fd.seek(0)
    line = fd.readline()
    while line:
        if battery_meter_view_regex.search(line) and level_regex.search(line):
            count -= 1
            if count == 1:
                plist.write("file:")
                plist.write(filep)
                plist.write("\n")
                plist.write(line)
                preport.write("*********Battery Meter level  !***************\n")
                preport.write("file:")
                preport.write(filep)
                preport.write("\n")
                preport.write(line)
                return
        line = fd.readline()

def find_tempreture_key_word(filep,preport,plist):
    Thermal_regex = re.compile(r'ThermalActionShutdown')
    ret = False
    try:
        fd = open(filep)
    except:
        print "find tempretrue key word\n"
        return
    line = fd.readline()
    print "tempreture key word\n"
    while line:
        if Thermal_regex.search(line):
		#if tempreture_regex.search(line):
            ret = True
			#print line
            plist.write("**********Thermal!!!************\n")
            plist.write("file: %s\n" %filep)
            plist.write(line)
            preport.write("**********Thermal!!!************\n")
            preport.write("file: %s\n" %filep)
            preport.write(line)
            break
	line = fd.readline()
    print "tempretrue ret[%d]\n"%ret
    return ret

def find_tempreture(filep,preport,plist,last_temp):
    Thermal_kernel_regex = re.compile(r'\s*sensor_id:.*\s*temp:(\d+)')
    Thermal_critical_regex = re.compile(r'critical temperature reached')
    cap_regex = re.compile(r'\s*cap:(\d+)')
    ret = False
    count = 0
    try:
        fd = open(filep)
    except:
        print "find tempretrue key word\n"
        return
    line = fd.readline()
    print "tempreture key word\n"
    while line:
        if cap_regex.search(line):
            last_temp[len(last_temp) - 1] = cap_regex.search(line).group(1)
            #print last_temp[10]
        if Thermal_kernel_regex.search(line):
            tmp_count = count % (len(last_temp)-1)
            last_temp[tmp_count] = line
            count += 1
		#if tempreture_regex.search(line):
            tempre = Thermal_kernel_regex.search(line).group(1)
            if int(tempre) > 105000:
                ret = True
                plist.write("**********Thermal!!!************\n")
                plist.write("file: %s\n" %filep)
                plist.write(line)
                preport.write("**********Thermal!!!************\n")
                preport.write("file: %s\n" %filep)
                preport.write(line)
                line = fd.readline()
                while line:
                    #if Thermal_critical_regex.search(line):
                    if Thermal_kernel_regex.search(line) and int(Thermal_kernel_regex.search(line).group(1)) > 105000:
                    #    plist.write(line)
                        plist.write(line)
                        preport.write(line)
                    if Thermal_critical_regex.search(line):
                        plist.write(line)
                        preport.write(line)
                    line = fd.readline()
                break
        line = fd.readline()
    print "tempretrue ret[%d]\n"%ret
    return ret

def find_freezescreen(filep,preport,plist):
    low_power_regex = re.compile(r'cap:0')
    ret = False
    try:
        fd = open(filep)
    except:
        print "find internal last ylog kernel log error\n"
        return 0
    line = fd.readline()
    print "tempreture key word\n"
    while line:
        if low_power_regex.search(line):
            ret = True
            plist.write("file: %s\n" %filep)
            plist.write(line)
            plist.write("There may be freezescreen!!!")
            preport.write("file: %s\n" %filep)
            preport.write(line)
            preport.write("There may be freezescreen!!!")
        line = fd.readline()
    return ret

def print_data_sd_cap(data_file, sd_file,preport,plist):
    cap_regex = re.compile(r',cap:')
    preport.write("*********Not high temperatrue!!!!!***************\n")
    plist.write("file:")
    plist.write(data_file)
    plist.write("\n")
    preport.write("file:")
    preport.write(data_file)
    preport.write("\n")
    dp = open(data_file)
    line = dp.readline()
    while line:
        if cap_regex.search(line):
            for i in range(0,4):
                plist.write(line)
                preport.write(line)
                line = dp.readline()
            break
        line = dp.readline()
    dp.close()

    preport.write("\n")
        
    plist.write("file:")
    plist.write(sd_file)
    plist.write("\n")
    preport.write("file:")
    preport.write(sd_file)
    preport.write("\n")
    sp = open(sd_file)
    sp_count = 0
    line = sp.readline()
    while line:
        if cap_regex.search(line):
            sp_count += 1
        line = sp.readline()
         
    sp.seek(0)
    line = sp.readline()
    while line:
        if cap_regex.search(line):
            sp_count -= 1
        if sp_count == 1:
            for i in range(0,4):
                plist.write(line)
                preport.write(line)
                line = sp.readline()
            break
        line = sp.readline()
    sp.close()

def parse_lowpower(input_dir,devnum):
    low_power_regex = re.compile(r'cap:0')
    tempreture_regex = re.compile(r'tempreture \d+ is Critical')
    current_regex = re.compile(r'current:(.\d+).*')
    vbat_regex = re.compile(r'vbat:(.\d+).*')

    if platform.system() == "Linux":
        location = input_dir.rfind("/")
    else:
        location = input_dir.rfind("\\")
    slogBasePath = input_dir[0:location]
  
    if input_dir == None:
        print "log directory is needed!"
        return 0
    else:
        fp = FolderParser(input_dir,devnum)
        logPath = None
        logPath = get_files(fp,"lowpower")
        if logPath:
            tmpfiles = FileSort(logPath)
            logPath = tmpfiles.fsort()
        else:
            return 0

        data_kernel_file_exist_flag = False
        sd_kernel_file_exist_flag = False
        sd_kernel_file = []
        android_main_file_exist_flag = False
        last_android_main_file_exist_flag = False
        last_android_main_file = []
        data_misc_cmdline = False

        reportpath = slogBasePath + os.path.sep + "post_process_report"
        if reportpath == '' or reportpath == None:
            print "get report path failed!"
            print "exit!"
            return 0
        print reportpath
        lowpower_path = reportpath + os.path.sep + "low_power"
        if os.path.exists(lowpower_path):
            shutil.rmtree(lowpower_path)
        if not os.path.exists(lowpower_path):
            os.makedirs(lowpower_path)

        lowpower_file = lowpower_path + os.path.sep + "lowpower_report.txt"
        lowpower_list = lowpower_path + os.path.sep + "lowpower_list.txt"
        preport = open(lowpower_file,"w+")
        plist = open(lowpower_list,"w+")
        tmpfile = os.path.abspath('.') + os.path.sep + "logs" + os.path.sep + "lowpower_file_tmp.txt"
        tmplist = os.path.abspath('.') + os.path.sep + "logs" + os.path.sep + "lowpower_list_tmp.txt"
    
        freezescreen = False
        for files in logPath:
            if files.find("kernel") != -1:
                sd_kernel_file_exist_flag = True
                sd_kernel_file.append(files)
    
            if files.find("main") != -1:
                last_android_main_file_exist_flag = True
                last_android_main_file.append(files)
        if sd_kernel_file_exist_flag:
            for sd_kernel_log_file in sd_kernel_file:
                ret = fileAnalyst(sd_kernel_log_file,preport,plist)
                if not ret:#file_analysis
                    base_dir = os.path.dirname(os.path.dirname(sd_kernel_log_file))
                    for sd_last_android_main_file in last_android_main_file:
                        if os.path.dirname(os.path.dirname(sd_last_android_main_file)) == base_dir:
                            ret = find_tempreture_key_word(sd_last_android_main_file,preport,plist)	
                            if not ret:
                                #preport.write("*****No result 3")
                                initv = ""
                                last_tempre = [initv for i in range(11) ]
                                preport.write("file: "+sd_kernel_log_file+"\n")
                                plist.write("file: "+sd_kernel_log_file+"\n")
                                plist.write("Last temprature values and last cap value will be written to the lowpower_report.txt\n")
                                
                                ret = find_tempreture(sd_kernel_log_file,preport,plist,last_tempre)
                                #将找到的最后几行的温度打印出来
                                for i in range(len(last_tempre)):
                                    if i == (len(last_tempre) - 1):
                                        preport.write("cap :" + last_tempre[i] + "\n")
                                    else:
                                        preport.write(last_tempre[i])
                                    #print (last_tempre[i])
                                if not ret:
                                    freezescreen = True
        else:#sd_last_kernel
            print("********* There is not main log1\n")
            preport.write("\nNo kernel log file in the (externel_storage/last_log/kernel/)\n")
            if android_main_file_exist_flag == True:
                for sd_last_android_main_file in last_android_main_file:
                     find_android_key_word(sd_last_android_main_file,preport,plist)
                else:
                    preport.write("there is not file:")
                    preport.write(sd_last_android_main_file)
                    freezescreen = True
        if freezescreen:
            kernel_log = input_dir + os.path.sep + "internal_storage" + os.path.sep + "last_ylog" + os.path.sep + "ylog1" + os.path.sep + "kernel" + os.path.sep + "kernel.log"
            print kernel_log
            find_freezescreen(kernel_log,preport,plist)

	
#	except:
#		print "************There is abnormal phenomenon!!!!!!***********\n"
#		pass
        preport.close()
        plist.close()
	

    if os.path.exists(tmpfile):
        os.remove(tmpfile)
    if os.path.exists(tmplist):
        os.remove(tmplist)

############parse_kmemleak##################

def check_list(data, List):
    ret = False

    for i in range(0,len(List)):
        if data == List[i]:
             ret = True

    return ret

def read_kmemleak_to_list(destFile):
    kmemleak_func_addr_regex = re.compile(r'\[<\w+>\]')
    fd = open(destFile)
    line = fd.readline()
    func_addr_list = []

    while line:
        #print line
        if line.find("kmemleak_alloc") != -1 or line.find("kmem_cache_alloc_trace") != -1:
            line = fd.readline()
            func_addr = kmemleak_func_addr_regex.search(line).group()[2:-2]
            if not check_list(func_addr, func_addr_list):
                func_addr_list.append(func_addr)
        line = fd.readline()
    return func_addr_list

def parse_kmemleak(input_dir, devnum):

    if platform.system() == "Linux":
	location = input_dir.rfind("/")
    else:
	location = input_dir.rfind("\\")
    slogBasePath = input_dir[0:location]
  
    if input_dir == None:
	print "log directory is needed!"
	return 0
    else:
	fp = FolderParser(input_dir,devnum)
        logPath = get_files(fp,"kmemleak")
        if logPath:
            tmpfiles = FileSort(logPath)
            logPath = tmpfiles.fsort()

    if not logPath:
        return
    LogFile = logPath[0]
    if not os.path.exists(LogFile[0]):
        print "kmemleak: There is no kmemleak file\n"
        return
    print "kmemleak:"
    print LogFile
    vmlinux_f = download_vmlinux()
    print "kmemleak: "+vmlinux_f

    memleakCmd_vmlinux = vmlinux_f

    if not os.path.exists(memleakCmd_vmlinux):
        print "kmemleak: There is no vmlinux file\n"
        return 

    reportpath = slogBasePath + os.path.sep + "post_process_report"
    if reportpath == '' or reportpath == None:
        print "get report path failed!"
        print "exit!"
        return 0
    print reportpath
    kmemleak_path = reportpath + os.path.sep + "kmemleak"
    if os.path.exists(kmemleak_path):
        shutil.rmtree(kmemleak_path)
    if not os.path.exists(kmemleak_path):
        os.makedirs(kmemleak_path)

    kmemleak_file = kmemleak_path + os.path.sep + "kmemleak_report.txt"

    memleakCmd = "./tools/aarch64-linux-android-addr2line  -e "
    memleakCmd_para = " -p -i "
    memleakCmd_to = " >> "
    memleakCmd_dest_file = kmemleak_file

    memleakList = read_kmemleak_to_list(LogFile)

    if os.path.exists(memleakCmd_dest_file):
        os.remove(memleakCmd_dest_file)

    for i in range(0,len(memleakList)):
        print memleakList[i]
        os.system(memleakCmd + memleakCmd_vmlinux + memleakCmd_para + " " + memleakList[i] + memleakCmd_to + memleakCmd_dest_file)

############parse_anr##################
def getReportDir_anr(folderParser):
     
    if platform.system() == "Linux":
        location = folderParser.rfind("/")
    else:
        location = folderParser.rfind("\\")
    slogBasePath = folderParser[0:location]
    reportDir = slogBasePath + os.path.sep + "post_process_report" + os.path.sep + "anr" 
    if not os.path.exists(reportDir):
        os.makedirs(reportDir)
    reportdir_g = reportDir
    return reportDir


def radio_parse(rad_file):
    radio_regex = re.compile(r'WAKE_LOCK_TIMEOUT')
    radio_num_regex = re.compile(r'mRequestList=(\d+)')
    radio_info_regex = re.compile(r'D\s+RILJ\s+:\s+(\d+):')
    rout_fd = open(rad_file,'w')
    for r_file in radio_file:
        r_fd = open(r_file)
        line = r_fd.readline()
        while line:
            if radio_regex.search(line):
                rout_fd.write(line)
                if radio_num_regex.search(line): 
                    num = int(radio_num_regex.search(line).group(1)) - 1
                line = r_fd.readline()
                while line:
                    if radio_info_regex.search(line):
                        rout_fd.write(line)
                        if radio_info_regex.search(line).group(1) == num:
                            break
                    line = r_fd.readline()
            line = r_fd.readline()
        r_fd.close()
    rout_fd.close()
                
def system_parse(c_pid,cur_fd_file):
    #print "Enter system parse"
    cur_fd_out = open(cur_fd_file,'a+')
    system_anr_pid_regex = re.compile(r'ActivityManager:\s*PID:\s*(\d+)') 
    for sys_file in system_file:
        sys_fd = open(sys_file)
        line = sys_fd.readline()
        i = 0
        while line:
            try:
                if ((system_anr_pid_regex.search(line)) and (system_anr_pid_regex.search(line).group(1) == c_pid[0])):
                    cur_fd_out.write("********************system   Begin    ********************\n")
                    cur_fd_out.write("%s\n" %sys_file)
                    while (i < 10):
                        line = line.strip()
                        cur_fd_out.write(line+'\n')
                        line = sys_fd.readline()
                        i  += 1
                    cur_fd_out.write("********************system   End    ********************\n")
            except:
                pass
            line = sys_fd.readline() 
        sys_fd.close()
    cur_fd_out.close()

def snapshot_parse(c_pid,cur_fd_file):
    #print "Enter snapshot parse"
    cur_fd_out = open(cur_fd_file, 'a+')
    snapshot_pid_regex = re.compile(r'-----\s*pid\s*(\d+)')
    snapshot_pid_end_regex = re.compile(r'-----\s*end\s*(\d+)')
    snapshot_meminfo_start_regex = re.compile(r'============\s*meminfo\s*')
    snapshot_meminfo_end_regex = re.compile(r'============\s*query_task_fd\s*')
    #for snap_file in snapshot_file:
    for snap_file in traces_file:
        snap_fd = open(snap_file)
        line = snap_fd.readline()
        while line :
            try:
                if ((snapshot_pid_regex.search(line)) and (snapshot_pid_regex.search(line).group(1) == c_pid[0])):
                    cur_fd_out.write("********************traces   Begin    ********************\n")
                    cur_fd_out.write("%s\n" %snap_file)
                    while line:
                        line = line.strip()
#           print line
#                   snap_lines.append(line)
                        cur_fd_out.write(line+'\n')
                        if ((snapshot_pid_end_regex.search(line)) and (snapshot_pid_end_regex.search(line).group(1))):
                            line = snap_fd.readline()
                            line = snap_fd.readline()
                            if snapshot_meminfo_start_regex.search(line):
                                while line:
                                    line = line.strip()
                                    cur_fd_out.write(line+'\n')
                                    if snapshot_meminfo_end_regex.search(line):
                                        cur_fd_out.write("********************  traces  End     ********************\n")
                                        break
                                    line = snap_fd.readline()
                                break
                            else:
                                cur_fd_out.write("********************  traces  End     ********************\n")
                                break
                        line = snap_fd.readline()
            except:
                pass
            line = snap_fd.readline()
        snap_fd.close()
    cur_fd_out.close()
#    if snap_lines:
#   return snap_lines
#    else:
#       print "no according snapshot file"    

def GCtime(cur_anr_begin_time,cur_out_file):
    #print "enter GCtime"
    #print cur_anr_begin_time
#    str_cur_anr_begin_time = str(cur_anr_begin_time)
    gc_for_alloc_regex = re.compile(r'GC_FOR_ALLOC')
    get_gc_for_alloc_regex = re.compile(r'total (\d+)')
# type C
    wait_for_concurrent_regex = re.compile(r'WAIT_FOR_CONCURRENT_GC')
    get_wait_for_concurrent_regex = re.compile(r'blocked (\d+)')
# type B
    gc_concurrent_regex = re.compile(r'GC_CONCURRENT')
    get_gc_concurrent_regex1 = re.compile(r'paused (\d+)')
    get_gc_concurrent_regex2 = re.compile(r'\+(\d+)')

    cur_fd_out = open(cur_out_file, 'r')
    gc_for_alloc = 0
    gc_concurrent = 0
    wait_for_concurrent = 0
    temp1 = 0
    fd_out_position = cur_fd_out.tell()
    cur_fd_out.close()
    #print "before w+++++++++++" +str(fd_out_position)
#    print "u_main_file " +str(u_main_file)
    for m_file in u_main_file:
        find_f = False
        end_f = False
	#print m_file
        cur_fd_out = open(cur_out_file,'a+')
        m_fd = open(m_file)
        line = m_fd.readline()
        cur_fd_out.write("******************** main file GCtime  Begin    ********************\n" )
        cur_fd_out.write("%s\n" %m_file)
        while line :
	    #print line
            ppo = m_fd.tell()
            exit_f = False
            for i in range(20000):
            	#print i
                try:
                    line = m_fd.readline()
                except:
                    exit_f = True
                    break
            if exit_f:
                end_f = True
                break
	    #print "1000000000000000000000000000000000000"
            if line[0] >= '0' and line[0] <= '9':
                #d = [datetime.datetime.now().year, string.atoi(line[0:2]), string.atoi(line[3:5]),string.atoi(line[6:8]), string.atoi(line[9:11]), string.atoi(line[12:14]), string.atoi(line[15:18])*1000]
                d = [string.atoi(cur_anr_begin_time[0:4]), string.atoi(line[0:2]), string.atoi(line[3:5]),string.atoi(line[6:8]), string.atoi(line[9:11]), string.atoi(line[12:14]), string.atoi(line[15:18])*1000]
                temp = datetime.datetime(d[0],d[1],d[2],d[3],d[4],d[5],d[6])
                #if (((temp - cur_anr_begin_time).days*24*3600 + (temp - cur_anr_begin_time).seconds) > 8):
		#print temp
                if temp > cur_anr_begin_time:
                    m_fd.seek(ppo)
                    line = m_fd.readline()
                    break
                else:
                    continue
        if end_f:
            continue
        while line :
	    #if len(line) >1:
            try:
                if line[0] >= '0' and line[0] <= '9':
                    d = [datetime.datetime.now().year, string.atoi(line[0:2]), string.atoi(line[3:5]),string.atoi(line[6:8]), string.atoi(line[9:11]), string.atoi(line[12:14]), string.atoi(line[15:18])*1000]
                    temp = datetime.datetime(d[0],d[1],d[2],d[3],d[4],d[5],d[6])
                    if (((temp - cur_anr_begin_time).days*24*3600 + (temp - cur_anr_begin_time).seconds) > 8):
                        break
#           if (((temp - cur_anr_begin_time).days*24*3600 + (temp - cur_anr_begin_time).seconds) < 8 or (((cur_anr_begin_time - temp).days*24*3600 + (cur_anr_begin_time - temp).seconds) < 8)):
                    if ((abs(temp - cur_anr_begin_time).days*24*3600 + abs(temp - cur_anr_begin_time).seconds) < 8):
#           temp2 = abs(temp - cur_anr_begin_time).days*24*3600 + abs(temp - cur_anr_begin_time).seconds
#           print "temp2 " +str(temp2)
                        find_f = True
                        if gc_for_alloc_regex.search(line):
                            line = line.strip()
                            cur_fd_out.write(line+'\n')
                        if gc_concurrent_regex.search(line):
                            line = line.strip()
                            cur_fd_out.write(line+'\n')
                            temp1 = temp
                        if wait_for_concurrent_regex.search(line):
                            if temp != temp1:
                                line = line.strip()
                                cur_fd_out.write(line+'\n')
                line = m_fd.readline()
	    #else:
            except:
                pass
        cur_fd_out.flush()
        pp = cur_fd_out.tell()
        #print "after w+++++++++++" +str(pp)
        cur_fd_out.seek(fd_out_position)
        pp = cur_fd_out.tell()
        #print "after seek+++++++++++" +str(pp)
        line = cur_fd_out.readline()
        while line :
            if gc_for_alloc_regex.search(line):
                gc_for_alloc += string.atoi(get_gc_for_alloc_regex.search(line).group(1))
            if gc_concurrent_regex.search(line):
                gc_concurrent += string.atoi(get_gc_concurrent_regex1.search(line).group(1))
                gc_concurrent += string.atoi(get_gc_concurrent_regex2.search(line).group(1))
            if wait_for_concurrent_regex.search(line):
                wait_for_concurrent += string.atoi(get_wait_for_concurrent_regex.search(line).group(1))
            line = cur_fd_out.readline()
        pp = cur_fd_out.tell()
        #print "after r+++++++++++" +str(pp)
        total = gc_for_alloc + gc_concurrent + wait_for_concurrent
        cur_fd_out.close()
        cur_fd_out = open(cur_out_file, 'a+')
        
        cur_fd_out.write("******************** Total time A    ********************\n")         
        cur_fd_out.write('totalA GC FOR ALLOC = %d\n' % gc_for_alloc)   
        cur_fd_out.write("******************** Total time B    ********************\n")             
        cur_fd_out.write('totalB GC CONCURRENT = %d\n' % gc_concurrent) 
        cur_fd_out.write("******************** Total time C    ********************\n")             
        cur_fd_out.write('totalC WAIT FOR CONCURRENT = %d\n' % wait_for_concurrent) 
        cur_fd_out.write("******************** Total time    ********************\n")               
        cur_fd_out.write('total = %d\n' % total)    
        cur_fd_out.write("********************  main  End     ********************\n")
        
        m_fd.close()
        cur_fd_out.close()
        if find_f:
            break
	    
def main_parse(cur_anr_begin_time,cur_fd_out_file):
    start_sprd_cpu_regex = re.compile(r'------------- start print sprd cpu info -------------')
    end_sprd_cpu_regex = re.compile(r'------------- end print sprd cpu info -------------')
    global u_main_file
    #print "enter main_parser"
    print cur_anr_begin_time
    u_main_file = []	
    cur_fd_out = open(cur_fd_out_file, 'a+')
    str_cur_anr_begin_time = str(cur_anr_begin_time)
    for m_file in main_file:
        find_f = False
        end_f = False
        m_fd = open(m_file)
        line = m_fd.readline()
        while line :
	    #print line
            ppo = m_fd.tell()
            exit_f = False
            for i in range(20000):
		#print i
                try:
                    line = m_fd.readline()
                except:
                    exit_f = True
                    break
            if exit_f:
                end_f = True
                break
	    #print "1000000000000000000000000000000000000"
            try:
                if line[0] >= '0' and line[0] <= '9':
                    #d = [datetime.datetime.now().year, string.atoi(line[0:2]), string.atoi(line[3:5]),string.atoi(line[6:8]), string.atoi(line[9:11]), string.atoi(line[12:14]), string.atoi(line[15:18])*1000]
                    d = [string.atoi(str_cur_anr_begin_time[0:4]), string.atoi(line[0:2]), string.atoi(line[3:5]),string.atoi(line[6:8]), string.atoi(line[9:11]), string.atoi(line[12:14]), string.atoi(line[15:18])*1000]
                    temp = datetime.datetime(d[0],d[1],d[2],d[3],d[4],d[5],d[6])
                #if (((temp - cur_anr_begin_time).days*24*3600 + (temp - cur_anr_begin_time).seconds) > 8):
		#print temp
                    if temp > cur_anr_begin_time:
                        m_fd.seek(ppo)
                        line = m_fd.readline()
                        break
                    else:
                        continue
            except:
                pass
        if end_f:
            continue
        ff = False
        while line :
            if start_sprd_cpu_regex.search(line):
                d = [string.atoi(str_cur_anr_begin_time[0:4]), string.atoi(line[0:2]), string.atoi(line[3:5]),string.atoi(line[6:8]), string.atoi(line[9:11]), string.atoi(line[12:14]), string.atoi(line[15:18])*1000]
                temp = datetime.datetime(d[0],d[1],d[2],d[3],d[4],d[5],d[6])
                #if (abs((int(line[13]) - int(str_cur_anr_begin_time[18])) < 8)):
		#if (((temp - cur_anr_begin_time).days*24*3600 + (temp - cur_anr_begin_time).seconds) < 8):
                if (((cur_anr_begin_time - temp).days*24*3600 + (cur_anr_begin_time -temp).seconds) < 8):
                    ff = True
                    cur_fd_out.write("******************** main   Begin    ********************\n" )
                    cur_fd_out.write("%s\n" %m_file)
                    u_main_file.append(m_file)
                    i = 0
                    while line:
                        i += 1
                        line = line.strip()
                        cur_fd_out.write(line+'\n')
                        if end_sprd_cpu_regex.search(line):
                            cur_fd_out.write("********************  main  End     ********************\n")
                            break
                        if i > 100:
                            break
                        line = m_fd.readline()
                    break
            line = m_fd.readline()
        m_fd.close()
        if ff:
            break 
    cur_fd_out.close()
    
def getAnrBeginTime(fd, pid,out_file,datatt):

    global anr_begin_time, anr_type, system_position, g_sys_position
    anr_pid_regex = re.compile(r'\s+am_anr\s+')
    anr_pid_get_regex = re.compile(r'am_anr\s*:\s*.0.(\d+)')
    Inputdispatch_reason_regex = re.compile(r'Input dispatching timed out')
    Boardcast_reason_regex = re.compile(r'Broadcast of Intent')
    Service_reason_regex = re.compile(r'Executing service')
    Service_reason_regex_2 = re.compile(r'executing service')
    ContentProvider_reason_regex = re.compile(r'ContentProvider not responding')
    system_position = fd.tell()
    line = fd.readline()
    while line:
        ## read ANR begin time
        if anr_pid_regex.search(line):
            try:
                if anr_pid_get_regex.search(line).group(1) == pid[0]:
                    d = [datetime.datetime.now().year, string.atoi(line[0:2]), string.atoi(line[3:5]), string.atoi(line[6:8]), string.atoi(line[9:11]), string.atoi(line[12:14]), string.atoi(line[15:18])*1000]
            #d = [string.atoi(datatt[:]), string.atoi(line[0:2]), string.atoi(line[3:5]), string.atoi(line[6:8]), string.atoi(line[9:11]), string.atoi(line[12:14]), string.atoi(line[15:18])*1000]
                    anr_begin_time = datetime.datetime(d[0],d[1],d[2],d[3],d[4],d[5],d[6])
                    print "\nanr_begin_time " + str(anr_begin_time)
                    print line
                    out_fd = open(out_file,'w+')
                    out_fd.write(line + "\n")
                    out_fd.close()
                    main_parse(anr_begin_time,out_file)
            #GCtime(anr_begin_time,out_file)
            
                ## to read reason
                #line = fd.readline()
                    if Inputdispatch_reason_regex.search(line):
                        anr_type = 'Inputdispatch'
                    elif Boardcast_reason_regex.search(line):
                        anr_type = 'Boardcast'
                    elif Service_reason_regex.search(line) or Service_reason_regex_2.search(line):
                        anr_type = 'Service'
                    elif ContentProvider_reason_regex.search(line):
                        anr_type = 'ContentProvider'
            except:
                pass
            #g_sys_position = fd.tell()
            break

        line = fd.readline()
    print "anr type" + str(anr_type)
    
def getAnrList(fd,pidp):

    anr_pid_regex = re.compile(r'\s+am_anr\s+')
    anr_pid_get_regex = re.compile(r'am_anr\s*:\s*.0.(\d+)')
    Inputdispatch_reason_regex = re.compile(r'Input dispatching timed out')
    Boardcast_reason_regex = re.compile(r'Broadcast of Intent')
    Service_reason_regex = re.compile(r'Executing service')
    Service_reason_regex_2 = re.compile(r'executing service')
    ContentProvider_reason_regex = re.compile(r'ContentProvider not responding')

    global anr_pids_list, g_sys_position
    anr_pids_list = []
    time_begin = True
    line = fd.readline()
    while line:
        if time_begin and line[0] >= '0' and line[0] <= '9':
            d = [datetime.datetime.now().year, string.atoi(line[0:2]), string.atoi(line[3:5]), string.atoi(line[6:8]), string.atoi(line[9:11]), string.atoi(line[12:14]), string.atoi(line[15:18])*1000]
            begin = datetime.datetime(d[0],d[1],d[2],d[3],d[4],d[5],d[6])
            end = begin + datetime.timedelta(hours = 10)
            end_time = '%s%d' % (end.strftime('%m-%d %H:%M:%S.'), end.microsecond/1000)
            time_begin = False
            g_sys_position = fd.tell()
            print g_sys_position

        ## read ANR pid
        #print "line--" + str(line)
        
        if anr_pid_regex.search(line):
            pidp.write(line) 
	    
        #print line
        #line=str(fd.readline())
#       print line.strip()
            try:
                current_pid = anr_pid_get_regex.search(line).group(1)
                current_module = line.split(',')[2][4:]
                if current_module.find(':') != -1:
                    current_module = current_module.split(':')[0]
	    #anr_pids_list[current_pid] = current_module
                anr_pids_list.append((current_pid,current_module))
#       print "PID " +  str(current_pid.group(1))
                if Inputdispatch_reason_regex.search(line):
                    anr_type = 'Inputdispatch'
                elif Boardcast_reason_regex.search(line):
                    anr_type = 'Boardcast'
                elif Service_reason_regex.search(line) or Service_reason_regex_2.search(line):
                    anr_type = 'Service'
                elif ContentProvider_reason_regex.search(line):
                    anr_type = 'ContentProvider'
            except:
                pass    
#           print "anr type " + str(anr_type)
#            if current_pid.group(1) != '0':
#                anr_pids_list.append(current_pid.group(1))
        #if line[0] >= '0' and line[0] <= '9' and line[:18] > end_time:
        #    break

        line = fd.readline()
    for key in anr_pids_list:
        #print key,anr_pids_list[key]
        print key

def parseFilePath(flag,input_file):
    global all_path, main_file, system_file, event_file, kernel_file, snapshot_file,radio_file,traces_file
    external_regex = re.compile(r'\last_ylog')
    mainlog_regex = re.compile(r'main')
    systemlog_regex = re.compile(r'system')
    eventlog_regex = re.compile(r'events')
    kernellog_regex = re.compile(r'kernel')
    snapshotlog_regex = re.compile(r'snapshot')
    traceslog_regex = re.compile(r'traces')
    radiolog_regex = re.compile(r'radio')

    # last log
    if flag == 0:
        all_path = input_file.split(',')
        for index in range(len(all_path)):
            if external_regex.search(all_path[index]):
                if mainlog_regex.search(all_path[index]):
                    main_file.append(all_path[index])
                elif systemlog_regex.search(all_path[index]):
                    system_file.append(all_path[index])
                elif eventlog_regex.search(all_path[index]):
                    event_file.append(all_path[index])
                elif kernellog_regex.search(all_path[index]):
                    kernel_file.append(all_path[index])
                elif snapshotlog_regex.search(all_path[index]):
                    snapshot_file.append(all_path[index])
                elif radiolog_regex.search(all_path[index]):
                    radio_file.append(all_path[index])
                elif traceslog_regex.search(all_path[index]):
                    traces_file.append(all_path[index])
        while len(all_path) >0:
            for ele in all_path:
                if external_regex.search(ele):
                    all_path.remove(ele)
                    break
            cc = 0
            for ele in all_path:
                if external_regex.search(ele):
                    cc = 1
            if cc:
                continue
            else:
                break
	#print all_path 

    # current log
    elif flag == 1:
        system_file = []
        main_file = []
        event_file = []
        kernel_file = []
        snapshot_file = []
        traces_file = []
        radio_file = []
        for index in range(len(all_path)):
            if mainlog_regex.search(all_path[index]):
                main_file.append(all_path[index])
            elif systemlog_regex.search(all_path[index]):
                system_file.append(all_path[index])
            elif eventlog_regex.search(all_path[index]):
                event_file.append(all_path[index])
            elif kernellog_regex.search(all_path[index]):
                kernel_file.append(all_path[index])
            elif snapshotlog_regex.search(all_path[index]):
                snapshot_file.append(all_path[index])
            elif radiolog_regex.search(all_path[index]):
                radio_file.append(all_path[index])
            elif traceslog_regex.search(all_path[index]):
                traces_file.append(all_path[index])

    # sort path
    try:
        system_file.sort(reverse = True)
    except:
        pass
    try:
        main_file.sort(reverse = True)
    except:
        pass
    try:
        event_file.sort(reverse = True)
    except:
        pass
    try:
        kernel_file.sort(reverse = True)
    except:
        pass
    try:
        snapshot_file.sort()
    except:
        pass
    try:
        radio_file.sort()   
    except:
        pass
    try:
        traces_file.sort()   
    except:
        pass
    
def parse_anr_ori(input_dir,devnum):

    global all_path, main_file, system_file, event_file, kernel_file, snapshot_file,radio_file,traces_file
    system_position = 0
    main_position = 0
    event_position = 0
    kernel_position = 0
    snapshot_position = 0
    g_position = 0
    g_sys_position = 0

    system_file = []
    main_file = []
    u_main_file = []
    event_file = []
    kernel_file = []
    snapshot_file = []
    traces_file = []
    all_path = []
    radio_file = []

    system_cur_item = 0
    main_cur_item = 0
    event_cur_item = 0
    kernel_cur_item = 0
    snapshot_cur_item = 0
    g_item = 0
    radio_cur_item = 0

    system_fd = None
    main_fd = None
    event_fd = None
    kernel_fd = None
    snapshot_fd = None
    fd_out = None
    g_fd = None
    radio_fd = None

    input_file = None
    output_file = None
    time_out = None
    begin_time = None
    end_time = None
    outfile = None
    radiofile =  None

    
    output_file = getReportDir_anr(input_dir)
    if os.path.exists(output_file):
        shutil.rmtree(output_file)
    try:
        os.makedirs(output_file)
    except:
        print "%s exixts." %(output_file)
        print output_file
    pidlist = output_file + os.path.sep + "anrpidlist.txt"
    pl = open(pidlist,"w+")
    if output_file:
        print str(output_file)
        if platform.system() == "Linux":
            #outputfolder = '%s/anr_%s' % (output_file, time.strftime('%H-%M-%S'))
            outputfolder = '%s' % (output_file)
        else:
            #outputfolder = '%s\\anr_%s' % (output_file, time.strftime('%H-%M-%S'))
            outputfolder = '%s' % (output_file)
    flag = 0
    while flag < 2:
        print flag
        event_cur_item = 0
        if input_dir:
            fp = FolderParser(input_dir,devnum)
            input_file = fp.getFilesBy('anr')
            parseFilePath(flag,input_file)
        else:
            print ' '
            print '  The input path is error !!!'
            print ' '
            sys.exit(1)
        if event_file:
#            while (event_cur_item < len(event_file) and system_cur_item < len(system_file)):
            while event_cur_item < len(event_file) :
                location = event_file[event_cur_item].rfind("201") 
                datat = event_file[event_cur_item][location:location+4]
                event_fd = open(event_file[event_cur_item], 'r')
#           system_fd = open(system_file[system_cur_item], 'r')
#           main_fd = open(main_file[main_cur_item], 'r')
#           kerenl_fd = open(kernel_file[kernel_cur_item], 'r')
#           print "^^^^^^^^^^system_file[system_cur_item]^^^^^^^^^^" + str(system_file[system_cur_item])
                getAnrList(event_fd,pl)
                if output_file:
                    if flag == 0:
                        print 'parse last log'
                        if platform.system() == "Linux":
                            outfolder = '%s/lastlog' % outputfolder
                            radiofile = '%s/lastradio.log' % outfolder
                        else:
                            outfolder = '%s\\lastlog' % outputfolder
                            radiofile = '%s\\lastradio.log' % outfolder
                        if not os.path.exists(outfolder):
                            print "++++" +str(outfolder)
                            os.makedirs(outfolder)
                        if platform.system() == "Linux" and (not os.path.exists(radiofile)):
                            os.mknod(radiofile)
                    elif flag == 1:
                        print ' '
                        print 'parse current log'
                        if platform.system() == "Linux":
                            outfolder = '%s/currlog' % outputfolder
                            radiofile = '%s/curradio.log' % outfolder
                        else:
                            outfolder = '%s\\currlog' % outputfolder
                            radiofile = '%s\\curradio.log' % outfolder
                        if not os.path.exists(outfolder):
                            os.makedirs(outfolder)
                        if platform.system() == "Linux" and (not os.path.exists(radiofile)):
                            os.mknod(radiofile)
                for pid in anr_pids_list:
                    cur_pid = pid[0]
		    #cur_module = anr_pids_list[pid]
                    cur_module = pid[1]
                    if output_file:
                        if platform.system() == "Linux":                            
                            outfile = '%s/PID_%s_%s.log' % (outfolder, cur_pid,cur_module)
			    #try:
                            #os.mknod(outfile)
			    #except:
			    #	print"MMMMMMMMMMMMMMMMMMMMMMMMMMMMMM"
                        else:
                            outfile = '%s\\PID_%s_%s.log' % (outfolder, cur_pid,cur_module)
                            
                        #fd_out = open(outfile, 'w+')
                    event_fd.seek(g_sys_position)
                    getAnrBeginTime(event_fd, pid,outfile,datat)
                    #getFile()
                    print 'parsing ANR of PID ' + pid[0]
#           lline = snapshot_parse(pid,fd_out)
                    snapshot_parse(pid,outfile)
                    system_parse(pid,outfile)
                    #fd_out_new.write("\n")
                    #fd_out_new.close()
                event_cur_item = event_cur_item + 1
        if radiofile:
            radio_parse(radiofile)        
        flag = flag + 1
        continue
    pl.close()
    print ''
    if outfile:
        if output_file:
            print 'the detail path of report : ' + output_file
    else:
        if output_file:
            shutil.rmtree(output_file)
        print "no anr found"
    print 'parse complete!'
    print ' '

def parse_anr(input_dir,devnum):
    anr_ylog_regex = re.compile(r"ylog.anr 000")
    anr_get_pid_regex = re.compile(r"----- pid\s*(\d+)\s*at\s*(.*)\s*-----")
    anr_get_module_regex = re.compile(r"Cmd line:\s*(.*)")
    output_file = getReportDir_anr(input_dir)
    if os.path.exists(output_file):
        shutil.rmtree(output_file)
    try:
        os.makedirs(output_file)
    except:
        print "%s exixts." %(output_file)
        print output_file
    pidlist = output_file + os.path.sep + "anrpidlist.txt"
    pidpath = output_file + os.path.sep + "ANR"
    if os.path.exists(pidpath):
        shutil.rmtree(pidpath)
    os.makedirs(pidpath)
    pidl = open(pidlist,"w+")
    traces_file = None
    if input_dir:
        fp = FolderParser(input_dir,devnum)
        traces_file = fp.getFilesBy('anrtraces')
        traces_file = traces_file.split(",")
        if traces_file[0] == '':
            pidl.close()
            return 0
        #traces_tmp = {}
        dirnames = []
        for tf in traces_file:
            dirnames.append(os.path.dirname(tf))
        dirnames = list(set(dirnames)) 
        dirnames.sort(reverse=True) 
        print "sorted"
        print dirnames
        for dirn in dirnames:
            print dirn
            tfiles = []
            for tf in traces_file:
                if tf.find(dirn) != -1:
                    tfiles.append(tf) 

            #traces_tmp[dirn] = tfiles
        #for keys in traces_tmp:
            traces = {}
            for tf in tfiles:
                print tf
                filenum = os.path.basename(tf).split(".")[0]
                print filenum
                filenum = int(filenum)
                traces[filenum] = tf
            
        
            tracesf = []
            for keys in traces:
                tracesf.append(traces[keys])
            print tracesf
            #tracesf.reverse()
            for tf in tracesf:
                print tf
                try:
                    tfp = open(tf)
                except:
                    print "open traces file error"
                    continue
                line = tfp.readline()
                while line: 
                    if anr_ylog_regex.search(line):
                        while line: 
                            line = tfp.readline()
                            if len(line) > 2:
                                break
                        print line
                        if anr_get_pid_regex.search(line):
                            pid = anr_get_pid_regex.search(line).group(1) 
                            anr_time = anr_get_pid_regex.search(line).group(2) 
                            line = tfp.readline()
                            if anr_get_module_regex.search(line):
                                module = anr_get_module_regex.search(line).group(1).replace("/",".")
                        break
                    line = tfp.readline()
                pidl.write("-----------------------------------------------------------------\n")
                pidl.write("file: " + tf)
                pidl.write("\npid %s, %s, happend anr at %s \n" %(pid,module,anr_time)) 
                tfp.seek(0)
                pidfile = pidpath + os.path.sep + "pid_" + pid + "_" + module
                pidr = open(pidfile,"w+")
                line = tfp.readline()
                while line:
                    if anr_ylog_regex.search(line):
                        while line:
                            if line.find("----- end ") != -1:
                                break
                            pidr.write(line)
                            line = tfp.readline()
                    if line.find("ylog.anr") != -1 and line.find('logcat -d') != -1:
                        pidr.write(line)
                        line = tfp.readline()
                        while line:
                            if line.find("ylog.anr") != -1:
                                break
                            if line.find("Application is not responding") != -1:
                                anrtype = None
                                
                                pidl.write(line)
                            pidr.write(line)
                            line = tfp.readline()
                    if line.find("ylog.anr") != -1 and line.find(" dmesg ") != -1:
                        while line:
                            pidr.write(line)
                            line = tfp.readline()
                    line = tfp.readline()
                tfp.close()
            
                              
                            

                    
                       

################################################################################################
###########parse_mm################
def get_excelrepo(filename_xlsx,filename_txt,draw):

    import xdrlib
    try:
        import xlrd
    except:
        print "need to install xlrd"
        os.system("pip install xlrd")
        import xlrd
    try:
        import xlwt
    except:
        print "need to install xlwt"
        os.system("pip install xlwt")
        import xlwt
    
    data = []

    if os.path.exists(filename_xlsx):
        os.remove(filename_xlsx)
    try:
        fd = open(filename_txt)
    except:
        print "open memory.txt error"
    return 0
    row = 0
    ctype = 1
    xf = 0
    col = 1
    book = xlwt.Workbook(encoding='utf-8',style_compression=0)
    sheet1 = book.add_sheet('sheet1',cell_overwrite_ok=True)

    line = fd.readline()
    while line:
        print line
        ll = line.strip().split(':')
        name = ll[0]
        value = ll[1]
        if col == 1:
            sheet1.write(row,0,name)
            try:
                if name == "lost_ration":
                    sheet1.write(row,1,float(value))
                else:
                    sheet1.write(row,1,int(value))
            except:
                sheet1.write(row,1,value) 
        else:
            try:
                if name == "lost_ration":
                    sheet1.write(row,col,float(value))
                else:
                    sheet1.write(row,col,int(value))
            except:
                sheet1.write(row,col,value)
        line = fd.readline()
        row += 1
        if line.find("Item") != -1:
            row = 0
            col += 1
            continue
    fd.close()
    book.save(filename_xlsx)
    if draw == "y":
        os.system("python draw_mem.py " + filename_xlsx)


def get_tasklist():
    task_file = os.path.abspath('.') + os.path.sep + "configs" + os.path.sep + "tasklist.txt"
    task_list = []
    try:
        ft = open(task_file)
    except:
        print "open task list file error"
        return 0
    line = ft.readline()
    while line:
        line = line.strip()
        task_list.append(line)
        line = ft.readline()
    if len(task_list) > 0:
        return task_list
    else:
        return 0
    
def write_data_to_file(final_report,mode,devicet,cnt):

    global ion,mali,kmalloclarge,p_mali,p_ion,position
    global dma_free,active_anon,inactive_anon,active_file,inactive_file,unevictable,\
           slab_reclaimable,slab_unreclaimable,kernel_stack,pagetables,memtotal,\
           buffers,swapcached,vmalloc,zram,pagerecorder
    task = get_tasklist()
    global data

    if pagerecorder > 0:
        if ion != 0:
            pagerecorder = int(pagerecorder) - int(ion)
        else:
            pagerecorder = int(pagerecorder) - int(p_ion)/1024
        print "++++++++++++++++++++++"
        print devicet
        if devicet == "t8" or devicet == "T8" or devicet.find("sp9838") != -1:
            print "is t8"	
            if p_mali != 0:
                mali = int(p_mali)/1024
                pagerecorder = int(pagerecorder) - int(p_mali)/1024
            else:
                pagerecorder = int(pagerecorder) - int(mali)
        else:
            print "not t8"	
            if mali != 0:
                pagerecorder = int(pagerecorder) - int(mali)
            else:
                mali = int(p_mali)/1024
                pagerecorder = int(pagerecorder) - int(p_mali)/1024
    print "pagerecorder:%d kB" %pagerecorder
    try:	
        framework_app = int(active_anon) + int(inactive_anon) + int(active_file) + int(inactive_file) + int(zram) + int(unevictable) + int(swapcached)
        kernel = int(slab_reclaimable) + int(slab_unreclaimable) + int(kmalloclarge) + int(kernel_stack) + int(pagetables) + int(buffers) + int(vmalloc) + int(pagerecorder)
        multimedia = int(ion) + int(mali)
        print "framework_app:%d " %framework_app
        print "kernel:%d " %kernel
        print "multimedia:%d " %multimedia
        mem_sum = framework_app + kernel + multimedia + int(dma_free)
        lost = int(memtotal) - mem_sum
        print "lost:%d " %lost
        lost_ration = round(lost/float(memtotal),5)
    #lost_ration = str(lost_ration) + "%"

        print "loat ration:%s " %lost_ration
	

	#write data to mem.txt
        mem_p = open(final_report,mode)
        mem_p.write("Items:%d_value/kB\n" %int(cnt))
        mem_p.write("active_anon:%s\n" %active_anon)
        mem_p.write("inactive_anon:%s\n" %inactive_anon)
        mem_p.write("active_file:%s\n" %active_file)
        mem_p.write("inactive_file:%s\n" %inactive_file)
        mem_p.write("zram:%s\n" %zram)
        mem_p.write("unevictable:%s\n" %unevictable)
        mem_p.write("swapcached:%s\n" %swapcached)
        mem_p.write("framework_app_total:%s\n" %str(framework_app))
        mem_p.write(" : \n")
        mem_p.write("slab_reclaimable:%s\n" %slab_reclaimable)
        mem_p.write("slab_unreclaimable:%s\n" %slab_unreclaimable)
        mem_p.write("kmalloclarge:%s\n" %kmalloclarge)
        mem_p.write("kernel_stack:%s\n" %kernel_stack)
        mem_p.write("pagetables:%s\n" %pagetables)
        mem_p.write("buffers:%s\n" %buffers)
        mem_p.write("vmalloc:%s\n" %vmalloc)
        mem_p.write("pagerecorder:%s\n" %pagerecorder)
        mem_p.write("kernel_total:%s\n" %str(kernel))
        mem_p.write(" : \n")
        mem_p.write("ion:%s\n" %str(ion))
        mem_p.write("mali:%s\n" %str(mali))
        mem_p.write("multimedia_total:%s\n" %str(multimedia))
        mem_p.write(" : \n")
        mem_p.write("memory_total:%s\n" %memtotal)
        mem_p.write("memory_free:%s\n" %dma_free)
        mem_p.write("memory_used_total:%s\n" %str(mem_sum))
        mem_p.write("lost:%d\n" %lost)
        mem_p.write("lost_ration:%s\n" %lost_ration)
        mem_p.write(" : \n")
        if task != 0:
            for tt in task:
                tmp_tt = tt + "_Rss"
                mem_p.write("%s:%s\n" %(tmp_tt,data[tmp_tt]))
                tmp_tt = tt + "_Pss"
                mem_p.write("%s:%s\n" %(tmp_tt,data[tmp_tt]))
                tmp_tt = tt + "_Uss"
                mem_p.write("%s:%s\n" %(tmp_tt,data[tmp_tt]))
            #mem_p.write("%s:%s\n" %str(c_Pss))
            #mem_p.write("%s:%s\n" %str(c_Uss))
                mem_p.write(" : \n")
    #mem_p.write("mediaserver_Rss:%s\n" %str(m_Rss))
   # mem_p.write("mediaserver_Pss:%s\n" %str(m_Pss))
   # mem_p.write("mediaserver_Uss:%s\n" %str(m_Uss))

        mem_p.close()
    except:
        print "Error data"
        return 0

def get_memory_info(m_file,devbit,timer,mem_file):
    
    dma_free_regex = re.compile(r'DMA free:')
    dma_free_get_regex = re.compile(r'DMA free:\s*(\d+)kB')
    n_dma_free_get_regex = re.compile(r'Normal free:\s*(\d+)kB')
    h_dma_free_get_regex = re.compile(r'HighMem free:\s*(\d+)kB')
    active_anon_regex = re.compile(r'\s*active_anon:(\d+)kB')
    inactive_anon_regex = re.compile(r'\s*inactive_anon:(\d+)kB')
    active_file_regex = re.compile(r'\s*active_file:(\d+)kB')
    inactive_file_regex = re.compile(r'\s*inactive_file:(\d+)kB')
    unevictable_regex = re.compile(r'\s*unevictable:(\d+)kB')
    slab_reclaimable_regex = re.compile(r'\s*slab_reclaimable:(\d+)kB')
    slab_unreclaimable_regex = re.compile(r'\s*slab_unreclaimable:(\d+)kB')
    kernel_stack_regex = re.compile(r'\s*kernel_stack:(\d+)kB')
    pagetables_regex = re.compile(r'\s*pagetables:(\d+)kB')

    kmalloclarge_regex = re.compile(r'\s*KmallocLarge:\s*(\d+)\s*kB')
    memtotal_regex = re.compile(r'\s*MemTotal:\s*(\d+)\s*kB')
    buffers_regex = re.compile(r'\s*Buffers:\s*(\d+)\s*kB')
    swapcached_regex = re.compile(r'\s*SwapCached:\s+(\d+)\s*kB')
    vmalloc_regex = re.compile(r'\s*Enhanced Mem-info :VMALLOC')
    vmalloc_get_regex = re.compile(r'\s*Total used:\s*(\d+)kB')
    zram_regex = re.compile(r'\s*Enhanced Mem-info :ZRAM')
    zram_get_regex = re.compile(r'\s*Total used:\d+\s*\w+,\s*(\d+)\s*kB')
    ion_regex = re.compile(r'Enhanced Mem-info :ION')
    ion_get_regex = re.compile(r'\s*Total used:\s*(\d+)\s*kB')
######mali#############
    mali_regex = re.compile(r'Enhanced Mem-info :MALI')
    mali_get_regex = re.compile(r'\s*Total used:\s*(\d+)\s*kB')
    pagerecorder_regex = re.compile(r'Enhanced Mem-info :PAGE RECORDER')
    pagerecorder_get_regex = re.compile(r'\s*Total used:\s*(\d+)\s*kB')
#p_ion_regex = re.compile(r'')
#p_ion_get_regex = re.compile(r'\s*Backtrace pages:\s*(\d+)\s*bytes')
#p_mali_get_regex = re.compile(r'\s*Backtrace pages:\s*(\d+)\s*bytes')
    tmp_backtrace_get_regex = re.compile(r'Backtrace\s*pages\s*(\d+)\s*bytes')
    global ion,mali,kmalloclarge,p_mali,p_ion
    global dma_free,active_anon,inactive_anon,active_file,inactive_file,unevictable,\
           slab_reclaimable,slab_unreclaimable,kernel_stack,pagetables,memtotal,\
           buffers,swapcached,vmalloc,zram,pagerecorder
    flag = False
    ion = 0
    mali = 0
    kmalloclarge = 0
    vmalloc = 0
    zram = 0
    dma_free = None
    h_dma_free = None
    n_dma_free = None
    fm = open(m_file)
    line = fm.readline()
    position = []
    p_ion = 0
    p_mali = 0
    pagerecorder = 0
    while line:
        tmp_position = fm.tell()
        line = fm.readline()
        if line.find("Enhanced Mem-Info:E_SHOW_MEM_BASIC") != -1 or line.find("Enhanced Mem-Info:E_SHOW_MEM_ALL") != -1 or line.find("Enhanced Mem-Info:E_SHOW_MEM_CLASSIC") != -1:
            if timer == "last_time":
                position.append(tmp_position)
            else:
                tmp_timer = get_timer(line)
                print tmp_timer
                if tmp_timer > timer:
                    break
                else:
                    position.append(tmp_position)
                    print tmp_position
                    print line
    print position
    if len(position) > 0:
        mem_p = open(mem_file,'w+')
        fm.seek(position[-1])
        line = fm.readline()
        while line:
            mem_p.write(line)
            line = fm.readline()
        mem_p.close()
    if len(position) > 0:
        fm.seek(position[-1])
        line = fm.readline()
        print line
        while line:
            if line.find("Enhanced Mem-Info:E_SHOW_MEM_BASIC") != -1 or line.find("Enhanced Mem-Info:E_SHOW_MEM_ALL") != -1 or line.find("Enhanced Mem-Info:E_SHOW_MEM_CLASSIC") != -1:
                print line
                while line:
                    if dma_free == None and line.find("DMA free") != -1:
                        print line
                        dma_free = dma_free_get_regex.search(line).group(1)
                        print dma_free
                        try:
                            print "dma_free:%s kB" %dma_free
                        except:
                            print "no dma_free"
                            dma_free = 0
                        active_anon = active_anon_regex.search(line).group(1)
                        try:
                            print "active_anon:%s kB" %active_anon
                        except:
                            print "no active_anon"
                            active_anon = 0
                        inactive_anon = inactive_anon_regex.search(line).group(1)
                        try:
                            print "inactive_inon:%s kB" %inactive_anon
                        except:
                            print "no inactive_anon"
                            inactive_anon = 0
                        active_file = active_file_regex.search(line).group(1)
                        try:
                            print "active_file:%s kB" %active_file
                        except:
                            print "no active_file"
                            active_file = 0
                        inactive_file = inactive_file_regex.search(line).group(1)
                        try:
                            print "inactive_file:%s kB" %inactive_file
                        except:
                            print "no n_inactive_file"
                            inactive_file = 0
                        unevictable = unevictable_regex.search(line).group(1)
                        try:
                            print "unevictable:%s kB" %unevictable
                        except:
                            print "no unevictable"
                            unevictable = 0
                        slab_reclaimable = slab_reclaimable_regex.search(line).group(1)
                        try:
                            print "slab_reclaimable:%s kB" %slab_reclaimable
                        except:
                            print "no slab_reclaimable"
                            slab_reclaimable = 0
                        slab_unreclaimable = slab_unreclaimable_regex.search(line).group(1)
                        try:
                            print "slab_unreclaimable:%s kB" %slab_unreclaimable
                        except:
                            print "no slab_unreclaimable"
                            slab_unreclaimable = 0
                        kernel_stack = kernel_stack_regex.search(line).group(1)
                        try:
                            print "kernel_stack:%s kB" %kernel_stack
                        except:
                            print "no kerenl_stack"
                            kernel_stack = 0
                        pagetables = pagetables_regex.search(line).group(1)
                        try:
                            print "pagetables:%s kB" %pagetables
                        except:
                            print "no pagetables"
                            pagetables = 0
                    ############if 32arm, there is normal and high free
                    ######this is normal free
                    if n_dma_free == None and line.find("Normal free") != -1:
                        print line
			
                        tmpp = fm.tell()
                        print tmpp
                        n_dma_free = n_dma_free_get_regex.search(line).group(1)
                        try:
                            print "n_dma_free:%s kB" %n_dma_free
                        except:
                            print "no n_dma_free"
                            n_dma_free = 0
                        n_active_anon = active_anon_regex.search(line).group(1)
                        try:
                            print "n_active_anon:%s kB" %n_active_anon
                        except:
                            print "no n_active_anon"
                            n_active_anon = 0
                        n_inactive_anon = inactive_anon_regex.search(line).group(1)
                        try:
                            print "n_inactive_inon:%s kB" %n_inactive_anon
                        except:
                            print "no n_inactive_anon"
                            n_inactive_anon = 0
                        n_active_file = active_file_regex.search(line).group(1)
                        try:
                            print "n_active_file:%s kB" %n_active_file
                        except:
                            print "no n_active_file"
                            n_active_file = 0
                        n_inactive_file = inactive_file_regex.search(line).group(1)
                        try:
                            print "n_inactive_file:%s kB" %n_inactive_file
                        except:
                            print "no inactive_file"
                            n_inactive_file = 0
                        n_unevictable = unevictable_regex.search(line).group(1)
                        try:
                            print "n_unevictable:%s kB" %n_unevictable
                        except:
                            print "no n_unevictable"
                            n_unevictable = 0
                        n_slab_reclaimable = slab_reclaimable_regex.search(line).group(1)
                        try:
                            print "n_slab_reclaimable:%s kB" %n_slab_reclaimable
                        except:
                            print "no n_slab_reclaimable"
                            n_slab_reclaimable = 0
                        n_slab_unreclaimable = slab_unreclaimable_regex.search(line).group(1)
                        try:
                            print "n_slab_unreclaimable:%s kB" %n_slab_unreclaimable
                        except:
                            print "no n_slab_unreclaimable"
                            n_slab_unreclaimable = 0
                        n_kernel_stack = kernel_stack_regex.search(line).group(1)
                        try:
                            print "n_kernel_stack:%s kB" %n_kernel_stack
                        except:
                            print "no n_kerenl_stack"
                            n_kernel_stack = 0
                        n_pagetables = pagetables_regex.search(line).group(1)
                        try:
                            print "n_pagetables:%s kB" %n_pagetables
                        except:
                            print "no h_pagetables"
                            n_pagetables = 0

                        dma_free = int(n_dma_free) 
                        print "dma_free:%d " %dma_free
                        active_anon = int(n_active_anon)
                        print "sctive_anon:%d " %(active_anon)
                        inactive_anon = int(n_inactive_anon) 
                        print "inactive_anon:%d" %(inactive_anon)
                        active_file = int(n_active_file) 
                        print "active_file:%d" %(active_file)
                        inactive_file = int(n_inactive_file)
                        print "inactive_file:%d " %(inactive_file)
                        unevictable = int(n_unevictable)
                        print "unevictable:%d " %(unevictable)
                        slab_reclaimable = int(n_slab_reclaimable)
                        print "slab_reclaimable:%d " %(slab_reclaimable)
                        slab_unreclaimable = int(n_slab_unreclaimable)
                        print "slab_unreclaimable:%d " %(slab_unreclaimable)
                        kernel_stack = int(n_kernel_stack)
                        print "kernel_stack:%d" %(kernel_stack)
                        pagetables = int(n_pagetables)
                        print "pagetables:%d " %(pagetables)
                    ######this is High free
                    if h_dma_free ==None and line.find("HighMem free") != -1:
                        print line
                        h_dma_free = h_dma_free_get_regex.search(line).group(1)
                        try:
                            print "h_dma_free:%s kB" %h_dma_free
                        except:
                            print "no h_dma_free"
                            h_dma_free = 0
                        h_active_anon = active_anon_regex.search(line).group(1)
                        try:
                            print "h_active_anon:%s kB" %h_active_anon
                        except:
                            print "no h_active_anon"
                            h_active_anon = 0
                        h_inactive_anon = inactive_anon_regex.search(line).group(1)
                        try:
                            print "h_inactive_inon:%s kB" %h_inactive_anon
                        except:
                            print "no h_inactive_anon"
                            h_inactive_anon = 0
                        h_active_file = active_file_regex.search(line).group(1)
                        try:
                            print "h_active_file:%s kB" %h_active_file
                        except:
                            print "no h_active_file"
                            h_active_file = 0
                        h_inactive_file = inactive_file_regex.search(line).group(1)
                        try:
                            print "h_inactive_file:%s kB" %h_inactive_file
                        except:
                            print "no h_inactive_file"
                            h_inactive_file = 0
                        h_unevictable = unevictable_regex.search(line).group(1)
                        try:
                            print "h_unevictable:%s kB" %h_unevictable
                        except:
                            print "no h_unevictable"
                            h_unevictable = 0
                        h_slab_reclaimable = slab_reclaimable_regex.search(line).group(1)
                        try:
                            print "h_slab_reclaimable:%s kB" %h_slab_reclaimable
                        except:
                            print "no h_slab_reclaimable"
                            h_slab_reclaimable = 0
                        h_slab_unreclaimable = slab_unreclaimable_regex.search(line).group(1)
                        try:
                            print "h_slab_unreclaimable:%s kB" %h_slab_unreclaimable
                        except:
                            print "no h_slab_unreclaimable"
                            h_slab_unreclaimable = 0
                        h_kernel_stack = kernel_stack_regex.search(line).group(1)
                        try:
                            print "h_kernel_stack:%s kB" %h_kernel_stack
                        except:
                            print "no h_kerenl_stack"
                            h_kernel_stack = 0
                        h_pagetables = pagetables_regex.search(line).group(1)
                        try:
                            print "h_pagetables:%s kB" %h_pagetables
                        except:
                            print "no h_pagetables"
                            h_pagetables = 0
                        #################add normal and high memory value
		    
                        dma_free = int(n_dma_free) + int(h_dma_free)
                        print "dma_free:%d " %dma_free
                        active_anon = int(n_active_anon) + int(h_active_anon)
                        print "sctive_anon:%d " %(active_anon)
                        inactive_anon = int(n_inactive_anon) + int(h_inactive_anon)
                        print "inactive_anon:%d" %(inactive_anon)
                        active_file = int(n_active_file) + int(h_active_file)
                        print "active_file:%d" %(active_file)
                        inactive_file = int(n_inactive_file) + int(h_inactive_file)
                        print "inactive_file:%d " %(inactive_file)
                        unevictable = int(n_unevictable) + int(h_unevictable)
                        print "unevictable:%d " %(unevictable)
                        slab_reclaimable = int(n_slab_reclaimable) + int(h_slab_reclaimable)
                        print "slab_reclaimable:%d " %(slab_reclaimable)
                        slab_unreclaimable = int(n_slab_unreclaimable) + int(h_slab_unreclaimable)
                        print "slab_unreclaimable:%d " %(slab_unreclaimable)
                        kernel_stack = int(n_kernel_stack) + int(h_kernel_stack)
                        print "kernel_stack:%d" %(kernel_stack)
                        pagetables = int(n_pagetables) + int(h_pagetables)
                        print "pagetables:%d " %(pagetables)
			###############no high memory value
                    
                    if memtotal_regex.search(line):
                        print line
                        flag = True
                        memtotal = memtotal_regex.search(line).group(1)
                        try:
                            print "memtotal:%s kB" %memtotal
                        except:
                            print "no memtotal"
                            memtotal = 0
                    if buffers_regex.search(line):
                        print line
                        buffers = buffers_regex.search(line).group(1)
                        try:
                            print "buffers:%s kB" %buffers
                        except:
                            print "no buffers"
                            buffers = 0
                    if swapcached_regex.search(line):
                        print line
                        swapcached = swapcached_regex.search(line).group(1)
                        try:
                            print "swapcached:%s kB" %swapcached
                        except:
                            print "no swapcached"
                            swapcached = 0
                    if kmalloclarge_regex.search(line):
                        print line
                        kmalloclarge = kmalloclarge_regex.search(line).group(1)
                        try:
                            print "kmalloclarge:%s kB" %kmalloclarge
                        except:
                            print "no kmalloclarge"
                    if vmalloc_regex.search(line):
                        print line
                        while line:
                            if vmalloc_get_regex.search(line):
                                vmalloc = vmalloc_get_regex.search(line).group(1)
                                print "vmalloc:%s kB" %vmalloc
                                break
                            line = fm.readline()
                    if zram_regex.search(line):
                        print line
                        while line:
                            if zram_get_regex.search(line):
                                zram = zram_get_regex.search(line).group(1)
                                print "zram:%s kB" %zram
                                break
                            line = fm.readline()
                    if ion_regex.search(line):
                        print line
                        while line:
                            if line.find("Heap: ion_heap_system") != -1:
                                while line:
                                    if ion_get_regex.search(line):
                                        ion = ion_get_regex.search(line).group(1)
                                        print "ion:%s kB" %ion
                                        break
                                    line = fm.readline()
                                break
                            line = fm.readline()
                    if mali_regex.search(line):
                        print line
                        while line:
                            if mali_get_regex.search(line):
                                mali = mali_get_regex.search(line).group(1)
                                print "mali:%s kB" %mali
                                break
                            line = fm.readline()
                    if pagerecorder_regex.search(line):
                        print line
                        while line:
                            if tmp_backtrace_get_regex.search(line):
                                tmp_backtrace = tmp_backtrace_get_regex.search(line).group(1)
                                print "tmp_backtrace"
                                print tmp_backtrace
                                for i in range(5):
                                    if line.find("ion") != -1:
                                        p_ion += int(tmp_backtrace)
                                        break
                                    if line.find("mali") != -1:
                                        p_mali += int(tmp_backtrace)
                                        break
                                    line = fm.readline()
                            if pagerecorder_get_regex.search(line):
                                pagerecorder = pagerecorder_get_regex.search(line).group(1)
                                break
                            line = fm.readline()
                        print "p_ion:%s bytes" %p_ion
                        print "p_mali:%s byte" %p_mali
                        print "total pagerecorder:%s kB" %pagerecorder
                        break
                    line = fm.readline()
                    if line.find("Enhanced Mem-Info:E_SHOW_MEM_BASIC") != -1 or line.find("Enhanced Mem-Info:E_SHOW_MEM_ALL") != -1:
                        break
                break
            line = fm.readline()
    fm.close()
    return position

def get_timer(lline):
    if lline == "last_time":
        temp = "last_time"
    else:
        print lline
        d = [datetime.datetime.now().year, string.atoi(lline[0:2]), string.atoi(lline[3:5]),
            string.atoi(lline[6:8]), string.atoi(lline[9:11]), string.atoi(lline[12:14]), string.atoi(lline[15:18])*1000]
        temp = datetime.datetime(d[0],d[1],d[2],d[3],d[4],d[5],d[6])
        print temp
    return temp


def getReportDir_mm(folderParser):

    if platform.system() == "Linux":
        location = folderParser.rfind("/")
    else:
        location = folderParser.rfind("\\")
    slogBasePath = folderParser[0:location]
    reportDir = slogBasePath + os.path.sep + "post_process_report" + os.path.sep + "memory"
    if not os.path.exists(reportDir):
        os.makedirs(reportDir)
    reportdir_g = reportDir
    return reportDir

def getReportFile_mm(folderParser):
    reportDir = getReportDir_mm(folderParser)
    reportFile = os.path.join(reportDir, 'memory_report.txt')
    return reportFile

def clearReportDir_mm(folderParser):
    reportDir = getReportDir_mm(folderParser) 
    shutil.rmtree(reportDir)

def get_memory_file(folderparser):
    PARSE_TYPE = "memory"
    memoryfile = None
    memoryfiles = folderparser.getFilesBy(PARSE_TYPE)
    if memoryfiles:
        memoryfile = memoryfiles.split(',')
    return memoryfile

def parse_mm(slog_path,timer,devnum):

    ##########set scan=None,will not scan all kernel log########
    scan = None
    global ion,mali,kmalloclarge,p_mali,p_ion
    global dma_free,active_anon,inactive_anon,active_file,inactive_file,unevictable,\
           slab_reclaimable,slab_unreclaimable,kernel_stack,pagetables,memtotal,\
           buffers,swapcached,vmalloc,zram,pagerecorder
    #global slog_path,devnum,timer,memleak_file,device_type,scan
    memleak_file = None
    if slog_path:
        if scan:
	    #arg_mem = ['python','parse_mm_all.py','--log-dir',slog_path,'--device-type',device_type]
	    #result = subprocess.Popen(arg_mem,stdout=subprocess.PIPE,shell=False).stdout.readlines()
	    #for line in result:
        #	print line
            os.system('python parse_mm_all.py ' + '--log-dir ' + slog_path + ' --device-type ' + device_type)
            sys.exit(1)
        print slog_path
        fp = FolderParser(slog_path,devnum)

        clearReportDir_mm(slog_path)
        reportFile = getReportFile_mm(slog_path)
        reportDir = getReportDir_mm(slog_path)
        if platform.system() == "Linux":
            p = reportDir.rfind("/")
	    #final_report_ods = reportDir[0:p] + os.path.sep + "final_report.xls"
        else:
            p = reportDir.rfind("\\")
	    #final_report_xlsx = reportDir[0:p] + os.path.sep + "final_report.xls"
	#final_report = reportDir[0:p] + os.path.sep + "final_report.xls"
        final_report = reportDir + os.path.sep + "final_report.xls"
	#final_report_txt = reportDir[0:p] + os.path.sep + "final_report_mm.txt"
        final_report_txt = reportDir + os.path.sep + "final_report_mm.txt"
	#parse kernel file
        memory_file = get_memory_file(fp)
        memory_file.sort(reverse=True)
	#memory_file = memory_file[0]
	
        tmp_memory_file = os.path.abspath('.') + os.path.sep + "logs" +os.path.sep + "tmp_memory_file.txt"
        devbit = get_device_mode()
	#for mem_file in memory_file:
        print "memory file " +str(memory_file)
        print timer
        timer = get_timer(timer)
        print timer
        print reportFile
        pp = None
	#if os.path.exists(memory_file):
        for mmfile in memory_file:
            if os.path.exists(mmfile):
                print reportFile
                pp = get_memory_info(mmfile,devbit,timer,reportFile)
            else:
                print "No memory related kernel log,quit."
	    
	
	#####if len(position) > 0,then there is enhanced meminfo,else exit.
            if pp:
	    #mem_p = open(final_report_txt,'w')
                open_m = 'w'
	    ##enhanced meminfo can get mali directly, because t8 has no mali info.
                result = None
                result = write_data_to_file(final_report_txt,open_m,devbit,1)
	    ####write data to excel file
                if result == None:
	            #os.system("python get_excelrepo_windows.py " + final_report + " " + final_report_txt + " n")
                    #get_excelrepo(final_report,final_report_txt,"n")
                    #if os.path.exists(final_report_txt):
                    #    os.remove(final_report_txt)
                    pass
                else:
                    clearReportDir_mm(slog_path) 
                print "No enhanced meminfo, quit."
                break
	
    if memleak_file:
	
        base_dir = os.path.dirname(memleak_file)
        memleak_mm_file = base_dir + os.path.sep + "memleak_mm.txt"
        if os.path.exists(memleak_mm_file):
            os.remove(memleak_mm_file)

        open_m = 'a+'
        m_fd = open(memleak_file)
        line = m_fd.readline()
        count = 0
        while line:
	    #if start_regex.search(line):
            if line.find(" start------------") != -1:
                count += 1
                print line
                get_memory_info_memleak(m_fd)
                write_data_to_file(memleak_mm_file,open_m,device_type,count)	
            line = m_fd.readline()
        final_report = base_dir + os.path.sep + "memleak_mm.xls"
        os.system("python get_excelrepo_windows.py " + final_report + " " + memleak_mm_file + " y")
	
################################################################################################
def generate_finalrepo(titles,slogtime):
    print "**********generate final report**********"
    arg_generate_repo = ['python','generate_final_report.py',titles,slogtime,serial_num]
    result_generate_repo = subprocess.Popen(arg_generate_repo,stdout=subprocess.PIPE,shell=False).stdout.readlines()
    tmp = ""
    for line in result_generate_repo:
        tmp = line
        print line
    return tmp
def sysdump_check(sysdump_info):
    flag = False
    for file in os.listdir(sysdump_p):
        if file.find("sysdump.core.00") != -1:
            flag = True
    if flag == False:
        print "No sysdump file"
        sys.exit(1)
    
    num = len(os.listdir(sysdump_p))
    num = int(num)
    print "num    " +str(num)
    size = 0
    for root, dirs, files in os.walk(sysdump_p):
        for name in files:
            size = os.path.getsize(os.path.join(root, name))
            if size == 0L:
                print "break"
                break
        if size == 0L:
            print "break"
            break
    sysdump_info[num] = size

			
def download_symbols(logdir,dev_mode,symbols_dir):
    import urllib  
    import urllib2
    import tarfile
    dev_info = get_device_mode()
    build_type = get_build_type()

    url = dev_mode + "symbols.vmlinux." + dev_info + "_" + build_type + "_" + "native.tgz"

    
    print url
    time.sleep(10)
    #dst_file = symbols_dir + os.path.sep + symbolname
    dst_file = symbols_dir + os.path.sep + "symbols.vmlinux." + dev_info + "_" + build_type + "_" + "native.tgz"
    print dst_file
    dst_path = symbols_dir
    urllib.urlretrieve(url, dst_file)
    print "extracting with tarfile"
    tar = tarfile.open(dst_file)
    tar.extractall(dst_path)
   # else:
    #    print "No device mode related file"
     #   sys.exit(1)
    
def get_device_mode():

    product_name_regex = re.compile(r'ro.product.name')
    product_name_get_regex = re.compile(r'(\w+)')
    dev_file = None
    dev_info = None
    for ff in os.listdir(ylog_p):
        if ff.find("sysprop.txt") != -1:
            dev_file = ff
            break
    if dev_file:
        #print "device file " +str(dev_file)
        fd = open(os.path.join(ylog_p,dev_file))
        line = fd.readline()
        while line:
            if product_name_regex.search(line):
                print line
                pattern = r"(\[.*?\])"
                line = re.findall(pattern,line,re.M)
                if (len(line)>1):
                    line = line[1]
                    dev_info = line.replace('[','').replace(']','')
                break
            line = fd.readline()
    if dev_info:
        print "device info " + str(dev_info)
        return dev_info   
    else:
        return "" 
    #"sp9838aea_oversea"

def get_build_host():
    
    build_host_regex = re.compile(r'ro.build.host')
    dev_file = None
    build_host = None
    for ff in os.listdir(ylog_p):
        if ff.find("sysprop.txt") != -1:
            dev_file = ff
            break
    if dev_file:
        fd = open(os.path.join(ylog_p,dev_file))
        line = fd.readline()
        while line:
            if build_host_regex.search(line):
                print line
                pattern = r"(\[.*?\])"
                line = re.findall(pattern,line,re.M)
                if (len(line)>1):
                    line = line[1]
                    build_host = line.replace('[','').replace(']','')
                break
            line = fd.readline()
    if build_host:
        #print build_host
        return build_host
    #build_host: http://10.0.1.56:8080/jenkins/job/sprdroid5.1_trunk_SharkLT8/68/  
    else:
        return ""

def get_build_type():
    build_type_regex = re.compile("ro.build.type") 
    dev_file = None
    build_type = None
    for ff in os.listdir(ylog_p):
        if ff.find("sysprop.txt") != -1:
            dev_file = ff
            break
    if dev_file:
        fd = open(os.path.join(ylog_p,dev_file))
        line = fd.readline()
        while line:
            if build_type_regex.search(line):
                print line
                pattern = r"(\[.*?\])"
                line = re.findall(pattern,line,re.M)
                if (len(line)>1):
                    line = line[1]
                    build_type = line.replace('[','').replace(']','')
                break
            line = fd.readline()
    if build_type:
        #print build_host
        return build_type
    #build_host: http://10.0.1.56:8080/jenkins/job/sprdroid5.1_trunk_SharkLT8/68/  
    else:
        return ""


def get_kernel_crash_time(final_repo):
    fd = open(final_repo)
    line = fd.readline()
    kernel_crash_time = None
    kernel_crash_module = None
    while line:
        if kernel_crash_regex.search(line):
            kernel_crash_module = line.split(' ')[-1]
            pattern = r"(\[.*?\])"
            line = re.findall(pattern,line,re.M)
            if (len(line)>0):
                line = line[0]
                kernel_crash_time = line.replace('[','').replace(']','').replace(' ','')
            break
        line = fd.readline()
    return (kernel_crash_time,kernel_crash_module)

def parse_kernel_warning(slogp,folderparser):

    kernel_warning_regex = re.compile(r'WARNING:')
    if platform.system() == "Linux":
        location = slogp.rfind("/")
    else:
        location = slogp.rfind("\\")
    slogbp = slogp[0:location]
    savepath = slogbp + os.path.sep + "post_process_report" + os.path.sep + "kernel_panic" + os.path.sep

    if os.path.exists(savepath):
        shutil.rmtree(savepath)		
    if not os.path.isdir(savepath):
        os.makedirs(savepath)
    print "savepath " +str(savepath)
    warningf = savepath + "warning.txt"
    wf = open(warningf,"w+")
    kernelfs = folderparser.getFilesBy("memory")
    kernelfs = kernelfs.split(",")
    sp = FileSort(kernelfs)
    kernelfs = sp.fsort()
    for kf in kernelfs:
        try:
            kp = open(kf)
        except:
            print kf
            print "Open kernel error."
            continue
        line = kp.readline()
        num = 0
        while line:
            if kernel_warning_regex.search(line):
                wf.write("file: %s\n" %kf)
                num += 1
                i = 0
                while i < 30:
                    wf.write(line)
                    line = kp.readline()
                    i += 1
                wf.write("\n")
            line = kp.readline()
        kp.close()
        print num
    wf.close()
		
def parse_kernel_BUG(slogp,folderparser):

    kernel_BUG_regex = re.compile(r'\s*BUG:\s*')
    if platform.system() == "Linux":
        location = slogp.rfind("/")
    else:
        location = slogp.rfind("\\")
    slogbp = slogp[0:location]
    savepath = slogbp + os.path.sep + "post_process_report" + os.path.sep + "kernel_panic" + os.path.sep
    if not os.path.isdir(savepath):
        os.makedirs(savepath)
    print "savepath " +str(savepath)
    bugf = savepath + "bug.txt"
    bf = open(bugf,"w+")
    kernelfs = folderparser.getFilesBy("memory")
    kernelfs = kernelfs.split(",")
    sp = FileSort(kernelfs)
    kernelfs = sp.fsort()
    for kf in kernelfs:
        try:
            kp = open(kf)
        except:
            print kf
            print "Open kernel error."
            continue
        line = kp.readline()
        num = 0
        while line:
            next_e = False
            if kernel_BUG_regex.search(line):
	    #if line.find("BUG:") != -1:
                bf.write("file: %s\n" %kf)
                num += 1
                bf.write(line)
                line = kp.readline()
                i = 0
                while line:
                    if i >= 30:
                        next_e = True
                        break
                    if kernel_BUG_regex.search(line):
		    #if line.find("BUG:") != -1:
                        next_e = True
                        break
                    bf.write(line)
                    line = kp.readline()
                    i += 1
            if next_e:
                continue
            line = kp.readline()
        kp.close()
        print num
    bf.close()
    
		
def parse_kernel_Error(slogp,folderparser):

    kernel_Error_regex = re.compile(r'\s*Error\s*')
    if platform.system() == "Linux":
        location = slogp.rfind("/")
    else:
        location = slogp.rfind("\\")
    slogbp = slogp[0:location]
    savepath = slogbp + os.path.sep + "post_process_report" + os.path.sep + "kernel_panic" + os.path.sep
    if not os.path.isdir(savepath):
        os.makedirs(savepath)
    print "savepath " +str(savepath)
    errorf = savepath + "error.txt"
    erf = open(errorf,"w+")
    kernelfs = folderparser.getFilesBy("memory")
    kernelfs = kernelfs.split(",")
    sp = FileSort(kernelfs)
    kernelfs = sp.fsort()
    for kf in kernelfs:
        try:
            kp = open(kf)
        except:
            print kf
            print "Open kernel error."
            continue
        line = kp.readline()
        while line:
            next_e = False
            if kernel_Error_regex.search(line):
                erf.write("file: %s\n" %kf)
                erf.write(line)
                line = kp.readline()
                i = 0
                while line:
                    if i >= 30:
                        next_e = True
                        break
                    if kernel_Error_regex.search(line):
                        next_e = True
                        break
                    erf.write(line)
                    line = kp.readline()
                    i += 1
            if next_e:
                continue
            line = kp.readline()
        kp.close()
    erf.close()
		
def parse_kernel_emmc(slogp,folderparser):

    kernel_emmc_regex = re.compile(r'REGISTER DUMP')
    if platform.system() == "Linux":
        location = slogp.rfind("/")
    else:
        location = slogp.rfind("\\")
    slogbp = slogp[0:location]
    savepath = slogbp + os.path.sep + "post_process_report" + os.path.sep + "kernel_panic" + os.path.sep
    if not os.path.isdir(savepath):
        os.makedirs(savepath)
    print "savepath " +str(savepath)
    emmcf = savepath + "emmc.txt"
    ef = open(emmcf,"w+")
    kernelfs = folderparser.getFilesBy("memory")
    kernelfs = kernelfs.split(",")
    sp = FileSort(kernelfs)
    kernelfs = sp.fsort()
    for kf in kernelfs:
        try:
            kp = open(kf)
        except:
            print kf
            print "Open kernel error."
            continue
        line = kp.readline()
        while line:
            next_e = False
            if kernel_emmc_regex.search(line):
                ef.write("file: %s\n" %kf)
                ef.write(line)
                line = kp.readline()
                while line:
                    if line.find("===================") != -1:
                        break
                    if kernel_emmc_regex.search(line):
                        next_e = True
                        break
                    ef.write(line)
                    line = kp.readline()
            if next_e:
                continue
            line = kp.readline()
        kp.close()
    ef.close()
		
def parse_kernel_dmc_mpu(slogp,folderparser,kernel_log=None):

    kernel_dmcmpu_regex = re.compile(r'Warning! DMC MPU detected violated transaction')
    if platform.system() == "Linux":
        location = slogp.rfind("/")
    else:
        location = slogp.rfind("\\")
    slogbp = slogp[0:location]
    savepath = slogbp + os.path.sep + "post_process_report" + os.path.sep + "kernel_panic" + os.path.sep
    if not os.path.isdir(savepath):
        os.makedirs(savepath)
    print "savepath " +str(savepath)
    dmcmpuf = savepath + "dmcmpu.txt"
    kernelfs = []
    if kernel_log:
        kernelfs.append(savepath + "kernel_log.log")
        print "kernel log.log"
        mf = open(dmcmpuf,"a")
    else:
        kernelfs = folderparser.getFilesBy("memory")
        kernelfs = kernelfs.split(",")
        sp = FileSort(kernelfs)
        kernelfs = sp.fsort()
        mf = open(dmcmpuf,"w+")
    for kf in kernelfs:
        try:
            kp = open(kf)
        except:
            print kf
            print "Open kernel error."
            continue
        line = kp.readline()
        while line:
            next_e = False
            if kernel_dmcmpu_regex.search(line):
                mf.write("file: %s\n" %kf)
                mf.write(line)
                line = kp.readline()
                i = 0
                while line:
                    if i >= 30:
                        next_e = True
                        break
                    if kernel_dmcmpu_regex.search(line):
                        next_e = True
                        break
                    mf.write(line)
                    line = kp.readline()
                    i += 1
            if next_e:
               continue
            line = kp.readline()
        kp.close()
    mf.close()
	
def parse_kernel_deepsleep(slogp,folderparser):

    kernel_deepsleep_regex = re.compile(r'Enter Deepsleep  Condition Check!')
    if platform.system() == "Linux":
        location = slogp.rfind("/")
    else:
        location = slogp.rfind("\\")
    slogbp = slogp[0:location]
    savepath = slogbp + os.path.sep + "post_process_report" + os.path.sep + "kernel_panic" + os.path.sep
    if not os.path.isdir(savepath):
        os.makedirs(savepath)
    print "savepath " +str(savepath)
    deepsleepf = savepath + "deepsleep.txt"
    dsf = open(deepsleepf,"w+")
    kernelfs = folderparser.getFilesBy("memory")
    kernelfs = kernelfs.split(",")
    sp = FileSort(kernelfs)
    kernelfs = sp.fsort()
    for kf in kernelfs:
        try:
            kp = open(kf)
        except:
            print kf
            print "Open kernel error."
            continue
        line = kp.readline()
        while line:
            if kernel_deepsleep_regex.search(line):
                dsf.write("file: %s\n" %kf)
                while line:
                    if kernel_deepsleep_regex.search(line):
                        dsf.write(line)
                    line = kp.readline()
                line = kp.readline()
            line = kp.readline()
        kp.close()
    dsf.close()
		
#def get_assert(path):
    
def parse_assert(slogp):

    if platform.system() == "Linux":
        location = slogp.rfind("/")
    else:
        location = slogp.rfind("\\")
    slogbp = slogp[0:location]
    savepath = slogbp + os.path.sep + "post_process_report" + os.path.sep + "kernel_panic" + os.path.sep
    if not os.path.isdir(savepath):
        os.makedirs(savepath)
    print "savepath " +str(savepath)
    modem = savepath + "modem.txt"
    wcn = savepath + "wcn.txt"
    apr = slogp + os.path.sep + "apr.xml"
    if not os.path.exists(apr):
        print "no apr file."
        return 0
    p1 = open(modem,"w+")
    p2 = open(wcn,"w+")
    p1.write("file: %s\n" %apr)
    p2.write("file: %s\n" %apr)

    root = et.parse(apr).getroot() 
    aprnode = root.findall("apr")
    for apr in aprnode:
        try:
            exc = apr.getchildren()[7]
            print exc
            ent = exc.findall("entry")
            for en in ent:
                if en.find("type").text == "wcn assert":
                    print "ok"
                    times = en.find("timestamp").text
                    brief = en.find("brief").text        
                    p2.write("%s happend Wcn assert: %s\n" %(times,brief))            
                if en.find("type").text == "modem assert":
                    print "ok"
                    times = en.find("timestamp").text
                    brief = en.find("brief").text        
                    p1.write("%s happend Modem assert: %s\n" %(times,brief))            
                
        except:
            continue
    '''
    line = aprp.readline()
    while line:
        if line.find(" Modem ") != -1:
            p1.write(line)
        if line.find(" Wcn ") != -1: 
            p2.write(line)
        line = aprp.readline()
    '''
    p1.close()
    p2.close() 
    

	
class AnalyzeYlog(object):
    def __init__(self,ylog_p):
        self.ylog_p = ylog_p
    def analyzef(self):
        current_dir = os.path.abspath('.')
        print current_dir
        for parent,dirnames,filenames in os.walk(self.ylog_p):
            for filename in filenames:
                if filename.find("analyzer.py") != -1:
                    print parent
                    os.chdir(parent)
                    os.system("python analyzer.py")
        os.chdir(current_dir)

############################################################################################
def download_vmlinux():
    v_path = None 
    v_path = get_build_host()
    if v_path.endswith("/"):
        v_path = v_path[:-1]
    tlocation = v_path.find("jenkins/job/")
    vmpath = v_path[tlocation+12:].replace("/",os.path.sep)
    print vmpath
    product = get_device_mode()
     
    vmlinux_p = os.path.dirname(os.path.abspath('.'))+ os.path.sep + "symbols" + os.path.sep + vmpath + os.path.sep + product
    vmlinux_f = vmlinux_p + os.path.sep + "symbols" + os.path.sep + "vmlinux"
    #v_path = "http://10.0.1.56:8080/jenkins/job/sprdroid5.1_trunk_SharkLT8/55/artifact/SYMBOLS/"
    print vmlinux_f
    print "\n"
    if os.path.exists(vmlinux_f):
        return vmlinux_f
        pass
    else:
        v_path = v_path + "/artifact/SYMBOLS/"
        try:    
            os.makedirs(vmlinux_p)    
        except:    
            sys.stderr.write('the dir is exists %s\n'%vmlinux_p) 
        if v_path:
            print "start to down load symbols..."
            download_symbols(ylog_p,v_path,vmlinux_p)
            return vmlinux_f
            #pass
        else:
            print "Cannot get symbols version path"
            sys.exit(1)
#############################download_vmlinux end #####################    
if __name__== '__main__':

    if len(sys.argv)  >1:
        '''
        ylog_base_p = sys.argv[1]
        date = ylog_base_p.split('_')[-1][0:8]
        serial_num = ylog_base_p.split('_')[0]
        print "date:" + str(date)
        '''
        ylog_base_p = sys.argv[1]
        date = ylog_base_p.split('_')[-1][0:8]
        serial_num = "000"
    else:
        print "please input params: SN_date"
        print "such as 'python slog_postprocess.py 0123456789ABCDEF_20150829135231' "
        sys.exit(1)
    #log_base_p = os.path.abspath('.') + os.path.sep + "logs" + os.path.sep + slog_base_p
    #ylog_base_p = os.path.dirname(os.path.abspath('.')) + os.path.sep + "logs" + os.path.sep + ylog_base_p
    ylog_base_p = os.path.abspath(ylog_base_p)
    print "111"
    print ylog_base_p
    post_process_report = ylog_base_p + os.path.sep + "post_process_report"
    if os.path.exists(post_process_report):
        shutil.rmtree(post_process_report)
    for p,d,f in os.walk(ylog_base_p):
        for dir_name in d:
            if dir_name.find("log_") != -1:
                print dir_name
                sysdump_p1 = os.path.join(p,dir_name) + os.path.sep + "sysdump"
                sysdump_p2 = os.path.join(p,dir_name) + os.path.sep + "external_storage" + os.path.sep + "sysdump"
                sysdump_p3 = os.path.join(p,dir_name) + os.path.sep + "external_storage" + os.path.sep + "SYSDUMP"
                ylog_p = os.path.join(p,dir_name)
    if os.path.exists(sysdump_p2):
        
        dd = len(os.listdir(sysdump_p2))
        if dd != 0:
            sysdump_p = os.path.join(sysdump_p2,str("1"))
    elif os.path.exists(sysdump_p3):
       
        dd = len(os.listdir(sysdump_p3))
        if dd != 0:
            
            sysdump_p = os.path.join(sysdump_p3,str("1"))
    else:
        
        sysdump_p = sysdump_p1

    if ylog_p:
        print "ylog_base_p: " +str(ylog_p)
    else:
        print "No ylog for %s: " %ylog_p
        sys.exit(1)


    asy = AnalyzeYlog(ylog_p)
    asy.analyzef()
    title = None
    v_path = None
    fw_crash = None

    fp = FolderParser(ylog_p,serial_num)
    parse_kernel_warning(ylog_p,fp)
    parse_kernel_BUG(ylog_p,fp)
    parse_kernel_Error(ylog_p,fp)
    parse_kernel_emmc(ylog_p,fp)
    parse_kernel_dmc_mpu(ylog_p,fp)
    #parse_kernel_deepsleep(ylog_p,fp)
    parse_assert(ylog_p)
    #sys.exit(1)
####################################################################
    crash = False
    try:
        dd = len(os.listdir(sysdump_p))
        if dd != 0: 
            crash = True
    except:
        pass
    if crash:
        title = "There is reboot caused by kernel crash"
        sysdump_ci = {}
        sysdump_check(sysdump_ci)
        dumpf = True
        for k in sysdump_ci:
            if k < 3 :
                title += "\nsysdump file num is not correct!!!!!!!!!!!!!!!!"
                print title
                dumpf = False
                #sys.exit(1)
            if sysdump_ci[k] == 0L:
                title += "\nsysdump file size is not correct!!!!!!!!!!!!!!!!!!!!"
                print title
                dumpf = False
                #sys.exit(1)
        if dumpf:
            vmlinux_f = download_vmlinux()
            dev_bit = get_device_mode()

        #run_kernel_panic()
            run_kernel_panic(dev_bit)
            run_java_crash()
            run_native_crash()
            run_watchdog_crash()
            run_anr()
            run_lowpower()
            run_kmemleak()
            parse_kernel_dmc_mpu(ylog_p,"default","kernelpanic")
        #run_mm()
            print title
        else:
            run_java_crash()
            run_native_crash()
            run_watchdog_crash()
            run_anr()
            run_lowpower()
            run_kmemleak()
            parse_kernel_dmc_mpu(ylog_p,"default","kernelpanic")
        #run_mm()
            print title
    else:
        title = "There is no reboot caused kernel crash"
        print title
        run_java_crash()
        run_native_crash()
        run_watchdog_crash()
        run_anr()
        run_lowpower()
        run_kmemleak()
        #run_mm()


    generate_list(ylog_base_p)
    folderp = FolderParser(ylog_p,serial_num)
    try:
        run_time(ylog_p,folderp)
    except:
        print "Failed to get run time."

