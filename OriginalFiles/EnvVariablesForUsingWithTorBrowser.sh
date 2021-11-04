# Use system daemon socks port
export TOR_SOCKS_PORT=9050
# Use system daemon control port
export TOR_CONTROL_PORT=9051
# Don't launch a second tor instance, and don't take ownership of it.
export TOR_SKIP_LAUNCH=1
# Tell it where to find the control auth cookie
#export TOR_CONTROL_COOKIE_AUTH_FILE=/var/run/tor/control.authcookie
