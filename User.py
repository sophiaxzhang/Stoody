import requests
class User:
    def __init__(self, name, email, token):
        self.name = name
        self.email = email
        self.token = token
        self.list = []
    
    def get_name(self):
        return self.name
    
    def get_email(self):
        return self.email
    
    def get_token(self):
        return self.token
    
    def set_name(self, name):
        self.name = name
    
    def set_email(self, email):
        self.email = email
    

    def list_courses(self, courses):
        for course in courses:
            if 'name' in course:
                self.list += (str(course['name']))
        
        for item in self.list:
            print(item)


    # Function to get course information from Canvas
    def get_courses(self):
        access_token = self.token
        canvas_instance = 'canvas.uw.edu'
        try:
            # API endpoint for fetching courses
            url = f'https://{canvas_instance}/api/v1/courses'
            
            # Set the Authorization header with the Bearer token
            headers = {
                'Authorization': f'Bearer {access_token}'
            }
            
            # Make the GET request to the Canvas API
            response = requests.get(url, headers=headers)
            
            # Raise an error for any HTTP response codes that are not 200 (OK)
            response.raise_for_status()

            # Parse and print the course data (as JSON)
            courses = response.json()

            self.list_courses(courses)
            
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
        except Exception as err:
            print(f"An error occurred: {err}")

        def __str__(self):
            return f"User: {self.name}, Email: {self.email}"

            # Call the function to fetch courses
    
    