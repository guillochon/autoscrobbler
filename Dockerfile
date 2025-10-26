# Dockerfile for autoscrobbler
#
# Usage:
#   docker build -t autoscrobbler .
#   docker run --rm -it --device /dev/snd \
#     -v /path/to/credentials.json:/app/credentials.json:ro \
#     autoscrobbler
#
# Note: You must mount your credentials.json at runtime for security.
#
# For audio input, the container must have access to /dev/snd (see --device flag above).

FROM python:3.13-slim

# Install system dependencies for sounddevice and soundfile
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        portaudio19-dev \
        libsndfile1 \
        alsa-utils \
        ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Install uv globally
RUN pip install --no-cache-dir uv

WORKDIR /app

# Copy only dependency files first for better caching
COPY pyproject.toml ./

# Install Python dependencies
RUN uv sync

# Copy the rest of the source code
COPY autoscrobbler/ ./autoscrobbler/

# Copy test script
COPY test_docker_audio.py ./test_docker_audio.py

# Copy Windows test script
COPY test_windows_audio.py ./test_windows_audio.py

# Create a helper script to check audio devices
RUN echo '#!/bin/bash\n\
echo "=== Audio Device Check ==="\n\
echo "Available ALSA devices:"\n\
aplay -l 2>/dev/null || echo "No ALSA devices found"\n\
echo -e "\nAvailable PortAudio devices:"\n\
python3 -c "import sounddevice as sd; print(sd.query_devices())" 2>/dev/null || echo "PortAudio not working"\n\
echo -e "\n=== End Audio Device Check ==="\n\
' > /app/check_audio.sh && chmod +x /app/check_audio.sh

# Set the default command (can override with docker run ...)
CMD ["uv", "run", "-m", "autoscrobbler", "--credentials", "./credentials.json", "--input-source", "auto", "--duty-cycle", "60"] 