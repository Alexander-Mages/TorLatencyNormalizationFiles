import sys
from stem import *
import getpass
import subprocess
import argparse
from termcolor import colored
import time
import requests
import functools
from tbselenium.tbdriver import TorBrowserDriver
from tbselenium.utils import launch_tbb_tor_with_stem
from selenium.webdriver.support.ui import Select

#script takes one argument: the path selection.
#should be in this format: '','','' -vv. e.g. '00240ECB2B535AA4C1E1874D744DFA6AF2E5E941','00283B5564E3072DCDDAB31D6EF622DD49BF524F','0011BD2485AD45D984EC4159C88FC066E5E3300E' -vv
#print("Note: default location of the log is /tmp/tor_error_log. Positional argument after path can specify a custom location")

tbb_dir = '/home/alex/tor-browser_en-US/'

if len(sys.argv[0]) < 1:
    print("ERR: No Argument\nusage: script.py -v [2-3 (one is default)] 'guard','middleman','exit'")
    sys.exit(1)

parser = argparse.ArgumentParser()
parser.add_argument('-v', type=int)
parser.add_argument('path', type=str)
parser.add_argument('-logfile', type=str)
args = parser.parse_args()

selectedPath = args.path
if args.logfile:
    logfilepath = args.logfile
else:
    logfilepath = '/tmp/torerror'

#select verbosity
if args.v == 2:
    log_level = "INFO"
elif args.v == 3:
    log_level = "DEBUG"
else:
    log_level = "NOTICE"

#prints out and (eventually) logs circuit and stream events. Relies on event listener
def circuitAnomaly(event):
    print(colored(f"CIRCUIT EVENT:\nTime Of Event: {time.time()}\nDetails: {event}", "yellow"))
    #log alert to file at some point along with the other output

def UneccecarilyVerboseAndRedundantPrintFunctionSinceUsingPythonsNormalPrintFunctionSomehowBreaksStemsMsgHandler(line):
    print(line)

def startTor(loglevel, logfilepath):
    tor_process = process.launch_tor_with_config(
        config = {
            'ControlPort': '9051',
            'Log': [
                loglevel+' stdout',
                loglevel+' file '+logfilepath,
            ],
            #'__DisablePredictedCircuits': '1',
            '__LeaveStreamsUnattached': '1',
            'HashedControlPassword': '16:1651BF63EE73164460ED67E7E4046DDB1FE7E408563A9CA566A0D3D538',
            'SocksPort': '9050 IPv6Traffic PreferIPv6 KeepAliveIsolateSOCKSAuth',
        }, completion_percent=0, take_ownership=True, close_output=False, init_msg_handler=UneccecarilyVerboseAndRedundantPrintFunctionSinceUsingPythonsNormalPrintFunctionSomehowBreaksStemsMsgHandler
    )
    #returns POPEN subprocess so I can communicate with it
    return tor_process

def startTorBrowser():
    with open('/home/alex/TorLatencyNormalizationFiles/OriginalFiles/customtorcircuit.py') as file:
        contents = file.read()
        search_word = "__LeaveStreamsUnattached 1"
        if search_word in contents:
            print("config modifications are verified: streams will not be attached automatically")
        else:
            print("config is not customized. Please add  __LeaveStreamsUnattached 1  to ~/tor-browser_en-US/Browser/TorBrowser/Data/Tor/torrc-defaults")
            sys.exit(1)
    subprocess.Popen(["/home/alex/tor-browser_en-US/Browser/start-tor-browser", '--default-torrc', '/home/alex/tor-browser_en-US/Browser/TorBrowser/Data/Tor/torrc-defaults'])

def visitWebRedirector():
    with TorBrowserDriver("/home/alex/tor-browser_en-US/") as driver:
        driver.get('http://127.0.0.1:8080')

#connect to tor control port using optional password authentication
def ConnectControlPort():
    try:
      controller = control.Controller.from_port("127.0.0.1",9151)
    except SocketError as exc:
      print('Unable to connect to port 9051 ', exc)
      sys.exit(1)

    try:
      control.Controller.authenticate(controller)
    except connection.IncorrectSocketType:
      print('Please check in your torrc that 9051 is the ControlPort.')
      print('Maybe you configured it to be the ORPort or SocksPort instead?')
      sys.exit(1)
    except connection.MissingPassword:
      controller_password = getpass.getpass('Controller password: ')

      try:
        connection.authenticate(controller, password = controller_password)
      except connection.PasswordAuthFailed:
        print('Unable to authenticate, password is incorrect')
        sys.exit(1)
    except connection.AuthenticationFailure as exc:
      print('Unable to authenticate: ', exc)
      sys.exit(1)
    print("Tor version", controller.get_version())
    return controller


#tor_process = startTor(log_level, logfilepath)
startTorBrowser()
time.sleep(5)
controller = ConnectControlPort()

#creating custom circuit
print("initial status: ", controller.get_info('circuit-status'))
customcircid = controller.new_circuit(selectedPath,'general')
print("Creating Circuit " + customcircid + " on custom path ",selectedPath)
print(colored("established status: " + controller.get_info('circuit-status'), 'green'))

#when passed a stream, it attaches it to the custom circuit. Always.
#allows other circuits to be present but not used for application traffic
def attachStream(stream):
    if stream.status == 'NEW':
        #stream is returned as a list of objects, regardless of the size
        print(colored(f"STREAM EVENT:\nstream + {stream.id} attached to circuit {customcircid}\nTime Of Event: {time.time()}\nDetails: {stream[0]}", 'blue'))
        controller.attach_stream(stream.id, customcircid)
#watches for streams and calls the preceding function
controller.add_event_listener(attachStream, control.EventType.STREAM)

#listens for circuit events to log
controller.add_event_listener(circuitAnomaly, control.EventType.CIRC)

visitWebRedirector()
while True:
    time.sleep(30)


#the following is for command line tor.

#watches the POPEN subprocess stdout indefinately
#for line in tor_process.stdout:
    #print("systime:", time.time(), line)
#I dont see any reason why the program would hit this line, but just for redundancy this will block the program
#since the tor process is terminated upon exit
#tor_process.wait()
#
