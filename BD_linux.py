import os
import random
import subprocess
import requests
import re
import pickle
from bs4 import BeautifulSoup
from config_linux import *
from linux_tools import get_bdinfo_path, get_mkbrr_path

# ===============================
# Let's Go!
# ===============================

# Function to delete specific files from the current directory.
def delete_files():
    extensions_to_delete = ['.txt', '.torrent', '.png']
    directory = os.getcwd()

    for filename in os.listdir(directory):
        if any(filename.endswith(ext) for ext in extensions_to_delete):
            file_path = os.path.join(directory, filename)
            try:
                os.remove(file_path)
            except OSError:
                pass
delete_files()

# Input direct path to Blu-ray folder to be uploaded
input_path = input("Input folder path to Blu-ray: ")
if not os.path.isdir(input_path):
    print("Invalid path.")
    exit()

def duration_to_seconds(duration_str):
    match = re.match(r'^(\d+):(\d{2}):(\d{2})(?:\.(\d+))?$', duration_str.strip())
    if not match:
        raise ValueError(f"Invalid duration format: {duration_str}")

    hours, minutes, seconds, _fraction = match.groups()
    return int(hours) * 3600 + int(minutes) * 60 + int(seconds)

def format_seconds(total_seconds):
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return f"{hours:02}:{minutes:02}:{seconds:02}"

def parse_playlist_candidates(bdinfo_output):
    candidates = []

    for line in bdinfo_output.splitlines():
        playlist_match = re.search(r'\b(\d{5}\.MPLS)\b', line, re.IGNORECASE)
        if not playlist_match:
            continue

        duration_match = re.search(r'(\d{2}:\d{2}:\d{2}(?:\.\d+)?)', line)
        duration_text = duration_match.group(1) if duration_match else None
        duration_seconds = None

        if duration_text:
            try:
                duration_seconds = duration_to_seconds(duration_text)
            except ValueError:
                duration_text = None

        candidates.append({
            'playlist': playlist_match.group(1),
            'duration_text': duration_text,
            'duration_seconds': duration_seconds,
        })

    unique_candidates = []
    seen_playlists = set()
    for candidate in candidates:
        if candidate['playlist'] in seen_playlists:
            continue
        seen_playlists.add(candidate['playlist'])
        unique_candidates.append(candidate)

    return unique_candidates

def select_playlist(playlists):
    if len(playlists) == 1:
        selected_playlist = playlists[0]
        duration_display = selected_playlist['duration_text'] or 'unknown duration'
        print(f"Only one playlist found. Automatically selecting {selected_playlist['playlist']} ({duration_display}).")
        return selected_playlist

    print("Available playlists:")
    for index, playlist in enumerate(playlists, start=1):
        duration_display = playlist['duration_text'] or 'unknown duration'
        print(f"{index}. {playlist['playlist']} - {duration_display}")

    while True:
        selection = input("Select playlist to scan [1]: ").strip()
        if not selection:
            return playlists[0]
        if selection.isdigit():
            selected_index = int(selection)
            if 1 <= selected_index <= len(playlists):
                return playlists[selected_index - 1]
        print("Invalid selection.")

def parse_m2ts_entries(report_path):
    with open(report_path, 'r', encoding='utf-8', errors='replace') as report_file:
        report_text = report_file.read()

    files_section = report_text
    if "FILES:" in report_text and "CHAPTERS:" in report_text:
        files_section = report_text.split("FILES:", 1)[1].split("CHAPTERS:", 1)[0]

    m2ts_entries = []
    seen_files = set()

    for raw_line in files_section.splitlines():
        line = raw_line.strip()
        if not line or ".M2TS" not in line.upper():
            continue

        parts = line.split()
        file_name = None
        duration_text = None

        if len(parts) >= 3:
            candidate_file_name = parts[0]
            if len(parts) >= 4 and parts[1].startswith("(") and parts[1].endswith(")"):
                candidate_file_name = f"{parts[0]} {parts[1]}"
                duration_candidate = parts[2]
            else:
                duration_candidate = parts[2]

            file_match = re.search(r'(\d{5}\.M2TS)', candidate_file_name, re.IGNORECASE)
            if file_match:
                file_name = file_match.group(1).upper()
                duration_text = duration_candidate

        if not file_name or not duration_text:
            file_match = re.search(r'\b(\d{5}\.M2TS)\b', line, re.IGNORECASE)
            duration_match = re.search(r'(\d{1,2}:\d{2}:\d{2}(?:\.\d+)?)', line)
            if not file_match or not duration_match:
                continue
            file_name = file_match.group(1).upper()
            duration_text = duration_match.group(1)

        if file_name in seen_files:
            continue

        try:
            duration_seconds = duration_to_seconds(duration_text)
        except ValueError:
            continue

        seen_files.add(file_name)
        m2ts_entries.append({
            'file_name': file_name,
            'duration_text': duration_text,
            'duration_seconds': duration_seconds,
        })

    return m2ts_entries

def select_screenshot_file(m2ts_entries, bdmv_dir):
    if not m2ts_entries:
        raise ValueError("No valid M2TS entries found in the BDInfo report.")

    sorted_entries = sorted(m2ts_entries, key=lambda entry: (-entry['duration_seconds'], entry['file_name']))

    print("M2TS files found in the selected playlist:")
    for index, entry in enumerate(sorted_entries, start=1):
        print(f"{index}. {entry['file_name']} - {entry['duration_text']}")

    while True:
        selection = input("Select M2TS file for screenshots [1]: ").strip()
        if not selection:
            selected_entry = sorted_entries[0]
            break
        if selection.isdigit():
            selected_index = int(selection)
            if 1 <= selected_index <= len(sorted_entries):
                selected_entry = sorted_entries[selected_index - 1]
                break
        print("Invalid selection.")

    selected_file_path = None
    for root, _, files in os.walk(bdmv_dir):
        for file_name in files:
            if file_name.lower() == selected_entry['file_name'].lower():
                selected_file_path = os.path.join(root, file_name)
                break
        if selected_file_path:
            break

    if not selected_file_path:
        raise ValueError(f"Selected M2TS file not found: {selected_entry['file_name']}")

    print(
        f"Using {selected_entry['file_name']} ({selected_entry['duration_text']}) for screenshots."
    )
    return selected_file_path, selected_entry['duration_seconds']

# Run BDInfoCLI to find the main playlist and generate report
report_output_dir = os.getcwd()
full_report_path = os.path.join(report_output_dir, "fullreport.txt")
summary_report_path = os.path.join(report_output_dir, "summary.txt")

# List playlist
command_list = [get_bdinfo_path(bdinfo_path), "-l", input_path]
result = subprocess.run(command_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

playlists = parse_playlist_candidates(result.stdout)

if not playlists:
    print("No playlists found.")
    if result.stderr:
        print(result.stderr.strip())
    exit()

selected_playlist = select_playlist(playlists)
selected_playlist_name = selected_playlist['playlist']
selected_playlist_duration = selected_playlist['duration_text'] or 'unknown duration'
print(f"Scanning playlist {selected_playlist_name} ({selected_playlist_duration})")

# Run BDInfo on selected playlist
command_scan = [get_bdinfo_path(bdinfo_path), "-m", selected_playlist_name, input_path, report_output_dir]
subprocess.run(command_scan, check=True)

# Looking for the generated report as text file
generated_report_file = None
for file in os.listdir(report_output_dir):
    if file.endswith(".txt"):
        generated_report_file = file
        break

if not generated_report_file:
    print("No report found.")
    exit()

generated_report_path = os.path.join(report_output_dir, generated_report_file)

# Rename report to fullreport.txt
os.rename(generated_report_path, full_report_path)

# Read fullreport.txt and extract "QUICK SUMMARY:"
with open(full_report_path, 'r', encoding='utf-8') as full_report:
    lines = full_report.readlines()

quick_summary_found = False
summary_lines = []

for line in lines:
    if "QUICK SUMMARY:" in line:
        quick_summary_found = True
    if quick_summary_found:
        summary_lines.append(line)

# Saving "QUICK SUMMARY:" in summary.txt
if summary_lines:
    with open(summary_report_path, 'w', encoding='utf-8') as summary_report:
        summary_report.writelines(summary_lines)
    print(f"Summary report saved in {summary_report_path}")
else:
    print("Section 'QUICK SUMMARY:' not found in fullsummary.txt.")
    exit()

bdmv_dir = os.path.join(input_path, "BDMV")
stream_dir = os.path.join(bdmv_dir, "STREAM")
if not os.path.isdir(stream_dir):
    print(r"Not any .m2ts file in BDMV\STREAM.")
    exit()

try:
    m2ts_entries = parse_m2ts_entries(full_report_path)
    screenshot_source_file, duration_in_seconds = select_screenshot_file(m2ts_entries, bdmv_dir)
    print(f"Selected video file duration is {duration_in_seconds} seconds.")
except ValueError as e:
    print(e)
    exit()

# Calculate skip time as 10% of the total duration
skip_time = int(duration_in_seconds * 0.10)

# Calculate valid duration range
valid_duration_in_seconds = duration_in_seconds - 2 * skip_time

if valid_duration_in_seconds <= 0:
    raise ValueError("Video is too short to skip the first and last 10%.")

# Generate random screenshot times
screenshot_times = sorted(random.sample(range(0, valid_duration_in_seconds), 3))
screenshot_times = [time + skip_time for time in screenshot_times]

# Get video resolution using ffprobe
def get_video_resolution(video_file):
    ffprobe_command = [
        globals().get('ffprobe_path', 'ffprobe'),
        '-v', 'error',
        '-select_streams', 'v:0',
        '-show_entries', 'stream=width,height',
        '-of', 'csv=s=x:p=0',
        video_file
    ]
    result = subprocess.run(ffprobe_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    resolution = result.stdout.strip()

    # Elimina liniile multiple și duplicatele
    resolution_lines = resolution.splitlines()
    if len(resolution_lines) > 1:
        resolution = resolution_lines[0]  # Păstrăm doar prima linie

    if result.returncode == 0 and resolution:
        try:
            width, height = map(int, resolution.replace("\n", "").split('x'))  # Elimina newline și split
            return width, height
        except ValueError:
            raise ValueError(f"Invalid resolution format: {resolution}")
    else:
        raise ValueError("Could not get video resolution.")

# FFmpeg screenshot function
def generate_screenshots_with_ffmpeg(video_file, screenshot_times, report_output_dir):
    screenshot_filenames = []
    for idx, time in enumerate(screenshot_times):
        screenshot_filename = os.path.join(report_output_dir, f"screenshot_{idx + 1}.png")
        ffmpeg_command = [
            ffmpeg_path,
            '-ss', str(time),
            '-i', video_file,
            '-frames:v', '1',
            '-q:v', '2',
            '-an',
            '-sn',
            '-y',
            screenshot_filename
        ]
        result = subprocess.run(ffmpeg_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            screenshot_filenames.append(screenshot_filename)
        else:
            print(f"Failed to save screenshot: {screenshot_filename}")
    return screenshot_filenames

# Main function to generate screenshots with FFmpeg
def generate_screenshots(video_file, report_output_dir):
    screenshot_filenames = []  # Inițializăm lista goală de capturi
    try:
        width, height = get_video_resolution(video_file)
        print(f"Video resolution is {width}x{height}")

        if width >= 1920 and height >= 1080:
            print("Using FFmpeg for screenshots...")
            screenshot_filenames = generate_screenshots_with_ffmpeg(video_file, screenshot_times, report_output_dir)
        else:
            raise ValueError("Unsupported resolution for screenshots.")
    except Exception as e:
        print(f"Error generating screenshots: {e}")

    return screenshot_filenames

# Generate screenshots
screenshot_filenames = generate_screenshots(screenshot_source_file, report_output_dir)

if screenshot_filenames:
    print("Screenshots generated successfully:")
    for screenshot_filename in screenshot_filenames:
        print(screenshot_filename)
else:
    print("Failed to generate screenshots.")

# Upload screenshots to img4k.net
uploaded_image_urls = []
for screenshot_filename in screenshot_filenames:
    with open(screenshot_filename, 'rb') as img_file:
        response = requests.post(
            img4k_api_url,
            data={'key': img4k_api_key, 'format': 'json'},
            files={'source': img_file}
        )
        if response.status_code == 200:
            response_data = response.json()
            if response_data['status_code'] == 200:
                image_url = response_data['image']['url_short']
                medium_url = response_data['image']['medium']['url']
                uploaded_image_urls.append((image_url, medium_url))
            else:
                print(f"Error while uploading saved screenshots: {response_data['error']['message']}")
        else:
            print(f"API error: {response.status_code}")

print("Screenshots uploaded to img4k.net")

with open("images.txt", "w") as file:
    bbcode = ' '.join([f"[url={image_url}][img={medium_url}][/url]" for image_url, medium_url in uploaded_image_urls])
    file.write(bbcode)

print("BBCode links saved in images.txt")

# Create description.txt using summary.txt instead of mediainfo.txt
def create_description_txt(summary_file, bbcode_images):
    with open(summary_file, "r", encoding="utf-8") as file:
        summary_content = file.read().strip()

    # Initialize the description with [quote][pre] and directly append formatted content
    description = "[quote][pre]"

    # Skip "QUICK SUMMARY:" line and do formatting
    formatted_summary = []
    lines = summary_content.splitlines()
    for line in lines:
        if "QUICK SUMMARY:" in line:
            continue
        elif line.startswith("Disc Title"):
            formatted_summary.append(f"[b][color=#2980b9]Disc Title[/color][/b]    : {line.split(':', 1)[1].strip()}")
        elif line.startswith("Disc Label"):
            formatted_summary.append(f"[b][color=#2980b9]Disc Label[/color][/b]    : {line.split(':', 1)[1].strip()}")
        elif line.startswith("Disc Size"):
            formatted_summary.append(f"[b][color=#2980b9]Disc Size[/color][/b]     : {line.split(':', 1)[1].strip()}")
        elif line.startswith("Protection"):
            formatted_summary.append(f"[b][color=#2980b9]Protection[/color][/b]    : {line.split(':', 1)[1].strip()}")
        elif line.startswith("Playlist"):
            formatted_summary.append(f"[b][color=#2980b9]Playlist[/color][/b]      : {line.split(':', 1)[1].strip()}")
        elif line.startswith("Size"):
            formatted_summary.append(f"[b][color=#2980b9]Size[/color][/b]          : {line.split(':', 1)[1].strip()}")
        elif line.startswith("Length"):
            formatted_summary.append(f"[b][color=#2980b9]Length[/color][/b]        : {line.split(':', 1)[1].strip()}")
        elif line.startswith("Total Bitrate"):
            formatted_summary.append(f"[b][color=#2980b9]Total Bitrate[/color][/b] : {line.split(':', 1)[1].strip()}")
        elif line.startswith("Video"):
            formatted_summary.append(f"[b][color=#2980b9]Video[/color][/b]         : {line.split(':', 1)[1].strip()}")
        elif line.startswith("Audio"):
            formatted_summary.append(f"[b][color=#2980b9]Audio[/color][/b]         : {line.split(':', 1)[1].strip()}")
        elif line.startswith("Subtitle"):
            formatted_summary.append(f"[b][color=#2980b9]Subtitle[/color][/b]      : {line.split(':', 1)[1].strip()}")
        elif line.startswith("* Subtitle"):
            formatted_summary.append(f"[b][color=#2980b9]* Subtitle[/color][/b]    : {line.split(':', 1)[1].strip()}")
        elif line.startswith("* Audio"):
            formatted_summary.append(f"[b][color=#2980b9]* Audio[/color][/b]       : {line.split(':', 1)[1].strip()}")
        else:
            formatted_summary.append(line.strip())

    # Ensure no leading/trailing whitespace
    formatted_summary_text = "\n".join(formatted_summary).lstrip()

    # Add the formatted content to the description
    description += formatted_summary_text + "[/pre][/quote]\n"

    # Append the screenshots section
    description += "[b][color=red]SCREENS:[/color][/b]\n"
    description += bbcode_images

    # Write the final description to a file
    with open("description.txt", "w", encoding="utf-8") as file:
        file.write("[center]" + description + "[/center]")

with open("images.txt", "r") as file:
    bbcode_images = file.read().strip()

create_description_txt(summary_report_path, bbcode_images)

# Input IMDb link from user
imdb_url = input("IMDb link: ")

# Extract IMDb ID from the URL
imdb_id_match = re.search(r'(tt\d+)', imdb_url)
if imdb_id_match:
    imdb_id = imdb_id_match.group(1)  # Extrage primul grup de capturare, adică ID-ul fără /
else:
    print("Invalid IMDb link.")
    exit()

local_api_url = f"https://imdb.luvbb.me/{imdb_id}"

# Realizează cererea GET la URL-ul local
response = requests.get(local_api_url)
if response.status_code != 200:
    print(f"Failed to fetch data from {local_api_url}. Status code: {response.status_code}")
    exit()

# Parsează răspunsul JSON
data = response.json()

# Debugging: Afișează JSON-ul returnat pentru a verifica structura
#print("JSON data received:", data)

# Extrage genurile din JSON
genres = []
if data and 'Genres' in data:  # Verifică existența cheii 'Genres' cu majusculă
    genres = data['Genres']    # Extrage valoarea asociată

# Debugging: Afișează genurile extrase
#print("Genres extracted:", genres)

# Limitează genurile la primele 3
top_genres = genres[:3]

# Salvarea genurilor în genres.txt
with open("genres.txt", "w", encoding="utf-8") as genres_file:
    genres_file.write(", ".join(top_genres))

# Salvarea link-ului IMDb în imdb.txt
with open("imdb.txt", "w", encoding="utf-8") as imdb_file:
    imdb_file.write(f"[url=https://www.imdb.com/title/{imdb_id}/][img=https://filelist.io/styles/images/imdb.png][/url]")

#print("IMDb link and genres saved.")

# Read the content of description.txt
with open("description.txt", "r", encoding="utf-8") as description_file:
    description_content = description_file.read()

# Read imdb.txt
with open("imdb.txt", "r", encoding="utf-8") as imdb_file:
    imdb_content = imdb_file.read().strip()

# Working IMDb
imdb_url_match = re.search(r'\[url=(https://www\.imdb\.com/title/tt\d+/)\]\[img=.*?\[/url\]', imdb_content)

if imdb_url_match:
    imdb_url = imdb_url_match.group(1)
    imdb_content = f'[url={imdb_url}[][/url]'

insert_position = description_content.find("[center]") + len("[center]")

new_content = (description_content[:insert_position] + "" +
               imdb_content + "\n" + description_content[insert_position:])

# Updating description.txt
with open("description.txt", "w", encoding="utf-8") as description_file:
    description_file.write(new_content)

print("description.txt updated")

# Create .torrent file
def get_total_size(path):
    if os.path.isfile(path):
        return os.path.getsize(path)
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size

def select_piece_length_exponent(total_size):
    size_gib = total_size / (1024 ** 3)  # Convertim în GiB
    if size_gib < 4:
        return "21"
    elif size_gib < 8:
        return "22"
    elif size_gib < 16:
        return "23"
    else:
        return "24"

def create_torrent(input_path):
    total_size = get_total_size(input_path)
    piece_length = select_piece_length_exponent(total_size)

    if os.path.isfile(input_path) or os.path.isdir(input_path):
        output_file = os.path.join(os.getcwd(),
                                   os.path.basename(input_path.rstrip('/\\')).replace('.mkv', '') + ".torrent")
        command = [
            get_mkbrr_path(mkbrr_path),
            'create',
            input_path,
            '--piece-length', piece_length,
            '--output', output_file,
            '--skip-prefix'
        ]

        result = subprocess.run(command, text=True)

        if result.returncode != 0:
            print("Failed to create .torrent with mkbrr.")
            exit()

        print(f"Succesfully .torrent file created -> {output_file}")

        # Rename .torrent file?
        rename_torrent_file(output_file)
    else:
        print("Invalid path")

def rename_torrent_file(torrent_file):
    user_input = input("Rename .torrent? (Y/N): ").strip().lower()

    if user_input == 'y':
        new_name = input("Input new .torrent name (without extension): ").strip()
        new_output_file = os.path.join(os.getcwd(), new_name + ".torrent")
        os.rename(torrent_file, new_output_file)
        print(f"Renamed to -> {new_output_file}")
    else:
        print("Going further!")

# Go
create_torrent(input_path)

# Login
login_url = 'https://filelist.io/login.php'
takelogin_url = 'https://filelist.io/takelogin.php'
upload_url = 'https://filelist.io/takeupload.php'
edit_url = 'https://filelist.io/takeedit.php'
download_base_url = 'https://filelist.io/download.php?id='
cookies_file = 'filelist_cookies.pkl'
check_login_url = 'https://filelist.io/'

username = filelist_username
password = filelist_password


qbittorrent_url = qbittorrent_url
qbittorrent_username = qbittorrent_username
qbittorrent_password = qbittorrent_password


# Inițializăm sesiunea
session = requests.Session()

def save_cookies(session, filename):
    with open(filename, 'wb') as f:
        pickle.dump(session.cookies, f)

def load_cookies(session, filename):
    if os.path.exists(filename):
        with open(filename, 'rb') as f:
            session.cookies.update(pickle.load(f))

def is_logged_in(session):
    """ Verifică dacă utilizatorul este deja logat. """
    response = session.get(check_login_url)
    return 'logout' in response.text  # Dacă există "logout", înseamnă că e logat

def login(session):
    """ Execută login-ul și salvează cookies dacă autentificarea reușește. """
    login_page = session.get(login_url)
    soup = BeautifulSoup(login_page.text, 'html.parser')
    validator = soup.find('input', {'name': 'validator'})['value']

    login_data = {
        'username': username,
        'password': password,
        'validator': validator,
        'unlock': '1'
    }
    login_response = session.post(takelogin_url, data=login_data)

    if 'logout' in login_response.text or login_response.url != takelogin_url:
        print('Auth to FileList OK')
        save_cookies(session, cookies_file)  # Salvăm cookies pentru sesiunea activă
    else:
        print('Auth to FileList Failed')
        print(login_response.text)
        exit()

# Încărcăm cookies și verificăm login-ul
load_cookies(session, cookies_file)

if not is_logged_in(session):
    print("Sesiunea inactiva!")
    login(session)
else:
    print("Sesiunea activă.")

# Locate the torrent file in the current directory
torrent_file_path = None
for file in os.listdir('.'):
    if file.endswith('.torrent'):
        torrent_file_path = file
        break

if not torrent_file_path:
    print('No .torrent file found in the current directory.')
    exit()

title = os.path.basename(torrent_file_path).replace('.torrent', '')

# Prompt user to select the category
print("Category:\n1. Filme Blu-ray\n2. Filme 4k Blu-ray")
category_options = {
    '1': '20', '2': '26'
}
category_choice = input("Input category value: ").strip()
category_value = category_options.get(category_choice, '21')  # Default to 'Seriale HD' if invalid choice

with open("genres.txt", "r", encoding="utf-8") as file:
    genre = file.read().strip()
with open("description.txt", "r", encoding="utf-8") as file:
    description = file.read().strip()
with open("summary.txt", "r", encoding="utf-8") as file:
    summary = file.read().strip()

# Extract IMDb ID from the description if available
imdb_id_match = re.search(r'tt(\d+)', description)
imdb_id = imdb_id_match.group(1) if imdb_id_match else ''

# Uploaded by din config.py
# Daca filelist_uploaded_by = "", FileList va lasa torrentul Anonymous.
uploaded_by = filelist_uploaded_by.strip()

# Prepare the upload payload and files
upload_payload = {
    'name': title,
    'type': category_value,
    'description': genre,
    'descr': description,
    'nfo': summary,
    'imdbid': imdb_id,
    'epenis': uploaded_by,
    'freeleech': '1' if input("FreeLeech? (Y/N): ").strip().lower() == 'y' else '0'
}

files = {
    'file': (os.path.basename(torrent_file_path), open(torrent_file_path, 'rb'))
}

# Perform the upload
upload_response = session.post(upload_url, data=upload_payload, files=files)

# Check if upload was successful
if 'success' in upload_response.text.lower():
    print('Torrent uploaded successfully')
else:
    print('Failed to upload torrent')
    print(upload_response.text)
    exit()

torrent_id_match = re.search(r'download\.php\?id=(\d+)', upload_response.text)
if torrent_id_match:
    torrent_id = torrent_id_match.group(1)
    print(f'Torrent ID: {torrent_id}')

    torrent_url = f'{download_base_url}{torrent_id}'
    response = session.get(torrent_url)
    if response.status_code == 200:
        torrent_filename = f'{torrent_id}.torrent'
        with open(torrent_filename, 'wb') as torrent_file:
            torrent_file.write(response.content)
        print(f'Torrent file downloaded: {torrent_filename}')

        save_path = os.path.dirname(input_path)
        print(f'Save path set to: {save_path}')

        with open(torrent_filename, 'rb') as torrent_file:
            files = {'torrents': torrent_file}
            data = {
                'savepath': save_path,
                'autoTMM': 'false',
                'paused': 'false',
                'root_folder': 'true' if os.path.isdir(input_path) else 'false',
                'dlLimit': '0',
                'upLimit': '0',
                'sequentialDownload': 'false',
                'firstLastPiecePrio': 'false',
                'skip_checking': 'true',
                'tags': 'FL'
            }

            login_data = {'username': qbittorrent_username, 'password': qbittorrent_password}
            session.post(f'{qbittorrent_url}/api/v2/auth/login', data=login_data)

            upload_response = session.post(f'{qbittorrent_url}/api/v2/torrents/add', files=files, data=data)
            if upload_response.status_code == 200 or 'Ok' in upload_response.text:
                print(f'Torrent added to qBittorrent')
            else:
                print(f'Failed to add torrent to qBittorrent: {upload_response.text}')


        edit_url = f'https://filelist.io/edit.php?id={torrent_id}'

        edit_page = session.get(edit_url)
        soup = BeautifulSoup(edit_page.text, 'html.parser')

        form_data = {}
        form = soup.find('form')  # Assuming there's only one form on the page

        for input_tag in form.find_all('input'):
            input_name = input_tag.get('name')
            if input_tag['type'] == 'checkbox':
                if input_name == 'visible':
                    form_data[input_name] = '1'
                elif input_tag.has_attr('checked'):
                    form_data[input_name] = input_tag['value']
            elif input_name:
                form_data[input_name] = input_tag.get('value', '')

        for textarea_tag in form.find_all('textarea'):
            form_data[textarea_tag['name']] = textarea_tag.get_text()

        for select_tag in form.find_all('select'):
            selected_option = select_tag.find('option', selected=True)
            if selected_option:
                form_data[select_tag['name']] = selected_option['value']

        edit_button = form.find('input', {'type': 'submit', 'value': 'Edit!'})

        if edit_button:
            if 'name' in edit_button.attrs:
                form_data[edit_button['name']] = edit_button['value']
            else:
                form_data['submit'] = edit_button['value']

        # Submit the form to `takeedit.php`
        takeedit_url = f'https://filelist.io/takeedit.php'
        edit_response = session.post(takeedit_url, data=form_data)
