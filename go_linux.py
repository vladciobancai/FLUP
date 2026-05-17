import os
import random
import subprocess
import requests
import pickle
import re
from bs4 import BeautifulSoup
from config_linux import *
from linux_tools import get_mkbrr_path

# ===============================
# Let's Go!
# ===============================

# Function to delete specific files from the current directory.
def delete_files():
    extensions_to_delete = ['.txt', '.torrent', '.png']
    directory = os.getcwd()

    def delete_file(file_path):
        try:
            os.remove(file_path)
        except Exception as e:
            pass

    for filename in os.listdir(directory):
        if any(filename.endswith(ext) for ext in extensions_to_delete):
            file_path = os.path.join(directory, filename)
            delete_file(file_path)


delete_files()


# Kill FFmpeg process
def kill_ffmpeg_processes():
    subprocess.run(
        ['pkill', '-TERM', '-x', 'ffmpeg'],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False
    )


kill_ffmpeg_processes()


# Input direct path to file (.mkv) or folder to be uploaded
input_path = input("Input folder or mkv file path to upload: ")

if os.path.isfile(input_path) and input_path.endswith('.mkv'):
    mkv_files = [os.path.basename(input_path)]
    file_location = os.path.dirname(input_path)
elif os.path.isdir(input_path):
    file_location = input_path
    files = os.listdir(file_location)
    mkv_files = [file for file in files if file.endswith('.mkv')]
else:
    print("Invalid path.")
    exit()

if not mkv_files:
    print("No mkv files in this path.")
    exit()

selected_file = random.choice(mkv_files)

mediainfo_command = [mediainfo_path, os.path.join(file_location, selected_file)]
mediainfo_output = subprocess.check_output(mediainfo_command, encoding='utf-8').strip()

mediainfo_output = re.sub(
    r'Complete name\s*:\s*(.*[\\/])([^\\/]+\.mkv)',
    r'Complete name                            : \2',
    mediainfo_output
)

with open("mediainfo.txt", "w", encoding="utf-8") as output_file:
    output_file.write(mediainfo_output)

duration_in_seconds = 0

for line in mediainfo_output.split('\n'):
    if "Duration" in line:
        duration_str = line.split(":")[1].strip()
        try:
            if 'h' in duration_str and 'min' in duration_str:
                # Format: X h Y min
                hours = int(duration_str.split('h')[0].strip())
                minutes = int(duration_str.split('h')[1].split('min')[0].strip())
                duration_in_seconds = (hours * 3600) + (minutes * 60)

            elif 'min' in duration_str and 's' in duration_str:
                # Format: X min Y s
                minutes = int(duration_str.split('min')[0].strip())
                seconds = int(duration_str.split('min')[1].split('s')[0].strip())
                duration_in_seconds = (minutes * 60) + seconds

            elif 'min' in duration_str:
                # Format: X min
                minutes = int(duration_str.split('min')[0].strip())
                duration_in_seconds = minutes * 60

            elif 's' in duration_str and not 'ms' in duration_str:
                # Format: X s
                seconds = int(duration_str.split('s')[0].strip())
                duration_in_seconds = seconds

            elif 'ms' in duration_str:
                # Format: X ms
                milliseconds = int(re.search(r'\d+', duration_str).group())
                duration_in_seconds = milliseconds / 1000

        except (ValueError, IndexError, AttributeError) as e:
            print(f"Failed to parse duration: {duration_str} ({e})")
            exit()

if duration_in_seconds == 0:
    print("I couldn't determine the duration of the video.")
    exit()


screenshot_dir = os.getcwd()
screenshot_times = sorted(random.sample(range(0, int(duration_in_seconds)), 4))
screenshot_filenames = []

for idx, time in enumerate(screenshot_times):
    screenshot_filename = os.path.join(screenshot_dir, f"screenshot_{idx + 1}.png")

    ffmpeg_command = [
        ffmpeg_path,
        '-ss', str(time),
        '-i', os.path.join(file_location, selected_file),
        '-frames:v', '1',
        '-q:v', '2',
        '-an',
        '-sn',
        screenshot_filename
    ]

    process = subprocess.Popen(
        ffmpeg_command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    process.communicate(input=b'\n\n')
    screenshot_filenames.append(screenshot_filename)


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


with open("images.txt", "w", encoding="utf-8") as file:
    bbcode = ' '.join(
        [f"[url={image_url}][img={medium_url}][/url]" for image_url, medium_url in uploaded_image_urls]
    )
    file.write(bbcode)


# Creating description.txt with only image BBCodes
with open("images.txt", "r", encoding="utf-8") as file:
    bbcode_images = file.read().strip()

with open("description.txt", "w", encoding="utf-8") as file:
    file.write(bbcode_images)

print("File description.txt created")


# Input IMDb link from user
imdb_url = input("IMDb link: ")

# Extract IMDb ID from the URL
imdb_id_match = re.search(r'(tt\d+)', imdb_url)

if imdb_id_match:
    imdb_id = imdb_id_match.group(1)
    imdb_id_numeric = imdb_id.replace('tt', '')
else:
    print("Invalid IMDb link.")
    exit()


# Fetch data from local API
local_api_url = f"https://imdb.luvbb.me/{imdb_id}"
response = requests.get(local_api_url)

if response.status_code != 200:
    print(f"Failed to fetch data from {local_api_url}. Status code: {response.status_code}")
    exit()

# Parse the JSON response
data = response.json()

# Extract genres
genres = data.get('Genres', [])

# Limit the genres to the top three
top_genres = genres[:3]

# Save the genres in genres.txt
with open("genres.txt", "w", encoding="utf-8") as genres_file:
    genres_file.write(", ".join(top_genres))


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
    size_gib = total_size / (1024 ** 3)

    # mkbrr foloseste exponent pentru 2^n bytes:
    # 2 MiB  = 2^21
    # 4 MiB  = 2^22
    # 8 MiB  = 2^23
    # 16 MiB = 2^24
    if size_gib < 4:
        return "21"
    elif size_gib < 8:
        return "22"
    elif size_gib < 16:
        return "23"
    else:
        return "24"


def create_torrent(input_path):
    if not os.path.isfile(input_path) and not os.path.isdir(input_path):
        print("Invalid path")
        exit()

    total_size = get_total_size(input_path)
    piece_length = select_piece_length_exponent(total_size)

    output_file = os.path.join(
        os.getcwd(),
        os.path.basename(input_path.rstrip('/\\')).replace('.mkv', '') + ".torrent"
    )

    # mkbrr: https://github.com/autobrr/mkbrr
    command = [
        get_mkbrr_path(mkbrr_path),
        "create",
        input_path,
        "--piece-length", piece_length,
        "--output", output_file,
        "--skip-prefix"
    ]

    result = subprocess.run(command, text=True)

    if result.returncode != 0:
        print("Failed to create .torrent with mkbrr.")
        exit()

    rename_torrent_file(output_file)


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


# Initializam sesiunea
session = requests.Session()


def save_cookies(session, filename):
    with open(filename, 'wb') as f:
        pickle.dump(session.cookies, f)


def load_cookies(session, filename):
    if os.path.exists(filename):
        with open(filename, 'rb') as f:
            session.cookies.update(pickle.load(f))


def is_logged_in(session):
    """Verifica daca utilizatorul este deja logat."""
    response = session.get(check_login_url)
    return 'logout' in response.text


def login(session):
    """Executa login-ul si salveaza cookies daca autentificarea reuseste."""
    login_page = session.get(login_url)
    soup = BeautifulSoup(login_page.text, 'html.parser')

    validator_input = soup.find('input', {'name': 'validator'})

    if not validator_input:
        print("Could not find validator on login page.")
        exit()

    validator = validator_input['value']

    login_data = {
        'username': username,
        'password': password,
        'validator': validator,
        'unlock': '1'
    }

    login_response = session.post(takelogin_url, data=login_data)

    if 'logout' in login_response.text or login_response.url != takelogin_url:
        print('Auth to FileList OK')
        save_cookies(session, cookies_file)
    else:
        print('Auth to FileList Failed')
        print(login_response.text)
        exit()


# Incarcam cookies si verificam login-ul
load_cookies(session, cookies_file)

if not is_logged_in(session):
    print("Sesiunea inactiva!")
    login(session)
else:
    print("Sesiunea activa.")


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
print(
    "Category:\n"
    "1. Anime\n"
    "2. Desene\n"
    "3. Seriale 4K\n"
    "4. Seriale HD\n"
    "5. Seriale SD\n"
    "6. Filme 3D\n"
    "7. Filme 4K\n"
    "8. Filme 4K Blu-Ray\n"
    "9. Filme Blu-Ray\n"
    "10. Filme DVD\n"
    "11. Filme DVD-RO\n"
    "12. Filme HD\n"
    "13. Filme HD-RO\n"
    "14. Filme SD\n"
    "15. K-Drama\n"
    "16. RO Dubbed"
)

category_options = {
    '1': '24',   # Anime
    '2': '15',   # Desene
    '3': '27',   # Seriale 4K
    '4': '21',   # Seriale HD
    '5': '23',   # Seriale SD
    '6': '25',   # Filme 3D
    '7': '6',    # Filme 4K
    '8': '26',   # Filme 4K Blu-Ray
    '9': '20',   # Filme Blu-Ray
    '10': '2',   # Filme DVD
    '11': '3',   # Filme DVD-RO
    '12': '4',   # Filme HD
    '13': '19',  # Filme HD-RO
    '14': '1',   # Filme SD
    '15': '31',  # K-Drama
    '16': '28'   # RO Dubbed
}

category_choice = input("Input category value: ").strip()
category_value = category_options.get(category_choice, '21')


with open("genres.txt", "r", encoding="utf-8") as file:
    genre = file.read().strip()

with open("description.txt", "r", encoding="utf-8") as file:
    description = file.read().strip()

with open("mediainfo.txt", "r", encoding="utf-8") as file:
    mediainfo = file.read().strip()


# Uploaded by din config.py
# Daca filelist_uploaded_by = "", FileList va lasa torrentul Anonymous.
uploaded_by = filelist_uploaded_by.strip()


# Prepare the upload payload and files
upload_payload = {
    'name': title,
    'type': category_value,
    'description': genre,
    'descr': description,
    'nfo': mediainfo,
    'imdbid': imdb_id_numeric,
    'epenis': uploaded_by,
    'freeleech': '1' if input("FreeLeech? (Y/N): ").strip().lower() == 'y' else '0'
}

with open(torrent_file_path, 'rb') as torrent_file:
    files = {
        'file': (os.path.basename(torrent_file_path), torrent_file)
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

    torrent_url = f'{download_base_url}{torrent_id}'
    response = session.get(torrent_url)

    if response.status_code == 200:
        torrent_filename = f'{torrent_id}.torrent'

        with open(torrent_filename, 'wb') as torrent_file:
            torrent_file.write(response.content)

        save_path = os.path.dirname(input_path)

        with open(torrent_filename, 'rb') as torrent_file:
            files = {
                'torrents': torrent_file
            }

            data = {
                'savepath': save_path,
                'autoTMM': 'false',
                'paused': 'false',
                'root_folder': 'true' if os.path.isdir(input_path) else 'false',
                'dlLimit': '0',
                'upLimit': '0',
                'sequentialDownload': 'false',
                'firstLastPiecePrio': 'false'
            }

            login_data = {
                'username': qbittorrent_username,
                'password': qbittorrent_password
            }

            session.post(f'{qbittorrent_url}/api/v2/auth/login', data=login_data)

            upload_response = session.post(
                f'{qbittorrent_url}/api/v2/torrents/add',
                files=files,
                data=data
            )

            if upload_response.status_code == 200 or 'Ok' in upload_response.text:
                print('Torrent added to qBittorrent')
            else:
                print(f'Failed to add torrent to qBittorrent: {upload_response.text}')


        # Start of the editing process
        edit_url = f'https://filelist.io/edit.php?id={torrent_id}'

        edit_page = session.get(edit_url)
        soup = BeautifulSoup(edit_page.text, 'html.parser')

        form_data = {}
        form = soup.find('form')

        if not form:
            print("Could not find edit form.")
            exit()

        # Collect all form fields and only modify `visible`
        for input_tag in form.find_all('input'):
            input_name = input_tag.get('name')
            input_type = input_tag.get('type', '').lower()

            if input_type == 'checkbox':
                if input_name == 'visible':
                    form_data[input_name] = '1'
                elif input_tag.has_attr('checked') and input_name:
                    form_data[input_name] = input_tag.get('value', '1')

            elif input_name:
                form_data[input_name] = input_tag.get('value', '')

        for textarea_tag in form.find_all('textarea'):
            textarea_name = textarea_tag.get('name')

            if textarea_name:
                form_data[textarea_name] = textarea_tag.get_text()

        for select_tag in form.find_all('select'):
            select_name = select_tag.get('name')
            selected_option = select_tag.find('option', selected=True)

            if select_name and selected_option:
                form_data[select_name] = selected_option.get('value', '')

        edit_button = form.find('input', {'type': 'submit', 'value': 'Edit!'})

        if edit_button:
            if 'name' in edit_button.attrs:
                form_data[edit_button['name']] = edit_button['value']
            else:
                form_data['submit'] = edit_button['value']

        # Submit the form to `takeedit.php`
        takeedit_url = 'https://filelist.io/takeedit.php'
        edit_response = session.post(takeedit_url, data=form_data)

        if edit_response.status_code == 200:
            print("Torrent visibility edited successfully.")
        else:
            print(f"Failed to edit torrent visibility. Status code: {edit_response.status_code}")

    else:
        print(f"Failed to download torrent from FileList. Status code: {response.status_code}")
        exit()

else:
    print("Could not find torrent ID after upload.")
    exit()
