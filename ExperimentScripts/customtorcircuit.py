import sys
from stem import *
from stem import ORPort
import stem.descriptor.remote
import getpass
import subprocess
import argparse
from termcolor import colored
import time
import requests
import functools
import tbselenium.common as cm
from tbselenium.tbdriver import TorBrowserDriver
from tbselenium.utils import launch_tbb_tor_with_stem
import os
#this might be a mistake, but I'll keep it simple
import threading

tbb_dir = '/home/alex/tor-browser_en-US/'

if len(sys.argv[0]) < 1:
    print("ERR: No Argument\nusage: script.py -v 2-3 (one is default) 'guard','middleman','exit' -logfile /errorfile")
    sys.exit(1)

parser = argparse.ArgumentParser()
parser.add_argument('-v', type=int)
parser.add_argument('path', type=str)
parser.add_argument('-logfile', type=str)
args = parser.parse_args()

selectedPath = args.path
selectedPathList = selectedPath.split(",")
if args.logfile:
    logfilepath = args.logfile
else:
    logfilepath = '/tmp/'+str(time.time())+'tor_error'

#select verbosity
if args.v == 2:
    log_level = "INFO"
elif args.v == 3:
    log_level = "DEBUG"
else:
    log_level = "NOTICE"


#theres a couple different functions in here that do the same thing differently, primarmily in regard to launching tor
#startTor() does so using stem and not with the tor browser.
#startTorBrowser() does so using the tor browser bundle through a subprocess
#startCustomTorBrowser() does so using tbselenium using a custom config and returns a subprocess. Also allows selenium to be used

def CheckTorrc():
    with open('/home/alex/tor-browser_en-US/Browser/TorBrowser/Data/Tor/torrc-defaults') as file:
         contents = file.read()
         search_word = "__LeaveStreamsUnattached 1"
         if search_word in contents:
             print("config modifications are verified: streams will not be attached automatically")
             return True
         else:
             print("config is not customized. Please add  __LeaveStreamsUnattached 1  to ~/tor-browser_en-US/Browser/TorBrowser/Data/Tor/torrc-defaults")
             sys.exit(1)


def UneccecarilyVerboseAndRedundantPrintFunctionSinceUsingPythonsNormalPrintFunctionSomehowBreaksStemsMsgHandler(line):
    print(line)
#starts tor directly through stem, no browser
def startTor(log_level, logfilepath):
    tor_process = process.launch_tor_with_config(
        config = {
            'ControlPort': '9051',
            'Log': [
                log_level+' stdout',
                log_level+' file '+logfilepath,
            ],
            #'__DisablePredictedCircuits': '1',
            #'UseBridges': '1',
            'ClientTransportPlugin': 'dummy exec /home/alex/goptlib/examples/dummy-client/dummy-client',
            '__LeaveStreamsUnattached': '1',
            'HashedControlPassword': '16:1651BF63EE73164460ED67E7E4046DDB1FE7E408563A9CA566A0D3D538',
            'SocksPort': '9050 IPv6Traffic PreferIPv6 KeepAliveIsolateSOCKSAuth',
        }, completion_percent=0, take_ownership=True, close_output=False, init_msg_handler=UneccecarilyVerboseAndRedundantPrintFunctionSinceUsingPythonsNormalPrintFunctionSomehowBreaksStemsMsgHandler
    )
    #returns POPEN subprocess so I can communicate with it
    return tor_process


#Launches Tor Browser using POPEN, does not use selenium but works well
def startTorBrowser():
     subprocess.Popen(["/home/alex/tor-browser_en-US/Browser/start-tor-browser", '--default-torrc', '/home/alex/tor-browser_en-US/Browser/TorBrowser/Data/Tor/torrc-defaults'])


#Launches tor browser with custom config using stem and selenium
#allows use of selenium AND the subprocess stuff
def LaunchCustomTorBrowser(tbb_dir, loglevel, logfilepath):
    tor_binary = os.path.join(tbb_dir, cm.DEFAULT_TOR_BINARY_PATH)
    #get exit node descriptor, useful later
    exitDescriptor = descriptor.remote.Query(resource='/tor/server/fp/' + selectedPathList[2]).run()[0]
    #in order to integrate with the pluggable transport, we need the IP of the guard node
    guardDescriptor = descriptor.remote.Query(resource='/tor/server/fp/' + selectedPathList[0]).run()[0]
    guardDir_Port = "{}:{}".format(guardDescriptor.address, guardDescriptor.or_port)
    
    torrc = {
        'ControlPort': '9051',
        'SOCKSPort': '9050',
        'Log': [
            loglevel + ' stdout',
            loglevel + ' file ' + logfilepath,
        ],
        'UseBridges': '1',
        #setting the entry node as the bridge allows a pluggable transport to be used as a proxy, without a server
        #this has no effect on circuit length or construction
        'Bridge': 'dummy ' + guardDir_Port + ' ' + selectedPathList[0],
        'ClientTransportPlugin': 'dummy exec /home/alex/goptlib/examples/dummy-client/dummy-client',
        # '__DisablePredictedCircuits': '1',
        '__LeaveStreamsUnattached': '1',
        #'HashedControlPassword': '16:1651BF63EE73164460ED67E7E4046DDB1FE7E408563A9CA566A0D3D538',
    }
    tor_process = launch_tbb_tor_with_stem(tbb_path=tbb_dir, torrc=torrc, tor_binary=tor_binary)
    return tor_process, exitDescriptor


#connect to tor control port using optional password authentication
def ConnectControlPort():
    try:
      controller = control.Controller.from_port("127.0.0.1",9051)
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

def BuildCustomCircAndOpenStreamListener(controller, selectedPath):
    # creating custom circuit
    print("initial status: ", controller.get_info('circuit-status'))
    customcircid = controller.new_circuit(selectedPath, 'general')
    print("Creating Circuit " + customcircid + " on custom path ", selectedPath)
    print(colored("established status: " + controller.get_info('circuit-status'), 'green'))
    # when passed a stream, it attaches it to the custom circuit. Always.
    # allows other circuits to be present but not used for application traffic
    def attachStream(stream):
        if stream.status == 'NEW':
            # stream is returned as a list of objects, regardless of the size
            print(colored(
                f"STREAM EVENT:\nstream + {stream.id} attached to circuit {customcircid}\nTime Of Event: {time.time()}\nDetails: {stream[0]}",
                'blue'))
            controller.attach_stream(stream.id, customcircid)
    # prints out and (eventually) logs circuit and stream events. Relies on event listener
    def circuitAnomaly(event):
        print(colored(f"CIRCUIT EVENT:\nTime Of Event: {time.time()}\nDetails: {event}", "yellow"))
        # log alert to file at some point along with the other output
    # watches for streams and calls the preceding function
    controller.add_event_listener(attachStream, control.EventType.STREAM)
    # listens for circuit events to log
    controller.add_event_listener(circuitAnomaly, control.EventType.CIRC)


def CircRTT(ExitDescriptor):
    exitFP = selectedPathList[2]
    DirPort = [stem.DirPort(ExitDescriptor.address, ExitDescriptor.or_port)]
    while True:
        starttime = time.time()
        rtttest = descriptor.remote.Query(resource='/tor/server/fp/' + exitFP, fall_back_to_authority=False,
                                          endpoints=DirPort).run(True)[0]
        hackyRTT = time.time() - starttime
        print("RTT of custom circuit is probably: " + hackyRTT)
        print("there's a log somewhere that has an rtt time, idk where it's at, but stem records the rtt of this command\n"
              "It has a time measurement right now, but i cannot verify it's accuracy")
        #totally arbitrary, collects every 30s
        time.sleep(30)

def VisitUrl(tbb_dir):
    with TorBrowserDriver(tbb_dir, socks_port=9050, control_port=9051, tor_cfg=cm.USE_STEM) as driver:
        driver.get('https://www.whatismyip.com/')
        while True:
            time.sleep(3000)
            driver.refresh()
        #time.sleep(99999)


#tor_process = startTor(log_level, logfilepath)
if CheckTorrc() == False:
    sys.exit()

#returns guard descriptor, not needed nor used, but might be useful
tor_process, exitDescriptor = LaunchCustomTorBrowser(tbb_dir, log_level, logfilepath)
controller = ConnectControlPort()
BuildCustomCircAndOpenStreamListener(controller, selectedPath)
VisitUrl(tbb_dir)
exitFP = selectedPathList[2]  
DirPort = [stem.DirPort(exitDescriptor.address, exitDescriptor.or_port)]
starttime = time.time()
rtttest = descriptor.remote.Query(resource='/tor/server/fp/' + exitFP, fall_back_to_authority=False, endpoints=DirPort).run(True)[0]
hackyRTT = time.time() - starttime
print("RTT of custom circuit is probably: " + hackyRTT)
print("there's a log somewhere that has an rtt time, idk where it's at, but stem records the rtt of this command\n"
"It has a time measurement right now, but i cannot verify it's accuracy")
print("\n\n\n\n\n\n\n\n\n\n\n")
periodicRTT = threading.Thread(target=CircRTT, args=[exitDescriptor])
periodicRTT.start()
VisitUrl(tbb_dir)
#only for sure works with exit node


#watches the POPEN subprocess stdout indefinately
for line in tor_process.stdout:
    print("systime:", time.time(), line)
#I dont see any reason why the program would hit this line, but just for redundancy this will block the program
#since the tor process is terminated upon exit
tor_process.wait()


#the following is for command line tor.

#watches the POPEN subprocess stdout indefinately
#for line in tor_process.stdout:
    #print("systime:", time.time(), line)
#I dont see any reason why the program would hit this line, but just for redundancy this will block the program
#since the tor process is terminated upon exit
#tor_process.wait()
#
