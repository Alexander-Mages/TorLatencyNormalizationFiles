#!/bin/bash

#printf "./rttViaTelnet IP-address Port\n"
#IP = $1;
#Port = $2;


for i in {1..200}
do
    ts=$(date +%s%N) ; nc -zw30 $1 $2 ; tt=$((($(date +%s%N) - $ts)/1000000)) ; echo $tt
    sleep .25
done
