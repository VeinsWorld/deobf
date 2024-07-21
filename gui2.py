import os
import requests
import tkinter as tk
from tkinter import filedialog
import ttkbootstrap as ttk
from mega import Mega
from methods.ben import BenDeobf
from methods.blank import BlankDeobf
from methods.empyrean import VespyDeobf
from methods.luna import LunaDeobf
from methods.notobf import NotObfuscated
from methods.other import OtherDeobf
from utils.decompile import unzipJava, checkUPX
from utils.pyinstaller.pyinstaller import ExtractPYInstaller
from utils.pyinstaller.pyinstallerExceptions import ExtractionError

# File download functions
def download_file(url):
    if "github.com" in url:
        url = url.replace("github.com", "api.github.com/repos") + "/zipball"
    response = requests.get(url, allow_redirects=True)
    filename = "downloaded_file"
    with open(filename, "wb") as f:
        f.write(response.content)
    return filename

def download_from_mega(url):
    mega = Mega().login()
    return mega.download_url(url)

# GUI message display function
def display_message(message):
    output_text.insert(tk.END, message + "\n")

# Deobfuscation function
def run_deobfuscator(filename, download=False, is_github=False):
    try:
        if is_github or download:
            display_message("[+] Downloading file")
            if "mega.nz" in filename:
                filename = download_from_mega(filename)
            else:
                filename = download_file(filename)
            display_message("[+] File downloaded")

        if not os.path.exists(filename):
            display_message("[-] This file does not exist")
            return

        filename = os.path.abspath(filename)
        webhook = ""

        if filename.endswith(".jar"):
            display_message("[+] Java grabber suspected, scanning strings...")
            javadir = unzipJava(filename)
            webhook = BenDeobf(javadir).Deobfuscate()
        else:
            if checkUPX(filename):
                display_message("[!] File packed with UPX")
            try:
                archive = ExtractPYInstaller(filename)
                obfuscators = [BlankDeobf, LunaDeobf, VespyDeobf, OtherDeobf, NotObfuscated]

                for Deobf in obfuscators:
                    try:
                        display_message(f"[!] Trying {Deobf.__name__} method")
                        deobf = Deobf(os.getcwd(), archive.entrypoints)
                        webhook = deobf.Deobfuscate()
                        if webhook:
                            break
                    except Exception:
                        continue
            except ExtractionError as e:
                display_message(str(e))
                return

        if not webhook:
            display_message("[-] No valid webhook found.")
        else:
            display_message(f"[+] Webhook: {webhook}")

    except Exception as e:
        display_message(f"Error: {str(e)}")

# GUI functions
def select_file():
    file_path = filedialog.askopenfilename()
    file_entry.delete(0, tk.END)
    file_entry.insert(0, file_path)

def start_deobfuscation():
    filename = file_entry.get()
    download = download_var.get()
    is_github = github_var.get()
    output_text.delete(1.0, tk.END)
    run_deobfuscator(filename, download, is_github)

def change_icon():
    icon_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.gif;*.ppm;*.pgm")])
    if icon_path:
        try:
            root.iconphoto(False, tk.PhotoImage(file=icon_path))
            display_message(f"[+] Icon changed to {icon_path}")
        except Exception as e:
            display_message(f"[-] Error setting icon: {str(e)}")

# Create the main window
root = ttk.Window(themename="flatly")
root.title("Deobfuscator GUI")
root.geometry("600x400")

# Create a Notebook widget (tabs)
notebook = ttk.Notebook(root)
notebook.pack(expand=True, fill='both')

# Tab 1 - Deobfuscation
tab1 = ttk.Frame(notebook)
notebook.add(tab1, text="Deobfuscate")

# Create and place widgets in tab1
ttk.Label(tab1, text="File to Deobfuscate (or GitHub URL):", bootstyle="primary").pack(pady=10)

file_entry = ttk.Entry(tab1, width=50)
file_entry.pack(pady=5)

ttk.Button(tab1, text="Browse", command=select_file, bootstyle="success-outline").pack(pady=5)

download_var = tk.BooleanVar()
ttk.Checkbutton(tab1, text="Download the file from a link", variable=download_var, bootstyle="round-toggle").pack(pady=5)

github_var = tk.BooleanVar()
ttk.Checkbutton(tab1, text="Download from GitHub", variable=github_var, bootstyle="round-toggle").pack(pady=5)

ttk.Button(tab1, text="Run Deobfuscator", command=start_deobfuscation, bootstyle="primary-outline").pack(pady=20)

output_text = tk.Text(tab1, height=10, width=70)
output_text.pack(pady=10)

# Tab 2 - Change Icon
tab2 = ttk.Frame(notebook)
notebook.add(tab2, text="Change Icon")

# Create and place widgets in tab2
ttk.Label(tab2, text="Select an icon image file:", bootstyle="primary").pack(pady=10)

ttk.Button(tab2, text="Change Icon", command=change_icon, bootstyle="success-outline").pack(pady=20)

# Start the main loop
root.mainloop()
