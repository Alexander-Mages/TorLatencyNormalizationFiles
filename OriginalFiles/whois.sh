#!/bin/bash
ip () {
local text=`/usr/bin/whois -h whois.ripe.net "$1"`
for x in $text
do
local range=`/usr/bin/grep -e "^inetnum: " <<< "$x"`
local cidr=`/usr/bin/grep -e "^CIDR: " <<< "$x"`
local org=`/usr/bin/grep -e "^Organization: " <<< "$x"`
done
if [[ -z "$org" && -z "$range" ]]
then
local unknown=`print $text | head -4`
print \\n$unknown\\n\\n
else
print \\n$org
print $range
print $cidr\\n
fi
}
