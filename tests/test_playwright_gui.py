import tkinter as tk
from playwright.sync_api import sync_playwright
import threading
import time
import os
import sys

def create_gui():
    print("pre root")
    """Creates a simple Tkinter GUI."""
    root = tk.Tk()
    root.title("Tkinter + Playwright Test")
    return root

def launch_browser():
    print("launch")
    """Launches a Playwright browser in a new thread."""
    def run_browser():
        print("run browser")
        with sync_playwright() as p:
            # Launch a browser (Chromium, Firefox, or WebKit)
            browser = p.chromium.launch(headless=False)  # Set headless=False to see the browser
            page = browser.new_page()

            # Navigate to a website
            page.goto("https://example.com")

            print("after goto")

            # Wait for 2 seconds
            time.sleep(2)

            # Print the title of the page
            title = page.title()
            print(f"Page title: {title}")

            # Close the browser
            browser.close()

    # Run the browser in a separate thread to avoid blocking the Tkinter event loop
    browser_thread = threading.Thread(target=run_browser)
    browser_thread.start()

def kill_gui(root):
    """Closes the Tkinter GUI and exits the program."""
    print("Killing GUI and exiting program...")
    root.destroy()  # Close the Tkinter window
    os._exit(0)  # Forcefully exit the program

def main():
    # Create the Tkinter GUI
    root = create_gui()

    # Launch the browser in a new thread
    launch_browser()

    # Schedule the GUI to be killed after 60 seconds
    root.after(10000, kill_gui, root)  # 60000 milliseconds = 60 seconds

    # Start the Tkinter main loop
    root.mainloop()

if __name__ == "__main__":
    main()