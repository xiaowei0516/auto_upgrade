#!/bin/bash
function showUsage(){
    echo "Usage:"
    echo "$1 -i input_file -o out_file "
	echo ""
}

while [ "$1" ]
do
    case "$1" in
        -i)
            INFILE=$2
            shift ;;
        -o)
            OUTFILE=$2
			shift ;;
        -h)
            showUsage $0
            exit;;
    esac
	shift
done

openssl rsautl -sign -in $INFILE -out $OUTFILE -inkey rsa_key
