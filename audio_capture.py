import subprocess
import time
import re

def extract_leading_number(line):
    match = re.match(r'\s*(\d+)', line)
    return int(match.group(1)) if match else None

DEVICE_NAME = "pipewire-screenaudio"
DEBUG_LOGS = False

blacklist_list = ["alsa", "bluez", "Midi", "pipewire", "Mumble", "Discord", "kwin_wayland", "CompletedProcess", "stderr", "Firefox:monitor", "Playback", "rnnoise", "Capture", "monitor"]

while True:
    log_buffer = ""

    raw_list = (str(subprocess.run(["pw-link", "-oI"], capture_output=True, timeout=1)).split("\\n"))

    log_buffer += "Raw list: " + str(raw_list) + "\n\n"

    allowed_list = []
    not_allowed_list = []

    for entry in raw_list:
        not_allowed_flag = False
        for backlist_entry in blacklist_list:
            if backlist_entry in entry:
                not_allowed_flag = True
                not_allowed_list.append(entry)
                break
        
        if not_allowed_flag == False:
            allowed_list.append(entry)

    log_buffer += "Allowed: " + str(allowed_list) + "\n\n"
    log_buffer += "Not Allowed: " + str(not_allowed_list) + "\n\n"
    #connecting

    for app in allowed_list:
        app_id = extract_leading_number(app)
        log_buffer += str(app_id) + " : "
        try:
            if str(app).endswith("FR"):  
                log_buffer += str(subprocess.run(["pw-link", str(app_id), DEVICE_NAME + ":input_FR"], capture_output=True, timeout=0.2))
                pass
            else:
                log_buffer += str(subprocess.run(["pw-link", str(app_id), DEVICE_NAME + ":input_FL"], capture_output=True, timeout=0.2))
                pass
        except:
            log_buffer += "timeout"

        log_buffer += "\n\n"

    #disconnecting not allowed

    for app in not_allowed_list:
        app_id = extract_leading_number(app)
        log_buffer += str(app_id) + " : "
        try:
            if str(app).endswith("FR"):
                log_buffer += str(subprocess.run(["pw-link", "-d", str(app_id), DEVICE_NAME + ":input_FR"], capture_output=True, timeout=0.2))
                pass
            else:
                log_buffer += str(subprocess.run(["pw-link", "-d", str(app_id), DEVICE_NAME + ":input_FL"], capture_output=True, timeout=0.2))
                pass
        except:
            log_buffer += "timeout"
        log_buffer += "\n\n"

    if DEBUG_LOGS:
        with open("log.txt", 'w') as file:
            file.write(log_buffer)


    time.sleep(0.15)