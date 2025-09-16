import subprocess
import time
import re
import os


def extract_leading_number(line):
    match = re.match(r'\s*(\d+)', line)
    return int(match.group(1)) if match else None


def get_node_id(add_info):
    match = re.search(r'node\.id = \"[0-9]+\"', add_info)
    if match != None:
        number = re.search(r'[0-9]+', match.group(0))
        return int(number.group(0)) if number else None

    return None



DEBUG_LOGS = False

blacklist_list = ["alsa", "bluez", "Midi", "pipewire", "Mumble", "Discord", "kwin_wayland",
                  "CompletedProcess", "stderr", "Playback", "rnnoise", "Capture", "monitor", 
                  "Vite", "ClownShare", "gnome-shell", "pci"]

DEVICE_NAME = "clownshare-mic"

# Creating virtual mic
pw_input_info = str(subprocess.run(["pw-link", "-i"], capture_output=True, timeout=1))
if DEVICE_NAME not in pw_input_info:
    print(f"No {DEVICE_NAME}, creating one...")
    os.system("pw-cli create-node adapter '{ \"factory.name\": \"support.null-audio-sink\", \"node.name\": \"clownshare-mic\", \"node.description\": \"ClownShare Virtual Microphone\", \"media.class\": \"Audio/Source/Virtual\", \"audio.position\": \"[ FL FR ]\", \"object.linger\": true}'")


cached_not_allowed_ids = []
cached_allowed_ids = []

while True:
    try:
        raw_list = (str(subprocess.run(
            ["pw-link", "-oI"], capture_output=True, timeout=1)).split("\\n"))[2:-1]

        allowed_list = []
        not_allowed_list = []

        for entry in raw_list:
            not_allowed_flag = False

            #Search in firefox and librewolf browsers for tab sound selecting
            if "Firefox" in entry or "LibreWolf" in entry:                
                try:
                    app_id = extract_leading_number(entry)
                    additional_entry_info = str(subprocess.run(
                        ["pw-cli", "info", str(app_id)], capture_output=True, timeout=1))
                    node_id = get_node_id(additional_entry_info)
                    additional_node_info = str(subprocess.run(
                        ["pw-cli", "info", str(node_id)], capture_output=True, timeout=1))

                    if "Vite" in additional_node_info or "ClownShare" in additional_node_info:
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
        # connecting allowed array

        for app in allowed_list:

            if app in cached_allowed_ids:
                continue

            print(f"connection {app}")

            app_id = extract_leading_number(app)
            try:
                if str(app).endswith("FR"):
                    subprocess.run(["pw-link", str(
                        app_id), DEVICE_NAME + ":input_FR"], capture_output=True, timeout=0.2)
                else:
                    subprocess.run(["pw-link", str(
                        app_id), DEVICE_NAME + ":input_FL"], capture_output=True, timeout=0.2)
            except:
                pass

        cached_allowed_ids = allowed_list

        # disconnecting not allowed array
        for app in not_allowed_list:

            if app in cached_not_allowed_ids:
                continue

            print(f"disconnection {app}")

            app_id = extract_leading_number(app)
            try:
                subprocess.run(["pw-link", "-d", str(
                    app_id), DEVICE_NAME + ":input_FR"], capture_output=True, timeout=0.2)
                subprocess.run(["pw-link", "-d", str(
                    app_id), DEVICE_NAME + ":input_FL"], capture_output=True, timeout=0.2)
            except:
                pass

        cached_not_allowed_ids = not_allowed_list

        time.sleep(0.5)
    except FileNotFoundError:
        print("Looks like pw-link is not installed, maybe system is updating, maybe pipewire is not installed, anyway, restarting script..")
        time.sleep(4)
    except KeyboardInterrupt:
        break
    except Exception as e:
        print(f"Unknown error: {e}. restarting script")
        time.sleep(1)
