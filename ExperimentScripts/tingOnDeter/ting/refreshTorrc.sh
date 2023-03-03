#!/bin/bash

TORRC="/users/magesap/TorLatencyNormalizationFiles/ExperimentScripts/tingOnDeter/ting/tor/configs/torrc-z"

# Get the current IP address
REMOTE_IP=$(curl -s https://checkip.amazonaws.com)

# Get the local IP address from ifconfig instead
LOCAL_IP=$(ifconfig | grep 'inet ' | grep -v '127.0.0.1' | awk '{print $2}' | cut -b 6-)

echo "Local IP: $LOCAL_IP"
# Replace the old IP address in the configuration file with the local IP address
#ChatGPT original:
#sed -E -i "s/(.*Address \b)[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+(\b.*)/\1$LOCAL_IP\2/g" /path/to/torrc
#My modified one:
sed -E -i "s/(^ORPort \b)[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+:([0-9]+)( NoAdvertise.*)/\1$LOCAL_IP:\2 \3/" "$TORRC"

#Then to handle other lines of different formats…
sed -E -i "s/(^Address \b)[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+(\b.*)/\1$REMOTE_IP\2/" "$TORRC"

sed -E -i "s/(^ORPort \b)[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+:([0-9]+)( NoListen.*)/\1$REMOTE_IP:\2 \3/" "$TORRC"

sed -E -i "s/(^Exitpolicy accept \b)[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+(\b.*)/\1$REMOTE_IP:\2/" "$TORRC"

