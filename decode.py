import  subprocess

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

if __name__ == '__main__':
	en = sys.argv[1]
    md5 = decode_file(en, "decode")
    verify_file("decode", md5)
