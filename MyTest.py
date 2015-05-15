__author__ = 'ehsan'

from pox.core import core                     # Main POX object
from pox.lib.util import dpid_to_str
import pox.openflow.libopenflow_01 as of      # OpenFlow 1.0 library
import time
#import pox.openflow as of

# Create a logger for this component
log = core.getLogger()

class MyTest (object):
    def __init__(self, an_arg):
        self.arg = an_arg
        self.macToPort = {}
        print "MyComponent instance registered with arg:", self.arg
        core.openflow.addListeners(self)

    def foo(self):
        log.info("MyTest with  " + self.arg)

    """
    The object event has three properties:
        .connection - A reference to the switch connection that caused the event
        .dpid - The DPID of the switch that caused the event
        .ofp - The openflow message tha caused the event to fire up (from libopenflow)
            Note that libopenflow_01 is the place where you have all types of OF messages.

    So right now a reference to the switch is copied to the object.
    """
    def _handle_ConnectionUp(self, event):
        log.info("Event DPID (i.e. DPID of the switch) : {0}\n".format(event.dpid) +
                 "Number of tables in the Switch : {0}\n".format(event.ofp.n_tables) +
                 "Number of buffers in the switch : {0}\n".format(event.ofp.n_buffers))

        m = "Ports of switches: \n"
        for p in event.ofp.ports:
            m += "\t Port Name: {0}\n".format(p) + "\t\t Port Number = {0}\n".format(p.port_no) + \
                 "\t\t Hardware Address = {0}\n".format(p.hw_addr) + \
                 "\t\t Name = {0}\n".format(p.name) + \
                 "\t\t Configuration = {0}\n".format(p.config) + \
                 "\t\t State = {0}\n".format(p.state) + \
                 "\t\t Curr = {0}\n".format(p.curr) + \
                 "\t\t Advertised = {0}\n".format(p.advertised) + \
                 "\t\t Supported = {0}\n".format(p.supported) + \
                 "\t\t Peer = {0}\n".format(p.peer)
        log.info(m)
        self.conn = event.connection

    def flood(self, event, message = None):
        """ Floods the packet """
        msg = of.ofp_packet_out()
        if time.time() - self.conn.connect_time >= _flood_delay:
            # Only flood if we've been connected for a little while...

            if message is not None:
                log.debug(message)
                #log.debug("%i: flood %s -> %s", event.dpid,packet.src,packet.dst)
                # OFPP_FLOOD is optional; on some switches you may need to change
                # this to OFPP_ALL.
            msg.actions.append(of.ofp_action_output(port=of.OFPP_FLOOD))
        else:
            pass

        msg.data = event.ofp
        msg.in_port = event.port
        self.conn.send(msg)

    """
    :type event: event
    :param event: Event that cause al these functions to execute
    :type packet: event.parsed
    :param packet: This is parsed packet
    """
    def drop(self, event, packet, duration=None):
        """
        Drops this packet and optionally installs a flow to continue
        dropping similar ones for a while
        """
        if duration is not None:
            if not isinstance(duration, tuple):
              duration = (duration,duration)
            msg = of.ofp_flow_mod()
            msg.match = of.ofp_match.from_packet(packet)
            msg.idle_timeout = duration[0]
            msg.hard_timeout = duration[1]
            msg.buffer_id = event.ofp.buffer_id
            self.conn.send(msg)
        elif event.ofp.buffer_id is not None:
            msg = of.ofp_packet_out()
            msg.buffer_id = event.ofp.buffer_id
            msg.in_port = event.port
            self.conn.send(msg)

    """
    :type event:event
    :param event: The PacketIn event which caused _handle_PacketIn to be executed.
    """
    def _handle_PacketIn(self, event):
        """
        Handles packet in messages from the switch.
        """
        log.info("Packet in was received. Processing the packet ...")

        packet = event.parsed  # This is the parsed packet data.
        if not packet.parsed:
            log.warning("Ignoring incomplete packet")
            return

        """ Use source address and switch port to update address/port table """
        log.info("\tSource of the packet -> {0}\n\t\tDestination of the packet -> {1}".format(packet.src, packet.dst))
        self.macToPort[packet.src] = event.port

        """
        If Ethertype is LLDP or the packet's destination address is a Bridge Filtered address?
            Yes:
                Drop packet -- don't forward link-local traffic (LLDP, 802.1x)

        Note that EtherType is a two-octet field in an Ethernet frame. It is used to indicate which protocol is
            encapsulated in the payload of an Ethernet Frame.
        """
        if packet.type == packet.LLDP_TYPE or packet.dst.isBridgeFiltered():
            log.info("\tPacket type is {0}. Drop the packet.".format(str(packet.type)))
            # drop() --> Note that this function is not implemented
            self.drop(event=event, packet=packet)
            return

        """ Is destination multicast?
            Yes:
                Flood the packet
        """
        if packet.dst.is_multicast:
            log.info("\tPacket is multicast. Doing nothing for now.")
            # flood()
            self.flood(event=event)
        else:
            """
            Port for destination address in our address/port table?
                No:
                    Flood the packet
            """
            if packet.dst not in self.macToPort:
                log.info("\tPort for {0} is unknown so flood he packet. ".format(packet.dst))
                self.flood(event=event, message="Port for %s unknown -- flooding " % (packet.dst, ))
            else:
                """
                Is output port the same as input port?
                    Yes:
                        Drop packet and similar ones for a while
                """
                port = self.macToPort[packet.dst]
                if port == event.port:
                    log.warning("\tSame port for packet from {0} -> {1} on {2}.{3}. Drop the packet. Not "
                                "implemented".format(packet.src, packet.dst, dpid_to_str(event.dpid), port))
                    # drop(10) --> Note that this function is not implemented
                    return

                port = self.macToPort[packet.dst]
                # TODO: Fix these strings
                log.info("\tInstalling a flow : "
                         "Setting port to {0}".format(port))
                flow_msg = of.ofp_flow_mod()
                flow_msg.match = of.ofp_match.from_packet(packet=packet, in_port=event.port)
                flow_msg.idle_timeout = 20
                flow_msg.hard_timeout = 40
                # TODO: Try to add a single flow
                flow_msg.actions.append(of.ofp_action_output(port=port))
                flow_msg.data = event.ofp
                self.conn.send(flow_msg)

    def _handle_PacketOut (self, event):
        log.info("Packet out was received")


def launch():
    global _flood_delay
    _flood_delay = 0
    component = MyTest("spam")
    core.register("thing", component)
    core.thing.foo() # prints "MyComponent with arg: spam"