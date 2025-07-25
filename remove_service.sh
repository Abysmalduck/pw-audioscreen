#!/bin/bash

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)

systemctl --user daemon-reload
systemctl --user disable pw-audioscreen.service
systemctl --user stop pw-audioscreen.service

rm ~/.local/share/pw-audioscreen/audio_capture.py
rm ~/.config/systemd/user/pw-audioscreen.service
rm -r ~/.local/share/pw-audioscreen/