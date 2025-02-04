import requests

BASE_URL = "https://uiowa.instructure.com"
ACCESS_TOKEN = "4298~KhVLKCYaVr7RtJrtPPUmFJEnUWJt8EyCYEDBrYytQEurZ296AQZQHXyat2tXfamv"

# Header for authentication
HEADERS = {
    "Authorization": f"Bearer {ACCESS_TOKEN}"
}

# Fetch announcements
def get_announcements(course_id):
    url = f"{BASE_URL}/api/v1/announcements"
    params = {"context_codes[]": f"course_{course_id}"}
    response = requests.get(url, headers=HEADERS, params=params)
    print(response)
    return response.json()

# Fetch assignments
def get_assignments(course_id):
    url = f"{BASE_URL}/api/v1/courses/{course_id}/assignments"
    response = requests.get(url, headers=HEADERS)
    print(response.json())
    return response.json()

# Example usage
course_id = 248000  # Replace with your course ID
announcements = get_announcements(course_id)
assignments = get_assignments(course_id)