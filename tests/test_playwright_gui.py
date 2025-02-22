import tkinter as tk
from playwright.sync_api import sync_playwright
import threading
import time

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


            # Print the title of the page
            title = page.title()
            print(f"Page title: {title}")

            # Close the browser
            browser.close()

    # Run the browser in a separate thread to avoid blocking the Tkinter event loop
    time.sleep(2)
    browser_thread = threading.Thread(target=run_browser)
    browser_thread.start()

def main():
    # Create the Tkinter GUI
    root = create_gui()

    # Launch the browser in a new thread
    launch_browser()

    # Start the Tkinter main loop
    root.mainloop()

if __name__ == "__main__":
    main()