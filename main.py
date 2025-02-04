import os
import tkinter as tk
from tkinter import ttk
import requests
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables using the .env file
load_dotenv()
CANVAS_BASE_URL = os.getenv("CANVAS_BASE_URL")
ACCESS_TOKEN = os.getenv("CANVAS_ACCESS_TOKEN")
COURSE_IDS_STR = os.getenv("CANVAS_COURSE_IDS", "")
COURSE_IDS = [cid.strip() for cid in COURSE_IDS_STR.split(",") if cid.strip()]

def get_course_details(course_id):
    """
    Retrieves course details (like the name) from Canvas.
    """
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    url = f"{CANVAS_BASE_URL}/api/v1/courses/{course_id}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return {"name": f"Course {course_id}"}

def fetch_course_announcements(course_id):
    """
    Fetches announcements for a specific course and sorts them by posted_at date (newest first).
    """
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    url = f"{CANVAS_BASE_URL}/api/v1/courses/{course_id}/discussion_topics?only_announcements=true"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return []
    announcements = response.json()

    def parse_date(ann):
        date_str = ann.get("posted_at")
        try:
            return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ") if date_str else datetime.min
        except Exception:
            return datetime.min

    # Sort so the newest announcements appear first.
    announcements_sorted = sorted(announcements, key=parse_date, reverse=True)
    return announcements_sorted

def fetch_course_assignments(course_id):
    """
    Fetches assignments for a specific course and sorts them by their posting date (using created_at)
    so that the newest assignments appear at the top.
    """
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    url = f"{CANVAS_BASE_URL}/api/v1/courses/{course_id}/assignments"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return []
    assignments = response.json()

    def parse_date(assign):
        date_str = assign.get("created_at")
        try:
            return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ") if date_str else datetime.min
        except Exception:
            return datetime.min

    # Sort so the newest assignments appear first.
    assignments_sorted = sorted(assignments, key=parse_date, reverse=True)
    return assignments_sorted

def format_date(date_str):
    """
    Converts an ISO date string to a more user-friendly format.
    """
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
        return dt.strftime("%b %d, %Y %I:%M %p")
    except Exception:
        return date_str

def refresh_data():
    """
    Clears and repopulates the Treeviews for announcements and assignments,
    grouping items by course and sorting them by their posting date.
    """
    # Clear existing data
    for item in announcement_tree.get_children():
        announcement_tree.delete(item)
    for item in assignment_tree.get_children():
        assignment_tree.delete(item)

    # Process each course in the list.
    for course_id in COURSE_IDS:
        course_details = get_course_details(course_id)
        course_name = course_details.get("name", f"Course {course_id}")

        # --- Announcements ---
        announcements = fetch_course_announcements(course_id)
        if announcements:
            parent_ann = announcement_tree.insert("", "end", text=course_name, open=True)
            for ann in announcements:
                title = ann.get("title", "No Title")
                posted_at = ann.get("posted_at", "")
                formatted_posted = format_date(posted_at) if posted_at else "N/A"
                announcement_tree.insert(parent_ann, "end", values=(title, formatted_posted))

        # --- Assignments ---
        assignments = fetch_course_assignments(course_id)
        if assignments:
            parent_assign = assignment_tree.insert("", "end", text=course_name, open=True)
            for assign in assignments:
                name = assign.get("name", "No Name")
                created_at = assign.get("created_at")
                formatted_created = format_date(created_at) if created_at else "N/A"
                assignment_tree.insert(parent_assign, "end", values=(name, formatted_created))

    status_label.config(text="Last updated: " + datetime.now().strftime("%I:%M %p"))

# --- GUI Setup ---
root = tk.Tk()
root.title("Canvas Updates")
root.geometry("700x500")
root.resizable(True, True)

style = ttk.Style(root)
style.theme_use("clam")
style.configure("Treeview.Heading", font=("Helvetica", 12, "bold"), foreground="#333", background="#ececec")
style.configure("Treeview", font=("Helvetica", 10), rowheight=25)

menubar = tk.Menu(root)
root.config(menu=menubar)

file_menu = tk.Menu(menubar, tearoff=0)
file_menu.add_command(label="Refresh", command=refresh_data)
file_menu.add_separator()
file_menu.add_command(label="Exit", command=root.quit)
menubar.add_cascade(label="File", menu=file_menu)

notebook = ttk.Notebook(root)
notebook.pack(expand=True, fill="both", padx=10, pady=10)

# --- Announcements Tab ---
frame_announcements = ttk.Frame(notebook)
notebook.add(frame_announcements, text="Announcements")

announcement_tree = ttk.Treeview(frame_announcements, columns=("Title", "Posted At"))
announcement_tree.heading("#0", text="Course")
announcement_tree.heading("Title", text="Title")
announcement_tree.heading("Posted At", text="Posted At")
announcement_tree.column("#0", width=300, anchor="w")
announcement_tree.column("Title", width=210)  # Reduced from 350 to 210 (3/5 of original)
announcement_tree.column("Posted At", width=120)
announcement_tree.pack(expand=True, fill="both", padx=10, pady=10)

# --- Assignments Tab ---
frame_assignments = ttk.Frame(notebook)
notebook.add(frame_assignments, text="Assignments")

assignment_tree = ttk.Treeview(frame_assignments, columns=("Name", "Posted At"))
assignment_tree.heading("#0", text="Course")
assignment_tree.heading("Name", text="Assignment Name")
assignment_tree.heading("Posted At", text="Posted At")
assignment_tree.column("#0", width=300, anchor="w")
assignment_tree.column("Name", width=210)  # Reduced from 350 to 210 (3/5 of original)
assignment_tree.column("Posted At", width=120)
assignment_tree.pack(expand=True, fill="both", padx=10, pady=10)

# Refresh Button and Status Label
control_frame = ttk.Frame(root)
control_frame.pack(fill="x", padx=10, pady=5)

refresh_button = ttk.Button(control_frame, text="Refresh Data", command=refresh_data)
refresh_button.pack(side="left", padx=(0, 10))

status_label = ttk.Label(control_frame, text="Last updated: Never")
status_label.pack(side="right")

# Initial data load
refresh_data()

root.mainloop()