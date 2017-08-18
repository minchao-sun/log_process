#!/usr/bin/env python
# coding:utf-8

import sys
import os
import shutil
import platform
import xml.etree.ElementTree as ET
import re

DEBUG = True


def isLinux():
    return platform.system() == "Linux"


class FileItem(object):
    '''
    used for file complition check
    '''

    def __init__(self, stype="file", ismust="0", checkitem="", condition="", path="", checktype="default"):
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

    def getCheckitem(self):
        return self.checkitem

    def getPath(self):
        return self.path

    def toStr(self):
        print str(self.stype), str(self.ismust), str(self.checkitem), str(self.condition), str(self.path)


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
            filelist_sort.append(ff)
        for ff in self.filelist_inter:
            filelist_sort.append(ff)
        for ff in self.filelist_last:
            filelist_sort.append(ff)
        filelist_sort.reverse()
        return filelist_sort


class FolderParser(object):
    def __init__(self, logfolder, devnum):
        """Constructor"""
        # static defined variable
        self.dateinternal = "DATE_INTERNAL"
        self.dateinternal_lastlog = "DATEINTERNAL_LASTLOG"
        self.dateexternal = "DATE_EXTERNAL"
        self.dateexternal_lastlog = "DATEEXTERNAL_LASTLOG"
        # store the fade and real path map
        self.mapfadereal = {}
        self.initdata()
        self.logfolder = logfolder  # ylog_p
        self.fullfilepaths = []
        self.fullfolderpaths = []
        self.cp = ConfigParser("configs/config.xml")
        self.workpath()

    def initdata(self):
        self.mapfadereal[self.dateinternal] = ""
        self.mapfadereal[self.dateinternal_lastlog] = []
        self.mapfadereal[self.dateexternal] = ""
        self.mapfadereal[self.dateexternal_lastlog] = []

    def workpath(self):
        for p, d, f in os.walk(self.logfolder):
            for dir in d:
                if dir.find("ylog") != -1 and p.endswith("last_ylog") and p.find(
                        "external_storage") != -1:
                    self.mapfadereal[self.dateexternal_lastlog].append(dir)
                if dir.find("ylog") != -1 and dir.find("last_ylog") < 0 and p.endswith("external_storage"):
                    self.mapfadereal[self.dateexternal] = dir
                if dir.find("ylog") != -1 and dir.find("last") < 0 and p.endswith("internal_storage"):
                    self.mapfadereal[self.dateinternal] = dir
                if dir.find("last_ylog") != -1 and p.endswith("internal_storage"):
                    self.mapfadereal[self.dateinternal_lastlog] = dir
                self.fullfolderpaths.append(os.path.join(p, dir))
            for filename in f:
                self.fullfilepaths.append(os.path.join(p, filename))

    # return the string list of files with "," split
    def getFilesBy(self, typeName):
        files = self.cp.getProblemFiles(typeName)
        tmprefiles = []
        for i in self.fullfilepaths:
            # all the files in log path
            for f in files:
                if platform.system() == "Linux":
                    pp = f.getPath().replace("\\", "/")
                else:
                    pp = f.getPath().replace("/", "\\")
                pp_list = self.getRealPath(pp)  # all the file paths
                for jn in range(len(pp_list)):
                    if i.find(pp_list[jn]) >= 0:
                        chk = f.getCheckitem()
                        if chk == "" or chk is None:
                            tmprefiles.append(i)
                        else:
                            for ii in chk.split(","):
                                if os.path.basename(i).find(ii) >= 0:
                                    tmprefiles.append(i)
                                    break
        tmprefiles = list(set(tmprefiles))
        return ",".join(tmprefiles)

    # return null if file path is not exist
    def getRealPath(self, fadepath):
        result = fadepath
        if result == "" or result is None:
            return ""
        results = []
        for (k, v) in self.mapfadereal.items():
            if result.find(k) != -1:
                if v == "" or v == []:
                    results.append(result.replace(k, "nofolderfound"))
                else:
                    if isinstance(v, list):
                        for i in range(len(v)):
                            vv = v[i]
                            if isinstance(vv, tuple):
                                results.append(result.replace(k, vv[1]).replace("DATEEXTERNAL_LASTLOG", vv[0]))
                            else:
                                results.append(result.replace(k, vv))
                    else:
                        results.append(result.replace(k, v))
            else:
                results.append(result)
        results = list(set(results))
        return results


class ConfigParser(object):
    def __init__(self, configfile):
        self.__root = ET.parse(configfile).getroot()
        self.__problems = None
        temp = self.__root.find("problemneededfile")
        if temp is not None:
            self.__problems = temp.findall("problem")

    def getProblemFiles(self, problemtype):
        files = []
        ffs = None
        for p in self.__problems:
            if p.get("type") == problemtype:
                # here get all file list
                ffs = p.findall("file")
                break
        if ffs is not None:
            for x in ffs:
                ff = FileItem(x.get("type"), "", x.get("checkitem"), "", x.text)
                files.append(ff)
        return files


class AnalyzeYlog(object):
    def __init__(self, ylog_p):
        self.ylog_p = ylog_p

    def analyzef(self):
        current_dir = os.path.abspath('.')
        for parent, dirnames, filenames in os.walk(self.ylog_p):
            for filename in filenames:
                if filename.find("analyzer.py") != -1:
                    os.chdir(parent)
                    os.system("python analyzer.py")
        os.chdir(current_dir)


class KernelParser(object):
    """
    generate kernel_panic
    """

    def __init__(self, log_path, folderparser):
        self.__log_path = log_path
        base_path = self.__log_path[0:log_path.rfind(os.path.sep)]
        self.__fp = folderparser
        self.__save_path = base_path + os.path.sep + "post_process_report" + os.path.sep + "kernel_panic" + os.path.sep
        if os.path.exists(self.__save_path):
            shutil.rmtree(self.__save_path)
        if not os.path.isdir(self.__save_path):
            os.makedirs(self.__save_path)  # make dir named kernel_panic

    def parse_kernel(self):
        # generate kernel warnings, bugs, errors
        kernel_warning_regex = re.compile(r'WARNING:')  # find warnings
        kernel_BUG_regex = re.compile(r'\s*BUG:\s*')
        kernel_Error_regex = re.compile(r'\s*Error\s*')

        erf = open(self.__save_path + "error.txt", "w")
        bf = open(self.__save_path + "bug.txt", "w")
        wf = open(self.__save_path + "warning.txt", "w")
        kernelfs = self.__fp.getFilesBy("memory")
        kernelfs = kernelfs.split(",")
        sp = FileSort(kernelfs)
        kernelfs = sp.fsort()
        num = [0, 0, 0]
        for kf in kernelfs:
            try:
                kp = open(kf)
            except:
                print kf
                print "Open kernel error."
                continue
            line = kp.readline()  # fist line
            while line:
                # read all lines
                if kernel_warning_regex.search(line):
                    # if find warnings in this line, write it
                    wf.write("file: %s\n" % kf)
                    i = 0
                    num[0] += 1
                    # write warning line and next 29 lines
                    while i < 30:
                        wf.write(line)
                        line = kp.readline()
                        if kernel_BUG_regex.search(line) or kernel_warning_regex.search(line) \
                                or kernel_Error_regex.search(line):
                            break
                        i += 1
                    wf.write("\n")
                elif kernel_BUG_regex.search(line):
                    # if find bugs in this line
                    bf.write("file: %s\n" % kf)
                    i = 0
                    num[1] += 1
                    while i < 30:
                        bf.write(line)
                        line = kp.readline()
                        if kernel_BUG_regex.search(line) or kernel_warning_regex.search(line) \
                                or kernel_Error_regex.search(line):
                            break
                        i += 1
                    bf.write('\n')
                elif kernel_Error_regex.search(line):
                    # if find error in this line
                    erf.write("file: %s\n" % kf)  # write the file path
                    i = 0
                    num[2] += 1
                    while i < 30:
                        erf.write(line)
                        line = kp.readline()
                        if kernel_BUG_regex.search(line) or kernel_warning_regex.search(line) \
                                or kernel_Error_regex.search(line):
                            break
                        i += 1
                else:
                    # not find any keyword
                    # keep on reading lines
                    line = kp.readline()
            kp.close()
        print "[warnings, bugs, errors] =", num
        wf.close()
        bf.close()
        erf.close()

    def parse_kernel_emmc(self):
        kernel_emmc_regex = re.compile(r'REGISTER DUMP')
        emmcf = self.__save_path + "emmc.txt"
        ef = open(emmcf, "w+")
        kernelfs = self.__fp.getFilesBy("memory")
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

    def parse_kernel_dmc_mpu(self, kernel_log=None):
        kernel_dmcmpu_regex = re.compile(r'Warning! DMC MPU detected violated transaction')
        dmcmpuf = self.__save_path + "dmcmpu.txt"
        kernelfs = []
        if kernel_log:
            kernelfs.append(self.__save_path + "kernel_log.log")
            print "kernel log.log"
            mf = open(dmcmpuf, "a")
        else:
            kernelfs = self.__fp.getFilesBy("memory")
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

    def parse_assert(self):
        modem = self.__save_path + "modem.txt"
        wcn = self.__save_path + "wcn.txt"
        apr = self.__log_path + os.path.sep + "apr.xml"
        if not os.path.exists(apr):
            print "no apr file."
            return 0
        p1 = open(modem, "w+")
        p2 = open(wcn, "w+")
        p1.write("file: %s\n" % apr)
        p2.write("file: %s\n" % apr)

        root = ET.parse(apr).getroot()
        for apr in root.findall("apr"):
            try:
                exc = apr.getchildren()[-1]
                # print exc
                for en in exc.findall("entry"):
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
        p1.close()
        p2.close()


def find_logdir(base_path):
    ylog = None
    for p, d, f in os.walk(base_path):
        for dir_name in d:
            if "log_" in dir_name:
                ylog = os.path.join(p, dir_name)
    return ylog


if __name__ == '__main__':

    if DEBUG:
        # ----------------------------------
        # Debug mode
        ylog_base_p = "/home/local/SPREADTRUM/minchao.sun/logs/from7054/116_20170227184951"
        # ylog_base_p = "/home/local/SPREADTRUM/minchao.sun/logs/233_20170213164728"
        date = ylog_base_p.split('_')[-1][0:8]
        serial_num = "000"
        os.chdir("/home/local/SPREADTRUM/minchao.sun/Documents/log_postprocess_7.0.1/PC64_ylog")
        # ---------------------------
    else:
        # check if the input is valid
        if len(sys.argv) > 1:
            # if valid, get the second input paramount as log base path
            ylog_base_p = sys.argv[1]
            date = ylog_base_p.split('_')[-1][0:8]
            serial_num = "000"
        else:
            # if invalid, then quit
            print "please input params: SN_date"
            print "such as 'python slog_postprocess.py 0123456789ABCDEF_20150829135231' "
            sys.exit(1)

    # absolute path of ylog directory
    ylog_base_p = os.path.abspath(ylog_base_p)
    post_process_report = ylog_base_p + os.path.sep + "post_process_report"
    # Delete an entire directory tree; path must point to a directory

    if os.path.exists(post_process_report):
        shutil.rmtree(post_process_report)
    ylog_p = find_logdir(ylog_base_p)
    if ylog_p is None:
        print "No ylog for %s: " % ylog_p
        sys.exit(1)

    asy = AnalyzeYlog(ylog_p)
    asy.analyzef()
    print "Analysis completed"

    FP = FolderParser(ylog_p, serial_num)
    print "Folder parsing completed"

    KP = KernelParser(ylog_p, FP)
    KP.parse_kernel()
    KP.parse_kernel_emmc()
    KP.parse_kernel_dmc_mpu()
    KP.parse_assert()
    print "Kernel panic parsing completed"
