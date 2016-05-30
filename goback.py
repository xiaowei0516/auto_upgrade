import requests
import subprocess
import platform
import os
import psutil
import shutil
import time
import urllib2
import sys
from shutil import copytree, ignore_patterns


post_url = 'http://192.168.10.22:8888/post_receive.php'

installdir = '/opt/iprobe'
backup_dir = installdir + '-backup'

def PostData(url, data, timeout=60):
    try:
        time_start = int(time.time())
        request = urllib2.Request(url, data, {'Content-Type': 'application/octet-stream'})
        response = urllib2.urlopen(request,timeout=timeout)
        time_end = int(time.time())
        #print "HTTP post response: ", response.read()
        if response.getcode() != 200:
            print "Post json failed"
        if time_end - time_start > 25: 
            print "timeout on posting"
        return response.getcode() == 200 
    except Exception, e:
        return False


def post(url, post_data):
    jdata = str(post_data).replace('\'','"')
    PostData(url, jdata)
	



#copy DIR  [iprobe ->  iprobe.backup]
def fullcopy(source, destination):
    if os.path.isdir(destination):
        shutil.rmtree(destination)
    try:
        copytree(source, destination)
    except OSError,e:
        print e


#Linux  Windows
def  check_platform():
    plat = platform.system()
    return plat

def check_os():
    osname = platform.dist()  #tuple
    return osname[0] + osname[1]



def Execute(cmd,close_fds=True):
    try:
        proc = subprocess.Popen(cmd, shell = True, stdout = subprocess.PIPE)
        return proc.communicate()[0]
    except Exception, e:
        print "Execute failed, command: %s, error: %s" %(cmd, str(e))
        return None




def stop_monit_self():
    osname = check_os()
    if 'centos7' in osname  or 'CentOS7' in osname  or 'opensuse' in osname:
        if os.path.exists('/usr/bin/sysemctl'):
            Execute('systemctl stop monit.service')
    if  'centos6' in osname  or  'CentOS6' in osname or 'ubuntu12'  in osname or 'ubuntu14' in osname or 'ubuntu8' in osname:
        if os.path.exists('/sbin/initctl'):
            Execute('initctl stop monit')



def  start_process_all():
    osname = check_os()
    if 'centos6' in osname or 'CentOS6' in osname or 'ubuntu12' in osname or 'ubuntu14' in osname:
        Execute('initctl start monit')
    if 'ubuntu8' in osname:
        Execute('initctl start monit')
    start_comm = installdir + '/monit -c ' + installdir + '/monitrc start all'
    Execute(start_comm)


def monit_stop_all():
    monit_status_comm = installdir + '/monit -c ' + installdir + '/monitrc status | grep "Process"'
    pro_state  = Execute(monit_status_comm)
    #print type(pro_state)
    arr_pro = pro_state.replace('Process',' ').replace('\n',' ').replace('\'', ' ').split()
    for i in range(len(arr_pro)):
        #print arr_pro[i]
        stop_comm = installdir + '/monit -c ' + installdir + '/monitrc stop ' + arr_pro[i]
        Execute(stop_comm)
    stop_monit_self()
    time.sleep(6)
##############################################


def goback_err():
    post_data = { 'goback_err': 1 }
    start_process_all()
    sys.exit(1)

	
if __name__ == '__main__':
    try:
        monit_stop_all()
        fullcopy(backupdir, installdir)
    except:
	    goback_err()
    start_process_all()



