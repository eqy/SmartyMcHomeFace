#!/bin/bash

sleep $2
#echo $1 | festival --tts
echo $1
espeak -ven+f2 -k5 "$1"
