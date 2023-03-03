#!/bin/bash

#
#
#CONFIG
#
#

#torrc for locally-ran W & Z relays
TORRCW="/users/magesap/TorLatencyNormalizationFiles/ExperimentScripts/tingOnDeter/ting/tor/configs/torrc-w"
TORRCZ="/users/magesap/TorLatencyNormalizationFiles/ExperimentScripts/tingOnDeter/ting/tor/configs/torrc-z"
#client torrc
TORRCCLIENT="/users/magesap/TorLatencyNormalizationFiles/ExperimentScripts/tingOnDeter/ting/tor/configs/torrc-client"
#Tor binary to run W & Z (currently v0.4.7.9)
WZTORBINARY="/users/magesap/TorLatencyNormalizationFiles/ExperimentScripts/tingOnDeter/ting/tor/tor-0.4.7.9/src/app/tor"
CLIENTTORBINARY="/users/magesap/TorLatencyNormalizationFiles/ExperimentScripts/tingOnDeter/ting/tor/tor-0.4.5.10/src/app/tor"




#
#
#CHECK CONNECTIVITY
#
#

# Test TCP connectivity to a well-known port
printf "checking 8.8.8.8:443 for TCP connectivity...\n"
if nc -zw1 8.8.8.8 443 >/dev/null; then
    # If the connection is successful, continue into the rest of the script
    printf "Success. External connectivity present.\n"
else
    # If the connection fails, print an error message and exit
    printf "Network connectivity not available\n"
    exit 1
fi




#
#
#FETCH ADDRESSES
#
#

# Get the current IP address
REMOTE_IP=$(curl -s https://checkip.amazonaws.com)
printf "Remote IP: $REMOTE_IP\n"
# Get the local IP address from ifconfig instead
LOCAL_IP=$(ifconfig | grep 'inet ' | grep -v '127.0.0.1' | awk '{print $2}' | cut -b 6-)
printf "Local IP: $LOCAL_IP\n"




#
#
#EDIT TORRCs
#
#

# Replace the old IP address in the configuration file with the local IP address
#ChatGPT original:
#sed -E -i "s/(.*Address \b)[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+(\b.*)/\1$LOCAL_IP\2/g" /path/to/torrc
#My modified one:
sed -E -i "s/(^ORPort \b)[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+:([0-9]+)( NoAdvertise.*)/\1$LOCAL_IP:\2 \3/" "$TORRCW"
sed -E -i "s/(^ORPort \b)[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+:([0-9]+)( NoAdvertise.*)/\1$LOCAL_IP:\2 \3/" "$TORRCZ"

#Then to handle other lines of different formats…
sed -E -i "s/(^Address \b)[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+(\b.*)/\1$REMOTE_IP\2/" "$TORRCW"
sed -E -i "s/(^Address \b)[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+(\b.*)/\1$REMOTE_IP\2/" "$TORRCZ"

sed -E -i "s/(^ORPort \b)[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+:([0-9]+)( NoListen.*)/\1$REMOTE_IP:\2 \3/" "$TORRCW"
sed -E -i "s/(^ORPort \b)[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+:([0-9]+)( NoListen.*)/\1$REMOTE_IP:\2 \3/" "$TORRCZ"

sed -E -i "s/(^Exitpolicy accept \b)[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+(\b.*)/\1$REMOTE_IP:\2/" "$TORRCW"
sed -E -i "s/(^Exitpolicy accept \b)[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+(\b.*)/\1$REMOTE_IP:\2/" "$TORRCZ"


printf "IPs updated in torrc's: $TORRCW\nand\n$TORRCZ\n"

#
#
#STARTING TOR
#
#

#Run W & Z as daemons w/ the new torrc
printf "Running Tor w/ torrc-w..."

$WZTORBINARY -f $TORRCW

printf "Daemonized.\nRunning Tor w/ torrc-z)
