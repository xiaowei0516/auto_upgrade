#-- compute md5sum
#-- write md5sum to  one_line
#-- encrypt  openssl

import subprocess
import sys

def Execute(cmd,close_fds=True):
    try:
        proc = subprocess.Popen(cmd, shell = True, stdout = subprocess.PIPE)
        return proc.communicate()[0]
    except Exception, e:
        print "Execute failed, command: %s, error: %s" %(cmd, str(e))
        return None

def encrypt_file(file_name, output_file):
    md5_comm = 'md5sum -t ' + file_name + "| sed 's/\s\S*//g'"
    #print md5_comm
    md5 = Execute(md5_comm).strip()
    sed_comm = 'sed -i ' + '\'1a ' +  md5 + '\' ' + file_name
    #print sed_comm
    Execute(sed_comm)
    openssl_comm = 'openssl rsautl -sign -in ' + file_name + ' -out ' + output_file + ' -inkey rsa_key'
    #print openssl_comm
    Execute(openssl_comm)

if __name__ == '__main__':
    for i in range(1, len(sys.argv)):
        output ='en'+sys.argv[i]
        #print output 
        encrypt_file(sys.argv[i], output)
