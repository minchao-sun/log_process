#!/usr/bin/env python
# coding:utf-8

import sys
import os
import platform
import re
import shutil
import gzip
import re
from kernel_process import FileItem, FileSort, FolderParser, ConfigParser

DEBUG = True


class CrashParser(object):
    def __init__(self, log_path):
        self.crash = False
        self.__log_path = log_path
        self.__sysdump_p = None
        self.__sysdump_ci = {}

        self.__sysdump_path()  # get sysdump_p
        try:
            dd = len(os.listdir(self.__sysdump_p))
            if dd != 0:
                # some things in sysdump_p
                self.crash = True
        except:
            pass


    def __sysdump_check(self):
        flag = False
        # check if "sysdump.core.00" exists
        for f in os.listdir(self.__sysdump_p):
            if f.find("sysdump.core.00") != -1:
                flag = True
                break
        if not flag:
            # if not exists, exit
            print "No sysdump file"
            sys.exit(1)

        num = len(os.listdir(self.__sysdump_p))
        print "file num in sysdump dir:" + str(num)
        size = 0
        for p, d, f in os.walk(self.__sysdump_p):
            for name in f:
                size = os.path.getsize(os.path.join(p, name))
                # the size of the file(storage space occupied)
                if size == 0L:
                    # find 0 size file
                    print os.path.join(p, name)
                    break
            if size == 0L:
                print "break"
                break
        self.__sysdump_ci[num] = size

    def __sysdump_path(self):
        sysdump_p1 = self.__log_path + os.path.sep + "sysdump"
        sysdump_p2 = self.__log_path + os.path.sep + "external_storage" + os.path.sep + "sysdump"
        sysdump_p3 = self.__log_path + os.path.sep + "external_storage" + os.path.sep + "SYSDUMP"
        if os.path.exists(sysdump_p2):
            dd = len(os.listdir(sysdump_p2))
            if dd != 0:
                self.__sysdump_p = os.path.join(sysdump_p2, str("1"))
        elif os.path.exists(sysdump_p3):
            dd = len(os.listdir(sysdump_p3))
            if dd != 0:
                self.__sysdump_p = os.path.join(sysdump_p3, str("1"))
        else:
            self.__sysdump_p = sysdump_p1



def sysdump_check(sysdump_info, sysdump_p):
    flag = False
    # check if "sysdump.core.00" exists
    for f in os.listdir(sysdump_p):
        if f.find("sysdump.core.00") != -1:
            flag = True
            break
    if not flag:
        # if not exists, exit
        print "No sysdump file"
        sys.exit(1)

    num = len(os.listdir(sysdump_p))
    print "file num in sysdump dir:" + str(num)
    size = 0
    for p, d, f in os.walk(sysdump_p):
        for name in f:
            size = os.path.getsize(os.path.join(p, name))
            # the size of the file(storage space occupied)
            if size == 0L:
                # find 0 size file
                print os.path.join(p, name)
                break
        if size == 0L:
            print "break"
            break
    sysdump_info[num] = size


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
    ylog_p = find_logdir(ylog_base_p)

    if ylog_p is None:
        print "No ylog for %s " % ylog_p
        sys.exit(1)
    # get sysdump path
    sysdump_p1 = ylog_p + os.path.sep + "sysdump"
    sysdump_p2 = ylog_p + os.path.sep + "external_storage" + os.path.sep + "sysdump"
    sysdump_p3 = ylog_p + os.path.sep + "external_storage" + os.path.sep + "SYSDUMP"
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

    # check if there is reboot caused by kernel crash
    crash = False
    try:
        dd = len(os.listdir(sysdump_p))
        if dd != 0:
            # some things in sysdump_p
            crash = True
    except:
        pass

    if crash:
        title = "There is reboot caused by kernel crash"
        sysdump_ci = {}
        sysdump_check(sysdump_ci, sysdump_p)
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
        print "There is no reboot caused kernel crash"
        # run_java_crash()
        # run_native_crash()
        # run_watchdog_crash()
        # run_anr()
        # run_lowpower()
        # run_kmemleak()
