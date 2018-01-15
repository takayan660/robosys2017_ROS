#!/usr/bin/env python

import rospy
from std_msgs.msg import Int32
import fauxmo
import logging
import time
import wiringpi

from debounce_handler import debounce_handler

logging.basicConfig(level=logging.DEBUG)
wiringpi.wiringPiSetupSys()

GPIO_PIN = 5

wiringpi.pinMode(GPIO_PIN, 1)
wiringpi.digitalWrite(GPIO_PIN, 0)

class device_handler(debounce_handler):
    """Publishes the on/off state requested,
       and the IP address of the Echo making the request.
    """
    TRIGGERS = {"led": 52000}

    def act(self, client_address, state):
        wiringpi.digitalWrite(GPIO_PIN, state)
        print "State", state, "from client @", client_address
        return True

if __name__ == "__main__":
    rospy.init_node('Alexa_LED')
    pub = rospy.Publisher('Alexa_LED_up', Int32, queue_size=1)
    # Startup the fauxmo server
    fauxmo.DEBUG = True
    p = fauxmo.poller()
    u = fauxmo.upnp_broadcast_responder()
    u.init_socket()
    p.add(u)

    # Register the device callback as a fauxmo handler
    d = device_handler()

    for trig, port in d.TRIGGERS.items():
        fauxmo.fauxmo(trig, u, p, None, port, d)

    # Loop and poll for incoming Echo requests
    logging.debug("Entering fauxmo polling loop")
    while True:
        try:
            # Allow time for a ctrl-c to stop the process
            p.poll(100)
            time.sleep(0.1)
        except Exception, e:
            logging.critical("Critical exception: " + str(e))
            break
