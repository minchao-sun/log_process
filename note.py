#!/usr/bin/env python
# coding:utf-8


import sys
import os
import platform
import re
import shutil
import gzip
import re
import kernel_process
from kernel_process import FileItem, FileSort, FolderParser, ConfigParser

global vmlinux_f
global sysdump_p
global ylog_p
global serial_num
global fp
global post_process_report


def isLinux():
    return platform.system() == 'Linux'


###############parse_kernel,anr,java.native,wt###################

def run_kernel_panic(devbit):
    print "***********kernel_panic begin************"

    m = Main(vmlinux_f, sysdump_p, ylog_p, devbit, serial_num)
    m.run()
    m.genReport()


def run_anr():
    print "***********anr begin************"
    parse_anr(serial_num)


def run_native_crash():
    print "***********native_crash begin************"
    parse_native_crash(serial_num)


def run_java_crash():
    print "***********java_crash begin************"
    parse_java_crash(serial_num)


def run_watchdog_crash():
    print "***********watchdog_crash begin************"
    parse_watchdog_crash(serial_num)


def run_lowpower():
    print "***********lowpower begin************"
    parse_lowpower(serial_num)


def run_kmemleak():
    print "***********kmemleak begin************"
    parse_kmemleak(ylog_p, serial_num)


############parse_anr##################
def parse_anr(devnum):
    anr_ylog_regex = re.compile(r"ylog.anr 000")
    anr_get_pid_regex = re.compile(r"----- pid\s*(\d+)\s*at\s*(.*)\s*-----")
    anr_get_module_regex = re.compile(r"Cmd line:\s*(.*)")

    reportDir = post_process_report + os.path.sep + "anr"
    if os.path.exists(reportDir):
        shutil.rmtree(reportDir)
    # create dir: post_process_report/anr
    os.makedirs(reportDir)

    pidlist = reportDir + os.path.sep + "anrpidlist.txt"
    pidpath = reportDir + os.path.sep + "ANR"
    if os.path.exists(pidpath):
        shutil.rmtree(pidpath)
    os.makedirs(pidpath)
    pidl = open(pidlist, "w+")

    traces_file = fp.getFilesBy('anrtraces')
    traces_file = traces_file.split(",")
    if traces_file[0] == '':
        pidl.close()
        return 0
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
                            pidl.write(line)
                        pidr.write(line)
                        line = tfp.readline()
                if line.find("ylog.anr") != -1 and line.find(" dmesg ") != -1:
                    while line:
                        pidr.write(line)
                        line = tfp.readline()
                line = tfp.readline()
            tfp.close()


################parse_lowpower###############

def get_files(filep, TYPE):
    files = filep.getFilesBy(TYPE)
    print files
    if files:
        return files.split(',')
    return None


def fileAnalyst(file_param, preport, plist):
    low_power_regex = re.compile(r'cap:0')
    current_regex = re.compile(r'current:(.\d+).*')
    vbat_regex = re.compile(r'vbat:(.\d+).*')
    state_regex = re.compile(r'state:(\d+)')
    ret = False
    line_count = 0

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
            ret = True

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

        if Thermal_kernel_regex.search(line):
            tmp_count = count % (len(last_temp) - 1)
            last_temp[tmp_count] = line
            count += 1
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
                    if Thermal_kernel_regex.search(line) and int(Thermal_kernel_regex.search(line).group(1)) > 105000:
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


def parse_lowpower(devnum):
    logPath = get_files(fp, "lowpower")
    if logPath:
        tmpfiles = FileSort(logPath)
        logPath = tmpfiles.fsort()
    sd_kernel_file_exist_flag = False
    sd_kernel_file = []
    android_main_file_exist_flag = False
    last_android_main_file = []

    lowpower_path = post_process_report + os.path.sep + "low_power"
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
        kernel_log = ylog_p + os.path.sep + "internal_storage" + os.path.sep + "last_ylog" + os.path.sep + "ylog1" + os.path.sep + "kernel" + os.path.sep + "kernel.log"
        print kernel_log
        find_freezescreen(kernel_log, preport, plist)
    preport.close()
    plist.close()

    if os.path.exists(tmpfile):
        os.remove(tmpfile)
    if os.path.exists(tmplist):
        os.remove(tmplist)


############parse_watchdog_crash#######################

def get_snapshot_file_info(sfiles, watchdog_file, listfile):
    thread_id_regex = re.compile(r'\s*held by thread\s*(\d+)')
    thread_id_line_regex = re.compile(r'\s*tid=(\d+)')
    tfp = open(watchdog_file, 'a+')
    lfp = open(listfile, 'a+')
    tid_list = []
    for snap_f in sfiles:

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


def get_watchdog_file_info(watchdog, np, ft):
    watchdog_regex = re.compile(r'Blocked in handler on')
    watchdog_regex2 = re.compile(r'Blocked in')
    watchdog_thread_regex = re.compile(r'\((.*?)\)', re.I | re.X)
    # tfp = open(watchdog_file,'w')
    enter = False
    watchdog_traces = []
    # try:
    if os.path.exists(watchdog):
        dfp = open(watchdog)
    # except:
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
            # tfp.write(line)
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
            dfp = gzip.GzipFile(wf, "r")
            outfile = open(dstfile, "w")
            outfile.write(dfp.read())
            outfile.close()
            watchdog_file.append(dstfile)
        else:
            watchdog_file.append(wf)
    # watchdog_file.sort()
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


def getReportDir_wt():
    reportDir = post_process_report + os.path.sep + "watchdog_timeout"
    if not os.path.exists(reportDir):
        os.makedirs(reportDir)
    return reportDir


def getReportFile_wt():
    reportDir = getReportDir_wt()
    reportFile = os.path.join(reportDir, 'watchdog_report.txt')
    return reportFile


def clearReportDir_wt():
    reportDir = getReportDir_wt()
    shutil.rmtree(reportDir)


def parse_watchdog_crash(devnum):
    watchdog_killing_system_process_regex = re.compile(r'WATCHDOG KILLING SYSTEM PROCESS')
    wat_flag = None
    sys_flag = None
    clearReportDir_wt()
    reportFile = getReportFile_wt()
    reportDir = getReportDir_wt()
    watchdog_list = reportDir + os.path.sep + "watchdog_list.txt"
    preport = open(reportFile, "w+")
    plist = open(watchdog_list, "w+")
    ####parse info from dropbox/file
    systemfiles = fp.getFilesBy("watchdogcrash")
    systemfiles = systemfiles.split(",")
    sp = FileSort(systemfiles)
    systemfiles = sp.fsort()
    if systemfiles:
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
        # print snapfiles
        get_snapshot_file_info(snapfiles, reportFile, watchdog_list)


############parse_native_crash##############################
def compare_slog_dropbox_native(report_p, list_p, tmpr_p, tmpl_p):
    native_crash_module_get_regex = re.compile(r'\s*name: (\w+)')
    reportp = open(report_p)
    listp = open(list_p)
    tmprp = open(tmpr_p)
    tmplp = open(tmpl_p)

    line1 = listp.readlines()
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
        if nativec:
            break
        line = fd.readline()
    fd.close()
    try:
        return (core_list, tmp_time)
    except:
        return 0


def parse_native_crash(devnum):
    nativepath = post_process_report + os.path.sep + "native_crash"
    if os.path.exists(nativepath):
        shutil.rmtree(nativepath)
    if not os.path.exists(nativepath):
        os.makedirs(nativepath)
    native_crash_file = nativepath + os.path.sep + "native_crash_report.txt"
    native_crash_list = nativepath + os.path.sep + "native_crash_list.txt"
    preport = open(native_crash_file, "w+")
    plist = open(native_crash_list, "w+")
    core_list = []
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
    preport.close()
    plist.close()
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

    if os.path.exists(tmpfile):
        os.remove(tmpfile)
    if os.path.exists(tmplist):
        os.remove(tmplist)


##############parse_java_crash################################
def getReportDir_java():
    reportDir = post_process_report + os.path.sep + "java_crash"
    if not os.path.exists(reportDir):
        os.makedirs(reportDir)
    return reportDir


def clearReportDir_java():
    reportDir = getReportDir_java()
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


def getCrashEvent(efile, pfile, rf):
    """
    :param efile: event log file
    :param pfile: problem list file
    :param rf: report file
    :return:
    """
    java_crash_regex = re.compile(r'\sFATAL EXCEPTION:')
    java_crash_line_regex = re.compile(r'\sAndroidRuntime:\s')
    ####get crash log
    sysfiles = getSystemLogPaths(fp, "javacrash")
    if sysfiles:
        sp = FileSort(sysfiles)
        sysfiles = sp.fsort()
    if os.path.exists(efile):
        fd = open(efile)
    else:
        # print "Open event file error,return"
        print "No event file for javacrash"
        return 0
    pfile.write("file: " + efile + "\n")
    line = fd.readline()
    # read each line in events.log
    while line:
        ######find am_crash from event file
        if line.find("am_crash") != -1 and line.find("java") != -1:
            pfile.write(line)
            line = line.strip().split(" ")
            crashtime = line[0] + " " + line[1].split(".")[0]
            print crashtime
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

    java_crash_regex = re.compile(r'\sFATAL EXCEPTION:')
    java_crash_line_regex = re.compile(r'\sAndroidRuntime:\s')
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
            pl.write(line)
            pf.write(line)
            for i in range(10):
                line = dfp.readline()
                pf.write(line)
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


def parse_java_crash(devnum):
    tmpfile = os.path.abspath('.') + os.path.sep + "logs" + os.path.sep + "javacrash_file_tmp.txt"
    tmplist = os.path.abspath('.') + os.path.sep + "logs" + os.path.sep + "javacrash_list_tmp.txt"

    # Delete dir: /post_process_report/java_crash
    clearReportDir_java()
    # Create dir: /post_process_report/java_crash
    reportDir = getReportDir_java()
    print "reportDir:", reportDir
    # /post_process_report/java_crash/java_crash_report.txt
    reportFile = os.path.join(reportDir, 'java_crash_report.txt')
    # /post_process_report/java_crash/java_crash_list.txt
    problemlist = os.path.join(reportDir, 'java_crash_list.txt')
    # dir paths of java crash log
    systemLogPaths = getSystemLogPaths(fp, "javacrash")
    # determine process order
    if systemLogPaths:
        sp = FileSort(systemLogPaths)
        systemLogPaths = sp.fsort()
    print "log file paths:", systemLogPaths
    # file: events.log
    eventlogs = getEventLogs(fp, "javacrashevent")
    if eventlogs:
        sp = FileSort(eventlogs)
        eventlogs = sp.fsort()
    dropboxlogs = getDropboxLogs(fp, "javacrashdropbox")
    if eventlogs:
        # create and write file
        plist = open(problemlist, "w+")
        rfile = open(reportFile, "w+")
        for eventfile in eventlogs:
            getCrashEvent(eventfile, plist, rfile)
        # get system log content
        plist.close()
        rfile.close()
    elif systemLogPaths:
        for systemLog in systemLogPaths:
            parse(systemLog, reportFile)
    else:
        print 'No system and event log file to parse.'
    if dropboxlogs:
        tmpfile_p = open(tmpfile, "w")
        tmplist_p = open(tmplist, "w")
        for dropboxlog in dropboxlogs:
            getSystemCrashFileinfo(dropboxlog, tmpfile_p, tmplist_p)

        tmpfile_p.close()
        tmplist_p.close()
        if os.path.exists(tmplist):
            compare_slog_dropbox_java(reportFile, problemlist, tmpfile, tmplist)
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


################# Main ##################
if __name__ == '__main__':

    DEBUG = True
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
    ylog_p = kernel_process.find_logdir(ylog_base_p)

    if ylog_p is None:
        print "No ylog for %s " % ylog_p
        sys.exit(1)

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

    title = None

    fp = FolderParser(ylog_p, serial_num)
    print "Folder parsing completed"

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
        sysdump_check(sysdump_ci)
        dumpf = True
        for k in sysdump_ci:
            if k < 3:
                title += "\nsysdump file num is not correct!!!!!!!!!!!!!!!!"
                print title
                dumpf = False
                # sys.exit(1)
            if sysdump_ci[k] == 0L:
                title += "\nsysdump file size is not correct!!!!!!!!!!!!!!!!!!!!"
                print title
                dumpf = False
                # sys.exit(1)
        if dumpf:
            vmlinux_f = download_vmlinux()
            dev_bit = get_device_mode()

            # run_kernel_panic()
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
