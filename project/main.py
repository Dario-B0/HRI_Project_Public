import os
import time
import sys
import user

pdir = os.getenv('PEPPER_TOOLS_HOME')
sys.path.append(pdir+ '/cmd_server')

import pepper_cmd
from pepper_cmd import *


def hand_touch(value):
    # This callback is called when a touch on the left hand is detected
    # during standing interaction
    print(value)
    if not value:  # When touch is released
        
        ALDialog.gotoTag("still_help" , nurseTopic)
        

def lastInputCallback(lastInput):
    # Redirect all inputs from Dialog channel to ASR channel to create a unique communication channel
    
    tm = int(time.time())  
    ALMemory.raiseEvent('FakeRobot/ASR', lastInput)
    ALMemory.insertData('FakeRobot/ASRevent', lastInput)
    ALMemory.insertData('FakeRobot/ASRtime', tm)
    
    return       


def AnsweredCallback(answer):
    
    global current_user
    
    answer = answer.split()
    
    tag = None

    for i in range(len(answer)):
        if answer[i][0] == "$":
            tag = answer[i][12:]

       
    if tag == "help_agreed":
            # The user asked for help standing up and confirmed it
        
            posture = [0, 0, 0.43, 0, -1.57, -0.23, 1.57, 0.43, 0, 1.57, 0.23, -1.57, 0.98, 0.98, 0, 0, 0]
            robot.setPosture(posture)
            
            # Subscribe to the events that listen for a touch on the hands
            global left_hand_subscriber, Lid_sub, right_hand_subscriber, Rid_sub
            left_hand_subscriber = ALMemory.subscriber("HandLeftTouched")
            Lid_sub = left_hand_subscriber.signal.connect(hand_touch)
            right_hand_subscriber = ALMemory.subscriber("HandRightTouched")
            Rid_sub = right_hand_subscriber.signal.connect(hand_touch)

    elif tag == "still_help_no":
        # The user does not require help standing up anymore 
        
        print("End of the functionality")
        robot.normalPosture()
        
        # Unsubscribe from the touch events
        left_hand_subscriber.signal.disconnect(Lid_sub)
        right_hand_subscriber.signal.disconnect(Rid_sub)
        


    elif tag == "tablet_schedule":
        # The user asked their schedule; start the tablet interaction
        
        print("\nStart tablet interaction\n")
        ALDialog.deactivateTopic(welcomeTopic)
        n_interaction = 0
        os.system("python tablet_modim/scripts/interactions.py --interaction {}".format(n_interaction))  
        
        ALDialog.activateTopic(welcomeTopic)    
        print("\nEnd tablet interaction\n")
        
    elif tag == "start_stressMan_session" :
        # The user confirmed to start the stress management session; start the tablet interaction
        
        ALDialog.deactivateTopic(welcomeTopic)  
        
        print("\nStart stress management interaction\n")
        n_interaction = 2
        os.system("python tablet_modim/scripts/interactions.py --interaction {}".format(n_interaction)) 
        current_user.stress_session = ALMemory.getData("userSession")
        #if not(robot.memget("userID") == 0 or robot.memget("userID") is None):
        if not(robot.memget("userID") == 0 ): # not guest user
            user.update_user(current_user)
        printUserData()
        ALDialog.activateTopic(welcomeTopic) 
        

        
    elif tag == "user_name":
        # User has declared their full name
        
        first_name = ALMemory.getData("firstName")
        last_name = ALMemory.getData("lastName")
        
        u = user.get_user_by_fullname(first_name, last_name)
        if u is None:
            # User not present in the database; ask for registration
            
            current_user.first_name = first_name
            current_user.last_name = last_name
            saveCurrentUser()
            
            ALDialog.gotoTag("user_registration" ,startTopic)
            
        else:
            # User in the database; load their data
            
            current_user = u
            saveCurrentUser()
            printUserData()
            ALDialog.activateTopic(welcomeTopic) 
            ALDialog.gotoTag("init_welcome" ,welcomeTopic)

            
            
    elif tag == "confirmed":
        # User has registered and agreed to save their data in the database
        
        id = user.get_next_id()
        first_name = ALMemory.getData("firstName")
        last_name = ALMemory.getData("lastName")
        age = ALMemory.getData("userAge")
        
        schedule = []
        schedule = user.random_schedule() # For simularion porpouses set a list of random elements in the schedule
        
        current_user = user.User(id, first_name, last_name, age, schedule=schedule)
        
        saveCurrentUser()
        user.add_user(current_user)
        
        print("ADDED NEW USER TO DATABSE")
        printUserData()
        
        ALDialog.deactivateTopic(startTopic)
        ALDialog.activateTopic(welcomeTopic)
        ALDialog.gotoTag("init_welcome" ,welcomeTopic)
        
    elif tag == "refuseRegistration":
        # The user refused to save their data on the database and thus continue as a guest user
        
        ALDialog.deactivateTopic(startTopic)
        ALDialog.activateTopic(welcomeTopic)
        ALDialog.gotoTag("init_welcome" ,welcomeTopic)
        
    elif tag == "startRiddle":
        # Start the riddle interaction on the tablet
        
        ALDialog.deactivateTopic(welcomeTopic)  
        
        print("\nStart riddle interaction\n")
        n_interaction = 1
        os.system("python tablet_modim/scripts/interactions.py --interaction {}".format(n_interaction)) 
        print("END RIDDLE")
        ALDialog.activateTopic(welcomeTopic)  
        
        
        
def getUserId():
    if current_user is None:
        return 0
    return ALMemory.getData("userID")
        

def saveCurrentUser():
    # id, first_name, last_name, age, language="eng", schedule=[], session = {}
    ALMemory.insertData("userID", current_user.id)
    ALMemory.insertData("userFirstName", current_user.first_name)
    ALMemory.insertData("userLastName", current_user.last_name)
    ALMemory.insertData("userAge", current_user.age)
    ALMemory.insertData("userLanguage", current_user.language)
    ALMemory.insertData("userSchedule", current_user.schedule)
    ALMemory.insertData("userSession", current_user.stress_session)
    
    return            

def printUserData():
    
    u = user.User(ALMemory.getData("userID"),
                  ALMemory.getData("userFirstName"),
                  ALMemory.getData("userLastName"),
                  ALMemory.getData("userAge"),
                  ALMemory.getData("userLanguage"),
                  ALMemory.getData("userSchedule"),
                  ALMemory.getData("userSession")
                  )  
    print(u)  
    return    

        
if __name__ == "__main__":

    begin()
    
    robot = pepper_cmd.robot
    session = robot.session
    
    current_user = user.User(0, "", "", 0)
    
    ALDialog = session.service("ALDialog")
    ALMemory = session.service("ALMemory")
    ALTouch = session.service("ALTouch")
    
    ALMemory.insertData("userID", 0)  # Default guest user id
    
    # Initialize the database the first time
    if not os.path.isfile("/home/robot/playground/project/users.db"):
        user.init_db()
    
    ALDialog.setLanguage("English")
    welcomeTopic = ALDialog.loadTopic("/home/robot/playground/project/dialog_topics/welcoming_topic.top")
    nurseTopic = ALDialog.loadTopic("/home/robot/playground/project/dialog_topics/nursing_topic.top")
    startTopic = ALDialog.loadTopic("/home/robot/playground/project/dialog_topics/start_topic.top") 
    
    ALDialog.activateTopic(startTopic)
    ALDialog.activateTopic(nurseTopic)
    
    answered = ALMemory.subscriber("Dialog/Answered")
    answered.signal.connect(AnsweredCallback)
    
    lastInput = ALMemory.subscriber("Dialog/LastInput")
    lastInput.signal.connect(lastInputCallback)
    
    ALDialog.gotoTag("start" , startTopic)
    
    user.init_db()
    
    try:
        raw_input("Pepper interaction program initialized; press ENTER to end the program\n")
    finally:
        
        ALDialog.deactivateTopic(welcomeTopic)
        ALDialog.deactivateTopic(nurseTopic)  
              
        ALDialog.unloadTopic(welcomeTopic)
        ALDialog.unloadTopic(nurseTopic)
        ALDialog.unloadTopic(startTopic)
        
    
    end()

