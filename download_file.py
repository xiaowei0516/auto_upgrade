import sys
import requests
import subprocess
import platform
import os
import psutil
import shutil
import time
import urllib2
import tarfile
import hashlib

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
	

def extractTar(tarname):
    if not tarfile.is_tarfile(tarname):
        return False
    tar = tarfile.open(tarname)
    tar.extractall()
    tar.close()
    return True

def get_file_md5(filename=''):
    with open(filename, 'r') as f:
        m = hashlib.md5()
        while True:
            data = f.read(10240)
            if not data:
                break
            m.update(data)
        return m.hexdigest()


def md5_check(md5file="all.md5"):
    with open(md5file,'r') as  fileHandle:
        fileList = fileHandle.readlines()
        for fileLine in fileList:
            if ".md5" not in fileLine:
                arr = fileLine.strip().split()
                if arr[0] !=  get_file_md5(arr[1]):
                    return  "False"
        return "Ok"                    

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



#upgrade , increment add file
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
                open(targetFile, "wb").write(open(sourceFile, "rb").read())  #create or replace file
        if os.path.isdir(sourceFile):
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


def  start_process_all():
    osname = check_os()
    if 'centos6' in osname or 'CentOS6' in osname or 'ubuntu12' in osname or 'ubuntu14' in osname:
        Execute('initctl start monit')
    if 'ubuntu8' in osname:
        Execute('initctl start monit')
    start_comm = installdir + '/monit -c ' + installdir + '/monitrc start all'
    Execute(start_comm)


def monit_stop_all():
    if os.name == "posix":  #Linux
        monit_status_comm = installdir + '/monit -c ' + installdir + '/monitrc status | grep "Process"'
    else:                  #Windows
        monit_status_comm = installdir + '/monit -c ' + installdir + '/monitrc status | findstr "Process"'
    pro_state  = Execute(monit_status_comm)
    arr_pro = pro_state.replace('Process',' ').replace('\n',' ').replace('\'', ' ').split()
    for i in range(len(arr_pro)):
        if "auto_upgarde" != arr_pro[i]:
            stop_comm = installdir + '/monit -c ' + installdir + '/monitrc stop ' + arr_pro[i]
            Execute(stop_comm)
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
        tar_file_name = 'upgrade.tar.gz'
        untar_file_arr = tar_file_name.split('.')
        untar_file_name = untar_file_arr[0]

        download_tar(tarurl, tar_file_name)

        #untar
        extractTar(tar_file_name)

        md5file = ''
        for root, dirs, files in os.walk(untar_file_name):
            for name in files:
                if ".md5" in os.path.join(root, name):  # is or not   all.md5
                    md5file = os.path.join(root,name)
                    break

        os.chdir(untar_file_name)
        if md5_check(md5file) == "False":
            continue
        os.chdir('..')
		
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



