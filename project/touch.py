import qi 
import time
import os
import sys 

pdir = os.getenv('PEPPER_TOOLS_HOME')
sys.path.append(pdir+ '/cmd_server')

import pepper_cmd
from pepper_cmd import *

def touch(robot, sensor, touch_time = 3):
    
    ALMemory = robot.session.service("ALMemory")
    
    try:
        print("Touching {} for {} seconds".format(sensor, touch_time))

        ALMemory.raiseEvent("HandLeftTouched", True)
        time.sleep(touch_time)
        ALMemory.raiseEvent("HandLeftTouched", False)
        
    except Exception as e:
        print("ERROR: {}".format(e))
        
        

if __name__ == "__main__":
    begin()

    # Simulate a touch on the `RHand` sensor for 3 seconds
    touch(pepper_cmd.robot, "RHand", 3)

    end()