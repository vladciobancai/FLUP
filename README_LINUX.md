# FLUP - Semi-Automatic Torrent Uploader for FileList.io on Linux

![FLUP Logo](https://github.com/user-attachments/assets/f947a7ae-a0d3-452b-a9e7-4f6f7bae7204)

## Overview

**FLUP is a semi-automated uploader for FileList.io, designed to streamline the process of uploading torrents for movies and Blu-ray discs on Linux.**

## Prerequisites

1. **Install system packages**

   Debian/Ubuntu example:

   ```sh
   sudo apt update
   sudo apt install python3 python3-venv python3-pip ffmpeg mediainfo
   ```

   `ffmpeg`, `ffprobe`, and `mediainfo` must be available from `PATH`.

2. **Create and activate a Python virtual environment**

   From the FLUP project directory:

   ```sh
   python3 -m venv .venv
   source .venv/bin/activate
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

   Activate the venv again before every FLUP run:

   ```sh
   source .venv/bin/activate
   ```

3. **BDInfoCLI-ng for Blu-ray uploads**

   Linux scripts use [BDInfoCLI-ng](https://github.com/Audionut/BDInfoCLI-ng).

   FLUP checks for `bdinfo` in `PATH` first. If it is not found, `BD_linux.py` downloads the matching Linux release automatically into:

   ```sh
   bin/bdinfo/linux/<arch>/bdinfo
   ```

4. **mkbrr for torrent creation**

   Linux scripts use [mkbrr](https://github.com/autobrr/mkbrr).

   FLUP checks for `mkbrr` in `PATH` first. If it is not found, the Linux scripts download the matching Linux release automatically into:

   ```sh
   bin/mkbrr/linux/<arch>/mkbrr
   ```

5. **Configure qBittorrent Web UI**

   Enable the qBittorrent Web UI and set the URL, username, and password in `config_linux.py`.

   <details>
      <summary>Click to see the image</summary>

   ![359194253-071c56f5-1780-40cd-9862-20b4a0b4601c](https://github.com/user-attachments/assets/e8f6c1dd-0e85-4539-a23d-ea7cc84b64da)

   </details>

## Configuration: API Keys, Paths, and Credentials

**Before using FLUP on Linux, configure API keys, credentials, and local service settings in `config_linux.py`.**

Important defaults:

```py
mediainfo_path = "mediainfo"
ffmpeg_path = "ffmpeg"
ffprobe_path = "ffprobe"
bdinfo_path = "bdinfo"
mkbrr_path = "mkbrr"
```

These values use binaries from `PATH`. `bdinfo` and `mkbrr` also have automatic local download fallbacks.

## Running the script in Terminal

Activate the virtual environment first:

```sh
source .venv/bin/activate
```

Run one of the Linux scripts:

```sh
python BD_linux.py
python go_linux.py
```
