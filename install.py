import os
import sys
import requests
import zipfile
import tarfile
from modules import shared
import launch

def download_chromedriver():
    chromedriver_version = "112.0.5615.49"  # Replace with a suitable version

    base_url = f"https://chromedriver.storage.googleapis.com/{chromedriver_version}"
    
    platform = sys.platform
    if platform == "linux":
        suffix = "linux64"
    elif platform == "darwin":
        suffix = "mac64"
    elif platform == "win32":
        suffix = "win32"
    else:
        raise ValueError("Unsupported platform: {}".format(platform))

    download_url = f"{base_url}/chromedriver_{suffix}.zip"
    response = requests.get(download_url)

    driver_directory = os.path.join(os.path.dirname(os.path.realpath(__file__)), "chromedriver")
    os.makedirs(driver_directory, exist_ok=True)

    archive_path = os.path.join(driver_directory, "chromedriver.zip")
    with open(archive_path, "wb") as f:
        f.write(response.content)

    with zipfile.ZipFile(archive_path, "r") as zip_ref:
        zip_ref.extractall(driver_directory)

    os.remove(archive_path)


if not launch.is_installed("selenium"):
    launch.run_pip("install selenium==3.141.0", "requirements for TestExtension")
    
download_chromedriver()
chromedriver_directory = os.path.join(os.path.dirname(os.path.realpath(__file__)), "chromedriver")
os.environ["PATH"] += os.pathsep + chromedriver_directory