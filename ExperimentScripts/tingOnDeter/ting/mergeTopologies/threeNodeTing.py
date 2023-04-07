from mergexp import *

net = Network('ThreeNode')

#using debian bullseye, as Deterlab's FreeBSD caused some issues, particularly with package dependencies
client = net.node('CLIENT', image == "bullseye")
w = net.node('W', image == "bullseye")
z = net.node('Z', image == "bullseye")

#interconnect all three nodes
link = net.connect(['CLIENT','W','Z'])

#set IP addresses - not sure if this is required, but the example did it...
link['CLIENT'].socket.addrs = ip4('10.0.0.1/24')
link['W'].socket.addrs = ip4('10.0.0.2/24')
link['Z'].socket.addrs = ip4('10.0.0.3/24')

#execute topology
experiment(net)
