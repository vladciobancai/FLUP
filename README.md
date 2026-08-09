# 🎬 FLUP

## FileList Semi-Automatic Torrent Uploader

![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge\&logo=python\&logoColor=white)
![Windows](https://img.shields.io/badge/Windows-Supported-0078D6?style=for-the-badge\&logo=windows\&logoColor=white)
![Linux](https://img.shields.io/badge/Linux-Supported-FCC624?style=for-the-badge\&logo=linux\&logoColor=black)
![qBittorrent](https://img.shields.io/badge/qBittorrent-Integration-2F67BA?style=for-the-badge\&logo=qbittorrent\&logoColor=white)

---

### 🚀 About

**FLUP** is a semi-automatic Python toolkit designed to simplify media preparation and torrent upload workflows for **FileList.io**.

It combines media analysis, metadata processing, torrent creation, image hosting and qBittorrent integration into one streamlined workflow.

---

## ✨ Features

* 🎬 Movie processing
* 📺 TV / Series processing
* 💿 Blu-ray support
* 💎 UHD / 4K Blu-ray support
* 📊 MediaInfo integration
* 🎞️ FFmpeg / FFprobe integration
* 💿 BDInfo integration
* 🧲 Torrent creation with mkbrr
* 📡 qBittorrent Web UI integration
* 🌐 FileList workflow integration
* 🖼️ Image hosting integration
* 🪟 Windows support
* 🐧 Linux support

---

## 🧰 Requirements

| Tool                 | Purpose                       |
| -------------------- | ----------------------------- |
| 🐍 Python 3          | Main runtime                  |
| 🎞️ FFmpeg / FFprobe | Video processing and analysis |
| 📊 MediaInfo         | Technical media information   |
| 💿 BDInfo            | Blu-ray analysis              |
| 🧲 mkbrr             | Torrent creation              |
| 📡 qBittorrent       | Torrent client integration    |
| ▶️ VLC               | Media playback                |
| 🌐 Requests          | API / HTTP communication      |
| 🍲 BeautifulSoup4    | HTML parsing                  |

---

## 📦 Installation

Clone the repository:

```bash
git clone https://github.com/luvBB/FLUP.git
cd FLUP
```

Install the Python dependencies:

```bash
pip install -r requirements.txt
```

Dependencies include:

```text
beautifulsoup4
requests
```

---

# 🪟 Windows

## FFmpeg

Download and extract FFmpeg.

Example location:

```text
C:\ffmpeg
```

Add FFmpeg to Windows PATH:

```cmd
setx /m PATH "C:\ffmpeg\bin;%PATH%"
```

---

## MediaInfo

Install **MediaInfo** and make sure its executable path matches the value configured in:

```text
config.py
```

---

## BDInfo

Install or configure **BDInfo** and set the correct path inside:

```text
config.py
```

---

## mkbrr

Download the Windows version of **mkbrr** and configure its location:

```python
mkbrr_path = ""
```

---

## VLC

Install VLC and configure its executable path if required:

```python
vlc_path = ""
```

---

# 🐧 Linux

For Debian / Ubuntu based distributions:

```bash
sudo apt update
sudo apt install python3 python3-venv python3-pip ffmpeg mediainfo
```

Create a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Upgrade pip:

```bash
python -m pip install --upgrade pip
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Linux configuration is located in:

```text
config_linux.py
```

Linux helper functions are located in:

```text
linux_tools.py
```

FLUP can use system binaries available through PATH:

```text
ffmpeg
ffprobe
mediainfo
bdinfo
mkbrr
```

For additional Linux information:

```text
README_LINUX.md
```

---

# ⚙️ Configuration

Before using FLUP, configure the application for your operating system.

### Windows

```text
config.py
```

### Linux

```text
config_linux.py
```

---

## 🌐 API Configuration

Configure the APIs used by FLUP:

```python
img4k_api_url = ""
img4k_api_key = ""

api_key = ""
pin = ""
```

> ⚠️ Never publish your real API keys.

---

## 🌐 FileList Configuration

Configure your FileList credentials:

```python
filelist_username = ""
filelist_password = ""
filelist_uploaded_by = ""
```

> ⚠️ Keep your FileList credentials private.

---

## 📡 qBittorrent

FLUP can communicate with the **qBittorrent Web UI**.

Configure:

```python
qbittorrent_url = "http://localhost:8089"
qbittorrent_username = ""
qbittorrent_password = ""
```

Make sure **Web UI** is enabled in qBittorrent.

The port may be different depending on your local configuration.

---

## 🛠️ External Tools

Verify the paths to the external applications used by FLUP:

```python
mediainfo_path = ""
ffmpeg_path = ""
bdinfo_path = ""
vlc_path = ""
mkbrr_path = ""
```

---

# 📂 Project Structure

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

# 🔄 Workflow

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
FileList
```

---

# 🔐 Security

> [!WARNING]
> Configuration files may contain private credentials.

Never publish:

* API keys
* passwords
* authentication tokens
* FileList credentials
* qBittorrent credentials
* private URLs

Before pushing changes to GitHub, always check:

```text
config.py
config_linux.py
```

---

# 🛠️ Built With

![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square\&logo=python\&logoColor=white)
![FFmpeg](https://img.shields.io/badge/FFmpeg-007808?style=flat-square\&logo=ffmpeg\&logoColor=white)
![qBittorrent](https://img.shields.io/badge/qBittorrent-2F67BA?style=flat-square\&logo=qbittorrent\&logoColor=white)
![Linux](https://img.shields.io/badge/Linux-FCC624?style=flat-square\&logo=linux\&logoColor=black)
![Windows](https://img.shields.io/badge/Windows-0078D6?style=flat-square\&logo=windows\&logoColor=white)

`Python` • `BeautifulSoup4` • `Requests` • `FFmpeg` • `MediaInfo` • `BDInfo` • `mkbrr` • `qBittorrent`

---

# 🤝 Contributing

Contributions, fixes and improvements are welcome.

1. Fork the repository
2. Create a new branch
3. Make your changes
4. Open a Pull Request

Example:

```bash
git checkout -b feature/my-improvement
```

---

# ⭐ Support

If FLUP is useful to you, consider giving the repository a **⭐ Star**.

---

# ❤️ FLUP

**FileList Semi-Automatic Torrent Uploader**

Made with ❤️ by **luvBB**
