import tkinter as tk
from PIL import Image, ImageTk
import requests
from io import BytesIO
import threading
import time

def load_image_from_url(url):
    response = requests.get(url)
    response.raise_for_status()  # Ensure the URL is valid
    return Image.open(BytesIO(response.content))

def show_splash():
    global splash, splash_img
    # Create the root window
    splash = tk.Tk()
    splash.overrideredirect(True)  # Remove the window border
    splash.geometry(f"{image_width}x{image_height}+{center_x}+{center_y}")  # Center the splash

    # Add the image
    canvas = tk.Canvas(splash, width=image_width, height=image_height, highlightthickness=0)
    canvas.pack()
    splash_img = ImageTk.PhotoImage(image)
    canvas.create_image(0, 0, anchor=tk.NW, image=splash_img)

    splash.after(100, run_task_in_background)  # Start loading task
    splash.mainloop()

def run_task_in_background():
    # Run the long-running task in a separate thread
    thread = threading.Thread(target=simulate_loading, daemon=True)
    thread.start()
    splash.after(100, check_task_status, thread)

def check_task_status(thread):
    if thread.is_alive():
        splash.after(100, check_task_status, thread)  # Check again after 100ms
    else:
        splash.destroy()  # Close the splash screen once the task is done

def simulate_loading():
    time.sleep(5)  # Simulate loading (e.g., Chromium initialization)

# Download the image
image_url = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTI2Fe3-ZYwWo76kk6fFaGjpRU1iyiqEv7jJw&s"
image = load_image_from_url(image_url)
image_width, image_height = image.size

# Calculate screen center
root = tk.Tk()
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
root.destroy()
center_x = int((screen_width - image_width) / 2)
center_y = int((screen_height - image_height) / 2)

# Show the splash screen in the main thread
show_splash()
print("Application ready!")
