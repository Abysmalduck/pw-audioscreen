import subprocess
import time
import re

def extract_leading_number(line):
    match = re.match(r'\s*(\d+)', line)
    return int(match.group(1)) if match else None

def get_node_id(add_info):
    match = re.search(r'node\.id = \"[0-9]+\"', add_info)
    if match != None:
        number = re.search(r'[0-9]+', match.group(0))
        return int(number.group(0)) if number else None

    return None

DEVICE_NAME = "pipewire-screenaudio"
DEBUG_LOGS = False

blacklist_list = ["alsa", "bluez", "Midi", "pipewire", "Mumble", "Discord", "kwin_wayland", "CompletedProcess", "stderr", "Playback", "rnnoise", "Capture", "monitor", "Screego"]

while True:
    try:
        log_buffer = ""

        raw_list = (str(subprocess.run(["pw-link", "-oI"], capture_output=True, timeout=1)).split("\\n"))[2:-1]

        log_buffer += "Raw list: " + str(raw_list) + "\n\n"

        allowed_list = []
        not_allowed_list = []

        for entry in raw_list:
            not_allowed_flag = False

            try:
                app_id = extract_leading_number(entry)
                additional_entry_info = str(subprocess.run(["pw-cli", "info", str(app_id)] , capture_output=True, timeout=1))
                node_id = get_node_id(additional_entry_info)
                additional_node_info = str(subprocess.run(["pw-cli", "info", str(node_id)] , capture_output=True, timeout=1))

                log_buffer += str(app_id) + " : additional_node_info : " + additional_node_info + "\n\n"

                if "Screego" in additional_node_info:
                    not_allowed_flag = True
                    not_allowed_list.append(entry)
            except FileNotFoundError:
                pass
            
            if not_allowed_flag == False:
                for blacklist_entry in blacklist_list:
                    
                    if blacklist_entry in entry:
                        not_allowed_flag = True
                        not_allowed_list.append(entry)
                        break
                
            if not_allowed_flag == False:
                allowed_list.append(entry)

        log_buffer += "Allowed: " + str(allowed_list) + "\n\n"
        log_buffer += "Not Allowed: " + str(not_allowed_list) + "\n\n"
        #connecting allowed array

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

        #disconnecting not allowed array
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


        time.sleep(0.5)
    except FileNotFoundError:
        print("Looks like pw-link is not installed, maybe system is updating, maybe pipewire is not installed, anyway, restarting script..")
        time.sleep(4)
    except KeyboardInterrupt:
        break
    except:
        print("Unknown error, restarting script")
        time.sleep(4)