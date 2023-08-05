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
# Description: You can use the following FPC(Flexible Programmable Choreography) APIs to define your Mini Pupper to dance.
# Test method: 
#   step1: Pair the controller to your Mini Pupper
#   step2: Click controller "L1" button
#   step3: Click controller "Circle" button 
#   the mini pupper will dance based on your following script.
# stop()
# look_up()
# look_down()
# look_right()
# look_left()
# look_upperleft()
# look_upperright()
# look_rightlower()
# look_leftlower()
# move_forward()
# move_backward()
# move_right()
# move_left()
# move_leftfront()
# move_rightfront()
# move_leftback()
# move_rightback()
#
from src.MovementGroup import MovementGroups

Move = MovementGroups()

Move.look_right()
Move.look_upperright()
Move.look_up()
Move.look_upperleft()
Move.look_left()
Move.look_leftlower()
Move.look_down()
Move.look_rightlower()
Move.look_right()
Move.stop()
Move.move_right()
Move.move_forward()
Move.move_left()
Move.move_backward()
Move.move_right()
Move.stop()

MovementLib = Move.MovementLib
