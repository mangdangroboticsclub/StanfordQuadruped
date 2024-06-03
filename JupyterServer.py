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
# Description: Jupyter server side
#              Make sure to run this file before use Jupyter client on your PC side.
#
import socket
import threading
import subprocess
import time

HOST = '0.0.0.0'
PORT = 8001
list_path = '/home/ubuntu/StanfordQuadruped/src/createDanceActionListSample.py'
run_path =  '/home/ubuntu/StanfordQuadruped/run_danceActionList.py'

class HandleCommand():

    def __init__(self):
        self.current_process = None
        self.process_running = False
        self.process_lock = threading.Lock()

    def handle_command(self,command):
        with self.process_lock:
            if command.startswith("MODIFY"):
                try:
                    parts = command.split(' ', 1)
                    contents = parts[1].split('|')
                    with open(list_path, 'r+') as f:
                        lines = []
                        for i in range(61):
                            line = f.readline()
                            lines.append(line)
                        f.seek(len(''.join(lines)))
                        f.truncate()
                        for content in contents:
                            f.write(content + '\n')
                        append_line = 'MovementLib = Move.MovementLib'
                        f.write(append_line)

                    return f"Successfully added danceList in: createDanceActionListSample.py"
                except Exception as e:
                    return f"Failed to modify file: {e}"
            
            elif command == ("STOP"):
                if self.current_process:
                    self.current_process.terminate()
                    self.current_process = None
                    self.process_running = False
                    return "Successfully cleared current process"
                else:
                    return "No process running"
            elif command == ("EXECUTE") and not self.process_running:
                try:
                    self.current_process = subprocess.Popen(['python', run_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                    self.process_running = True
                    return f"Process started"
                except Exception as e:
                    return f"Failed to start process: {e}"
            else:
                return "Unknown command"

    def server(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((HOST, PORT))
            s.listen()
            print(f"server listening on {HOST}:{PORT}")

            while True:
                conn, addr = s.accept()
                with conn:
                    print(f"Connected by {addr}")
                    while True:
                        data = conn.recv(1024)
                        if not data:
                            time.sleep(0.1)
                            break
                        command = data.decode().strip()
                        if self.process_running and command != 'STOP':
                            if self.current_process.poll() is None:
                                response = "Current Process is still running, please wait."
                                conn.sendall(response.encode())
                                break
                            else:
                                self.process_running = False
                                self.current_process = None
                        print(f"Received command: {command}")
                        response = self.handle_command(command)
                        conn.sendall(response.encode())
                        if command == "STOP":
                            break
                    print(f"Connection with {addr} closed")

if __name__ == "__main__":
    handler = HandleCommand()
    handler.server()

