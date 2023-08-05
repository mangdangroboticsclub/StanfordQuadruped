#
# Copyright 2023 MangDang (www.mangdang.net) 
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Description: FPC(Flexible Programmable Choreography) APIs
#
import numpy as np
from src.MovementScheme import Movements 

"please comfirm the size of legs,speed,attitude all same in youe design movements"
class MovementGroups:

    def __init__(self):
        self.MovementLib = []
        self.default_stand = [[[0.06,-0.05,-0.07]],[[0.06, 0.05,-0.07]],[[-0.06,-0.05,-0.07]],[[-0.06, 0.05,-0.07]]]
 
    def stop(self):
        """Return to the default natural standing position
        Returns:
        	Append the default standing position into MovementLib
        """
        dance_scheme = Movements('stop')
        dance_all_legs = self.default_stand
        dance_speed = [[0,0,0]]        # speed_x, speed_y, no_use
        dance_attitude = [[0,0,0]]     # roll, pitch, yaw degree
        dance_scheme.setAllSequence(dance_all_legs,dance_speed,dance_attitude)
        self.MovementLib.append(dance_scheme)      # append dance
        return self.MovementLib

    def look_up(self):  
        """Set robot look up 20deg, you can change the deg parameter in this function.
        Returns:
        	Append the look up movement into MovementLib
        """    
        dance_scheme = Movements('look_up')
        dance_all_legs = self.default_stand
        dance_speed = [[0,0,0]]       # speed_x, speed_y, no_use
        dance_attitude = [[0,20,0]]   # roll, pitch, yaw degree
        dance_scheme.setAllSequence(dance_all_legs,dance_speed,dance_attitude)
        self.MovementLib.append(dance_scheme)     # append dance
        return self.MovementLib
 
    def look_down(self):
        """Set robot look down 20deg, you can change the deg parameter in this function.
        Returns:
        	Append the look down movement into MovementLib
        """ 
        dance_scheme = Movements('look_down')
        dance_all_legs = self.default_stand
        dance_speed = [[0,0,0]]       # speed_x, speed_y, no_use
        dance_attitude = [[0,-20,0]]  # roll, pitch, yaw degree
        dance_scheme.setAllSequence(dance_all_legs,dance_speed,dance_attitude)
        self.MovementLib.append(dance_scheme)      # append dance
        return self.MovementLib

    def look_right(self):
        """Set robot look right 30deg, you can change the deg parameter in this function.
        Returns:
        	Append the look right movement into MovementLib
        """
        dance_scheme = Movements('look_right')
        dance_all_legs = self.default_stand
        dance_speed = [[0,0,0]]       # speed_x, speed_y, no_use
        dance_attitude = [[0,0,30]]   # roll, pitch, yaw degree
        dance_scheme.setAllSequence(dance_all_legs,dance_speed,dance_attitude)
        self.MovementLib.append(dance_scheme)      # append dance
        return self.MovementLib
 
    def look_left(self):
        """Set robot look left 30deg, you can change the deg parameter in this function.
        Returns:
        	Append the look left movement into MovementLib
        """
        dance_scheme = Movements('look_left')
        dance_all_legs = self.default_stand
        dance_speed = [[0,0,0]]       # speed_x, speed_y, no_use
        dance_attitude = [[0,0,-30]]  # roll, pitch, yaw degree
        dance_scheme.setAllSequence(dance_all_legs,dance_speed,dance_attitude)
        self.MovementLib.append(dance_scheme)      # append dance
        return self.MovementLib
  
    def look_upperleft(self):
        """Set robot look up 20deg and look left 30deg, you can change the deg parameter in this function.
        Returns:
        	Append the look upperleft movement into MovementLib
        """
        dance_scheme = Movements('look_upperleft')
        dance_all_legs = self.default_stand
        dance_speed = [[0,0,0]]       # speed_x, speed_y, no_use
        dance_attitude = [[0,20,-30]] # roll, pitch, yaw degree
        dance_scheme.setAllSequence(dance_all_legs,dance_speed,dance_attitude)
        self.MovementLib.append(dance_scheme)      # append dance
        return self.MovementLib

    def look_upperright(self):
        """Set robot look up 20deg and look right 30deg, you can change the deg parameter in this function.
        Returns:
        	Append the look upperright movement into MovementLib
        """
        dance_scheme = Movements('look_upperright')
        dance_all_legs = self.default_stand
        dance_speed = [[0,0,0]]       # speed_x, speed_y, no_use
        dance_attitude = [[0,20,30]]  # roll, pitch, yaw degree
        dance_scheme.setAllSequence(dance_all_legs,dance_speed,dance_attitude)
        self.MovementLib.append(dance_scheme)      # append dance
        return self.MovementLib
  
    def look_rightlower(self):
        """Set robot look down 20deg and look right 30deg, you can change the deg parameter in this function.
        Returns:
        	Append the look rightlower movement into MovementLib
        """
        dance_scheme = Movements('look_rightlower')
        dance_all_legs = self.default_stand
        dance_speed = [[0,0,0]]       # speed_x, speed_y, no_use
        dance_attitude = [[0,-20,30]] # roll, pitch, yaw degree
        dance_scheme.setAllSequence(dance_all_legs,dance_speed,dance_attitude)
        self.MovementLib.append(dance_scheme)      # append dance
        return self.MovementLib
  
    def look_leftlower(self):
        """Set robot look down 20deg and look left 30deg, you can change the deg parameter in this function.
        Returns:
        	Append the look leftlower movement into MovementLib
        """
        dance_scheme = Movements('look_leftlower')
        dance_all_legs = self.default_stand
        dance_speed = [[0,0,0]]       # speed_x, speed_y, no_use
        dance_attitude = [[0,-20,-30]]# roll, pitch, yaw degree
        dance_scheme.setAllSequence(dance_all_legs,dance_speed,dance_attitude)
        self.MovementLib.append(dance_scheme)      # append dance
        return self.MovementLib
                          
    def move_forward(self):
        """Set robot move forward as 0.15m/s, you can change the velocity parameter in this function.
        Returns:
        	Append the move forward movement into MovementLib
        """
        dance_scheme = Movements('move_forward')
        dance_all_legs = self.default_stand
        dance_speed = [[0.15,0,0]]    # speed_x, speed_y, no_use
        dance_attitude = [[0,0,0]]    # roll, pitch, yaw degree
        dance_scheme.setAllSequence(dance_all_legs,dance_speed,dance_attitude)
        self.MovementLib.append(dance_scheme)      # append dance
        return self.MovementLib
     
    def move_backward(self):
        """Set robot move backward as 0.15m/s, you can change the velocity parameter in this function.
        Returns:
        	Append the move backward movement into MovementLib
        """
        dance_scheme = Movements('move_backward')
        dance_all_legs = self.default_stand
        dance_speed = [[-0.15,0,0]]   # speed_x, speed_y, no_use
        dance_attitude = [[0,0,0]]    # roll, pitch, yaw degree
        dance_scheme.setAllSequence(dance_all_legs,dance_speed,dance_attitude)
        self.MovementLib.append(dance_scheme)      # append dance
        return self.MovementLib

    def move_right(self):
        """Set robot move right as 0.15m/s, you can change the velocity parameter in this function.
        Returns:
        	Append the move right movement into MovementLib
        """
        dance_scheme = Movements('move_right')
        dance_all_legs = self.default_stand
        dance_speed = [[0,-0.15,0]]    # speed_x, speed_y, no_use
        dance_attitude = [[0,0,0]]     # roll, pitch, yaw rate
        dance_scheme.setAllSequence(dance_all_legs,dance_speed,dance_attitude)
        self.MovementLib.append(dance_scheme)      # append dance
        return self.MovementLib
  
    def move_left(self):
        """Set robot move left as 0.15m/s, you can change the velocity parameter in this function.
        Returns:
        	Append the move left movement into MovementLib
        """
        dance_scheme = Movements('move_left')
        dance_all_legs = self.default_stand
        dance_speed = [[0,0.15,0]]    # speed_x, speed_y, no_use
        dance_attitude = [[0,0,0]]    # roll, pitch, yaw degree
        dance_scheme.setAllSequence(dance_all_legs,dance_speed,dance_attitude)
        self.MovementLib.append(dance_scheme)      # append dance
        return self.MovementLib
   
    def move_leftfront(self):
        """Set robot move leftfront as 0.15*sqrt(2)m/s, you can change the velocity parameter in this function.
        Returns:
        	Append the move leftfront movement into MovementLib
        """
        dance_scheme = Movements('move_leftfront')
        dance_all_legs = self.default_stand
        dance_speed = [[0.15,0.15,0]] # speed_x, speed_y, no_use
        dance_attitude = [[0,0,0]]    # roll, pitch, yaw rate
        dance_scheme.setAllSequence(dance_all_legs,dance_speed,dance_attitude)
        self.MovementLib.append(dance_scheme)      # append dance
        return self.MovementLib
    
    def move_rightfront(self):
        """Set robot move rightfront as 0.15*sqrt(2)m/s, you can change the velocity parameter in this function.
        Returns:
        	Append the move rightfront movement into MovementLib
        """
        dance_scheme = Movements('move_rightfront')
        dance_all_legs = self.default_stand
        dance_speed = [[0.15,-0.15,0]] # speed_x, speed_y, no_use
        dance_attitude = [[0,0,0]]     # roll, pitch, yaw degree
        dance_scheme.setAllSequence(dance_all_legs,dance_speed,dance_attitude)
        self.MovementLib.append(dance_scheme)      # append dance
        return self.MovementLib
    
    def move_leftback(self):
        """Set robot move leftback as 0.15*sqrt(2)m/s, you can change the velocity parameter in this function.
        Returns:
        	Append the move leftback movement into MovementLib
        """
        dance_scheme = Movements('move_leftback')
        dance_all_legs = self.default_stand
        dance_speed = [[-0.15,0.15,0]]# speed_x, speed_y, no_use
        dance_attitude = [[0,0,0]]    # roll, pitch, yaw degree
        dance_scheme.setAllSequence(dance_all_legs,dance_speed,dance_attitude)
        self.MovementLib.append(dance_scheme)      # append dance
        return self.MovementLib
 
    def move_rightback(self):
        """Set robot move rightback as 0.15*sqrt(2)m/s, you can change the velocity parameter in this function.
        Returns:
        	Append the move rightback movement into MovementLib
        """
        dance_scheme = Movements('move_rightback')
        dance_all_legs = self.default_stand
        dance_speed = [[-0.15,-0.15,0]]# speed_x, speed_y, no_use
        dance_attitude = [[0,0,0]]     # roll, pitch, yaw rate
        dance_scheme.setAllSequence(dance_all_legs,dance_speed,dance_attitude)
        self.MovementLib.append(dance_scheme)      # append dance
        return self.MovementLib
        
      
"""  
    #multiple move in one movement example1
    #it is a series of movement,keep down first then back to default stand ,move forward ,finally stop  
    def down_trot(self):    
        dance_scheme = Movements('down_trot')

        dance_all_legs = []
        dance_all_legs.append([[ 0.06,-0.05,-0.07],[ 0.06,-0.05,-0.04],[ 0.06,-0.05,-0.07],[ 0.06,-0.05,-0.07],[ 0.06,-0.05,-0.07]]) #leg1
        dance_all_legs.append([[ 0.06, 0.05,-0.07],[ 0.06, 0.05,-0.04],[ 0.06, 0.05,-0.07],[ 0.06, 0.05,-0.07],[ 0.06, 0.05,-0.07]]) #leg2
        dance_all_legs.append([[-0.06,-0.05,-0.07],[-0.06,-0.05,-0.04],[-0.06,-0.05,-0.07],[-0.06,-0.05,-0.07],[-0.06,-0.05,-0.07]]) #leg3
        dance_all_legs.append([[-0.06, 0.05,-0.07],[-0.06, 0.05,-0.04],[-0.06, 0.05,-0.07],[-0.06, 0.05,-0.07],[-0.06, 0.05,-0.07]]) #leg4

        dance_speed = [[0,0,0],[0,0,0],[0,0,0],[0.15,0,0],[0,0,0]]    # speed_x, speed_y, no_use

        dance_attitude = [[0,0,0],[10,0,0],[0,0,0],[0,0,0],[0,0,0]]   # roll, pitch, yaw degree
        dance_scheme.setAllSequence(dance_all_legs,dance_speed,dance_attitude)
        self.MovementLib.append(dance_scheme)

        return self.MovementLib

    #multiple move in one movement example2  
    #it is a series of movement,keep up first then back to default stand ,move forward ,finally stop
    def up_trot(self):    
        dance_scheme = Movements('up_trot')

        dance_all_legs = []
        dance_all_legs.append([[ 0.06,-0.05,-0.07],[ 0.06,-0.05,-0.10],[ 0.06,-0.05,-0.07],[ 0.06,-0.05,-0.07],[ 0.06,-0.05,-0.07]])# leg1
        dance_all_legs.append([[ 0.06, 0.05,-0.07],[ 0.06, 0.05,-0.10],[ 0.06, 0.05,-0.07],[ 0.06, 0.05,-0.07],[ 0.06, 0.05,-0.07]])# leg2
        dance_all_legs.append([[-0.06,-0.05,-0.07],[-0.06,-0.05,-0.10],[-0.06,-0.05,-0.07],[-0.06,-0.05,-0.07],[-0.06,-0.05,-0.07]])# leg3
        dance_all_legs.append([[-0.06, 0.05,-0.07],[-0.06, 0.05,-0.10],[-0.06, 0.05,-0.07],[-0.06, 0.05,-0.07],[-0.06, 0.05,-0.07]])# leg4

        dance_speed = [[0,0,0],[0,0,0],[0,0,0],[0.1,0,0],[0,0,0]]    # speed_, speed_y, no_use

        dance_attitude = [[0,0,0],[10,0,0],[0,0,0],[0,0,0],[0,0,0]]  # roll, pitch, yaw rate
        dance_scheme.setAllSequence(dance_all_legs,dance_speed,dance_attitude)
        self.MovementLib.append(dance_scheme)      # append dance

        return self.MovementLib
"""
