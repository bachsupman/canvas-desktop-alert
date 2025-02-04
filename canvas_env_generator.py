import os
import sys
import tkinter as tk
from tkinter import messagebox
import requests

def token_exists():
    """
    Returns True if a non-empty CANVAS_ACCESS_TOKEN is found in the .env file.
    """
    if os.path.exists(".env"):
        with open(".env", "r") as f:
            for line in f:
                if line.startswith("CANVAS_ACCESS_TOKEN="):
                    token = line.split("=", 1)[1].strip()
                    if token:  # Token is non-empty
                        return True
    return False

if token_exists():
    print("A Canvas access token was detected in the .env file. Skipping the token generator GUI.")
    sys.exit(0)

def get_canvas_courses(base_url, token):
    """
    Fetches only favorited courses from Canvas using the provided base URL and access token.
    Returns a list of course IDs as strings.
    """
    # Remove any trailing slash from the base URL
    base_url = base_url.rstrip('/')
    # Use the favorites courses endpoint (this endpoint returns only favorited courses)
    url = f"{base_url}/api/v1/users/self/favorites/courses"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch favorited courses: {response.status_code}\n{response.text}")
    
    courses = response.json()
    # Extract course IDs from the courses list
    course_ids = [str(course.get("id")) for course in courses if "id" in course]
    return course_ids

def generate_env():
    """
    Retrieves user inputs, calls the Canvas API to get course IDs,
    and writes them along with the base URL and access token into a .env file.
    Then automatically exits the GUI.
    """
    base_url = entry_base_url.get().strip()
    token = entry_token.get().strip()
    
    if not base_url or not token:
        messagebox.showerror("Input Error", "Both the Canvas Base URL and Access Token are required.")
        return
    
    try:
        course_ids = get_canvas_courses(base_url, token)
    except Exception as e:
        messagebox.showerror("API Error", f"An error occurred while fetching courses:\n{e}")
        return
    
    # Generate .env file content
    env_content = (
        f"CANVAS_BASE_URL={base_url}\n"
        f"CANVAS_ACCESS_TOKEN={token}\n"
        f"CANVAS_COURSE_IDS={','.join(course_ids)}\n"
    )
    
    try:
        with open(".env", "w") as f:
            f.write(env_content)
        messagebox.showinfo("Success", f".env file successfully created with {len(course_ids)} course ID(s).\nThe application will now exit.")
        root.destroy()  # Auto exit the GUI after success.
    except Exception as e:
        messagebox.showerror("File Error", f"An error occurred while writing the .env file:\n{e}")

# --- GUI Setup ---
root = tk.Tk()
root.title("Canvas .env Generator")
root.geometry("500x180")
root.resizable(False, False)

# Canvas Base URL label and entry
label_base_url = tk.Label(root, text="Canvas Base URL:")
label_base_url.grid(row=0, column=0, padx=10, pady=10, sticky="e")
entry_base_url = tk.Entry(root, width=45)
entry_base_url.grid(row=0, column=1, padx=10, pady=10)
entry_base_url.insert(0, "https://canvas.instructure.com")

# Canvas Access Token label and entry
label_token = tk.Label(root, text="Access Token:")
label_token.grid(row=1, column=0, padx=10, pady=10, sticky="e")
entry_token = tk.Entry(root, width=45, show="*")
entry_token.grid(row=1, column=1, padx=10, pady=10)

# Generate .env button
button_generate = tk.Button(root, text="Generate .env", command=generate_env, width=20)
button_generate.grid(row=2, column=0, columnspan=2, pady=15)

# Run the main loop
root.mainloop()