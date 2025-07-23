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
echo "Creating local service directory..."
mkdir -p ~/.config/systemd/user

# Copy service file
echo "Copying service file..."
cp autoscrobbler.service ~/.config/systemd/user/

# Enable user service
echo "Enabling user service..."
systemctl --user enable autoscrobbler.service

# Test audio device access
echo "Testing audio device access..."
uv run python -c "
import sounddevice as sd
devices = sd.query_devices()
input_devices = [d for d in devices if d['max_input_channels'] > 0]
print(f'Found {len(input_devices)} input devices:')
for i, dev in enumerate(input_devices):
    print(f'  [{i}] {dev[\"name\"]} (channels: {dev[\"max_input_channels\"]})')
"

echo ""
echo "Setup complete!"
echo ""
echo "Start the service:"
echo "   systemctl --user start autoscrobbler.service"
echo "   systemctl --user status autoscrobbler.service"
echo ""
echo "Check logs:"
echo "   journalctl --user -u autoscrobbler.service -f"
echo ""
echo "Note: If you added yourself to the audio group, please log out and log back in first." 
