# Autoscrobbler Service Setup Guide

This guide helps you set up autoscrobbler as a systemd user service on Raspberry Pi with proper audio device access.

## Problem

When running autoscrobbler as a systemd service, it often can't find audio devices even though it works fine when run from the command line. This is because:

1. Systemd services run in a restricted environment
2. Audio devices require specific permissions and environment variables
3. PulseAudio/ALSA access is limited for system services

## Solution: User Service

User services run in your user environment and have better access to audio devices.

1. **Run the setup script:**
   ```bash
   chmod +x setup_audio_service.sh
   ./setup_audio_service.sh
   ```

2. **Start the service:**
   ```bash
   systemctl --user start autoscrobbler.service
   systemctl --user enable autoscrobbler.service
   ```

3. **Check status:**
   ```bash
   systemctl --user status autoscrobbler.service
   ```

4. **View logs:**
   ```bash
   journalctl --user -u autoscrobbler.service -f
   ```

## Troubleshooting

### Run the diagnostic script

```bash
python3 troubleshoot_audio.py
```

This will check:
- Environment variables
- Audio device availability
- PulseAudio status
- Permissions
- Audio recording capability

### Common Issues and Solutions

#### 1. "No input devices found"

**Symptoms:** Service logs show "No input devices found" error

**Solutions:**
- Ensure user is in audio group: `sudo usermod -a -G audio $USER`
- Log out and log back in after adding to audio group
- Check if PulseAudio is running: `pulseaudio --check`
- Try the user service instead of system service

#### 2. "PulseAudio not running"

**Symptoms:** Service can't connect to PulseAudio

**Solutions:**
- Start PulseAudio: `pulseaudio --start`
- Enable PulseAudio autostart: `systemctl --user enable pulseaudio`
- Check PulseAudio status: `pactl info`

#### 3. "Permission denied" errors

**Symptoms:** Permission errors when accessing audio devices

**Solutions:**
- Check audio group membership: `groups`
- Verify /dev/snd permissions: `ls -la /dev/snd`
- Restart the service after fixing permissions

#### 4. Environment variables not set

**Symptoms:** Missing XDG_RUNTIME_DIR or PULSE_RUNTIME_PATH

**Solutions:**
- Use the user service which inherits your environment
- Or manually set environment variables in the service file
- Ensure PulseAudio is running before starting the service

### Manual Configuration

If the automated setup doesn't work, you can manually configure:

1. **Add user to audio group:**
   ```bash
   sudo usermod -a -G audio $USER
   ```

2. **Configure PulseAudio:**
   ```bash
   mkdir -p ~/.config/pulse
   # Create ~/.config/pulse/client.conf with autospawn = yes
   ```

3. **Set up user service:**
   ```bash
   mkdir -p ~/.config/systemd/user
   cp autoscrobbler.service ~/.config/systemd/user/
   systemctl --user enable autoscrobbler.service
   ```

## Service Configuration Details

### User Service (`autoscrobbler.service`)

- Runs as your user account
- Inherits your environment variables
- Has access to your PulseAudio session
- Uses `%h` for home directory expansion
- Waits for PulseAudio to be ready

## Environment Variables

The user service inherits your environment variables, including:

- `XDG_RUNTIME_DIR` - Runtime directory for user services
- `PULSE_RUNTIME_PATH` - PulseAudio runtime path
- `DBUS_SESSION_BUS_ADDRESS` - D-Bus session address

## Testing

After setup, test that audio devices are accessible:

```bash
# Test from command line
python3 -c "import sounddevice as sd; print(sd.query_devices())"

# Test from service environment
systemctl --user exec autoscrobbler-user.service python3 -c "import sounddevice as sd; print(sd.query_devices())"
```

## Logs and Debugging

- **Service logs:** `journalctl --user -u autoscrobbler.service -f`
- **PulseAudio logs:** `journalctl -u pulseaudio -f`
- **System logs:** `sudo journalctl -f`

## Support

If you're still having issues:

1. Run the troubleshooting script: `python3 troubleshoot_audio.py`
2. Check the service logs for specific error messages
3. Verify your audio setup works from command line first
4. Try running the service manually to see immediate errors 