import sys
import requests
import subprocess
import platform
import os
import psutil
import shutil
import time
import urllib2

post_url = 'http://192.168.10.22:8888/post_receive.php'
tarurl = 'http://192.168.10.22:8888/upgrade.tar.gz'
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
	


def GetNowTime():
    return time.strftime("%Y-%m-%d",time.localtime(time.time()))

# add  backup  directory
def make_copy_dir(copydir='/opt/iprobe'):
    copy_dir = copydir + 'backup'
    if os.path.isdir(copy_dir):
        shutil.rmtree(copy_dir)
    try:
        os.makedirs(copy_dir)
    except OSError,e:
       print e
    return copy_dir



#backuping , copy file to -> targetDir
def copyFiles(sourceDir,  targetDir):
    if sourceDir == targetDir:
        print "sourceDIR  and targetDIR not same!"
        return
    for file in os.listdir(sourceDir):
        sourceFile = os.path.join(sourceDir,  file)
        targetFile = os.path.join(targetDir,  file)
        if os.path.isfile(sourceFile):
            if not os.path.exists(targetDir):
                os.makedirs(targetDir)
            if not os.path.exists(targetFile) or(os.path.exists(targetFile)):
                    open(targetFile, "wb").write(open(sourceFile, "rb").read())
        if os.path.isdir(sourceFile):
            First_Directory = False
            copyFiles(sourceFile, targetFile)


#copy DIR  [iprobe ->  iprobe.backup]
from shutil import copytree, ignore_patterns
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

def  download_tar(url, tar_file_name):
    r = requests.get(url)
    with open(tar_file_name ,"w")  as code:
        code.write(r.content)

def find_md5_file(tar_filename):
    md5file = "tar -tf " + tar_filename + " | sed -n  \' /.md5/p\' "
    return Execute(md5file)



def  check_tar(tar_filename, md5_filename):
    untar_comm = 'tar -xvf ' + tar_filename
    Execute(untar_comm)

    untar_file_arr = tar_filename.split('.')
    untar_file_name = untar_file_arr[0]
    print untar_file_name

    os.chdir(untar_file_name)
    print os.getcwd()
    md5_comm = 'md5sum -c --quiet ' + md5_filename
    ismd5ok = Execute(md5_comm)
    os.chdir('..')
    print os.getcwd()
    if "FAILED" in ismd5ok:
        value = "FAILED"
    else:
        value = "OK"
    return value


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
    print type(pro_state)
    arr_pro = pro_state.replace('Process',' ').replace('\n',' ').replace('\'', ' ').split()
    for i in range(len(arr_pro)):
        print arr_pro[i]
        stop_comm = installdir + '/monit -c ' + installdir + '/monitrc stop ' + arr_pro[i]
        Execute(stop_comm)
    stop_monit_self()
    time.sleep(6)
##############################################
def backup_err():
    post_data =  { 'backup_err': 1 }
    post(post_url,post_data)
    start_process_all()
    sys.exit(1)

def upgrade_err():
    post_data = { 'upgrade_err': 1 }
    post(post_url. post_data)
    fullcopy(backupdir, installdir)
    start_process_all()
    sys.exit(1)

def goback_err():
    post_data = { 'goback_err': 1 }
    start_process_all()
    sys.exit(1)
	
def upgrade_ok():
    post_data = { 'upgrade_ok': 1 }
    post(post_url, post_data)
    sys.exit(0)


if __name__ == '__main__':
    for  i  in range(3):
        #download tar  package
#        get_tar_url()
        tar_file_name = 'upgrade.tar.gz'
        untar_file_arr = tar_file_name.split('.')
        untar_file_name = untar_file_arr[0]
        download_tar(tarurl, tar_file_name)
        #check file not change in untar
        try:
            md5filename = find_md5_file(tar_file_name).strip()
            print md5filename
        except IOError, e:
            continue

        arr_path = md5filename.split('/')
        md5file = arr_path[-1]
        if md5file == "":
            print "%s no exist" %md5file
            continue
		

        isok = check_tar(tar_file_name, md5file)
        if isok == "FAILED":
            continue

        monit_stop_all()

		#install dir backup
        try:
            fullcopy(installdir, backup_dir)
        except IOError,e:
            backup_err()


        # upgradeing
        try:
            copyFiles(untar_file_name, installdir)
        except:
            upgrade_err()

        #start monit
        start_process_all()
        upgrade_ok()



