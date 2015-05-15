__author__ = 'ehsan'

# Import some POX stuff
from pox.core import core                     # Main POX object
import pox.openflow.libopenflow_01 as of      # OpenFlow 1.0 library
from pox.lib.packet.ethernet import ethernet
import pox.lib.packet as pkt                  # Packet parsing/construction
from pox.lib.addresses import EthAddr, IPAddr # Address types
import pox.lib.util as poxutil                # Various util functions
import pox.lib.revent as revent               # Event library
import pox.lib.recoco as recoco               # Multitasking library


# Create a logger for this component
log = core.getLogger()


class MyModule (object):

    def __init__(self, connection):
        # Keep track of the connection to the switch so that we can
        # send it messages!
        # self.conn = connection
        self.conn = connection

        # This binds our PacketIn event listener and other event
        #connection.addListeners(self)

        # Use this table to keep track of which ethernet address is on
        # which switch port (keys are MACs, values are ports).
        self.mac_to_port = {}

    def resend_packet(self, packet_in, out_port):
        """
        Instructs the switch to resend a packet that it had sent to us.
        "packet_in" is the ofp_packet_in object the switch had sent to the
        controller due to a table-miss.
        """
        msg = of.ofp_packet_out()
        msg.data = packet_in

        # Add an action to send to the specified port
        action = of.ofp_action_output(port = out_port)
        msg.actions.append(action)

        # Send message to switch
        self.conn.send(msg)

    def _handle_PacketIn(self, event):
        """
        Handles packet in messages from the switch.
        """

        packet = event.parsed # This is the parsed packet data.
        if not packet.parsed:
          log.warning("Ignoring incomplete packet")
          return

        packet_in = event.ofp # The actual ofp_packet_in message.

        # Comment out the following line and uncomment the one after
        # when starting the exercise.
        self.act_like_hub(packet, packet_in)
        # self.act_like_switch(packet, packet_in)

    """
     tracks connections and stores references to them itself.  It does this by listening to the ConnectionUp event
     on the OpenFlow nexus.  This event includes a reference to the new connection, which is added to its own set
     of connections.
    """
    def _handle_ConnectionUp(self, event):
        log.info("Connection is recived in handle connection up")
        self.conn.add(event.connection)






################################### End of Class ###################################

def launch(bar=1):
    """
    Starts the component
    """
    def start_switch(event):
        log.debug("Controlling %s" % (event.connection,))
        MyModule(connection=event.connection)
        core.registerNew(MyModule)


    print ("Bar is " + bar)

    #   core.registerNew(MyModule)

    """
    Note that a EhsanObj object is created for each switch that connects. A connection object for that switch is
    passed to the __init__ function
    """
    core.openflow.addListenerByName("ConnectionUp", start_switch)
    #EhsanObj = EhsanComponent()
