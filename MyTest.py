__author__ = 'ehsan'

from pox.core import core                     # Main POX object
import pox.openflow.libopenflow_01 as of      # OpenFlow 1.0 library
import pox.openflow as of

# Create a logger for this component
log = core.getLogger()

class MyTest (object):
    def __init__(self, an_arg):
        self.arg = an_arg
        print "MyComponent instance registered with arg:", self.arg
        core.openflow.addListeners(self)

    def foo(self):
        log.info("MyComponent with "+ self.arg)

    def _handle_ConnectionUp(self, event):
        log.info("Connection is up")


def launch():
    component = MyTest("spam")
    core.register("thing", component)
    core.thing.foo() # prints "MyComponent with arg: spam"