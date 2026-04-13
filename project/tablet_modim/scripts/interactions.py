# -*- coding: utf-8 -*-

import sys
import time
import os
import argparse
import math

# os.environ['MODIM_HOME'] = '/src/modim' # set the env. variable MODIM_HOME to the folder of modim
# print(os.getenv('MODIM_HOME'))
try:
    sys.path.insert(0, os.getenv('MODIM_HOME')+'/src/GUI')
except Exception as e:
    print("Please set MODIM_HOME environment variable to MODIM folder.")
    sys.exit(1)

# Set MODIM_IP to connnect to remote MODIM server

import ws_client
from ws_client import *


try:
    sys.path.insert(1, '/home/robot/playground/project')
except Exception as e:
    print("Please set HOME environment variable to plaground folder.")
    sys.exit(1)

    
def riddle_interaction():
    
    # Present a riddle to the user who has to try to guess the correct answer
    
    im.init()
    
    riddle = True       
    
    while riddle:
        answer = im.ask(actionname='riddle', timeout=60)
        
        if answer == 'correct':
            im.execute('correct')
            riddle = False
            time.sleep(2)
            
        
        elif answer == 'timeout':
            im.executeModality('TTS', 'TIMESUP: you will get it next time!')
            riddle = False
            time.sleep(2)
            
        else:
            im.execute('wrong')
            time.sleep(2)
            
    
    im.executeModality('TTS', 'That\'s all!')
    im.execute('queryHelp')
    time.sleep(2)
    im.init()    
        

def stress_interaction():    
    
    robot = im.robot

    # to be sure we are in StandInit position
    robot.normalPosture()
    
    ## The expected behaviour is that the robot change the volume based on the current time; this is not possible in simulation
    # current_hour = time.localtime().tm_hour
    # if current_hour > 21:
    #     robot.setVolume(20)
    # else :
    #     robot.setVolume(80)
    
    # Auxiliary to interact with the webpage script
    im.execute("blueScreen") 


    session = robot.memget("userSession")
    
    n_session = int(session[0][1])
    last_session = session[6][1]
    n_cycles = int(session[1][1])
    preferred_pace = int(session[3][1])
    preference_speed = int(session[4][1])
    take_hand = int(session[5][1])

    # First session
    if n_session == 0:
        im.executeModality("TTS", "This is your first session, i will help you throughout the whole experience")
        
    else:
        # If last session went well
        if last_session:
                        
            im.executeModality("TTS", "I'm sure it will be useful to you again this time. We will do together {} cycles.".format(n_cycles))
            
            if preferred_pace > 2 and preference_speed > 2:
                im.executeModality("TTS", "I will go to a faster pace")
            
            else :
                im.executeModality("TTS", "I will go to a slower pace")
        
        # If last session was not as good      
        else:
            im.executeModality("TTS", "I’m sorry last time didn’t go as well. Let's try again this time ")
        
    ## The expected behaviour is that the robot change the talk speed to the usere preference; however this is not possible in simulation
    # tts_service = robot.session.service("ALTextToSpeech")
    # tts_service.setParameter("speed", preference_speed*100)
         
    # --- anchor  gesture ------------------------------------
    robot.speed_fraction = 0.05  #manage velocity
    pose = robot.getPosture()

    pose[2]  = 0.6   
    pose[7]  = 0.6       # ShoulderPitch
    pose[3]  = 0.1   
    pose[8]  = -0.1      # ShoulderRoll
    pose[4]  = -3.0  
    pose[9]  = 3.0       # ElbowYaw  
    pose[5]  = -1.35 
    pose[10] =  1.35     # ElbowRoll
    pose[6]  = -1.57 
    pose[11] = 1.57      # WristYaw 
    pose[12] = 0.20  
    pose[13] = 0.20      # Hands
    robot.setPosture(pose)  #apply
    
    time.sleep(2)                           # hold 2 s
    robot.normalPosture() # return 
    
    if take_hand != 3:
        
        # im.executeModality("TTS", "Would you like to hold my hand during the exercise?")
        # im.executeModality("ASR", ["yes", "no"])
        ans = im.ask(actionname="askHoldHand", timeout=15)
        if ans == "yes":
            
            take_hand = 0
            im.executeModality("TTS", "Hold my hand")
            # --- take the hand -------------------------
            robot.speed_fraction = 0.05
            pose = robot.getPosture()
            pose[5]  = -math.pi/2; pose[10] =  math.pi/2   # elbows 90°
            #pose[7]  = pose[13] = 1.0            
            robot.setPosture(pose)
        else:
            take_hand = take_hand + 1
            im.executeModality("TTS", "No need to hold my hand")
         
    im.execute("blueScreen")             
    pausa = 5 / (preferred_pace + 0.001) 
    
    repeat = True

    # Slow and fluid movement for the breathing cycle
    robot.speed_fraction = 0.05          
    pose = robot.getPosture()
    change= False # we will use this variable at the end to see if the user has made any changes
    while repeat:
        
        im.executeModality("TEXT_default", "cycles_show_0_{}".format(n_cycles))
        
        im.executeModality("TTS", "Let's make an effort to feel how our breath acts in the body, what sensations it gives us; let's imagine and perceive fresh air entering through the nostrils or mouth and then coming out warmer.")
        time.sleep(pausa) 
        im.executeModality("TTS", "We concentrate on the movements that the body generates during breathing, and we make a slight effort, but without persisting, to breathe into the belly, we begin to feel the breath with the movement of the navel rising and falling, together with the abdomen and chest")
        time.sleep(pausa/2) 
            
        im.executeModality("TTS", "If any thoughts or emotions arise, simply notice them and gently bring your focus back to your breath. Let’s breathe in together for five seconds")
        im.executeModality("TEXT_default", "BREATHE IN")
        #INSPIRE (head up, torso slightly back)
        pose[1]  = -0.60
        pose[15] = -0.20
        robot.setPosture(pose)
        time.sleep(5)
        
        im.executeModality("TEXT_default", "BREATHE OUT")
        im.executeModality("TTS", "Now, let’s exhale slowly")
        # Exhale (head slightly down, torso upright)
        pose[1]  =  0.30
        pose[15] =  0.00
        robot.setPosture(pose)
        time.sleep(5)
        # back neutral
        pose[1] = 0.0
        robot.setPosture(pose)

        
        for i in range(n_cycles-1):
            im.executeModality("TEXT_default", "cycles_show_{}_{}".format(i+1,n_cycles))
            im.executeModality("TTS", "If any thoughts or emotions arise, simply notice them and gently bring your focus back to your breath. Let’s breathe in together again for five seconds")
            im.executeModality("TEXT_default", "BREATHE IN")
            #inhale
            pose[1]  = -0.60
            pose[15] = -0.20
            robot.setPosture(pose)
            time.sleep(5)

            im.executeModality("TEXT_default", "BREATHE OUT")            
            im.executeModality("TTS", "Now, let’s exhale slowly")
            #exhale
            pose[1]  =  0.30
            pose[15] =  0.00
            robot.setPosture(pose)
            time.sleep(5)
            #return neutral
            pose[1] = 0.0
            robot.setPosture(pose)
            time.sleep(5)
            
        im.executeModality("TEXT_default", "cycles_show_{}_{}".format(n_cycles,n_cycles))
        im.executeModality("TTS", "We’ve completed our breathing exercises. I hope you feel a little calmer now.")
        time.sleep(pausa)
        
        
        im.executeModality("TEXT_default", "cycles_hide")
        
        n_session += 1

        # No need for the hand anymore
        robot.normalPosture()
        
        ans = im.ask("askFeedback", timeout = 60)
        
        if ans == "yes":
            
            ans = im.ask("feedbackSession", timeout = 60)
            
            if ans == "notreally" or ans == "notatall":
                last_session = False
                im.executeModality("TTS", "I'm sorry I couldn't satisfy you fully, maybe by making some changes to the exercise, I'm sure it will go better next time,especially with the new modifications")
                #Pepper moves to express sadness
                pose = robot.getPosture()
                pose[1] = 0.40            # HeadPitch downward ≈ 23 °
                robot.setPosture(pose)
                time.sleep(2)                           # hold 2s
                robot.normalPosture()
                
            elif ans == "helpfull" or ans == "somewhat":
                last_session = True
                im.executeModality("TTS", "I am very happy to have been helpful")      
                #Pepper moves to express happiness
                robot.speed_fraction = 0.08
                pose = robot.getPosture()
                pose[2] = 0.10
                pose[7] = 0.10
                pose[5] = -math.pi/2
                pose[10] = math.pi/2
                robot.setPosture(pose)
                # ---------- torso swing ----------
                robot.speed_fraction = 1          # vel max
                pose = robot.getPosture()

                AMP   = 0.2        # ±0.25 rad ≈ 14°
                CYCLES = 1         # how many complete oscillations

                for _ in range(CYCLES):
                    # # sx
                    pose[14] =  AMP
                    robot.setPosture(pose)

                    # dx
                    pose[14] = -AMP
                    robot.setPosture(pose)
                    
                
                
                # for _ in range(CYCLES):
                    # # sx
                    # robot.session.service("ALMotion").setAngles(["HipRoll"], AMP, 0.5)
                    # time.sleep(0.6)

                    # dx
                    # robot.session.service("ALMotion").setAngles(["HipRoll"], -AMP, 0.5)
                    # time.sleep(0.6)
                    
                    
                # robot.session.service("ALMotion").setAngles(["HipRoll"], 0., 0.5)
                # time.sleep(0.7)

                # straighten up
                pose[14] = 0.0
                robot.setPosture(pose)

                robot.normalPosture()
                
            ans = im.ask("feedbackCycles", timeout = 60)
            
            # increse/decrease by 5 each time
            if ans == "increase":
                    n_cycles = n_cycles + 5
                    im.executeModality("TTS", "Great! Next time we will do {} cycles".format(n_cycles))
                    change = True 
                
            elif ans == "decrease":
                if n_cycles > 6:
                    n_cycles = n_cycles - 5 
                    im.executeModality("TTS", "Great! Next time we will do {} cycles".format(n_cycles))
                    change = True 
                    
            ans = im.ask("feedbackSpeed", timeout = 60)
            
            if ans == "faster":
                if preference_speed < 4:
                    preference_speed = preference_speed + 1  # this correpond to an increment 100
                    preferred_pace = preferred_pace + 1
                    im.executeModality("TTS", "Ok! Next time I will talk faster.")
                    change = True 
                    ## The expected behaviour is that the robot change the talk speed to the usere preference; however this is not possible in simulation
                    # tts_service = robot.session.service("ALTextToSpeech")
                    # tts_service.setParameter("speed", preference_speed*100)
                            
            elif ans == "slower":
                if preference_speed > 1:
                    preference_speed = preference_speed - 1  # this correpond to an increment 100
                    preferred_pace = preferred_pace - 1
                    im.executeModality("TTS", "Ok! Next time I will talk slower.") 
                    change = True 
                    ## The expected behaviour is that the robot change the talk speed to the usere preference; however this is not possible in simulation
                    # tts_service = robot.session.service("ALTextToSpeech")
                    # tts_service.setParameter("speed", preference_speed*100)
                    
        
            
        ans = im.ask("askEndStress", timeout = 60)
        if ans == "repeat":
            im.executeModality("TTS", "Ok, let's start again")
            time.sleep(pausa)
            
            
        elif ans == "call":
            repeat = False
            im.executeModality("TTS", "I’m calling a nurse now to ensure you’re well taken care of.")
            ### CALL NURSE
            
        else:
            repeat = False
            if change == True: # a change has been made
                im.executeModality("TTS", "I'm sure it will go better next time, expecially with the new modifications")
                change= False
            else:
                im.executeModality("TTS", "I hope this exercise was useful and that you are feeling better")
   
    im.init()
    
    session[0][1] = n_session
    session[6][1] = last_session
    session[1][1] = n_cycles
    session[3][1] = preferred_pace
    session[4][1] = preference_speed
    session[5][1] = take_hand
    robot.memset("userSession", session)
    
     


def schedule_interaction():
    
    # Display the schedule of the user. Make they choose the type of schedule to display between daily, weekly and complete.
    
    im.init()
    robot.normalPosture()
    
    if robot.memget("userID") == 0: 
        im.executeModality("TTS","You are currently a guest user, so the schedule may not be updated")
        
    schedule = im.robot.memget("userSchedule")
    for i in range(len(schedule)):
        for j in range(1,len(schedule[0])):
            schedule[i][j] = int(schedule[i][j])
            
    schedule = sorted(schedule, key=lambda e: (e[1], e[2], e[3], e[4], e[5]))
    
    answer = im.ask(actionname='askSchedule', timeout = 60)
                
    if answer == "daily":
        im.executeModality("TEXT_default","schedule_daily_{}".format(schedule))
        answer = im.ask(actionname='dailySchedule', timeout = 120)
                    

    elif answer == 'weekly':
        im.executeModality("TEXT_default","schedule_weekly_{}".format(schedule))
        answer = im.ask(actionname='weeklySchedule', timeout = 120)
        
    elif answer == 'complete':
        im.executeModality("TEXT_default","schedule_complete_{}".format(schedule))
        answer = im.ask(actionname='completeSchedule', timeout = 120)

    
    im.executeModality("TEXT_default","schedule_reset")
    im.execute('queryHelp')
    
    time.sleep(2)
    im.init()
          


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    
    parser.add_argument("--interaction", type=int, default=0,
                        help="The number associated to the interaction.")
    
    args = parser.parse_args()
    intN = args.interaction
        
    mws = ModimWSClient()

    # local execution
    mws.setDemoPathAuto(__file__)
    
    # Select one of the three interactions
    if intN == 0:
        mws.run_interaction(schedule_interaction)
        
    elif intN == 1: 
        mws.run_interaction(riddle_interaction)
        
    elif intN ==2:
        mws.run_interaction(stress_interaction)
        
