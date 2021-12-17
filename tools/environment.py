#from _typeshed import Self
import numpy as np
import cv2
import pyautogui
import time
from copy import deepcopy
from collections import Counter
import traceback
import os

import torch

from yolox2dqn import Predictor
import utils
#import utils

class ItemCheck:
    def __init__(self) -> None:
        self.item_list={'sweet flower':0, 'mint':1}
    

class Environment:
    def __init__(self,predictor=None) -> None:
        self.predictor=predictor
        self.state=None
        self.reward=0
        self.done=False
        self.time=0
        self.total_time=500
    
    def distance(self):
        player_pos,item_pos=self.state
        if item_pos == 0:
            return 0
        return 1/abs(player_pos.int()-item_pos.int())

    def get_state(self):
        while True:
            while True:
                outputs = self.predictor.image_det(utils.cap())
                if outputs is None:
                    self.go_straight(0.2)
                else: break
            #print(outputs)
            #outputs=self.predictor.image_det(utils.cap())
            #here the output in outputs is  {class name, score, [x1,y1,x2,y2]}
            item_info_list=[]
            player_info=[]
            for output in outputs:
                if output[0]=='player':
                    player_info=output
                else:
                    item_info_list.append(output)
            if not player_info:
                self.go_straight(0.2)
                print("player lost")
            else:
                break
        self.state=(player_info,item_info_list)
        self.state=self.shape_state()
        return self.state
    
    def reset(self):
        #open the menu and select the map menu
        pyautogui.press('m')
        time.sleep(0.5)
        # temperate position of map menu (need to check)
        pyautogui.click(x=960,y=540)
        time.sleep(0.5)
        # choose an seven heaven statue
        pyautogui.click(x=1705,y=1036)
        time.sleep(2)
        self.state=self.get_state()
        self.reward=0
        self.time=0
        self.done=False

        return self.state
    
    def get_reward(self):
        min_distance=self.distance()
        if min_distance ==0:
            return 0
        return 1/min_distance

    def go_straight(self,time1):
        pyautogui.keyDown('w')
        time.sleep(time1)
        pyautogui.keyUp('w')
    
    def go_back(self,time1):
        pyautogui.keyDown('s')
        time.sleep(time1)
        pyautogui.keyUp('s')
    
    def go_left(self,time1):
        pyautogui.keyDown('a')
        time.sleep(time1)
        pyautogui.keyUp('a')

    def go_right(self,time1):
        pyautogui.keyDown('d')
        time.sleep(time1)
        pyautogui.keyUp('d')

    def see_around(self,time1):
        pyautogui.moveRel(200,0)
    
    def harvesting(self):
        pyautogui.press('f')
    
    def  step(self,action):
        action_list=["self.go_straight","self.go_back","self.go_left","self.go_right","self.see_around"]

        # do action here ,action{action type(int),action time(int)}
        action_time=0.5
        eval(action_list[action])(action_time)
        # get state and check the reward and done
        self.state=self.get_state()
        self.reward=self.get_reward()
        self.time+=1
        if self.time> self.total_time:
            self.done=True
        # try to harvest item
        self.harvesting()
        self.state=self.get_state()
        return  self.state,self.reward,self.done

    def shape_state(self):
        player_info, item_list = self.state
        print(np.array(player_info).shape)
        print(np.array(item_list).shape)
        shape_list=[]
        shape_list.append(player_info[2][2])
        if item_list:
            print("item not null")
            shape_list.append(item_list[0][2][2])
        else:
            shape_list.append(0)
        print(shape_list)
        return shape_list

