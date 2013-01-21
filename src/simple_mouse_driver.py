#!/usr/bin/env python
#import roslib; roslib.load_manifest('mouse_driver')
import rospy
import evdev

from mouse_driver.msg import mouse_event

class Mouse_to_ptz_driver:
    '''Driver only publishes motion, wheel scrolling, left, middle and right 
    clicks'''
    def __init__(self):
        self.initialise_variables()
        self.initialise_ros_variables()
    
    def initialise_variables(self):
        '''This method requires one of the devices /dev/input/event* to be a 
        mouse'''
        try:
            self.find_mouse_device()
        except:
            rospy.logerr('Could not open input device.  ' + \
                   + 'Make sure file representing the mouse (eg. ' + \
                   + '/dev/input/event2) is readable.')
    
    def find_mouse_device(self):
        '''Checks in /dev/input/event* for a device with capabilities that
        include evdev.ecodes.EV_REL.  We will call any type of device that has
        EV_REL as a capability a mouse'''
        device_list = evdev.list_devices()
        for device in device_list:
            input_device = evdev.InputDevice(device)
            caps = input_device.capabilities()
            if (evdev.ecodes.EV_REL in caps.keys()):
                values = caps[evdev.ecodes.EV_REL]
                if (evdev.ecodes.REL_X in values) and \
                        (evdev.ecodes.REL_Y in values) and \
                        (evdev.ecodes.REL_WHEEL in values):
                    self.mouse_device_file = device # eg "/dev/input/event2"
                    rospy.logwarn('%s appears to be a mouse.' % \
                            self.mouse_device_file)
                    self.mouse_events = evdev.InputDevice(self.mouse_device_file)
                    return # if there are multiple mice then we use the first one
        rospy.logwarn('It looks like there are no readable mouse devices' + \
                                    + ' in /dev/input/event*')

    def initialise_ros_variables(self):
        '''Set up topic called mouse_event and initialise mouse_to_ptz_driver 
        node'''
        self.pub = rospy.Publisher('mouse_event', mouse_event)
        rospy.init_node('mouse_to_ptz_driver', anonymous=False)
        self.msg_default = mouse_event() # instantiate a default ros_message
        
    def start(self):
        while not rospy.is_shutdown():
            self.watch_for_mouse_events_and_publish()

    def watch_for_mouse_events_and_publish(self):
        '''infinite loop to monitor and publish mouse events'''
        for event in self.mouse_events.read_loop(): # infinite loop
            if (event.type==evdev.ecodes.EV_REL) or \
                    (event.type==evdev.ecodes.EV_KEY):
                self.handle_mouse_event(event)
                #rospy.sleep(0.04)

    def handle_mouse_event(self, event):
        msg = mouse_event() # instantiate ros message
        if (event.type==evdev.ecodes.EV_REL): # if mouse motion
            if event.code==evdev.ecodes.REL_X:
                msg.right_displacement = event.value
            elif event.code==evdev.ecodes.REL_Y:
                msg.down_displacement = event.value
            elif event.code==evdev.ecodes.REL_WHEEL:
                msg.wheel_up_displacement = event.value
        elif (event.type==evdev.ecodes.EV_KEY): # if button clicked
            if event.code==evdev.ecodes.BTN_MOUSE:
                msg.left_click = True
            elif (event.code==evdev.ecodes.BTN_RIGHT):
                msg.right_click = True
            elif (event.code==evdev.ecodes.BTN_MIDDLE):
                msg.middle_click = True
        if (msg!=self.msg_default): # only publish non-default message
            self.pub.publish(msg)

def main():
    try:
        mouse_to_ptz_driver = Mouse_to_ptz_driver()
        mouse_to_ptz_driver.start()
    except rospy.ROSInterruptException:
        pass

if __name__=='__main__':
    main()
