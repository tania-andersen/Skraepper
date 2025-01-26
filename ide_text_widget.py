import tkinter as tk
from ctypes import windll

# Enable Windows DPI scaling
windll.shcore.SetProcessDpiAwareness(1)

# Define keywords
keywords = {"filldown", "dropna", "selector", "contains", "regex!", "nodes"}

# Color Scheme
background_color = "#FFFFFF"  # White
keyword_color = "#643973"     # Purple
identifier_color = "#3f7898"  # Blue
value_color = "#609b55"       # Green
default_color = "black"       # Default text color

# Constants
TAB_SIZE = 3  # Number of spaces to insert when Tab is pressed

# Track the current foreground color state
current_foreground_color = default_color

# Track the last known text state
last_text = None

def highlight_syntax(text_widget):
    #print("HILITE!")
    global current_foreground_color, last_text

    # Get the entire text content
    text = text_widget.get("1.0", "end-1c")

    # Check if the text has changed
    if text == last_text:
        return  # Skip highlighting if the text hasn't changed

    last_text = text

    # Check if there is a colon to the left of the cursor
    cursor_index = text_widget.index("insert")
    line, col = map(int, cursor_index.split("."))  # Get line and column of cursor
    line_text = text_widget.get(f"{line}.0", f"{line}.end")  # Get text of the current line

    # Determine if the foreground color needs to change
    if ":" in line_text[:col]:  # If there's a colon to the left of the cursor
        new_foreground_color = value_color
        #print("GREEN!")
    else:
        new_foreground_color = default_color  # Default to black if no colon
        #print("BLACK!")


    # Only update the foreground color if it has changed
    if new_foreground_color != current_foreground_color:
        text_widget.configure(foreground=new_foreground_color)
        current_foreground_color = new_foreground_color

    #REFAC
    # Remove all existing tags (to reset highlighting)
    for tag in text_widget.tag_names():
        text_widget.tag_remove(tag, "1.0", "end")
    #REFAC SLUT

    # Highlight keywords, identifiers, and values
    lines = text.split("\n")  # Split text into lines
    for line_num, line in enumerate(lines, start=1):
        if ":" in line:  # Check if the line contains a colon
            colon_pos = line.find(":")  # Find the position of the colon
            left = line[:colon_pos].strip()  # Left part (identifier)
            right = line[colon_pos + 1:].strip()  # Right part (value)

            # Highlight the colon itself with the "colon" tag
            start_index = f"{line_num}.{colon_pos}"
            end_index = f"{line_num}.{colon_pos + 1}"
            text_widget.tag_add("colon", start_index, end_index)

            # Highlight identifiers (left of colon, not a keyword)
            if left and left not in keywords:
                # Find the exact start position of the identifier
                start_pos = line.find(left)
                start_index = f"{line_num}.{start_pos}"
                end_index = f"{line_num}.{start_pos + len(left)}"
                text_widget.tag_add("identifier", start_index, end_index)

            # Highlight values (right of colon)
            if right:
                # Highlight the entire value in green
                start_index = f"{line_num}.{colon_pos + 1}"
                end_index = f"{line_num}.end"
                text_widget.tag_add("value", start_index, end_index)

                # Highlight `regex!` in values
                if "regex!" in right:
                    # Find the position of `regex!` within the value part
                    regex_start = right.find("regex!")
                    regex_end = regex_start + len("regex!")

                    # Calculate the absolute start and end positions in the line
                    colon_pos = line.find(":")
                    start_index = f"{line_num}.{colon_pos + 1 + regex_start}"
                    end_index = f"{line_num}.{colon_pos + 1 + regex_end}"

                    # Apply the keyword highlight
                    text_widget.tag_add("keyword", start_index, end_index)
                    # Ensure the `keyword` tag takes precedence over the `value` tag
                    text_widget.tag_raise("keyword")

        #REFAC
        else:
            #print(f"No colon in {line}")
            # Explicitly tag lines without a colon in black (default color)
            start_index = f"{line_num}.0"
            end_index = f"{line_num}.end"
            text_widget.tag_add("bad_token", start_index, end_index)
        #REFAC SLUT

        # Highlight keywords (anywhere in the text)
        for keyword in keywords:
            start_index = "1.0"
            while True:
                start_index = text_widget.search(keyword, start_index, stopindex=tk.END)
                if not start_index:
                    break
                end_index = f"{start_index}+{len(keyword)}c"
                text_widget.tag_add("keyword", start_index, end_index)
                start_index = end_index

def schedule_highlighting(text_widget, root, delay=300):
    highlight_syntax(text_widget)
    root.after(delay, schedule_highlighting, text_widget, root, delay)

def handle_return(event):
    """
    Handle the Return key press to preserve indentation (spaces only).
    """
    text_widget = event.widget

    # Get the current cursor position
    cursor_index = text_widget.index("insert")
    line, col = map(int, cursor_index.split("."))  # Get line and column of cursor

    # Get the text of the current line
    line_text = text_widget.get(f"{line}.0", f"{line}.end")

    # Calculate the indentation (leading spaces only)
    indentation = ""
    for char in line_text:
        if char == " ":
            indentation += char
        else:
            break

    # Insert a newline and the same indentation
    text_widget.insert("insert", "\n" + indentation)

    # Move the cursor to the end of the inserted indentation
    text_widget.mark_set("insert", f"{line + 1}.{len(indentation)}")

    # Return "break" to prevent the default behavior of the Return key
    return "break"

def handle_tab(event):
    """
    Handle the Tab key press to insert 3 spaces.
    """
    text_widget = event.widget

    # Insert 3 spaces at the cursor position
    text_widget.insert("insert", " " * TAB_SIZE)

    # Return "break" to prevent the default behavior of the Tab key
    return "break"


def create_simple_ide_textfield(parent):
    """
    Create and configure a Text widget for an IDE-like interface without scrollbars or enclosing frame.
    """
    # Create a Text widget with no line wrapping
    text_widget = tk.Text(parent, wrap="none", font=("Consolas", 10), foreground=default_color)

    # Bind the Return key to the custom handler
    text_widget.bind("<Return>", handle_return)

    # Bind the Tab key to the custom handler
    text_widget.bind("<Tab>", handle_tab)

    # Configure tag colors
    text_widget.tag_config("keyword", foreground=keyword_color)
    text_widget.tag_config("identifier", foreground=identifier_color)
    text_widget.tag_config("value", foreground=value_color)
    text_widget.tag_config("colon", foreground=default_color)  # Ensure colon is always black
    text_widget.tag_config("bad_token", foreground=default_color)  # Ensure colon is always black

    # Start the syntax highlighting loop
    schedule_highlighting(text_widget, parent, delay=300)

    return text_widget

# if __name__ == "__main__":
#     root = tk.Tk()
#     root.title("Syntax Highlighting")
#
#     # Create the IDE text field
#     text_widget = create_ide_textfield(root)
#
#     root.mainloop()