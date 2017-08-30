#!usr/bin/env python
# coding:utf-8


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

global ylog_p
global serial_num
num64 = "sp9850"
num642 = "sp9860"
num643 = "sp9832"

crash = None
savepath = None


def isLinux():
    sysstr = platform.system()
    if (sysstr == "Windows"):
        return False
    elif (sysstr == "Linux"):
        return True
    else:
        return False


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
        self.dateinternal = "DATE_INTERNAL"
        self.dateinternal_lastlog = "DATEINTERNAL_LASTLOG"
        self.dateexternal = "DATE_EXTERNAL"
        self.dateexternal_lastlog = "DATEEXTERNAL_LASTLOG"
        # store the fade and real path map
        self.mapfadereal = {}
        self.initdata()
        self.logfolder = logfolder
        if self.logfolder == None or self.logfolder == "":
            self.logfolder = self.getLogPath()
        print "logfolder " + str(self.logfolder)
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

    def workpath(self):
        for parent, dirnames, filenames in os.walk(self.logfolder):
            for dirname in dirnames:
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
                if dirname.find("ylog") != -1 and parent.endswith("last_ylog") and parent.find(
                        "external_storage") != -1:
                    print "last_ext"
                    print dirname
                    print parent
                    self.mapfadereal[self.dateexternal_lastlog].append(dirname)
                if dirname.find("ylog") != -1 and dirname.find("last_ylog") < 0 and parent.endswith("external_storage"):
                    print "ext"
                    print dirname
                    print parent
                    self.mapfadereal[self.dateexternal] = dirname
                if dirname.find("ylog") != -1 and dirname.find("last") < 0 and parent.endswith("internal_storage"):
                    print "inter"
                    print dirname
                    print parent
                    self.mapfadereal[self.dateinternal] = dirname
                if dirname.find("last_ylog") != -1 and parent.endswith("internal_storage"):
                    print "last_inter"
                    print dirname
                    print parent
                    self.mapfadereal[self.dateinternal_lastlog] = dirname
                self.fullfolderpaths.append(os.path.join(parent, dirname))

            # self.printData()
            for filename in filenames:
                # print "parent is"+ parent
                # print "filename is:" + filename
                # print "the full name of the file is:" + os.path.join(parent,filename)
                self.fullfilepaths.append(os.path.join(parent, filename))
                # print "*****************self.mapfadereal*************"
                # print self.mapfadereal

    # return the string list of files with "," split
    def getFilesBy(self, typeName):
        files = self.cp.getProblemFiles(typeName)
        print typeName
        for f in files:
            f.toStr()
        # print f
        print typeName
        tmprefiles = []
        # count_num = 0
        # print files
        # get all path meeted files
        for i in self.fullfilepaths:
            #    count_num += 1
            #   print "--------------print count_num----------------"
            #    print str(count_num)
            #    print "------------print i----------------"
            #    print i
            for f in files:
                # print "xx"+f.getPath()
                # print "yy"+self.getRealPath(f.getPath())
                # print "0000000000f in files0000000000"
                # print f
                pp = ""
                if not isLinux():
                    pp = f.getPath().replace("/", "\\")
                else:
                    pp = f.getPath().replace("\\", "/")
                    # print "tototoototototototot"
                    # f.toStr()
                    # print "--------------print pp----------------"
                    # print pp
                    # print self.getRealPath(pp)
                    # print i
                pp_list = self.getRealPath(pp)
                # print "plplplplplplplplplplplplplp"
                # for pl in pp_list:
                #    print pl
                # for ppl in pp_list:
                for jn in range(len(pp_list)):
                    if i.find(pp_list[jn]) >= 0:
                        # check items
                        chk = f.getCheckitem()
                        # print "chk" + str(chk)
                        if chk == "" or chk == None:
                            tmprefiles.append(i)
                        else:
                            for ii in chk.split(","):
                                if os.path.basename(i).find(ii) >= 0:
                                    tmprefiles.append(i)
                                    break
                                    # break
        print "tmprefile " + str(tmprefiles)
        tmprefiles = list(set(tmprefiles))
        return ",".join(tmprefiles)
        pass

    def __checkComplete(self, f):
        i = 0
        while i < len(f):
            i += 1
        return f

    # return null if file path is not exist
    def getRealPath(self, fadepath):
        result = fadepath
        if result == "" or result == None:
            return ""
        results = []
        # print "---------self.mapfadereal.item------"
        # print self.mapfadereal.items
        for (k, v) in self.mapfadereal.items():
            if result.find(k) != -1:

                # print "************print k v**************88"
                # print k,v
                if v == "" or v == []:
                    results.append(result.replace(k, "nofolderfound"))
                else:
                    if isinstance(v, list):
                        for i in range(len(v)):
                            # print "list"
                            # print v[i]
                            vv = v[i]
                            if isinstance(vv, tuple):
                                results.append(result.replace(k, vv[1]).replace("DATEEXTERNAL_LASTLOG", vv[0]))
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


class ConfigParser:
    def __init__(self, configfile):
        self.configfile = configfile
        self.root = et.parse(configfile).getroot()
        pass

    # get checkItems
    def getCheckItems(self):
        checkfileNode = self.root.find("checkfile")
        files = checkfileNode.findall("file")
        fArr = []
        # stype="file",ismust=0,checkitem="",condition="",path=""
        for f in files:
            # print f.get("type"),f.get("ismust"),f.get("checkitem"),f.get("condition"),f.text
            ff = FileItem(f.get("type"), f.get("ismust"), f.get("checkitem"), f.get("condition"), f.text)
            fArr.append(ff)
            pass
        return fArr

    def getProblemFiles(self, problemtype):
        problems = self.getProblems()
        files = []
        ffs = None
        for p in problems:
            if p.get("type") == problemtype:
                # here get all file list
                ffs = p.findall("file")
                break
        if ffs != None:
            for x in ffs:
                ff = FileItem(x.get("type"), "", x.get("checkitem"), "", x.text)
                ff.toStr()
                files.append(ff)
            pass
        return files
        pass

    def getProblems(self):
        problemneedfilenode = self.root.find("problemneededfile")
        return problemneedfilenode.findall("problem")


class FileItem(object):
    '''
    used for file complition check
    '''

    def __init__(self, stype="file", ismust=0, checkitem="", condition="", path="", checktype="default"):
        '''
        Constructor
        '''
        self.stype = stype
        self.ismust = ismust
        self.checkitem = checkitem
        self.condition = condition
        self.path = path
        self.checktype = checktype
        self.checkresult = ""
        pass

    def getCheckitem(self):
        return self.checkitem

    def getPath(self):
        return self.path

    def toStr(self):
        print str(self.stype) + str(self.ismust) + str(self.checkitem) + str(self.condition) + str(self.path)


def printstr(str):
    # if debug:
    if True:
        print str


class Main:
    def __init__(self, vmlinuxPath, sysdumpPath=None, slogPath=None, devbitInfo=None, devNum=None):
        # def __init__(self, sysdumpPath=None, slogPath=None, devNum=None):
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
        self.oops_log_report_tag = "------ Oops log result ------"
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
        self.savePath = self.slogBasePath + os.path.sep + "post_process_report" + os.path.sep + "kernel_panic" + os.path.sep + "kernel_panic" + ".txt"
        self.savePath_dir = self.slogBasePath + os.path.sep + "post_process_report" + os.path.sep + "kernel_panic" + os.path.sep

        if not os.path.isdir(self.savePath_dir):
            os.makedirs(self.savePath_dir)
        print "savepath " + str(self.savePath)
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
        # printstr("begin run")
        # self.report_content += self.getSlogCheckReport() + "\n"
        # self.report_content += self.getAndroidKernelLogkReport() + "\n"
        self.report_content += str(self.getAndroidRebootMode()) + "\n"
        # self.report_content += self.getCheckSysdumpReport() + "\n"
        # self.report_content += self.getLastRegAccess() + "\n"
        self.report_content += self.getSysdumpKernelLog() + "\n"
        # self.report_content += self.getTextSegmentCompareResult() + "\n"
        pass

    def getSysdumpKernelLog(self):
        global bit_t
        result = self.kernel_log_sysdump_report_tag + "\n"
        sysdumpfile = self.getfile("01_0x80000000-0x87ffffff")
        if sysdumpfile == None:
            sysdumpfile = self.getfile("01_0x80000000-0xbfffffff")
        if sysdumpfile == None:
            sysdumpfile = self.getfile("sysdump.core.01")
        print sysdumpfile
        klp = KernelLogParser(self.vmlinuxPath, sysdumpfile, self.devbitInfo,
                              self.slogBasePath + os.path.sep + "post_process_report" + os.path.sep + "kernel_panic" + os.path.sep)

        res = klp.parser()

        result += "kernel log location:\n" + res[0] + "\n" + res[1]
        print result
        # write Oops log to logreport
        result += self.oops_log_report_tag + "\n"
        if os.path.exists(res[1]):
            f = open(res[1])
            result += f.read()
            f.close()
            pass
        else:
            result += "No Oops log"

        return result
        if sysdumpfile.find("dumpall") != -1:
            os.remove(sysdumpfile)
        pass

    def getAndroidRebootMode(self):
        # get cmdline.log path
        '''
        import os
        path=last_log_path+"*/misc/cmdline.log"
        result = os.popen("ls " + path).read()
        print result
        '''
        fp = FolderParser(self.slogPath, self.devnum)
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
                    return self.startmode_report_tag + "\n" + "no androidboot.mode"
                    # return "norebootmode"
                else:
                    subresult = str(content)[rebootmodeindex:len(content)]
                    subresult = subresult.split(" ")[0]
                    subresult = subresult.split("=")[1]
                    return self.startmode_report_tag + "\n" + subresult
                    # return subresult
            else:
                print "file  " + f + " is not exist"
                return self.startmode_report_tag + "\n" + "no cmdline.log file"
        pass

        '''
            get all content from kernel log contains log keys
        '''

    def genReport(self):
        printstr("generate report")
        printstr("detail pls refer to the report")
        f = open(self.savePath, 'w')
        f.write(self.report_content)
        f.close()
        print "report store in  file " + self.savePath
        pass


class KernelLogParser:
    def __init__(self, vmpath, dumppath, devbit, savelocation):
        self.vmpath = vmpath
        self.dumppath = os.path.dirname(dumppath)
        self.dumpfile = self.dumppath + os.path.sep + "dump"
        self.devbit = devbit
        self.savelocation = savelocation
        if not os.path.isdir(self.savelocation):
            os.makedirs(self.savelocation)
        pass
        if (self.devbit.find("9850") != -1 or self.devbit.find("9860") != -1) and self.devbit.find("9850ka") < 0:
            self.tool = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
                os.path.dirname(os.path.dirname(self.vmpath)))))) + os.path.sep + "tools" + os.path.sep + "crash64"
        elif self.devbit.find("9861") != -1:
            self.tool = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
                os.path.dirname(os.path.dirname(self.vmpath)))))) + os.path.sep + "tools" + os.path.sep + "crash64_2"
        else:
            self.tool = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
                os.path.dirname(os.path.dirname(self.vmpath)))))) + os.path.sep + "tools" + os.path.sep + "crash32"
        print self.vmpath
        print self.tool

    def parser(self):
        overw_flag = False
        os.system("cat %s/sysdump.core.0* >%s" % (self.dumppath, self.dumpfile))
        print "parser vmlinux"
        if (self.devbit.find("9850") != -1 or self.devbit.find("9860") != -1) and self.devbit.find("9850ka") < 0:
            cmd = "%s -m phys_offset=0x80000000 %s %s" % (self.tool, self.dumpfile, self.vmpath)
        elif self.devbit.find("9861") != -1:
            cmd = "%s -m phys_base=0x34200000 %s %s --cpus 8" % (self.tool, self.dumpfile, self.vmpath)
        else:
            cmd = "%s -m phys_base=0x80000000 %s %s" % (self.tool, self.dumpfile, self.vmpath)
        print cmd
        child = pexpect.spawn(cmd)
        if (self.devbit.find("9850") != -1 or self.devbit.find("9860") != -1) and self.devbit.find("9850ka") < 0:
            child.expect("crash64>")
        elif self.devbit.find("9861") != -1:
            child.expect("crash64_2>")
        else:
            child.expect("crash32>")
        # crash = child.expect('erin')
        # child.expect(cmdline)
        print "crashhhhhhhhhhhhhhhhhhhhhh"
        # print crash
        # fout = open (self.savelocation + "kernel_log.log", "w")
        kernel_log = self.savelocation + "kernel_log.log"
        #########time.sleep(30)
        # cmd1 = "log >%s" %kernel_log
        cmd1 = "log > %s" % kernel_log
        print cmd1
        # child.sendline("log > kernel_log.txt")
        child.sendline(cmd1)
        child.sendline("q")
        time.sleep(2)
        child.close(force=True)
        print self.dumpfile
        os.system("rm %s" % self.dumpfile)
        kernelpath = self.savelocation + 'kernel_log.log'
        oopspath = self.savelocation + 'kernel_Oops.log'

        return kernelpath, oopspath


class FileSort(object):
    def __init__(self, filelist):

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


def get_product(devf):
    product = get_build_host()
    try:
        product = product.split('/')[5]
        return product
    except:
        pass

        # product:sprdroid5.1_trunk_SharkLT8


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
                line = re.findall(pattern, line, re.M)
                if (len(line) > 1):
                    line = line[1]
                    b_version = line.replace('[', '').replace(']', '')
                    location = b_version.find('/')
                    b_version = b_version[location + 1:-1]
                break
            line = fd.readline()
    if b_version:
        # print b_version
        return b_version
        # sp9838aea_oversea/scx35l64_sp9838aea_5mod:5.1/LMY47D-W15.24.2-01:userdebug/test-key


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
                line = re.findall(pattern, line, re.M)
                if (len(line) > 1):
                    line = line[1]
                    hw_version = line.replace('[', '').replace(']', '')
                break
            line = fd.readline()
    if hw_version:
        # print hw_version
        return hw_version
        # pass
        # [ro.product.hardware]: [SP9838A-1_V1.0.0(5M)]


def get_version_pac(devicef, fingerf):
    # b_host = get_build_host(devicef)
    b_host = ""
    b_host = get_build_host()
    b_host = b_host + "artifact/PAC/"
    d_mode = ""
    d_mode = get_device_mode()
    ss = get_base_version(fingerf)
    location = ss.rfind(':')
    ss = ss[location + 1:]
    ss = ss.split('/')[0]
    pac = b_host + d_mode + "_" + ss + "-native"
    # print pac
    return pac


def get_logcheck(logpath, pp):
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


def get_serverp(logpath, pp):
    baset = logpath.split(os.path.sep)
    base = baset[-2] + os.path.sep + baset[-1]
    serverp = "erin.liu@10.0.64.46:~/log_postprocess/log_postprocess_5.0.5/logs/" + base
    pp.write("Log path in server: %s\n" % serverp)
    pp.write("Password:PSD#sciuser\n")


def get_basic_info(logpath, pp):
    deviceinfo = logpath + os.path.sep + "sysprop.txt"
    fingerinfo = logpath + os.path.sep + "ro.build.fingerprint.txt"
    product = ""
    base_version = ""
    hardware_version = ""
    version_pac = ""

    if os.path.exists(deviceinfo):
        product = get_product(deviceinfo)
        pp.write("Product name: %s\n" % product)
        hardware_version = get_hw_version(deviceinfo)
        pp.write("Hardware version: %s\n" % hardware_version)
    if os.path.exists(fingerinfo):
        base_version = get_base_version(fingerinfo)
        pp.write("Base version: %s\n" % base_version)

    if os.path.exists(deviceinfo) and os.path.exists(fingerinfo):
        version_pac = get_version_pac(deviceinfo, fingerinfo)
        pp.write("Version pac: %s\n\n" % version_pac)


def walkpath(log_path):
    global kernel_panic
    kernel_panic = False

    problem_file = []
    for p, d, f in os.walk(log_path):
        for file_list in f:
            if file_list.find("kernel_log.log") != -1:
                problem_file.append(os.path.join(p, file_list))
                kernel_panic = True
            # break
            if file_list.find("watchdog_list.txt") != -1:
                problem_file.append(os.path.join(p, file_list))
            if file_list.find("java_crash_list.txt") != -1:
                problem_file.append(os.path.join(p, file_list))
            if file_list.find("native_crash_list.txt") != -1:
                problem_file.append(os.path.join(p, file_list))
            if file_list.find("lowpower_list.txt") != -1:
                problem_file.append(os.path.join(p, file_list))
            if file_list.find("kmemleak_list.txt") != -1:
                problem_file.append(os.path.join(p, file_list))
            if file_list.find("anrpidlist.txt") != -1:
                problem_file.append(os.path.join(p, file_list))
        for dir_list in d:
            dirlist = None
            dirlist = os.listdir(os.path.join(p, dir_list))
            if dirlist:
                pass
            else:
                shutil.rmtree(os.path.join(p, dir_list))
    return problem_file


def get_probleminfo(ll, pro):
    for pp in pro.keys():

        if isinstance(pp, tuple):
            if ll.find(pp[0]) != -1 and ll.find(pp[1]) != -1:
                return (pp, pro[pp])
        else:
            if ll.find(pp) != -1:
                return (pp, pro[pp])
    return 0


def generate_final_report(finalf, plist, repol):
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
                if len(plist) > 0:
                    flag = get_probleminfo(line, plist)
                    if flag != 0:
                        # plist.remove(flag)
                        del plist[flag[0]]
                        finalf.write("\n")
                        if isinstance(flag[0], tuple):
                            finalf.write(
                                str(flag[0][0]) + " " + str(flag[0][1]) + " crash " + str(flag[1]) + " times.\n")
                        else:
                            finalf.write(str(flag[0].strip()) + " " + " crash " + str(flag[1]) + " times.\n")
                        finalf.write(linefile)
                        while line:
                            finalf.write(line)
                            line = pl.readline()
                            if line.find("file: ") != -1 or line.find("--------------") != -1:
                                next_flag = True
                                break
                            # if line.find("am_crash") != -1 or line.find("pid:") != -1 or line.find("Subject:") != -1:
                            if javacrash_regex.search(line) or nativecrash_regex.search(line) or watchdog1_regex.search(
                                    line) or watchdog2_regex.search(line):
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


def generate_final_report2(finalf, plist, repol):
    watchdog3_regex = re.compile("tid=")
    watchdog_crash1_regex = re.compile(r'waiting')
    watchdog_crash_get_regex = re.compile(r'\((.*?)\)')
    pl = open(repol)
    line = pl.readline()
    while line:
        # next_flag = False
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
                                if len(plist) > 0:
                                    flag = get_probleminfo(tmp, plist)
                                    if flag != 0:
                                        del plist[flag[0]]
                                        finalf.write("\n")
                                        finalf.write(
                                            str(flag[0].strip()) + " " + " crash " + str(flag[1]) + " times.\n")
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
        hours = sec / 3600
        minutes = sec / 60 - sec / 3600 * 60
        seconds = sec - sec / 60 * 60
        time = str(hours) + ":" + str(minutes) + ":" + str(seconds)
        return time
    except:
        pass


def kernel_panic_abstr(kernel_t, fp_out):
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
    fp = open(kernel_t, 'r')
    line = fp.readline()
    warningf = os.path.dirname(kernel_t) + os.path.sep + "warning.txt"
    emmcf = os.path.dirname(kernel_t) + os.path.sep + "emmc.txt"
    fp_out.write("Kernel crash:\n")
    kernel_crash_time = None
    kernel_crash_module = None
    while line:
        if kernel_panic_regex.search(line) or kernel_bug_regex.search(line):
            # if kernel_panic_regex.search(line):
            line_ori = line
            kernel_crash_module = line.split(' ')[-1].strip()
            pattern = r"(\[.*?\])"
            line = re.findall(pattern, line, re.M)
            if (len(line) > 0):
                line = line[0]
                kernel_crash_time = line.replace('[', '').replace(']', '').replace(' ', '')
                kernel_crash_time = convert(kernel_crash_time)
                break
        line = fp.readline()
    fp_out.write("Kernel crash module: %s\n" % kernel_crash_module)
    fp_out.write("kernel crash time: %s\n" % kernel_crash_time)
    # fp_out.write("***********************kernel_panic_log*******************\n")
    # fp_out.write("Kernel crash log:\n")
    fp.seek(0)
    line = fp.readline()
    f_flag = False
    pc_flag = False
    while line:
        if line.find(" cut here ") != -1:
            cut_line = line
            # fp_out.write(line)
            line = fp.readline()
            while line:
                if kernel_warning_regex.search(line):
                    wp = open(warningf, 'a+')
                    wp.write("file: %s\n" % kernel_t)
                    wp.write(cut_line)
                    i = 0
                    while line and i < 30:
                        # fp_out.write(line)
                        wp.write(line)
                        i += 1
                        line = fp.readline()
                        if line.find(" end trace ") != -1:
                            # fp_out.write(line)
                            wp.write(line)
                            wp.write("\n")
                            break
                    wp.close()
                if kernel_panic_Panic_regex.search(line) or kernel_panic_panic_regex.search(
                        line) or kernel_panic_oops_regex.search(line) or kernel_panic_bug_regex.search(line):
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
            if kernel_panic_Panic_regex.search(line) or kernel_panic_panic_regex.search(
                    line) or kernel_panic_oops_regex.search(line) or kernel_panic_bug_regex.search(line) or line.find(
                "Unable to handle kernel") != -1 or line.find("Modules linked in") != -1:
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
                wp = open(warningf, 'a+')
                wp.write("file: %s\n" % kernel_t)
                i = 0
                wp.write("\n")
                while line and i < 30:
                    # fp_out.write(line)
                    wp.write(line)
                    i += 1
                    line = fp.readline()
                    if line.find(" end trace ") != -1:
                        # fp_out.write(line)
                        wp.write(line)
                        wp.write("\n")
                        break
                wp.close()

            line = fp.readline()

    if not f_flag:
        fp.seek(0)
        line = fp.readline()
        while line:
            if kernel_panic_panic_regex.search(line) or kernel_panic_oops_regex.search(
                    line) or kernel_panic_bug_regex.search(line):
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
        fp_out.write("please refer to %s" % kernel_t)

    fp.seek(0)
    line = fp.readline()

    ef = open(emmcf, "a+")

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
    nativecrash_system_server_regex = re.compile(
        r'pid: [0-9]+, tid: [0-9]+,\s*name:\s*(.*)\s*>>>\s*system_server\s*<<<')
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

    # slog_base_p = sys.argv[1]
    crash_file = None
    log_dir = slog_base_p + os.path.sep + "post_process_report"
    # warning_file = log_dir + os.path.sep + "warning_file"
    pproblem_list = log_dir + os.path.sep + "problem_list.txt"
    final_report = log_dir + os.path.sep + "final_report.txt"
    pidlist = log_dir + os.path.sep + "anr" + os.path.sep + "anrpidlist.txt"
    if os.path.exists(pproblem_list):
        os.remove(pproblem_list)
    if os.path.exists(final_report):
        os.remove(final_report)

    fp = open(pproblem_list, "w+")
    # fr = open(final_report,"w+")
    get_serverp(slog_base_p, fp)

    for dd in os.listdir(slog_base_p):
        if dd.find("log_") != -1:
            slogp = os.path.join(slog_base_p, dd)
            get_logcheck(slogp, fp)
            get_basic_info(slogp, fp)
            break
    # kernel_panic = False
    problem_list = walkpath(log_dir)
    num_java = 0
    num_native = 0
    num_watchdog = 0
    num_anr = 0

    if kernel_panic:
        fr = open(final_report, "w+")
        kernel_log = log_dir + os.path.sep + "kernel_panic" + os.path.sep + "kernel_log.log"
        # ff = open(final_report,"w")
        kernel_panic_abstr(kernel_log, fr)
        # ff.close()
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
            fp.write("\nThere is warning error in kernel log: total %s times.\n" % str(i))
            fp.write("Please refer to %s\n" % warningf)
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
            fp.write("\nThere is BUG error in kernel log: total %s times.\n" % str(i))
            fp.write("Please refer to %s\n" % bugf)
        else:
            os.remove(bugf)

    if os.path.exists(errorf):
        erf = open(errorf)
        line = erf.readline()
        i = 0
        while line:
            if kernel_Error_regex.search(line):
                i += 1
            line = erf.readline()
        erf.close()
        if i > 0:
            fp.write("\nThere is Error in kernel log: total %s times.\n" % str(i))
            fp.write("Please refer to %s\n" % errorf)
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
            fp.write("\nThere is emmc error in kernel log: total %s times.\n" % str(i))
            fp.write("Please refer to %s\n" % emmcf)
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
            fp.write("\nThere is DMC MPU error in kernel log: total %s times.\n" % str(i))
            fp.write("Please refer to %s\n" % dmcmpuf)
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
            fp.write("\nThere is modem assert: total %s times.\n" % str(i))
            fp.write("Please refer to %s\n" % modemf)
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
            fp.write("\nThere is wcn assert: total %s times.\n" % str(i))
            fp.write("Please refer to %s\n" % wcnf)
        else:
            os.remove(wcnf)

    if len(problem_list) < 1:
        # fp.write("No crash java/native/wt crash issue found.")
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
        fr = open(final_report, "a")
        for pp in problem_list:
            if pp.find("lowpower_list.txt") != -1:
                fd = open(pp)
                line = fd.readline()
                while line:
                    if line.find("file: ") != -1 or line.find("-----------") != -1 or line.find(
                            "Last temprature values and last cap value will be written") != -1:
                        pass
                    else:
                        fp.write("\nPowerdown & charging:\n")
                        fr.write("-----------------lowpower charger--------------------\n")
                        break
                    line = fd.readline()
                fd.seek(0)
                line = fd.readline()
                while line:
                    if line.find("file: ") != -1 or line.find(
                            "Last temprature values and last cap value will be written") != -1:
                        pass
                    else:
                        fp.write(line)
                    fr.write(line)
                    line = fd.readline()
                fd.close()

            if pp.find("java_crash_list.txt") != -1:
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
                                tmp = re.findall(pattern, line, re.M)[0].split(",")
                                javacrashmodule = tmp[2]
                                javacrashp = tmp[4]
                                # problemlist[javacrashmodule] = javacrashp
                                problemlist.append((javacrashmodule, javacrashp))
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
                # print "Java crash: Total %s." %(num_java)
                problemlist = list(set(problemlist))
                pnum = problemnum.copy()
                for k in problemlist:
                    print k
                fd.close()
                # generate_final_report(fr,problemlist,pp)
                ######write to final_report
                generate_final_report(fr, problemnum, pp)
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
                                flag = get_probleminfo(line, pnum)
                                if flag != 0 and (
                                                line.find("IN SYSTEM PROCESS") != -1 or line.find(
                                            "system_server") != -1):
                                    del pnum[flag[0]]
                                    javacrash_module = None
                                    javacrash_time = None
                                    if isinstance(flag[0], tuple):
                                        javacrash_module = flag[0][0]
                                    else:
                                        javacrash_module = flag[0]
                                    if line[0] >= "0" and line[0] <= "9":
                                        javacrash_time = line.split(" ")
                                        javacrash_time = javacrash_time[0] + "_" + javacrash_time[1]
                                    fp.write("\nJava crash:\n")
                                    fp.write("Java crash module: %s\n" % javacrash_module)
                                    fp.write("Java crash time: %s\n" % javacrash_time)
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

            if pp.find("native_crash_list.txt") != -1:
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
                                problemlist.append((nativecrasht, nativecrashp))
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
                print "Native crash: Total %s." % (num_native)
                problemlist = list(set(problemlist))
                pnum = problemnum.copy()
                for k in problemlist:
                    print k
                fd.close()
                ########write to final_report
                generate_final_report(fr, problemnum, report)
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
                                flag = get_probleminfo(line, pnum)
                                if flag != 0 and nativecrash_system_server_regex.search(line):
                                    del pnum[flag[0]]
                                    nativecrash_module = None
                                    nativecrash_time = None
                                    if isinstance(flag[0], tuple):
                                        nativecrash_module = flag[0][0]
                                    else:
                                        nativecrash_module = flag[0]
                                    if line[0] >= "0" and line[0] <= "9":
                                        nativecrash_time = line.split(" ")
                                        nativecrash_time = nativecrash_time[0] + "_" + nativecrash_time[1]
                                    fp.write("\nNative crash:\n")
                                    fp.write("Native crash module: %s\n" % nativecrash_module)
                                    fp.write("Native crash time: %s\n" % nativecrash_time)
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

            if pp.find("watchdog_list.txt") != -1:
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
                print "Watchdog timeout: Total %s." % (num_watchdog)
                problemlist = list(set(problemlist))
                pnum = problemnum.copy()
                generate_final_report(fr, problemnum, report)
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
                                flag = get_probleminfo(line, pnum)
                                if flag != 0:
                                    del pnum[flag[0]]
                                    wtcrash_module = None
                                    wtcrash_time = None
                                    if isinstance(flag[0], tuple):
                                        wtcrash_module = flag[0][0]
                                    else:
                                        wtcrash_module = flag[0]
                                    if line[0] >= "0" and line[0] <= "9":
                                        wtcrash_time = line.split(" ")
                                        wtcrash_time = wtcrash_time[0] + "_" + wtcrash_time[1]
                                    fp.write("\nWatchdog timeout crash:\n")
                                    fp.write("Watchdog timeout crash module: %s\n" % wtcrash_module)
                                    fp.write("Watchdog timeout crash time: %s\n" % wtcrash_time)
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
                    print "Watchdog timeout: Total %s." % (num_watchdog)
                    generate_final_report2(fr, problemnum, report)
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

                                        # if watchdog1_regex.search(wtline) or watchdog2_regex.search(wtline):
                                        if watchdog_crash1_regex.search(wtline):
                                            wtcrash_module = watchdog_crash_get_regex.search(wtline)
                                            if wtcrash_module:
                                                wtcrash_module = wtcrash_module.groups()[0].split('.')[-1]
                                                break
                                        wtline = reportp.readline()
                                    fp.write("Watchdog timeout crash module: %s\n" % wtcrash_module)
                                    fp.write("Watchdog timeout crash time: %s\n" % wtcrash_time)

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
        fp.write("\nJava crash:Total %s times.\n" % num_java)
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
        fp.write("\nNative crash:Total %s times.\n" % num_native)
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
        fp.write("\nWatchdog timeout:Total %s times.\n" % num_watchdog)
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
        fp.write("\nANR:Total %s times.\n" % num_anr)
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
def getKernelLogPaths(fparser, TYPE):
    logstr = fparser.getFilesBy(TYPE)
    if logstr:
        return logstr.split(',')
    return None


def get_time(line):
    if line == "":
        return None
    d = [datetime.datetime.now().year, string.atoi(line[5:7]), string.atoi(line[8:10]), string.atoi(line[11:13]),
         string.atoi(line[14:16]), string.atoi(line[17:19])]
    Time = datetime.datetime(d[0], d[1], d[2], d[3], d[4], d[5])
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
        if time_lenth.seconds > 300:  # 如果超过5分钟就判断reboot测试出现问题，就判定end time 是出现问题出现之前的时间
            fd.close()
            return (start_time, next_time)
    fd.seek(0)
    line = fd.readline()
    while line:
        tmpline = line
        line = fd.readline()
    fd.close()
    next_time = get_time(tmpline)
    return (start_time, next_time)


def get_start_end_time_msr(filep):
    rtime = 0
    time_line_regex = re.compile(r'\d\d:\d\d:\d\d GMT ')
    dated = {'Sun': '1', 'Mon': '2', 'Tue': '3', 'Wed': '4', 'Thu': '5', 'Fri': '6', 'Sat': '7'}
    fd = open(filep)
    line = fd.readline()
    while line:
        if line.find("/data/pid.txt exist") != -1:
            line = fd.readline()
            if time_line_regex.search(line):
                tmp_time = line.split(" ")
                day = dated[tmp_time[1]]
                (h, m, s) = tmp_time[5].split(":")
                print h, m, s
                d = [datetime.datetime.now().year, datetime.datetime.now().month, string.atoi(str(day)),
                     string.atoi(str(h)), string.atoi(str(m)), string.atoi(str(s))]
                start_time = datetime.datetime(d[0], d[1], d[2], d[3], d[4], d[5])
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
                    (h, m, s) = tmp_time[5].split(":")
                    d = [datetime.datetime.now().year, datetime.datetime.now().month, string.atoi(str(day)),
                         string.atoi(str(h)), string.atoi(str(m)), string.atoi(str(s))]
                    first_time = datetime.datetime(d[0], d[1], d[2], d[3], d[4], d[5])
                    break
            line = fd.readline()
        # if (first_time - start_time).seconds > 259200:
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
                    (h, m, s) = tmp_time[5].split(":")
                    d = [datetime.datetime.now().year, datetime.datetime.now().month, string.atoi(str(day)),
                         string.atoi(str(h)), string.atoi(str(m)), string.atoi(str(s))]
                    end_time = datetime.datetime(d[0], d[1], d[2], d[3], d[4], d[5])
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
        return (end_time - start_time + rtime)
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
        d = [datetime.datetime.now().year, string.atoi(line[1:3]), string.atoi(line[4:6]), string.atoi(line[7:9]),
             string.atoi(line[10:12]), string.atoi(line[13:15])]
        start_time = datetime.datetime(d[0], d[1], d[2], d[3], d[4], d[5])
        print start_time
        dp.close()
        return start_time

    def find_test_end_time(self, keyword):
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
                if line[1] >= '0' and line[1] <= '9':
                    count -= 1
                    if count == 0:
                        break
                line = fd.readline()
            fd.close()
            d = [datetime.datetime.now().year, string.atoi(line[1:3]), string.atoi(line[4:6]), string.atoi(line[7:9]),
                 string.atoi(line[10:12]), string.atoi(line[13:15])]
            end_time = datetime.datetime(d[0], d[1], d[2], d[3], d[4], d[5])
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
                        if len(line) < 2:
                            line = fd.readline()
                            continue
                        if line[1] >= '0' and line[1] <= '9':
                            break
                        line = fd.readline()
                    print line
                    try:
                        d = [datetime.datetime.now().year, string.atoi(line[1:3]), string.atoi(line[4:6]),
                             string.atoi(line[7:9]), string.atoi(line[10:12]), string.atoi(line[13:15])]
                    except:
                        d = [datetime.datetime.now().year, string.atoi(line[0:2]), string.atoi(line[3:5]),
                             string.atoi(line[6:8]), string.atoi(line[9:11]), string.atoi(line[12:14])]
                    end_time = datetime.datetime(d[0], d[1], d[2], d[3], d[4], d[5])

                    print end_time
                    fd.close()
                    return end_time

                line = fd.readline()

            fd.close()
            return False  # 如果没有找到返回false


def sd_last_kernel_get_time(line):
    if line[1] < '0' or line[1] > '9':
        return False
    d = [datetime.datetime.now().year, string.atoi(line[1:3]), string.atoi(line[4:6]), string.atoi(line[7:9]),
         string.atoi(line[10:12]), string.atoi(line[13:15])]
    Time = datetime.datetime(d[0], d[1], d[2], d[3], d[4], d[5])
    return Time


def sd_last_kernel_start_end_time(filep2):
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
        return end_time
    return ret


def run_time(log_p, folderparser):
    calendar_time_regex = re.compile("(calendar_time):([0-9]+)")
    Monkey_Start_Calendar_Time = re.compile(r"( Monkey Start Calendar Time ):( [0-9]+)")
    log_base_p = os.path.dirname(log_p)
    log_dir = log_base_p + os.path.sep + "post_process_report"
    test_time_file = log_dir + os.path.sep + "test_time_report.txt"
    # test_time_list = log_dir + os.path.sep + "test_time_list.txt"
    preport = open(test_time_file, "w+")

    #######calculate all ylog runtime#############
    ylogpath = log_p + os.path.sep + "external_storage" + os.path.sep + "last_ylog" + os.path.sep + "ylog"
    for i in range(1, 6):
        ylog = ylogpath + str(i) + os.path.sep + "kernel" + os.path.sep + "kernel.log"
        if os.path.exists(ylog):
            print ylog
            runtimec = runTime(ylog)
            start_time = runtimec.find_test_start_time()
            end_time = runtimec.find_test_end_time(None)
            test_time = end_time - start_time
            preport.write("last_ylog/ylog%s runtime is %s\n" % (i, test_time))
    current_ylog = log_p + os.path.sep + "external_storage" + os.path.sep + "ylog" + os.path.sep + "kernel" + os.path.sep + "kernel.log"
    if os.path.exists(current_ylog):
        print current_ylog
        runtimec = runTime(current_ylog)
        start_time = runtimec.find_test_start_time()
        end_time = runtimec.find_test_end_time(None)
        test_time = end_time - start_time
        preport.write("current ylog runtime is %s\n\n" % test_time)

    sd_file_flag = False
    # logPath = getKernelLogPaths(folderparser,"runtime")
    logPath = getKernelLogPaths(folderparser, 'runtime')
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

    if not sd_kernel_file_exist_flag:
        preport.write("no sd last kernel log\n")

    if not sd_monkey_flag:
        preport.write("no sd monkey log\n")


    sd_last_kernel.sort()
    print sd_last_kernel
    print sd_monkey

    sd_path = log_p + os.path.sep + "external_storage"
    problem_list_txt = log_dir + os.path.sep + "problem_list.txt"
    lowpower_path = log_dir + os.path.sep + "low_power"

    # reboot_test = False
    if not os.path.exists(sd_path + os.path.sep + 'rebootlog.log'):  # reboot_test:
        preport.write("there is no \"rebootlog.log\"\n")
    if not os.path.exists(sd_path + os.path.sep + 'MSR.log'):  # reboot_test:
        preport.write("there is no \"MSR.log\"\n")
    if os.path.exists(sd_path + os.path.sep + 'rebootlog.log'):  # reboot_test:
        # 统计sdcard last log kernel log 的时间差
        filep = sd_path + os.path.sep + 'rebootlog.log'
        start_time, end_time = get_start_end_time(filep)

        preport.write("This result from \"rebootlog.log\" \n")
        print start_time
        print end_time
        runtime = (end_time - start_time)
        start_time = "start time: %s\n" % start_time
        end_time = "end time: %s\n" % end_time
        preport.write(start_time)
        preport.write(end_time)
        print runtime.seconds
        # formate_str = "How long test time1: [%s]\n"%runtime
        formate_str = "\nReboot Run Time: [%s]\n" % runtime
        preport.write(formate_str)
    if os.path.exists(sd_path + os.path.sep + 'MSR.log'):  # reboot_test:
        # 统计sdcard last log kernel log 的时间差
        filep = sd_path + os.path.sep + 'MSR.log'
        runtime = get_start_end_time_msr(filep)

        preport.write("This result from \"MSR.log\" \n")
        formate_str = "\nMSR Run Time: [%s]\n" % runtime
        preport.write(formate_str)
    elif sd_kernel_file_exist_flag:
        # 通过关键字分析problem_list文件 并找到结束时间
        result_flag = False
        rtf = runTime(sd_last_kernel[0])
        st = rtf.find_test_start_time()
        start_time = st
        file_name = "start time from file:%s\n" % sd_last_kernel[0]
        preport.write(file_name)
        st = "start time %s\n" % st
        preport.write(st)
        print st

        filep = problem_list_txt
        rtf = runTime(filep)
        keyword_list = ['WATCHDOG KILLING SYSTEM PROCESS', '>>> system_server <<<', 'FATAL EXCEPTION IN SYSTEM PROCESS']
        for keyword in keyword_list:
            et = rtf.find_test_end_time(keyword)
            if et:
                end_time_file = "end time from file:%s\n" % filep
                tmp_et = "end_time:%s\n" % et
                preport.write(end_time_file)
                preport.write(tmp_et)
                runtime = (et - start_time)
                preport.write("\nRun Time: %s" % runtime)
                result_flag = True
                break
        if result_flag == False and os.path.exists(lowpower_path):
            if sd_kernel_file_exist_flag == True:
                ret = sd_last_kernel_start_end_time(sd_last_kernel[0])
                if ret:
                    end_time = ret
                    end_time_file = "end time from file:%s\n" % sd_last_kernel[0]
                    preport.write(end_time_file)
                    st = "end time %s\n" % end_time
                    preport.write(st)
                    time_lenth = end_time - start_time
                    result_flag = True
                    st = "\nRun Time: %s\n" % time_lenth
                    preport.write(st)

        if result_flag == False:
            preport.write("did'not find key word in the proplem.list\n")
            rtf = runTime(sd_last_kernel[0])
            et = rtf.find_test_end_time(None)
            end_time = et
            file_name = "end time from file:%s\n" % sd_last_kernel[0]
            preport.write(file_name)
            et = "end time %s\n" % et
            preport.write(et)
            runtime = (end_time - start_time)
            preport.write("\nRun Time %s\n" % runtime)

        if sd_monkey_flag:
            rtime = 0
            fd = open(sd_monkey)
            line = fd.readline()
            while line:
                if Monkey_Start_Calendar_Time.search(line):
                    ttime = line.split(" ")[-3:-1]
                    print "ttt"
                    print ttime
                    print ttime[0]
                    print ttime[1]
                    d = [string.atoi(ttime[0][0:4]), string.atoi(ttime[0][5:7]), string.atoi(ttime[0][8:10]),
                         string.atoi(ttime[1][0:2]), string.atoi(ttime[1][3:5]), string.atoi(ttime[1][6:8]), ]
                    start_time = datetime.datetime(d[0], d[1], d[2], d[3], d[4], d[5])
                    print start_time
                    break
                line = fd.readline()
            while line:
                while line:
                    if calendar_time_regex.search(line):
                        ttime = line.split("calendar_time:")[-1].split(" ")
                        d = [string.atoi(ttime[0][0:4]), string.atoi(ttime[0][5:7]), string.atoi(ttime[0][8:10]),
                             string.atoi(ttime[1][0:2]), string.atoi(ttime[1][3:5]), string.atoi(ttime[1][6:8]), ]
                        first_time = datetime.datetime(d[0], d[1], d[2], d[3], d[4], d[5])
                        break
                    line = fd.readline()
                if (first_time - start_time).days > 4:
                    if rtime == 0:
                        rtime = end_time - start_time
                    else:
                        rtime += end_time - start_time
                    start_time = first_time
                    continue
                line = fd.readline()
                while line:
                    if calendar_time_regex.search(line):
                        ttime = line.split("calendar_time:")[-1].split(" ")
                        d = [string.atoi(ttime[0][0:4]), string.atoi(ttime[0][5:7]), string.atoi(ttime[0][8:10]),
                             string.atoi(ttime[1][0:2]), string.atoi(ttime[1][3:5]), string.atoi(ttime[1][6:8]), ]
                        end_time = datetime.datetime(d[0], d[1], d[2], d[3], d[4], d[5])
                        break
                    line = fd.readline()
                if (end_time - start_time).days > 4:
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
            print runtime
            formate_str = "\nMonkey Run Time: %s\n" % runtime
            preport.write(formate_str)


################################################################################################
###############parse_kernel,anr,java.native,wt###################

def run_kernel_panic(devbit):
    global vmlinux_f
    global sysdump_p
    print "***********kernel_panic begin************"

    m = Main(vmlinux_f, sysdump_p, ylog_p, devbit, serial_num)
    m.run()
    m.genReport()


def run_anr():
    print "***********anr begin************"
    parse_anr(ylog_p, serial_num)


def run_native_crash():
    print "***********native_crash begin************"
    parse_native_crash(ylog_p, serial_num)


def run_java_crash():
    print "***********java_crash begin************"
    parse_java_crash(ylog_p, serial_num)


def run_watchdog_crash():
    print "***********watchdog_crash begin************"
    parse_watchdog_crash(ylog_p, serial_num)


def run_lowpower():
    print "***********lowpower begin************"
    parse_lowpower(ylog_p, serial_num)


def run_kmemleak():
    print "***********kmemleak begin************"
    parse_kmemleak(ylog_p, serial_num)


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


def clearReportDir_java(folderParser):
    reportDir = getReportDir_java(folderParser)
    shutil.rmtree(reportDir)


def getSystemLogPaths(folderParser, PARSE_TYPE):
    logstr = folderParser.getFilesBy(PARSE_TYPE)
    if logstr:
        return logstr.split(',')
    return None


def getEventLogs(folderParser, PARSE_TYPE):
    logstr = folderParser.getFilesBy(PARSE_TYPE)
    if logstr:
        return logstr.split(',')
    return None


def getDropboxLogs(folderParser, PARSE_TYPE):
    logstr = folderParser.getFilesBy(PARSE_TYPE)
    if logstr:
        return logstr.split(',')
    return None


def getCrashEvent(efile, pfile, rf, fpp):
    java_crash_pattern = r'\sFATAL EXCEPTION:'
    java_crash_regex = re.compile(java_crash_pattern)
    java_crash_line_pattern = r'\sAndroidRuntime:\s'
    java_crash_line_regex = re.compile(java_crash_line_pattern)
    basedir = os.path.dirname(efile)
    print basedir
    ####get crash log
    sysfiles = None
    sysfiles = getSystemLogPaths(fpp, "javacrash")
    print sysfiles
    if sysfiles:
        sp = FileSort(sysfiles)
        sysfiles = sp.fsort()
        print sysfiles
    if os.path.exists(efile):
        fd = open(efile)
    else:
        # print "Open event file error,return"
        print "No event file for javacrash"
        return 0
    pfile.write("file: " + efile + "\n")
    # rf.write("------------------------------------------------------------\n")
    # rf.write("file: " + efile + "\n")
    line = fd.readline()
    while line:
        ######find am_crash from event file
        if line.find("am_crash") != -1 and line.find("java") != -1:
            pfile.write(line)
            # rf.write(line)
            line = line.strip().split(" ")
            crashtime = line[0] + " " + line[1].split(".")[0]
            print crashtime
            ct = line[0] + "-" + line[1]
            d = [datetime.datetime.now().year, string.atoi(ct[0:2]), string.atoi(ct[3:5]), string.atoi(ct[6:8]),
                 string.atoi(ct[9:11]), string.atoi(ct[12:14])]
            ct = datetime.datetime(d[0], d[1], d[2], d[3], d[4], d[5])
            if sysfiles:
                for ffs in sysfiles:
                    ff = False
                    fs = open(ffs)
                    ll = fs.readline()
                    while ll:
                        ######find according system info(timer and FATAL EXCEPTION)
                        if ll.find(crashtime) != -1 and java_crash_regex.search(ll):
                            # if java_crash_regex.search(ll):
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

        line = fd.readline()
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
                fd_out.write(line + '\n')
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


def getSystemCrashFileinfo(crash_file, pf, pl):
    java_crash_pattern = r'\sFATAL EXCEPTION:'
    java_crash_regex = re.compile(java_crash_pattern)
    if os.path.exists(crash_file):
        dfp = open(crash_file)
    else:
        # print "Cannot open system_server_crash@ file,return."
        print "No system_server_crash@ file."
        return 0
    pf.write("file: " + crash_file + "\n")
    pl.write("file: " + crash_file + "\n")
    line = dfp.readline()
    # lline = []
    t_flag = False
    while line:
        if java_crash_regex.search(line):
            t_flag = True
            # get java_crash timer for memory analyse
            # ll = line.split(" ")
            # java_timer_for_mm = ll[0] + " " + ll[1]
            # print "java_timer_for_mm:**********************************************"
            pl.write(line)
            pf.write(line)
            for i in range(10):
                # lline.append(line)
                # tfp_p.write(line)
                # line = dfp.readline()
                line = dfp.readline()
                pf.write(line)
        # break
        # break
        line = dfp.readline()
    # if there is no "FATAL EXCEPTION IN SYSTEM PROCESS:" info,then copy all system_server_crash@ content to tmp_report
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


def compare_slog_dropbox_java(report_p, list_p, tmpr_p, tmpl_p):
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
                listp = open(list_p, "a+")
                #	listp.write("-------------------------------------\n")
                listp.write(file_line)
                listp.write(line)
                listp.close()
                tmprp.seek(0)
                mm = tmprp.readline()
                while mm:
                    if mm.find(crash_time) != -1:
                        reportp = open(report_p, "a+")
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


def parse_java_crash(input_dir, devnum):
    # script_file = sys.argv[0]
    # global java_time_for_mm
    tmpfile = os.path.abspath('.') + os.path.sep + "logs" + os.path.sep + "javacrash_file_tmp.txt"
    tmplist = os.path.abspath('.') + os.path.sep + "logs" + os.path.sep + "javacrash_list_tmp.txt"
    eventlogs = None
    dropboxlogs = None
    systemLogPaths = None
    if input_dir:
        fp = FolderParser(input_dir, devnum)

        clearReportDir_java(input_dir)
        reportFile = getReportFile_java(input_dir)
        problemlist = getProblemList(input_dir)
        ## get crash log file
        systemLogPaths = getSystemLogPaths(fp, "javacrash")
        if systemLogPaths:
            sp = FileSort(systemLogPaths)
            systemLogPaths = sp.fsort()
        print systemLogPaths
        eventlogs = getEventLogs(fp, "javacrashevent")
        if eventlogs:
            sp = FileSort(eventlogs)
            eventlogs = sp.fsort()
        dropboxlogs = getDropboxLogs(fp, "javacrashdropbox")
        if dropboxlogs:
            sp = FileSort(dropboxlogs)
            Dropboxlogs = sp.fsort()
        if eventlogs:
            plist = open(problemlist, "w+")
            rfile = open(reportFile, "w+")
            for eventfile in eventlogs:
                getCrashEvent(eventfile, plist, rfile, fp)
                # systemLogPaths.sort()
            ##get system log content
            plist.close()
            rfile.close()
        elif systemLogPaths:
            for systemLog in systemLogPaths:
                parse(systemLog, reportFile)
        else:
            ## no system log to parse java crash
            print 'No system and event log file to parse.'
            # rfile.wtite("\nNo system and event log file to parse")
        if dropboxlogs:
            tmpfile_p = open(tmpfile, "w")
            tmplist_p = open(tmplist, "w")
            for dropboxlog in dropboxlogs:
                getSystemCrashFileinfo(dropboxlog, tmpfile_p, tmplist_p)

            tmpfile_p.close()
            tmplist_p.close()
            if os.path.exists(tmplist):
                compare_slog_dropbox_java(reportFile, problemlist, tmpfile, tmplist)
                # java_timer_for_mm = java_timer_for_mm.replace(" ","_")
                # os.system("python parse_mm.py " + "--log-dir " + input_dir + " --serial-num " + devnum + " --timer " + "last_time")
    else:
        ## no input file, just return
        usage()
        # sys.exit(1)
        return 0
    if os.path.exists(tmpfile):
        os.remove(tmpfile)
    if os.path.exists(tmplist):
        os.remove(tmplist)


################################################################################################
############parse_native_crash##############################
def compare_slog_dropbox_native(report_p, list_p, tmpr_p, tmpl_p):
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
                    listp = open(list_p, "a+")
                    #	    listp.write("-------------------------------------\n")
                    listp.write(file_line)
                    listp.write(line)
                    listp.close()
                    tmprp.seek(0)
                    mm = tmprp.readline()
                    while mm:
                        if mm.find(tmpline) != -1:
                            reportp = open(report_p, "a+")
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
    if len(corelist) > 0:
        return corelist
    else:
        return 0


def get_tombstonefile_info(tombstonef, np, ft):
    native_crash_regex = re.compile(r'pid: [0-9]+, tid: [0-9]+,\s*name:\s*.*\s*>>>\s*.*\s*<<<')
    D_LINE_new = re.compile("stack:")
    end_line = re.compile("(--- --- --- --- --- --- --- )")
    flag = False
    if os.path.exists(tombstonef):
        tsp = open(tombstonef)
    else:
        # print "Cannot open SYSTEM TOMBSTONE@, return"
        print "No SYSTEM TOMBSTONE@."
        return 0
    np.write("file: " + tombstonef + "\n")
    ft.write("file: " + tombstonef + "\n")
    line = tsp.readline()
    #########write to tmp_log and native_crash_file.txt
    while line:
        if native_crash_regex.search(line):
            # r_line = line
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
        # np.write(line)
    #########write more info to native_crash_file.txt
    while line:
        if end_line.search(line):
            # np.close()
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
            ffp = gzip.GzipFile(ts, "r")
            outfile = open(dstfile, "w")
            outfile.write(ffp.read())
            outfile.close()
            tombstonefile.append(dstfile)
        else:
            tombstonefile.append(ts)
    tombstonefile.sort()
    tombstonefile = list(set(tombstonefile))
    print tombstonefile
    return tombstonefile


def check_corefile(folderparser, native_p, corelist, parsetype):
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
            cc_new = cct.replace(" ", "-").replace("!", "-")
            try:
                os.rename(cc, cc_new)
            except:
                pass
            cc = cc_new
        # print "native core file " + str(cc)
        result = os.popen("python readelf.py -l " + cc)
        line = ""
        for p in result:
            line = p
        line = line.strip().split(' ')
        print line
        try:
            size = int(line[-5], 16) + int(line[-8], 16)
            size_r = os.path.getsize(cc)
            print size_r

            # if real_size/gdb_excepted_size >0.85,then copy corefile to postprocess_report folder
            if size_r / size > float(0.85):
                dstfile = native_p + os.path.sep + os.path.basename(cc)
                shutil.copyfile(cc, dstfile)
            else:
                print "corefile size is incorrect."
        except:
            print "cannot get size of corefile"
            dstfile = native_p + os.path.sep + os.path.basename(cc)
            shutil.copyfile(cc, dstfile)


def get_nativecrash_info(tombsf, pl, pr):
    tombstone_regex = re.compile(r'ylog.tombstone 000')
    native_crash_line_regex = re.compile(r'Fatal signal')
    native_crash_regex = re.compile(r'pid: [0-9]+, tid: [0-9]+,\s*name:\s*.*\s*>>>\s*.*\s*<<<')
    native_crash_module_get_regex = re.compile(r'\s*name: (.\w+)')
    D_LINE_new = re.compile("stack:")
    # D_LINE_new = re.compile("Tombstone written to")
    if os.path.exists(tombsf):
        fd = open(tombsf)
    else:
        # print "Open main file error,return."
        print "No tombstone file for nativecrash"
        return 0
    line = fd.readline()
    nativec = False
    while line:
        if tombstone_regex.search(line):
            pattern = r"(\[.*?\])"
            tmp_time = re.findall(pattern, line, re.M)[-1]
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
                    # time_list.append(tmp_time.replace(":","-"))
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
        return (core_list, tmp_time)
    except:
        return 0


def parse_native_crash(logdir, devnum):
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
        # sys.exit(0)
        return 0
    else:
        fp = FolderParser(logdir, devnum)
        reportpath = slogBasePath + os.path.sep + "post_process_report"
        if reportpath == '' or reportpath == None:
            print "get report path failed!"
            print "exit!"
            # sys.exit(0)
            return 0
        print reportpath
        nativepath = reportpath + os.path.sep + "native_crash"
        if os.path.exists(nativepath):
            shutil.rmtree(nativepath)
        if not os.path.exists(nativepath):
            os.makedirs(nativepath)
        # write pid...---ip lines to tmp_core_file, write pid and backtrace lines to native_crash_file and stored in report folder
        native_crash_file = nativepath + os.path.sep + "native_crash_report.txt"
        native_crash_list = nativepath + os.path.sep + "native_crash_list.txt"
        preport = open(native_crash_file, "w+")
        plist = open(native_crash_list, "w+")
        core_list = []
        trace_log = None
        trace_log = fp.getFilesBy("nativecrashtraces")
        trace_log = trace_log.split(",")
        sp = FileSort(trace_log)
        trace_log = sp.fsort()
        if trace_log:
            for tracefile in trace_log:
                crash_list = get_nativecrash_info(tracefile, plist, preport)
                if crash_list != 0:
                    core_list.append(crash_list[0])
                    ###there,,,ft_p will be written temporarily, just fit function of get_tombstonefile_info
                    ###if there is snapshot file, it will be written by snapshot content
                    # native_crash_line = get_tombstonefile_info(main_log,np_p,ft_p)
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
            check_corefile(fp, nativepath, core_list, "nativecrashcore")
        plist.close()

        dropboxlogs = getTombstoneFile(fp)
        tmpfile = os.path.abspath('.') + os.path.sep + "logs" + os.path.sep + "nativecrash_file_tmp.txt"
        tmplist = os.path.abspath('.') + os.path.sep + "logs" + os.path.sep + "nativecrash_list_tmp.txt"
        if len(dropboxlogs) > 0:

            tmpfile_p = open(tmpfile, "w")
            tmplist_p = open(tmplist, "w")
            for dropboxlog in dropboxlogs:
                get_tombstonefile_info(dropboxlog, tmpfile_p, tmplist_p)

            tmpfile_p.close()
            tmplist_p.close()

        if os.path.exists(tmplist):
            dropcore = compare_slog_dropbox_native(native_crash_file, native_crash_list, tmpfile, tmplist)
        if dropcore != 0:
            check_corefile(fp, nativepath, dropcore, "nativecrashcore")

        # native_timer_for_mm = native_timer_for_mm.replace(" ","_")
        # print native_timer_for_mm
        # os.system("python parse_mm.py " + "--log-dir " + logdir + " --serial-num " + devnum + " --timer " + "last_time")


        if os.path.exists(tmpfile):
            os.remove(tmpfile)
        if os.path.exists(tmplist):
            os.remove(tmplist)


##################################################################################################
############parse_watchdog_crash#######################

def get_snapshot_file_info(sfiles, watchdog_file, listfile):
    thread_id_regex = re.compile(r'\s*held by thread\s*(\d+)')
    thread_id_line_regex = re.compile(r'\s*tid=(\d+)')
    tfp = open(watchdog_file, 'a+')
    lfp = open(listfile, 'a+')
    tid_list = []
    for snap_f in sfiles:
        # print "ss" + snap_f
        try:
            dfp = open(snap_f)
        except:
            print "Cannot open snapshot file, exit."
            tfp.close()
            lfp.close()
            return 0
            # tmp_p = dfp.tell()
        line = dfp.readline()
        tid = None
        main_t = False
        while line:
            if line.find(" tid=1 ") != -1 and line.find("Blocked") != -1:
                pp = tmp_p
                # line_tid = line
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
                # break
        dfp.close()
    tfp.close()
    lfp.close()


def compare_slog_dropbox_wt(report_p, list_p, tmpr_p, tmpl_p):
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
                tmprp.seek(0)
                mm = tmprp.readline()
                while mm:
                    if mm.find(tmpline) != -1:
                        reportp = open(report_p, "a+")
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
                listp = open(list_p, "a+")
                listp.write(file_line)
                listp.write(line)
                listp.close()
                tmprp.seek(0)
                mm = tmprp.readline()
                while mm:
                    if mm.find(tmpline) != -1:
                        reportp = open(report_p, "a+")
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


def get_watchdog_file_info(watchdog, np, ft):
    watchdog_regex = re.compile(r'Blocked in handler on')
    watchdog_regex2 = re.compile(r'Blocked in')
    watchdog_thread_regex = re.compile(r'\((.*?)\)', re.I | re.X)
    enter = False
    watchdog_traces = []
    if os.path.exists(watchdog):
        dfp = open(watchdog)
    else:
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
            watchdog_threads = watchdog_thread_regex.findall(line)
            for watchdog_thread in watchdog_threads:
                watchdog_traces.append('"' + watchdog_thread + '"' + ' ' + 'prio=')
            print watchdog_threads
            for watchdog_trace in watchdog_traces:
                findf = False
                next_cmd = False
                dfp.seek(0)
                line = dfp.readline()
                while line:
                    if line.find("Cmd line: system_server") != -1:
                        line = dfp.readline()
                        while line:
                            if line.find(watchdog_trace) != -1:
                                np.write(line)
                                findf = True
                                line = dfp.readline()
                                while line:
                                    if re.match(r'^(\")', line):
                                        break
                                    else:
                                        np.write(line)
                                        line = dfp.readline()
                                break
                            if line.find("Cmd line: ") != -1:
                                next_cmd = True
                                break
                            line = dfp.readline()
                        if (not findf) and next_cmd:
                            continue
                        break
                    line = dfp.readline()
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
            dfp = gzip.GzipFile(wf, "r")
            outfile = open(dstfile, "w")
            outfile.write(dfp.read())
            outfile.close()
            watchdog_file.append(dstfile)
        else:
            watchdog_file.append(wf)
    watchdog_file = list(set(watchdog_file))
    sp = FileSort(watchdog_file)
    watchdog_file = sp.fsort()
    return watchdog_file


def get_watchdogcrash_info(sysf, pr, pl):
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
    return reportDir


def getReportFile_wt(folderParser):
    reportDir = getReportDir_wt(folderParser)
    reportFile = os.path.join(reportDir, 'watchdog_report.txt')
    return reportFile


def clearReportDir_wt(folderParser):
    reportDir = getReportDir_wt(folderParser)
    shutil.rmtree(reportDir)


def parse_watchdog_crash(slog_path, devnum):
    watchdog_killing_system_process_regex = re.compile(r'WATCHDOG KILLING SYSTEM PROCESS')
    wat_flag = None
    sys_flag = None
    if slog_path:
        fp = FolderParser(slog_path, devnum)

        clearReportDir_wt(slog_path)
        reportFile = getReportFile_wt(slog_path)
        reportDir = getReportDir_wt(slog_path)
        tmp_watchdog_file = os.path.abspath('.') + os.path.sep + "logs" + os.path.sep + "tmp_watchdog_file.txt"
        watchdog_list = reportDir + os.path.sep + "watchdog_list.txt"
        preport = open(reportFile, "w+")
        plist = open(watchdog_list, "w+")
        ####parse info from dropbox/file
        systemfiles = None
        systemfiles = fp.getFilesBy("watchdogcrash")
        systemfiles = systemfiles.split(",")
        sp = FileSort(systemfiles)
        systemfiles = sp.fsort()
        if systemfiles:
            # tmp_result = get_system_watchdog(systemfiles,tmp_watchdog_file)
            for systemfile in systemfiles:
                sys_flag = get_watchdogcrash_info(systemfile, preport, plist)
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
                        time_list.append(tmp_time.replace(":", "-"))
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

        tmpfile_p = open(tmpfile, "w")
        tmplist_p = open(tmplist, "w")
        for dropboxlog in dropboxlogs:
            wat_flag = get_watchdog_file_info(dropboxlog, tmpfile_p, tmplist_p)

        tmpfile_p.close()
        tmplist_p.close()
    if os.path.exists(tmplist):
        dropcore = compare_slog_dropbox_wt(reportFile, watchdog_list, tmpfile, tmplist)

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
        get_snapshot_file_info(snapfiles, reportFile, watchdog_list)


#####################################################################################################
################parse_lowpower###############


def get_files(filep, TYPE):
    files = filep.getFilesBy(TYPE)
    print files
    if files:
        return files.split(',')
    return None


def fileAnalyst(file_param, preport, plist):
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
        if low_power_regex.search(line):
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
            preport.write("\nfile: %s\n" % file_param)
            preport.write(line)
            plist.write("\nfile: %s\n" % file_param)
            plist.write(line)
            for i in range(0, 4):
                line = fd.readline()
                preport.write(line)
                if state_regex.search(line):
                    state = state_regex.search(line).group(1)
                    state = int(state)
                    if state == 3 and current < 0:
                        preport.write("*****Phone is charging but the power concume is too soon********\n")
                    break
            try:
                current = int(current)
                vbat = int(vbat)

                # print "dong:current:%d vbat:%d state %d\n"%(current ,vbat ,state)
                if current < 0 and vbat < 3200 and vbat > 0:
                    plist.write("Result : low power !!!!!!!!!!!!!!!!!!!!\n")
                    preport.write("Result : low power !!!!!!!!!!!!!!!!!!!!\n")
            except ValueError:
                pass
        line = fd.readline()

    return ret


def find_android_key_word(filep, preport, plist):
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


def find_tempreture_key_word(filep, preport, plist):
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
            # if tempreture_regex.search(line):
            ret = True
            # print line
            plist.write("**********Thermal!!!************\n")
            plist.write("file: %s\n" % filep)
            plist.write(line)
            preport.write("**********Thermal!!!************\n")
            preport.write("file: %s\n" % filep)
            preport.write(line)
            break
        line = fd.readline()
    print "tempretrue ret[%d]\n" % ret
    return ret


def find_tempreture(filep, preport, plist, last_temp):
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
            # print last_temp[10]
        if Thermal_kernel_regex.search(line):
            tmp_count = count % (len(last_temp) - 1)
            last_temp[tmp_count] = line
            count += 1
            # if tempreture_regex.search(line):
            tempre = Thermal_kernel_regex.search(line).group(1)
            if int(tempre) > 105000:
                ret = True
                plist.write("**********Thermal!!!************\n")
                plist.write("file: %s\n" % filep)
                plist.write(line)
                preport.write("**********Thermal!!!************\n")
                preport.write("file: %s\n" % filep)
                preport.write(line)
                line = fd.readline()
                while line:
                    # if Thermal_critical_regex.search(line):
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
    print "tempretrue ret[%d]\n" % ret
    return ret


def find_freezescreen(filep, preport, plist):
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
            plist.write("file: %s\n" % filep)
            plist.write(line)
            plist.write("There may be freezescreen!!!")
            preport.write("file: %s\n" % filep)
            preport.write(line)
            preport.write("There may be freezescreen!!!")
        line = fd.readline()
    return ret


def parse_lowpower(input_dir, devnum):
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
        fp = FolderParser(input_dir, devnum)
        logPath = None
        logPath = get_files(fp, "lowpower")
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
        preport = open(lowpower_file, "w+")
        plist = open(lowpower_list, "w+")
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
                ret = fileAnalyst(sd_kernel_log_file, preport, plist)
                if not ret:  # file_analysis
                    base_dir = os.path.dirname(os.path.dirname(sd_kernel_log_file))
                    for sd_last_android_main_file in last_android_main_file:
                        if os.path.dirname(os.path.dirname(sd_last_android_main_file)) == base_dir:
                            ret = find_tempreture_key_word(sd_last_android_main_file, preport, plist)
                            if not ret:
                                # preport.write("*****No result 3")
                                initv = ""
                                last_tempre = [initv for i in range(11)]
                                preport.write("file: " + sd_kernel_log_file + "\n")
                                plist.write("file: " + sd_kernel_log_file + "\n")
                                plist.write(
                                    "Last temprature values and last cap value will be written to the lowpower_report.txt\n")

                                ret = find_tempreture(sd_kernel_log_file, preport, plist, last_tempre)
                                # 将找到的最后几行的温度打印出来
                                for i in range(len(last_tempre)):
                                    if i == (len(last_tempre) - 1):
                                        preport.write("cap :" + last_tempre[i] + "\n")
                                    else:
                                        preport.write(last_tempre[i])
                                        # print (last_tempre[i])
                                if not ret:
                                    freezescreen = True
        else:  # sd_last_kernel
            print("********* There is not main log1\n")
            preport.write("\nNo kernel log file in the (externel_storage/last_log/kernel/)\n")
            if android_main_file_exist_flag == True:
                for sd_last_android_main_file in last_android_main_file:
                    find_android_key_word(sd_last_android_main_file, preport, plist)
                else:
                    preport.write("there is not file:")
                    preport.write(sd_last_android_main_file)
                    freezescreen = True
        if freezescreen:
            kernel_log = input_dir + os.path.sep + "internal_storage" + os.path.sep + "last_ylog" + os.path.sep + "ylog1" + os.path.sep + "kernel" + os.path.sep + "kernel.log"
            print kernel_log
            find_freezescreen(kernel_log, preport, plist)

        # except:
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

    for i in range(0, len(List)):
        if data == List[i]:
            ret = True

    return ret


def read_kmemleak_to_list(destFile):
    kmemleak_func_addr_regex = re.compile(r'\[<\w+>\]')
    fd = open(destFile)
    line = fd.readline()
    func_addr_list = []

    while line:
        # print line
        if line.find("kmemleak_alloc") != -1 or line.find("kmem_cache_alloc_trace") != -1:
            line = fd.readline()
            func_addr = kmemleak_func_addr_regex.search(line).group()[2:-2]
            if not check_list(func_addr, func_addr_list):
                func_addr_list.append(func_addr)
        line = fd.readline()
    return func_addr_list


def parse_kmemleak(input_dir, devnum):
    global vmlinux_f
    if platform.system() == "Linux":
        location = input_dir.rfind("/")
    else:
        location = input_dir.rfind("\\")
    slogBasePath = input_dir[0:location]

    if input_dir == None:
        print "log directory is needed!"
        return 0
    else:
        fp = FolderParser(input_dir, devnum)
        logPath = get_files(fp, "kmemleak")
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
    print "kmemleak: " + vmlinux_f

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

    for i in range(0, len(memleakList)):
        print memleakList[i]
        os.system(memleakCmd + memleakCmd_vmlinux + memleakCmd_para + " " + memleakList[
            i] + memleakCmd_to + memleakCmd_dest_file)


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


def parse_anr(input_dir, devnum):
    anr_ylog_regex = re.compile(r"ylog.anr 000")
    anr_get_pid_regex = re.compile(r"----- pid\s*(\d+)\s*at\s*(.*)\s*-----")
    anr_get_module_regex = re.compile(r"Cmd line:\s*(.*)")
    output_file = getReportDir_anr(input_dir)
    if os.path.exists(output_file):
        shutil.rmtree(output_file)
    try:
        os.makedirs(output_file)
    except:
        print "%s exixts." % (output_file)
        print output_file
    pidlist = output_file + os.path.sep + "anrpidlist.txt"
    pidpath = output_file + os.path.sep + "ANR"
    if os.path.exists(pidpath):
        shutil.rmtree(pidpath)
    os.makedirs(pidpath)
    pidl = open(pidlist, "w+")
    traces_file = None
    if input_dir:
        fp = FolderParser(input_dir, devnum)
        traces_file = fp.getFilesBy('anrtraces')
        traces_file = traces_file.split(",")
        if traces_file[0] == '':
            pidl.close()
            return 0
        # traces_tmp = {}
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

                    # traces_tmp[dirn] = tfiles
                    # for keys in traces_tmp:
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
            # tracesf.reverse()
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
                                module = anr_get_module_regex.search(line).group(1).replace("/", ".")
                        break
                    line = tfp.readline()
                pidl.write("-----------------------------------------------------------------\n")
                pidl.write("file: " + tf)
                pidl.write("\npid %s, %s, happend anr at %s \n" % (pid, module, anr_time))
                tfp.seek(0)
                pidfile = pidpath + os.path.sep + "pid_" + pid + "_" + module
                pidr = open(pidfile, "w+")
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

def sysdump_check(sysdump_info):
    global sysdump_p
    flag = False
    for file in os.listdir(sysdump_p):
        if file.find("sysdump.core.00") != -1:
            flag = True
    if flag == False:
        print "No sysdump file"
        sys.exit(1)

    num = len(os.listdir(sysdump_p))
    num = int(num)
    print "num    " + str(num)
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


def download_symbols(logdir, dev_mode, symbols_dir):
    import urllib
    import urllib2
    import tarfile
    dev_info = get_device_mode()
    build_type = get_build_type()

    url = dev_mode + "symbols.vmlinux." + dev_info + "_" + build_type + "_" + "native.tgz"

    print url
    time.sleep(10)
    # dst_file = symbols_dir + os.path.sep + symbolname
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
        # print "device file " +str(dev_file)
        fd = open(os.path.join(ylog_p, dev_file))
        line = fd.readline()
        while line:
            if product_name_regex.search(line):
                print line
                pattern = r"(\[.*?\])"
                line = re.findall(pattern, line, re.M)
                if (len(line) > 1):
                    line = line[1]
                    dev_info = line.replace('[', '').replace(']', '')
                break
            line = fd.readline()
    if dev_info:
        print "device info " + str(dev_info)
        return dev_info
    else:
        return ""
        # "sp9838aea_oversea"


def get_build_host():
    build_host_regex = re.compile(r'ro.build.host')
    dev_file = None
    build_host = None
    for ff in os.listdir(ylog_p):
        if ff.find("sysprop.txt") != -1:
            dev_file = ff
            break
    if dev_file:
        fd = open(os.path.join(ylog_p, dev_file))
        line = fd.readline()
        while line:
            if build_host_regex.search(line):
                print line
                pattern = r"(\[.*?\])"
                line = re.findall(pattern, line, re.M)
                if (len(line) > 1):
                    line = line[1]
                    build_host = line.replace('[', '').replace(']', '')
                break
            line = fd.readline()
    if build_host:
        # print build_host
        return build_host
    # build_host: http://10.0.1.56:8080/jenkins/job/sprdroid5.1_trunk_SharkLT8/68/
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
        fd = open(os.path.join(ylog_p, dev_file))
        line = fd.readline()
        while line:
            if build_type_regex.search(line):
                print line
                pattern = r"(\[.*?\])"
                line = re.findall(pattern, line, re.M)
                if (len(line) > 1):
                    line = line[1]
                    build_type = line.replace('[', '').replace(']', '')
                break
            line = fd.readline()
    if build_type:
        # print build_host
        return build_type
    # build_host: http://10.0.1.56:8080/jenkins/job/sprdroid5.1_trunk_SharkLT8/68/
    else:
        return ""


def parse_kernel_warning(slogp, folderparser):
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
    print "savepath " + str(savepath)
    warningf = savepath + "warning.txt"
    wf = open(warningf, "w+")
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
                wf.write("file: %s\n" % kf)
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


def parse_kernel_BUG(slogp, folderparser):
    kernel_BUG_regex = re.compile(r'\s*BUG:\s*')
    if platform.system() == "Linux":
        location = slogp.rfind("/")
    else:
        location = slogp.rfind("\\")
    slogbp = slogp[0:location]
    savepath = slogbp + os.path.sep + "post_process_report" + os.path.sep + "kernel_panic" + os.path.sep
    if not os.path.isdir(savepath):
        os.makedirs(savepath)
    print "savepath " + str(savepath)
    bugf = savepath + "bug.txt"
    bf = open(bugf, "w+")
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
                # if line.find("BUG:") != -1:
                bf.write("file: %s\n" % kf)
                num += 1
                bf.write(line)
                line = kp.readline()
                i = 0
                while line:
                    if i >= 30:
                        next_e = True
                        break
                    if kernel_BUG_regex.search(line):
                        # if line.find("BUG:") != -1:
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


def parse_kernel_Error(slogp, folderparser):
    kernel_Error_regex = re.compile(r'\s*Error\s*')
    if platform.system() == "Linux":
        location = slogp.rfind("/")
    else:
        location = slogp.rfind("\\")
    slogbp = slogp[0:location]
    savepath = slogbp + os.path.sep + "post_process_report" + os.path.sep + "kernel_panic" + os.path.sep
    if not os.path.isdir(savepath):
        os.makedirs(savepath)
    print "savepath " + str(savepath)
    errorf = savepath + "error.txt"
    erf = open(errorf, "w+")
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
                erf.write("file: %s\n" % kf)
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


def parse_kernel_emmc(slogp, folderparser):
    kernel_emmc_regex = re.compile(r'REGISTER DUMP')
    if platform.system() == "Linux":
        location = slogp.rfind("/")
    else:
        location = slogp.rfind("\\")
    slogbp = slogp[0:location]
    savepath = slogbp + os.path.sep + "post_process_report" + os.path.sep + "kernel_panic" + os.path.sep
    if not os.path.isdir(savepath):
        os.makedirs(savepath)
    print "savepath " + str(savepath)
    emmcf = savepath + "emmc.txt"
    ef = open(emmcf, "w+")
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
                ef.write("file: %s\n" % kf)
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


def parse_kernel_dmc_mpu(slogp, folderparser, kernel_log=None):
    kernel_dmcmpu_regex = re.compile(r'Warning! DMC MPU detected violated transaction')
    if platform.system() == "Linux":
        location = slogp.rfind("/")
    else:
        location = slogp.rfind("\\")
    slogbp = slogp[0:location]
    savepath = slogbp + os.path.sep + "post_process_report" + os.path.sep + "kernel_panic" + os.path.sep
    if not os.path.isdir(savepath):
        os.makedirs(savepath)
    print "savepath " + str(savepath)
    dmcmpuf = savepath + "dmcmpu.txt"
    kernelfs = []
    if kernel_log:
        kernelfs.append(savepath + "kernel_log.log")
        print "kernel log.log"
        mf = open(dmcmpuf, "a")
    else:
        kernelfs = folderparser.getFilesBy("memory")
        kernelfs = kernelfs.split(",")
        sp = FileSort(kernelfs)
        kernelfs = sp.fsort()
        mf = open(dmcmpuf, "w+")
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
                mf.write("file: %s\n" % kf)
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


def parse_assert(slogp):
    if platform.system() == "Linux":
        location = slogp.rfind("/")
    else:
        location = slogp.rfind("\\")
    slogbp = slogp[0:location]
    savepath = slogbp + os.path.sep + "post_process_report" + os.path.sep + "kernel_panic" + os.path.sep
    if not os.path.isdir(savepath):
        os.makedirs(savepath)
    print "savepath " + str(savepath)
    modem = savepath + "modem.txt"
    wcn = savepath + "wcn.txt"
    apr = slogp + os.path.sep + "apr.xml"
    if not os.path.exists(apr):
        print "no apr file."
        return 0
    p1 = open(modem, "w+")
    p2 = open(wcn, "w+")
    p1.write("file: %s\n" % apr)
    p2.write("file: %s\n" % apr)

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
                    p2.write("%s happend Wcn assert: %s\n" % (times, brief))
                if en.find("type").text == "modem assert":
                    print "ok"
                    times = en.find("timestamp").text
                    brief = en.find("brief").text
                    p1.write("%s happend Modem assert: %s\n" % (times, brief))

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
    def __init__(self, ylog_p):
        self.ylog_p = ylog_p

    def analyzef(self):
        current_dir = os.path.abspath('.')
        print current_dir
        for parent, dirnames, filenames in os.walk(self.ylog_p):
            for filename in filenames:
                if filename.find("analyzer.py") != -1:
                    print parent
                    os.chdir(parent)
                    os.system("python analyzer.py")
        os.chdir(current_dir)


############################################################################################
def download_vmlinux():
    global vmlinux_f
    v_path = None
    v_path = get_build_host()
    if v_path.endswith("/"):
        v_path = v_path[:-1]
    tlocation = v_path.find("jenkins/job/")
    vmpath = v_path[tlocation + 12:].replace("/", os.path.sep)
    print vmpath
    product = get_device_mode()

    vmlinux_p = os.path.dirname(
        os.path.abspath('.')) + os.path.sep + "symbols" + os.path.sep + vmpath + os.path.sep + product
    vmlinux_f = vmlinux_p + os.path.sep + "symbols" + os.path.sep + "vmlinux"
    # v_path = "http://10.0.1.56:8080/jenkins/job/sprdroid5.1_trunk_SharkLT8/55/artifact/SYMBOLS/"
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
            sys.stderr.write('the dir is exists %s\n' % vmlinux_p)
        if v_path:
            print "start to down load symbols..."
            download_symbols(ylog_p, v_path, vmlinux_p)
            return vmlinux_f
            # pass
        else:
            print "Cannot get symbols version path"
            sys.exit(1)


if __name__ == '__main__':
    global sysdump_p

    if len(sys.argv) > 1:
        ylog_base_p = sys.argv[1]
        date = ylog_base_p.split('_')[-1][0:8]
        serial_num = "000"
    else:
        print "please input params: SN_date"
        print "such as 'python slog_postprocess.py 0123456789ABCDEF_20150829135231' "
        sys.exit(1)
    ylog_base_p = os.path.abspath(ylog_base_p)
    print "111"
    print ylog_base_p
    post_process_report = ylog_base_p + os.path.sep + "post_process_report"
    if os.path.exists(post_process_report):
        shutil.rmtree(post_process_report)
    for p, d, f in os.walk(ylog_base_p):
        for dir_name in d:
            if dir_name.find("log_") != -1:
                print dir_name
                sysdump_p1 = os.path.join(p, dir_name) + os.path.sep + "sysdump"
                sysdump_p2 = os.path.join(p, dir_name) + os.path.sep + "external_storage" + os.path.sep + "sysdump"
                sysdump_p3 = os.path.join(p, dir_name) + os.path.sep + "external_storage" + os.path.sep + "SYSDUMP"
                ylog_p = os.path.join(p, dir_name)
    if os.path.exists(sysdump_p2):

        dd = len(os.listdir(sysdump_p2))
        if dd != 0:
            sysdump_p = os.path.join(sysdump_p2, str("1"))
    elif os.path.exists(sysdump_p3):

        dd = len(os.listdir(sysdump_p3))
        if dd != 0:
            sysdump_p = os.path.join(sysdump_p3, str("1"))
    else:

        sysdump_p = sysdump_p1

    if ylog_p:
        print "ylog_base_p: " + str(ylog_p)
    else:
        print "No ylog for %s: " % ylog_p
        sys.exit(1)

    asy = AnalyzeYlog(ylog_p)
    asy.analyzef()
    title = None
    v_path = None
    fw_crash = None

    fp = FolderParser(ylog_p, serial_num)
    parse_kernel_warning(ylog_p, fp)
    parse_kernel_BUG(ylog_p, fp)
    parse_kernel_Error(ylog_p, fp)
    parse_kernel_emmc(ylog_p, fp)
    parse_kernel_dmc_mpu(ylog_p, fp)
    parse_assert(ylog_p)
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
            if k < 3:
                title += "\nsysdump file num is not correct!!!!!!!!!!!!!!!!"
                print title
                dumpf = False
            if sysdump_ci[k] == 0L:
                title += "\nsysdump file size is not correct!!!!!!!!!!!!!!!!!!!!"
                print title
                dumpf = False
        if dumpf:
            vmlinux_f = download_vmlinux()
            dev_bit = get_device_mode()

            run_kernel_panic(dev_bit)
            run_java_crash()
            run_native_crash()
            run_watchdog_crash()
            run_anr()
            run_lowpower()
            run_kmemleak()
            parse_kernel_dmc_mpu(ylog_p, "default", "kernelpanic")
            print title
        else:
            run_java_crash()
            run_native_crash()
            run_watchdog_crash()
            run_anr()
            run_lowpower()
            run_kmemleak()
            parse_kernel_dmc_mpu(ylog_p, "default", "kernelpanic")
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

    generate_list(ylog_base_p)
    folderp = FolderParser(ylog_p, serial_num)
    run_time(ylog_p, folderp)
    # try:
    #     run_time(ylog_p, folderp)
    # except:
    #     print "Failed to get run time."
