import json
import os
import platform
import shutil
import tarfile
import tempfile
import urllib.request


MKBRR_RELEASE_API = "https://api.github.com/repos/autobrr/mkbrr/releases/latest"
BDINFO_RELEASE_API = "https://api.github.com/repos/Audionut/BDInfoCLI-ng/releases/latest"


def _mkbrr_arch_names():
    arch = platform.machine().lower()

    if arch in {"x86_64", "amd64"}:
        return "amd64", "x86_64"
    if arch in {"aarch64", "arm64"}:
        return "arm64", "arm64"
    if "armv6" in arch:
        return "armv6", "armv6"
    if "arm" in arch:
        return "arm", "arm"

    raise RuntimeError(f"Unsupported Linux architecture for mkbrr: {arch}")


def _bdinfo_arch_name():
    arch = platform.machine().lower()

    if arch in {"x86_64", "amd64"}:
        return "x64"
    if arch in {"aarch64", "arm64"}:
        return "arm64"

    raise RuntimeError(f"Unsupported Linux architecture for BDInfoCLI-ng: {arch}")


def _download_file(url, destination):
    with urllib.request.urlopen(url, timeout=60) as response:
        with open(destination, "wb") as output_file:
            shutil.copyfileobj(response, output_file)


def _extract_binary(archive_path, destination, binary_name):
    with tarfile.open(archive_path, "r:gz") as archive:
        for member in archive.getmembers():
            if os.path.basename(member.name) != binary_name or not member.isfile():
                continue

            source = archive.extractfile(member)
            if source is None:
                continue

            os.makedirs(os.path.dirname(destination), exist_ok=True)
            with source, open(destination, "wb") as output_file:
                shutil.copyfileobj(source, output_file)
            os.chmod(destination, 0o700)
            return

    raise RuntimeError(f"Downloaded archive did not contain a {binary_name} binary")


def _download_mkbrr(destination):
    _, release_arch = _mkbrr_arch_names()
    expected_suffix = f"linux_{release_arch}.tar.gz"

    with urllib.request.urlopen(MKBRR_RELEASE_API, timeout=30) as response:
        release = json.loads(response.read().decode("utf-8"))

    for asset in release.get("assets", []):
        name = asset.get("name", "")
        if name.startswith("mkbrr_") and name.endswith(expected_suffix):
            with tempfile.TemporaryDirectory() as temp_dir:
                archive_path = os.path.join(temp_dir, name)
                print(f"Downloading mkbrr from {asset['browser_download_url']}")
                _download_file(asset["browser_download_url"], archive_path)
                _extract_binary(archive_path, destination, "mkbrr")
            return destination

    raise RuntimeError(f"No mkbrr Linux release asset found for {release_arch}")


def _download_bdinfo(destination):
    release_arch = _bdinfo_arch_name()
    expected_name = f"bdinfo-linux-{release_arch}.tar.gz"

    with urllib.request.urlopen(BDINFO_RELEASE_API, timeout=30) as response:
        release = json.loads(response.read().decode("utf-8"))

    for asset in release.get("assets", []):
        if asset.get("name") == expected_name:
            with tempfile.TemporaryDirectory() as temp_dir:
                archive_path = os.path.join(temp_dir, expected_name)
                print(f"Downloading BDInfoCLI-ng from {asset['browser_download_url']}")
                _download_file(asset["browser_download_url"], archive_path)
                _extract_binary(archive_path, destination, "bdinfo")
            return destination

    raise RuntimeError(f"No BDInfoCLI-ng Linux release asset found for {release_arch}")


def get_mkbrr_path(configured_path="mkbrr"):
    configured_path = configured_path or "mkbrr"

    if os.path.sep in configured_path or (os.path.altsep and os.path.altsep in configured_path):
        if os.path.exists(configured_path):
            os.chmod(configured_path, 0o700)
            return configured_path

    system_mkbrr = shutil.which(configured_path)
    if system_mkbrr:
        return system_mkbrr

    local_arch, _ = _mkbrr_arch_names()
    local_mkbrr = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "bin",
        "mkbrr",
        "linux",
        local_arch,
        "mkbrr"
    )

    if os.path.exists(local_mkbrr):
        os.chmod(local_mkbrr, 0o700)
        return local_mkbrr

    return _download_mkbrr(local_mkbrr)


def get_bdinfo_path(configured_path="bdinfo"):
    configured_path = configured_path or "bdinfo"

    if os.path.sep in configured_path or (os.path.altsep and os.path.altsep in configured_path):
        if os.path.exists(configured_path):
            os.chmod(configured_path, 0o700)
            return configured_path

    system_bdinfo = shutil.which(configured_path)
    if system_bdinfo:
        return system_bdinfo

    local_arch = _bdinfo_arch_name()
    local_bdinfo = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "bin",
        "bdinfo",
        "linux",
        local_arch,
        "bdinfo"
    )

    if os.path.exists(local_bdinfo):
        os.chmod(local_bdinfo, 0o700)
        return local_bdinfo

    return _download_bdinfo(local_bdinfo)
