````markdown
<div align="center">

# 🎬 FLUP

### FileList Semi-Automatic Torrent Uploader

<br>

<img src="https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge&logo=python&logoColor=white">
<img src="https://img.shields.io/badge/Windows-Supported-0078D6?style=for-the-badge&logo=windows&logoColor=white">
<img src="https://img.shields.io/badge/Linux-Supported-FCC624?style=for-the-badge&logo=linux&logoColor=black">
<img src="https://img.shields.io/badge/qBittorrent-Integration-2F67BA?style=for-the-badge&logo=qbittorrent&logoColor=white">

<br><br>

**A semi-automatic media preparation and torrent upload toolkit created for FileList.io workflows.**

<br>

[Features](#-features) •
[Requirements](#-requirements) •
[Installation](#-installation) •
[Configuration](#️-configuration) •
[Linux](#-linux-support) •
[Security](#-security)

</div>

---

## 🚀 Overview

**FLUP** is a Python-based toolkit designed to simplify repetitive tasks involved in preparing media releases and torrent uploads.

It combines several external utilities and APIs into one workflow, helping with:

- media analysis
- metadata processing
- Blu-ray information
- torrent creation
- screenshots and image hosting
- qBittorrent integration
- FileList upload preparation

The project supports both **Windows** and **Linux** environments.

---

## ✨ Features

<table>
<tr>
<td width="50%">

### 🎬 Media Processing

- Movie processing
- TV / Series processing
- Blu-ray support
- UHD / 4K Blu-ray support
- Media information extraction
- Video analysis

</td>
<td width="50%">

### ⚡ Automation

- Torrent creation
- Metadata processing
- Image hosting integration
- qBittorrent Web UI integration
- FileList workflow integration
- Configurable external tools

</td>
</tr>
</table>

---

## 🧰 Requirements

FLUP uses several external applications and Python packages.

| Component | Purpose |
|:---|:---|
| 🐍 **Python 3** | Main runtime |
| 🎞️ **FFmpeg / FFprobe** | Video processing and analysis |
| 📊 **MediaInfo** | Technical media information |
| 💿 **BDInfo** | Blu-ray analysis |
| 🧲 **mkbrr** | Torrent creation |
| 📡 **qBittorrent** | Torrent client integration |
| ▶️ **VLC** | Media playback / preview |
| 🌐 **Requests** | HTTP/API communication |
| 🍲 **BeautifulSoup4** | HTML parsing |

---

## 📦 Installation

### 1️⃣ Clone FLUP

```bash
git clone https://github.com/luvBB/FLUP.git
cd FLUP
````

### 2️⃣ Install Python dependencies

```bash
pip install -r requirements.txt
```

Current Python dependencies include:

```text
beautifulsoup4
requests
```

---

<details>
<summary><b>🪟 Windows Setup</b></summary>

<br>

### FFmpeg

Download FFmpeg and extract it to a location such as:

```text
C:\ffmpeg
```

Add the `bin` directory to your Windows PATH:

```cmd
setx /m PATH "C:\ffmpeg\bin;%PATH%"
```

---

### MediaInfo

Install MediaInfo and verify that the executable path matches the value configured inside:

```text
config.py
```

---

### BDInfo

Install or configure BDInfo and set the correct executable path inside:

```text
config.py
```

---

### mkbrr

Download the Windows build of **mkbrr**.

Place it in the desired location and configure:

```python
mkbrr_path = "..."
```

---

### VLC

Install VLC and configure its path if required:

```python
vlc_path = "..."
```

</details>

---

## 🐧 Linux Support

FLUP includes Linux-specific files and configuration.

For Debian / Ubuntu based systems:

```bash
sudo apt update
sudo apt install python3 python3-venv python3-pip ffmpeg mediainfo
```

It is recommended to use a Python virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Upgrade pip:

```bash
python -m pip install --upgrade pip
```

Install FLUP dependencies:

```bash
pip install -r requirements.txt
```

Linux configuration is handled through:

```text
config_linux.py
```

Linux helper functions are available in:

```text
linux_tools.py
```

Depending on your configuration, FLUP can use system binaries available through `PATH`:

```text
ffmpeg
ffprobe
mediainfo
bdinfo
mkbrr
```

For additional Linux-specific information see:

```text
README_LINUX.md
```

---

## ⚙️ Configuration

Before using FLUP, configure the application for your environment.

### 🪟 Windows

Edit:

```text
config.py
```

### 🐧 Linux

Edit:

```text
config_linux.py
```

---

<details>
<summary><b>🌐 API Configuration</b></summary>

<br>

Configure the APIs used by FLUP.

Example:

```python
img4k_api_url = ""
img4k_api_key = ""

api_key = ""
pin = ""
```

Never publish real API credentials.

</details>

---

<details>
<summary><b>🌐 FileList Configuration</b></summary>

<br>

Configure your FileList information:

```python
filelist_username = ""
filelist_password = ""
filelist_uploaded_by = ""
```

> ⚠️ Keep your FileList credentials private.

</details>

---

<details>
<summary><b>📡 qBittorrent Configuration</b></summary>

<br>

FLUP can communicate with the **qBittorrent Web UI**.

Configure:

```python
qbittorrent_url = "http://localhost:8089"
qbittorrent_username = ""
qbittorrent_password = ""
```

The address and port depend on your local qBittorrent configuration.

Make sure **Web UI** is enabled in qBittorrent.

</details>

---

<details>
<summary><b>🛠️ External Tool Paths</b></summary>

<br>

Verify the executable paths used by FLUP:

```python
mediainfo_path = ""
ffmpeg_path = ""
bdinfo_path = ""
vlc_path = ""
mkbrr_path = ""
```

The exact values depend on your operating system and installation locations.

</details>

---

## 📂 Project Structure

```text
FLUP/
│
├── BD.py
├── BD_linux.py
│
├── go.py
├── go_linux.py
│
├── play.py
│
├── config.py
├── config_linux.py
├── linux_tools.py
│
├── requirements.txt
│
├── README.md
├── README_LINUX.md
│
├── BDInfo/
└── mediainfo/
```

---

## 🧩 Main Components

<table>
<tr>
<td>

### 💿 Blu-ray

Blu-ray and UHD media analysis using tools such as:

* BDInfo
* MediaInfo
* FFmpeg

</td>
<td>

### 🎥 Video

Video information and processing using:

* FFmpeg
* FFprobe
* MediaInfo

</td>
</tr>

<tr>
<td>

### 🧲 Torrent

Torrent generation using:

* mkbrr
* qBittorrent

</td>
<td>

### 🌐 Online Services

Integration with:

* FileList
* Metadata APIs
* Image hosting APIs

</td>
</tr>
</table>

---

## 🔐 Security

> [!WARNING]
> Configuration files may contain private credentials.

Never commit or publish:

```text
API keys
Passwords
Authentication tokens
FileList credentials
qBittorrent credentials
Private URLs
```

Before pushing changes to GitHub, always verify:

```text
config.py
config_linux.py
```

If possible, keep private credentials outside the repository.

---

## 💡 Recommended Workflow

```text
Media
  │
  ▼
Media Analysis
  │
  ├── MediaInfo
  ├── FFmpeg / FFprobe
  └── BDInfo
  │
  ▼
Metadata Processing
  │
  ▼
Screenshots / Images
  │
  ▼
Torrent Creation
  │
  ▼
qBittorrent
  │
  ▼
FileList Upload
```

---

## 🛠️ Built With

<div align="center">

<img src="https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white">
<img src="https://img.shields.io/badge/FFmpeg-007808?style=flat-square&logo=ffmpeg&logoColor=white">
<img src="https://img.shields.io/badge/qBittorrent-2F67BA?style=flat-square&logo=qbittorrent&logoColor=white">
<img src="https://img.shields.io/badge/Linux-FCC624?style=flat-square&logo=linux&logoColor=black">
<img src="https://img.shields.io/badge/Windows-0078D6?style=flat-square&logo=windows&logoColor=white">

<br><br>

`Python` • `BeautifulSoup4` • `Requests` • `FFmpeg` • `MediaInfo` • `BDInfo` • `mkbrr` • `qBittorrent`

</div>

---

## 📌 Notes

FLUP is intended to reduce repetitive manual work.

Some functionality depends on:

* external applications
* API availability
* local configuration
* qBittorrent Web UI
* operating system specific paths

Always verify your configuration before running the application.

---

## 🤝 Contributing

Contributions, fixes and improvements are welcome.

You can:

1. Fork the repository
2. Create a new branch
3. Make your changes
4. Open a Pull Request

```bash
git checkout -b feature/my-improvement
```

---

## ⭐ Support

If you find FLUP useful, consider giving the repository a **⭐ Star**.

It helps support the project and makes it easier for others to discover it.

---

<div align="center">

## 🎬 FLUP

**FileList Semi-Automatic Torrent Uploader**

Made with ❤️ by **luvBB**

<br>

[⬆ Back to top](#-flup)

</div>
```
