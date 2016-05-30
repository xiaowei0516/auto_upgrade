import requests
import time
import subprocess

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

def decode_file(encryptfile, output_file):
    openssl_comm = 'openssl  rsautl -verify -in ' + encryptfile + ' -out ' + output_file + ' -inkey rsa_key.pub  -pubin'
    #print openssl_comm
    Execute(openssl_comm)
    md5_comm = 'sed ' + '\'3,$d\' ' + output_file + ' | sed \'1d\''
    #print md5_comm
    md5 = Execute(md5_comm)
    #print md5
    sed_comm = 'sed -i ' + '\'2d\' '  + output_file
    #print  sed_comm
    Execute(sed_comm)
    #Execute("python output_file.py")
    return md5

def verify_file(filename, md5_origin):
    md5_comm = 'md5sum -t ' + filename + "| sed 's/\s\S*//g'"
    md5_now = Execute(md5_comm)
    if md5_now == md5_origin:
     #   print "aabb"
        return  "TRUE"
    else:
        return "FALSE"

def delay_time(tim):
	time.sleep(tim)

if __name__ == '__main__':
    while True:
        up_statue = check_upgrade_statues(upgrade_url)
        back_statue = check_back_status(back_url)

        if (up_statue == '1') and (back_statue == '1')
            continue

        if (up_statue == '1') or (back_statue == '1'):

			if up_statue == '1':
				download_script(upgrade_script_url, up_filename)
				md5 = decode_file(up_filename, up_decode_filename)
				isTrue = verify_file(up_decode_filename, md5)
				if isTrue == 'TRUE':
					py_comm = 'python ' + up_decode_filename
					#print py_comm
					Execute(py_comm)
				else:
					continue

			if back_statue == '1':
				download_script(back_script_url, back_filename)
				md5 = decode_file(back_filename, back_decode_filename)
				isTrue = verify_file(back_decode_filename, md5)
				if isTrue == 'TRUE':
					py_comm = 'python ' + back_decode_filename
					Execute(py_comm)
				else:
					continue
        else:
			continue
        delay_time(3600)
