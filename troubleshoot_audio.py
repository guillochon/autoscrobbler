#!/usr/bin/env python3
"""
Audio troubleshooting script for autoscrobbler
This script helps diagnose audio device access issues when running as a service
"""

import os
import subprocess
import sys

import sounddevice as sd


def check_environment():
    """Check the current environment variables and permissions"""
    print("=== Environment Check ===")
    print(f"User: {os.getenv('USER', 'Unknown')}")
    print(f"UID: {os.getuid()}")
    print(f"GID: {os.getgid()}")
    print(f"Groups: {os.getgroups()}")
    print(f"XDG_RUNTIME_DIR: {os.getenv('XDG_RUNTIME_DIR', 'Not set')}")
    print(f"PULSE_RUNTIME_PATH: {os.getenv('PULSE_RUNTIME_PATH', 'Not set')}")
    print(f"DBUS_SESSION_BUS_ADDRESS: {os.getenv('DBUS_SESSION_BUS_ADDRESS', 'Not set')}")
    print()

def check_audio_devices():
    """Check available audio devices"""
    print("=== Audio Devices Check ===")
    try:
        devices = sd.query_devices()
        input_devices = [d for d in devices if d['max_input_channels'] > 0]
        
        print(f"Total devices: {len(devices)}")
        print(f"Input devices: {len(input_devices)}")
        print()
        
        if input_devices:
            print("Available input devices:")
            for i, dev in enumerate(input_devices):
                print(f"  [{i}] {dev['name']}")
                print(f"      Index: {dev['index']}")
                print(f"      Channels: {dev['max_input_channels']}")
                print(f"      Sample rate: {dev['default_samplerate']}")
                print()
        else:
            print("No input devices found!")
            return False
            
        # Check default device
        try:
            default_input = sd.default.device[0]
            default_info = sd.query_devices(default_input)
            print(f"Default input device: {default_info['name']} (index: {default_input})")
        except Exception as e:
            print(f"Error getting default input device: {e}")
            return False
            
        return True
    except Exception as e:
        print(f"Error querying audio devices: {e}")
        return False

def check_pulseaudio():
    """Check PulseAudio status"""
    print("=== PulseAudio Check ===")
    try:
        # Check if pulseaudio is running
        result = subprocess.run(['pulseaudio', '--check'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ PulseAudio is running")
        else:
            print("✗ PulseAudio is not running")
            return False
            
        # Check pulseaudio info
        result = subprocess.run(['pactl', 'info'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ PulseAudio control interface accessible")
            print(result.stdout)
        else:
            print("✗ Cannot access PulseAudio control interface")
            print(f"Error: {result.stderr}")
            return False
            
        return True
    except FileNotFoundError:
        print("✗ PulseAudio not found")
        return False
    except Exception as e:
        print(f"✗ Error checking PulseAudio: {e}")
        return False

def test_audio_recording():
    """Test audio recording capability"""
    print("=== Audio Recording Test ===")
    try:
        # Try to record a short audio sample
        print("Attempting to record 1 second of audio...")
        audio = sd.rec(int(1 * 44100), samplerate=44100, channels=1, dtype='int16')
        sd.wait()
        print("✓ Audio recording successful")
        print(f"  Recorded {len(audio)} samples")
        return True
    except Exception as e:
        print(f"✗ Audio recording failed: {e}")
        return False

def check_permissions():
    """Check audio device permissions"""
    print("=== Permissions Check ===")
    
    # Check /dev/snd permissions
    if os.path.exists('/dev/snd'):
        print("Audio device directory exists")
        try:
            stat = os.stat('/dev/snd')
            print(f"  Owner: {stat.st_uid}")
            print(f"  Group: {stat.st_gid}")
            print(f"  Mode: {oct(stat.st_mode)}")
        except Exception as e:
            print(f"  Error checking /dev/snd: {e}")
    else:
        print("✗ /dev/snd does not exist")
    
    # Check if user is in audio group
    try:
        groups = os.getgroups()
        if 29 in groups:  # audio group is typically GID 29
            print("✓ User is in audio group")
        else:
            print("✗ User is not in audio group")
            print("  Run: sudo usermod -a -G audio $USER")
    except Exception as e:
        print(f"Error checking groups: {e}")

def main():
    """Main troubleshooting function"""
    print("Autoscrobbler Audio Troubleshooting")
    print("=" * 40)
    print()
    
    check_environment()
    print()
    
    check_permissions()
    print()
    
    pulse_ok = check_pulseaudio()
    print()
    
    devices_ok = check_audio_devices()
    print()
    
    if pulse_ok and devices_ok:
        recording_ok = test_audio_recording()
        print()
        
        if recording_ok:
            print("✓ All audio checks passed! Autoscrobbler should work.")
        else:
            print("✗ Audio recording failed. Check permissions and device access.")
    else:
        print("✗ Audio system not properly configured.")
        print("  - Make sure PulseAudio is running")
        print("  - Ensure user is in audio group")
        print("  - Check that audio devices are available")

if __name__ == "__main__":
    main() 