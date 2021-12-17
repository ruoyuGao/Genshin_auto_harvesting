import random
#import environment
import keyboard
import winsound
import typing
import pyautogui
import time
from environment import Environment


def main():
    env=Environment()
    action_list=["env.go_straight","env.go_back","env.go_left","env.go_right","env.see_around"]
    time=0.5
    winsound.Beep(500, 500)
    keyboard.wait('r')
    for i in range (0,20):
        r_number=random.randint(0,4)
        action=[r_number,time]
        # do action here ,action{action type(int),action time(int)}
        eval(action_list[action[0]])(action[1])
        env.harvesting()
        if i%10 == 0:
            reset_test()
    #get_position()
    #get_human_action()
    #sim_genshin_action(env,action_list,time)
    # for i in range (0,100):
    #     env.see_around(time)

def get_position():
    """get mouse coordinate in real time"""
    print('mouse coordinate now: ')
    try:
        while 1:
            x, y = pyautogui.position()
            print_position = f'X: {str(x).rjust(5)}, Y: {str(y).rjust(5)}'
            print(f"\r{print_position}", end='', flush=True)
    except KeyboardInterrupt:
        print('\n')

def reset_test():
    pyautogui.press('esc')
    time.sleep(0.3)
    pyautogui.click(x=664,y=600)
    pyautogui.press('m')
    # temperate position of map menu (need to check)
    time.sleep(0.5)
    pyautogui.click(x=960,y=540)
    time.sleep(0.5)
    # choose an seven heaven statue
    pyautogui.click(x=1675,y=1022)
    time.sleep(0.5)
    pyautogui.keyDown('w')
    time.sleep(3)
    pyautogui.keyUp('w')

def get_human_action():
    keyboard.start_recording()
    time.sleep(30)
    events = keyboard.stop_recording()
    keyboard.replay(events)

def sim_genshin_action(env,action_list,time):
    while True:
        if keyboard.is_pressed('8'):
            print('Forward')
            eval(action_list[0])(time)
        elif keyboard.is_pressed('2'):
            print('Backward')
            eval(action_list[1])(time)
        elif keyboard.is_pressed('4'):
            print('Left')
            eval(action_list[2])(time)
        elif keyboard.is_pressed('6'):
            print('Right')
            eval(action_list[3])(time)
        elif keyboard.is_pressed('0'):  # if key 'enter' is pressed 
            print('You pressed see around!')
            eval(action_list[4])(time)
        elif keyboard.is_pressed('q'):
            print('Quit!')
            break
    
if __name__ == '__main__':
    print("\nwaiting test")
    #main()
    get_position()
