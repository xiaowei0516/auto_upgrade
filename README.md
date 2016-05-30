# auto_upgrade
encrypt-translate , using network node auto upgrade, upgrade error, auto goback

1. [gen_rsa.sh] gen  private key,  using private key generate public key  {in server}
2. [priv_encrypt.sh] using private encrypt file {in server}
3. [check_upgrade.py] daemon,auto check server flags, upgrade or goback,  check once every 3600s {in client}
4. [encrypt.py] encrypt file[md5 and openssl] {in server}
5. [download_file.py] decode file, download tar file, verify tar file, install upgrade tar, except handle {in client}
6. [decode.py] using testing {in server,use test}
7. [goback.py] [goback] {in client}

