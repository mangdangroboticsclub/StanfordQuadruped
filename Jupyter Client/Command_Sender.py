#
# Copyright 2024 MangDang (www.mangdang.net) 
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
# Description: Jupyter client side
#              Send Jupyter PC client commands to Jupyter server Mini Pupper side.
#

import socket
import time
import re

class SocketSender:
    def __init__(self, HOST, Lib):
        self.HOST = HOST
        self.PORT = 8001
        self.Lib = Lib
        self.checksum = 0
        self.Group = [
            "Move.look_up()",
            "Move.look_down()",
            "Move.look_left()",
            "Move.look_right()",
            "Move.look_upperleft()",
            "Move.look_upperright()",
            "Move.look_rightlower()",
            "Move.look_leftlower()",
            "Move.move_forward()",
            "Move.move_backward()",
            "Move.move_left()",
            "Move.move_right()",
            "Move.move_leftfront()",
            "Move.move_rightfront()",
            "Move.move_leftback()",
            "Move.move_rightback()",
            "Move.stop",
            "Move.head_move",
            "Move.body_row",
            "Move.gait_uni",
            "Move.height_move",
            "Move.foreleg_lift",
            "Move.backleg_lift",
            "Move.body_cycle()",
            "Move.head_ellipse()",
        ]

    def send_modified_command(self, command):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.HOST, self.PORT))
            try:
                if command == 'MODIFY':
                    content = '|'.join(self.Lib)
                    command = f"MODIFY {content}"
                    s.sendall(command.encode())
                    response = s.recv(1024).decode()
                    if response != "Current Process is still running, please wait.":
                        print(f"Server response: {response}")
                else:
                    s.sendall(command.encode())
                    response = s.recv(1024).decode()
                    print(f"Server response: {response}")
            finally:
                s.close()

    def lib_check(self):
        for move in self.Lib:
            patten = r"^Move\.\w+\([^)]*\)$"
            if re.match(patten, move):
                self.checksum += 1
        if self.checksum == len(self.Lib):
            return True
        else:
            return False
        
    def fit_check(self):
        for target in self.Lib:
            for reference in self.Group:
                if target.startswith(reference):
                    self.checksum += 1
        if self.checksum == len(self.Lib):
            return True
        else:
            return False

    def command_dance(self):
        if self.fit_check() == True:
            #self.send_modified_command('STOP')
            self.send_modified_command('MODIFY')
            time.sleep(0.1)
            self.send_modified_command('EXECUTE')
        else:
            print("\n##############################################################")
            print("  danceList input error! Please double check your danceList!  ")
            print("  correct elements: " + str(self.checksum) + "                ")
            print("##############################################################\n")
    
    def command_stop(self):
        self.send_modified_command('STOP')




