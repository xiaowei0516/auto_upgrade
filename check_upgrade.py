import requests
import time
import subprocess
import hashlib

upgrade_url = 'http://192.168.10.22:8888/upgrade.txt'
back_url = 'http://192.168.10.22:8888/goback.txt'

upgrade_script_url = 'http://192.168.10.22:8888/en_upgrade.py'
back_script_url = 'http://192.168.10.22:8888/en_back.py'

up_filename = 'enupgrade_probe.py'
back_filename = 'enback_probe.py'

up_decode_filename = 'upgrade_probe.py'
back_decode_filename = 'back_probe.py'

def  check_upgrade_statues(url):
    r = requests.get(url)
    return r.content

def  check_back_status(url):
    r = requests.get(url)
    return r.content

def  download_script(url,filename):
    r = requests.get(url)
    with open(filename,"w")  as code:
        code.write(r.content)

def Execute(cmd,close_fds=True):
    try:
        proc = subprocess.Popen(cmd, shell = True, stdout = subprocess.PIPE)
        return proc.communicate()[0]
    except Exception, e:
        print "Execute failed, command: %s, error: %s" %(cmd, str(e))
        return None

def decode_file(encryptfile, defile):
    openssl_comm = 'openssl  rsautl -verify -in ' + encryptfile + ' -out ' + defile + ' -inkey rsa_key.pub  -pubin'
    #print openssl_comm
    Execute(openssl_comm)

def recover_file(defile, output_file):
    md5 = ''
    try:
       origin = open(output_file, 'w')
    except Exception, e:
       print "open %s error" % output
       exit(0)

    with open(defile, 'r') as f:
        flieList = f.readlines()
        if i in range(len(fileList)):
            if i != 1 :
                origin.write(fileList[i])
            else:
                md5 = fileList[1]
        origin.close()
    return md5
            
def verify_file(filename, md5_origin):
    with open(filename, 'r') as f:
        m = hashlib.md5()
        while True:
            data = f.read(8192)
            if not data:
                break
            m.update(data)
        if m.hexdigest() == md5_origin:
            return  "TRUE"
        else:
            return "FALSE"

def delay_time(tim):
    time.sleep(tim)

if __name__ == '__main__':
    while True:
        tmp_file="tmp_file.py"
        up_statue = check_upgrade_statues(upgrade_url)
        back_statue = check_back_status(back_url)

        if (up_statue == '1') and (back_statue == '1'):
            continue

        if (up_statue == '1') or (back_statue == '1'):

            if up_statue == '1':
                download_script(upgrade_script_url, up_filename)
                decode_file(up_filename, tmp_file)
            
                md5 = recover_file(defile, up_decode_filename)
                
                isTrue = verify_file(up_decode_filename, md5)
                if isTrue == 'TRUE':
                    py_comm = 'python ' + up_decode_filename
                    Execute(py_comm)
                else:
                    continue

            if back_statue == '1':
                py_comm = 'python ' + back_decode_filename
                Execute(py_comm)
        else:
            continue
        delay_time(3600)
