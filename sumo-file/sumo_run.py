#!/usr/bin/python

"""Sample file for SUMO

***Requirements***:

Kernel version: 5.8+ (due to the 802.11p support)
sumo 1.5.0 or higher
sumo-gui"""

from mininet.log import setLogLevel, info
from mn_wifi.cli import CLI
from mn_wifi.net import Mininet_wifi
from mn_wifi.sumo.runner import sumo
from mn_wifi.link import wmediumd, ITSLink
from mn_wifi.wmediumdConnector import interference


def topology():

    "Create a network."
    net = Mininet_wifi(link=wmediumd, wmediumd_mode=interference)

    info("*** Creating nodes\n")
    for id in range(0, 5):
        net.addCar('car%s' % (id+1), wlans=2, encrypt=['wpa2', ''])

    kwargs = {'ssid': 'vanet-ssid', 'mode': 'g', 'passwd': '123456789a',
              'encrypt': 'wpa2', 'failMode': 'standalone', 'datapath': 'user'}
    e1 = net.addAccessPoint('Tower1', mac='00:00:00:11:00:01', channel='1',
                            position='2600,3500,0', **kwargs)
    e2 = net.addAccessPoint('Tower2', mac='00:00:00:11:00:02', channel='6',
                            position='2800,3250,0', **kwargs)

    info("*** Configuring Propagation Model\n")
    net.setPropagationModel(model="logDistance", exp=2.8)

    info("*** Configuring wifi nodes\n")
    net.configureWifiNodes()

    net.addLink(e1, e2)
    for car in net.cars:
        net.addLink(car, intf=car.wintfs[1].name,
                    cls=ITSLink, band=20, channel=181)

    # exec_order: Tells TraCI to give the current
    # client the given position in the execution order.
    # We may have to change it from 0 to 1 if we want to
    # load/reload the current simulation from a 2nd client
    net.useExternalProgram(program=sumo, port=8813,
                           config_file='polban1.sumo', 				
                           extra_params=["--start --delay 300"],
                           clients=1, exec_order=0)

    info("*** Starting network\n")
    net.build()

    for enb in net.aps:
        enb.start([])

    for id, car in enumerate(net.cars):
        car.setIP('192.168.0.{}/24'.format(id+1),
                  intf='{}'.format(car.wintfs[0].name))
        car.setIP('192.168.1.{}/24'.format(id+1),
                  intf='{}'.format(car.wintfs[1].name))

    # Track the position of the nodes
    nodes = net.cars + net.aps
    net.telemetry(nodes=nodes, data_type='position',
                  min_x=2200, min_y=2800,
                  max_x=3200, max_y=3900)

    info("*** Running CLI\n")
    CLI(net)

    info("*** Stopping network\n")
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    topology()
