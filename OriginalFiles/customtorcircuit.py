import sys
from stem import *
import getpass
import subprocess
import argparse
from termcolor import colored

#makes a new circuit with custom path and stops tor from creating new ones
#note: if you add more than 3 fingerprints, the circuit just extends to whatever size you want

#script takes one argument: the path selection.
#should be in this format: '','','' -vv. e.g. '00240ECB2B535AA4C1E1874D744DFA6AF2E5E941','00283B5564E3072DCDDAB31D6EF622DD49BF524F','0011BD2485AD45D984EC4159C88FC066E5E3300E' -vv
if len(sys.argv[0]) < 1:
    print("ERR: No Argument\nusage: script.py -v [2-3 (one is default)] 'guard_fingerprint','middleman_fingerprint','exit_fingerprint'")
    sys.exit(1)

parser = argparse.ArgumentParser()
parser.add_argument('-v', type=int)
parser.add_argument('pos_arg', type=str)
args = parser.parse_args()

selectedPath = args.pos_arg

#select verbosity
if args.v == 2:
    log_level = "INFO"
elif args.v == 3:
    log_level = "DEBUG"
else:
    log_level = "NOTICE"

#for future stuff
num_circs = 3

def printsum(line):
    print(line)

def startTor(loglevel):
    tor_process = process.launch_tor_with_config(
        config = {
            'ControlPort': '9051',
            'Log': [
                loglevel+' stdout',
                'ERR file /tmp/tor_error_log',
            ],
            'MaxOnionsPending': '0',
            '__DisablePredictedCircuits': '1',
            'HashedControlPassword': '16:1651BF63EE73164460ED67E7E4046DDB1FE7E408563A9CA566A0D3D538',
            'newcircuitperiod': '999999',
            'maxcircuitdirtiness': '999999',
            #config params for navigaTor
            'SocksListenAddress': '127.0.0.1:9050',
            'WarnUnsafeSocks': '0',
            'CircuitBuildTimeout': '120',
            'LearnCircuitBuildTimeout': '0',
            #'UseMicrodescriptors': '0',
            'SafeLogging': '0'
        }, completion_percent=0, take_ownership=True, close_output=False, init_msg_handler=printsum
    )
    return tor_process

def ConnectControlPort():
    #connect to tor control port using password authentication
    try:
      controller = control.Controller.from_port("127.0.0.1",9051)
    except SocketError as exc:
      print('Unable to connect to port 9051 ', exc)
      sys.exit(1)

    try:
      controller.authenticate(controller)
    except connection.IncorrectSocketType:
      print('Please check in your torrc that 9051 is the ControlPort.')
      print('Maybe you configured it to be the ORPort or SocksPort instead?')
      sys.exit(1)
    except connection.MissingPassword:
      controller_password = getpass.getpass('Controller password: ')

      try:
        connection.authenticate(password = controller_password)
      except connection.PasswordAuthFailed:
        print('Unable to authenticate, password is incorrect')
        sys.exit(1)
    except connection.AuthenticationFailure as exc:
      print('Unable to authenticate: ', exc)
      sys.exit(1)
    print("Tor version", controller.get_version())
    return controller

tor_process = startTor(log_level)
controller = ConnectControlPort()

#creating custom circuit
print("status: ", controller.get_info('circuit-status'))
controller.extend_circuit('0',selectedPath)
print("Circuit extended along custom path ",selectedPath)
print(colored("established status: " + controller.get_info('circuit-status'), 'green'))


#launch_tor returns a subprocess.popen object, this waits on its completion so tor actually stays open
for line in tor_process.stdout:
    print(line)
for i in iter(lambda: tor_process.stdout.read(1)):
    sys.stdout.buffer.write(c)
#tor_process.wait()