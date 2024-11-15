import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import requests
import os
import subprocess
import threading
import time

# URL of the latest version text file (raw file link from GitHub)
LATEST_GAME_VERSION_URL = "https://raw.githubusercontent.com/SaakethPandu/latest_version.txt/main/latest_version.txt"

# Paths to the version and installation information files
version_file = "installed_version.txt"  # Stores the current installed version
installation_path_file = "installation_path.txt"  # Stores the installation folder

# Base name for the installer file
installer_file_base = "valuable_hour_game_installer"
installer_extension = ".exe"

# Default current version if version file is not found
current_version = "0.0"  # Default version for first-time use

# Function to check for updates from the latest_version.txt file
def check_for_updates():
    global current_version  # Access the global current_version variable
    try:
        # Request the latest version info from the URL
        response = requests.get(LATEST_GAME_VERSION_URL)
        
        if response.status_code == 200:
            lines = response.text.strip().split("\n")
            latest_version = lines[0]  # First line: version number
            download_url = lines[1]  # Second line: download URL

            # Read the current installed version from version_file
            if os.path.exists(version_file):
                with open(version_file, "r") as f:
                    current_version = f.read().strip()

            # Compare current version with the latest version from the server
            if latest_version != current_version:
                update_label.config(text=f"Update Available! (v{latest_version})", foreground="#FF6347")
                download_game(download_url, latest_version)
            else:
                update_label.config(text="You have the latest version!", foreground="#32CD32")
                launch_game()
        else:
            update_label.config(text="Failed to check for updates. Please try again later.", foreground="#FF6347")
    except requests.exceptions.RequestException as e:
        update_label.config(text=f"Network error: {e}", foreground="#FF6347")
        print(f"Network error: {e}")

# Function to download the latest version using the URL from latest_version.txt
def download_game(download_url, version):
    download_path = filedialog.askdirectory(title="Choose Installation Folder")
    if download_path:
        file_name = os.path.join(download_path, f"{installer_file_base}_v{version}{installer_extension}")
        download_thread = threading.Thread(target=download_file, args=(download_url, file_name, version, download_path))
        download_thread.start()

# Function to download the file in the background and update the progress bar with throttling
def download_file(download_url, file_name, version, download_path):
    try:
        response = requests.get(download_url, stream=True)
        if response.status_code == 200:
            total_size = int(response.headers.get('Content-Length', 0))
            downloaded_size = 0
            progress_bar.pack(pady=20)
            progress_bar.config(maximum=total_size, value=0)
            
            buffer_size = 8192  # 8KB buffer size
            with open(file_name, 'wb') as f:
                for chunk in response.iter_content(chunk_size=buffer_size):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        progress_bar['value'] = downloaded_size
                        root.update_idletasks()

            update_label.config(text="Game downloaded! Installing now...", foreground="#32CD32")
            install_game(file_name, version, download_path)
        else:
            update_label.config(text="Failed to download the game.", foreground="#FF6347")
    except Exception as e:
        update_label.config(text=f"Error downloading the game: {e}", foreground="#FF6347")
        print(f"Error downloading the game: {e}")

# Function to install the game after download
def install_game(file_name, version, download_path):
    try:
        subprocess.Popen(file_name, shell=True)
        
        with open(version_file, "w") as version_file_handle:
            version_file_handle.write(version)

        with open(installation_path_file, "w") as path_file_handle:
            path_file_handle.write(download_path)
        
        update_label.config(text="Installing game...", foreground="#FFD700")
    except Exception as e:
        update_label.config(text=f"Failed to install the game: {e}", foreground="#FF6347")
        print(f"Failed to install the game: {e}")

# Function to open the game if it's installed
def launch_game():
    if os.path.exists(game_exe_path):
        subprocess.Popen(game_exe_path)
        update_label.config(text="Launching Game...", foreground="#32CD32")
    else:
        update_label.config(text="Game not found. Please install the game.", foreground="#FF6347")

# Create the main window
root = tk.Tk()
root.title("Valuable Hour Launcher")
root.geometry("600x400")
root.config(bg="#121212")  # Dark background for cyber theme

# Load and display the background image
bg_image = Image.open("background_image.jpg")
bg_image = bg_image.resize((600, 400), Image.LANCZOS)
bg_photo = ImageTk.PhotoImage(bg_image)
bg_label = tk.Label(root, image=bg_photo)
