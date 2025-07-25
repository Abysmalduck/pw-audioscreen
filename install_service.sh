#!/bin/bash

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)

mkdir ~/.local/share/pw-audioscreen/

cp $SCRIPT_DIR/audio_capture.py ~/.local/share/pw-audioscreen/audio_capture.py
cp $SCRIPT_DIR/pw-audioscreen.service ~/.config/systemd/user/pw-audioscreen.service

systemctl --user daemon-reload
systemctl --user enable --now pw-audioscreen.service
systemctl --user status pw-audioscreen
