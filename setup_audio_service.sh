#!/bin/bash

# Setup script for autoscrobbler audio service
# This script configures the necessary permissions and environment for autoscrobbler to access audio devices

set -e

echo "Setting up autoscrobbler audio service..."

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo "This script should not be run as root. Please run as the pi user."
   exit 1
fi

# Add user to audio group if not already added
if ! groups | grep -q audio; then
    echo "Adding user to audio group..."
    sudo usermod -a -G audio $USER
    echo "Please log out and log back in for group changes to take effect."
fi

# Create necessary directories
echo "Creating necessary directories..."
mkdir -p ~/.config/systemd/user
mkdir -p ~/autoscrobbler

# Copy service files
echo "Copying service files..."
cp autoscrobbler.service ~/.config/systemd/user/
cp autoscrobbler-user.service ~/.config/systemd/user/

# Enable user service
echo "Enabling user service..."
systemctl --user enable autoscrobbler-user.service

# Create a system-wide service as backup
echo "Installing system-wide service..."
sudo cp autoscrobbler.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable autoscrobbler.service

# Configure PulseAudio for system-wide access
echo "Configuring PulseAudio..."
mkdir -p ~/.config/pulse

# Create pulseaudio config for better device access
cat > ~/.config/pulse/client.conf << EOF
# This file is part of PulseAudio.
#
# PulseAudio is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# PulseAudio is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with PulseAudio; if not, see <http://www.gnu.org/licenses/>.

## Configuration file for PulseAudio clients

# Allow anonymous authentication
autospawn = yes
daemon-binary = /usr/bin/pulseaudio
enable-shm = yes
shm-size-bytes = 0 # setting to 0 will use the system-default
EOF

# Test audio device access
echo "Testing audio device access..."
python3 -c "
import sounddevice as sd
devices = sd.query_devices()
input_devices = [d for d in devices if d['max_input_channels'] > 0]
print(f'Found {len(input_devices)} input devices:')
for i, dev in enumerate(input_devices):
    print(f'  [{i}] {dev[\"name\"]} (channels: {dev[\"max_input_channels\"]})')
"

echo ""
echo "Setup complete! Here are your options:"
echo ""
echo "1. User service (recommended):"
echo "   systemctl --user start autoscrobbler-user.service"
echo "   systemctl --user status autoscrobbler-user.service"
echo ""
echo "2. System service (alternative):"
echo "   sudo systemctl start autoscrobbler.service"
echo "   sudo systemctl status autoscrobbler.service"
echo ""
echo "3. Check logs:"
echo "   journalctl --user -u autoscrobbler-user.service -f"
echo "   # or for system service:"
echo "   sudo journalctl -u autoscrobbler.service -f"
echo ""
echo "Note: If you added yourself to the audio group, please log out and log back in first." 