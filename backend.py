from flask import Flask, render_template, request, redirect, url_for
import firebase_admin
from firebase_admin import credentials, db
import requests

app = Flask(__name__)

# Initialize Firebase Admin SDK
cred = credentials.Certificate("credentials.json")  # Path to your Firebase service account key
# firebase_admin.initialize_app(cred)
firebase_admin.initialize_app(cred,{"databaseURL":"https://stoody-7ad62-default-rtdb.firebaseio.com/"}) # Firestore Database

#global variables
name = ""
email = ""
safe_email = ""
list = []


# /http://127.0.0.1:5000
@app.route('/', methods=["GET", "POST"])
def gfg():
    global email, name, safe_email
    if request.method == "POST":
        # Getting input with name = name in HTML form
        name = request.form.get("name")
        # Getting input with name = token in HTML form 
        token = request.form.get("token") 
        # Getting input with name = email in HTML form
        email = str(request.form.get("email"))
        print(f"Name: {name}, Token: {token}, Email: {email}")

       # Save the data to Realtime Database
        ref = db.reference('/')  # Create a reference to the 'users' node
        ref.get()
        safe_email = email.replace('.', '_').replace('$', '_')

        db.reference("/emails/").update({safe_email: {"name":name, 
                                                    "token":token}})
        #db.reference("/emails/").update({safe_email: {"token":token}})
        get_classes()

        return redirect(url_for('preferences'))

    return render_template("login.html")

@app.route('/preferences', methods=["GET", "POST"])
def preferences():
    global list
    print("PREFERENCES CALLED")
    if request.method == "POST":
        print("REQUEST METHOD IS POST")
        return getPref()
    return render_template("preferences.html", list = list)


def getPref():
    global safe_email
    print("getPref function called")  # Debugging
    if request.method == "POST":
        print("Inside POST method of getPref")  # Debugging
        course = request.form.get("class")
        noise = request.form.get("noise")
        size = request.form.get("group")  # Ensure this matches your form
        time = request.form.get("times")

        # Update preferences in the database
        db.reference("/emails/" + safe_email + "/classes/" + course).update({"noise": noise})
        db.reference("/emails/" + safe_email + "/classes/" + course).update({"time": time})
        db.reference("/emails/" + safe_email + "/classes/" + course).update({"size": size})

        print(f"Class: {course}, Noise Level: {noise}, Preferred Time: {time}, Group Size: {size}")  # Should print on successful update
        return redirect(url_for('preferences'))
    # global safe_email
    # print("PREF IS CALLED")
    
    # # Getting input data from the preferences form
    # course = request.form.get("class")
    # noise = request.form.get("noise")
    # size = request.form.get("group")  # Changed from size to group to match your form
    # time = request.form.get("times") 

    
    # # Update the Firebase database
    # print()
    # db.reference(f"/emails/{safe_email}/classes/").update({
    #     course: {
    #         "noise": noise,
    #         "time": time,
    #         "size": size
    #     }
    # })
    # print(f"Class: {course}, Noise Level: {noise}, Preferred Time: {time}, Group Size: {size}")

    # return render_template("preferences.html", list=list)  # Render preferences with updated list

    # global safe_email
    # print("PREF IS CALLED")
    # if request.method == "POST":
    #     print("IF WENT THROUGH")
    #     course = request.form.get("class")
    #     # Getting input with name = name in HTML form
    #     noise = request.form.get("noise")
    #     # Getting input with name = token in HTML form 
    #     size = request.form.get("size") 
    #     # Getting input with name = email in HTML form
    #     time = request.form.get("times") 
        
    #     db.reference("/emails/" + safe_email + "/classes/").update({
    #                 course: {
    #                     {"noise": noise},
    #                     {"time": time},
    #                     {"size": size}
    #                 }
    #             })

    #     print(f"Class: {course}, Noise Level: {noise}, Preferred Time: {time}, Group Size: {size}")
    # else:
    #     print("NOOOOOOOOOOOOOOOOOOO")
        
    # return render_template("/preferences.html", list = list)

#         # List of courses
#         course_names = list(db.reference("/emails/" + safe_email + "/classes/").get())
        
        # HTML uses course 


        
        # db.reference("/emails/" + safe_email + "/classes/").update({
        #             course_names from db: {
        #                 "noise": noise,
        #                 "time": time,
        #                 "size": size
        #             }
        #         })

       # Save the data to Realtime Database
        # ref = db.reference('/')  # Create a reference to the 'users' node
        # ref.get()
        # db.reference("/emails/").update({safe_email: {"name":name, 
        #                                             "token":token}})
        # #db.reference("/emails/").update({safe_email: {"token":token}})
        # get_classes()

        # return f"Your name is {name}, your token is {token}, and your email is {email}. Data saved to Firestore."

    # return render_template("/preferences.html")

def keep_after_colon(input_string):
    # Split the string at the first occurrence of ': '
    parts = input_string.split(': ', 1)
    # Return the part after ': ', or an empty string if not found
    return parts[1] 

#@app.route('/', methods=["GET", "POST"])
def list_courses(courses):
        print("got to list_courses")
        global safe_email, list
        print(courses)
        for course in courses:
            print(course)
            if 'name' in course:
                print(course['name'])
                list += [keep_after_colon(str(course['name']))]
                #db.reference("/emails/" + safe_email + "/classes/").update({str(course['name']): {"noise":0} {"times":0} {"size":0}})
                # Assuming safe_email and course are defined appropriately
                db.reference("/emails/" + safe_email + "/classes/").update({
                    keep_after_colon(str(course['name'])): {
                        "noise": 0,
                        "time": 0,
                        "size": 0
                    }
                })
        return render_template('/preferences.html')

        
        #for i in range(len(list)):
         #   db.reference("/emails/" + safe_email + "/classes/").update(list[i])

def get_classes():
    global safe_email
    token = db.reference("/emails/" + safe_email + "/token").get()

    canvas_instance = 'canvas.uw.edu'
    try:
        # API endpoint for fetching courses
        url = f'https://{canvas_instance}/api/v1/courses'
            
        # Set the Authorization header with the Bearer token
        headers = {
            'Authorization': f'Bearer {token}'
        }
            
        # Make the GET request to the Canvas API
        response = requests.get(url, headers=headers)
            
        # Raise an error for any HTTP response codes that are not 200 (OK)
        response.raise_for_status()

        # Parse and print the course data (as JSON)
        courses = response.json()

        list_courses(courses)
            
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"An error occurred: {err}")

    #def __str__(self):
    #   return f"User: {self.name}, Email: {self.email}"



if __name__ == '__main__':
    app.run(debug=True)


# from flask import Flask, render_template, request, jsonify
# # import firebase_admin
# # from firebase_admin import credentials, firestore

# # Flask constructor
# app = Flask(__name__)   
 
# # A decorator used to tell the application
# # which URL is associated function
# @app.route('/login.html', methods =["GET", "POST"])
# def gfg():
#     if request.method == "POST":
#        # getting input with name = fname in HTML form
#        name = request.form.get("name")
#        # getting input with name = lname in HTML form 
#        token = request.form.get("token") 
#        print(name + " " + token)
#        return "Your name is "+ name + token
#     return render_template("form.html")
 
# if __name__=='__main__':
#    app.run()

# app = Flask(__name__)

# # Initialize Firebase Admin SDK
# cred = credentials.Certificate("serviceAccountKey.json")  # Your Firebase private key JSON file
# firebase_admin.initialize_app(cred)
# db = firestore.client()  # Firestore Database

# @app.route('/')
# def index():
#     return render_template('index.html')

# # Route to handle form submission and save data to Firestore
# @app.route('/submit-form', methods=['POST'])
# def submit_form():
#     # Get data from the form submission
#     name = request.form['name']
#     age = request.form['age']

#     # Save the data to Firestore
#     doc_ref = db.collection('users').add({'name': name, 'age': int(age)})

#     return jsonify({"success": True, "message": "Data submitted successfully", "id": doc_ref[1].id})

# if __name__ == '__main__':
#     app.run(debug=True)

# from User import *
# import firebase_admin
# from firebase_admin import db, credentials

# #autheticate to firebase
# cred = credentials.Certificate("credentials.json")
# firebase_admin.initialize_app(cred,{"https://stoody-7ad62-default-rtdb.firebaseio.com/"})

# #creating reference to root node
# ref = db.reference("/")
# #retrieving data from root node (value)
# ref.get()


# #ref.key() gets name of reference
    

    
# name = input("Enter your name: ")
# email = input("Enter your email: ")
# token = input("Enter your token: ")

# def list_courses(self, courses):
#         for course in courses:
#             if 'name' in course:
#                 self.list += (str(course['name']))

# def get_courses(self):
#         access_token = self.token
#         canvas_instance = 'canvas.uw.edu'
#         try:
#             # API endpoint for fetching courses
#             url = f'https://{canvas_instance}/api/v1/courses'
            
#             # Set the Authorization header with the Bearer token
#             headers = {
#                 'Authorization': f'Bearer {access_token}'
#             }
            
#             # Make the GET request to the Canvas API
#             response = requests.get(url, headers=headers)
            
#             # Raise an error for any HTTP response codes that are not 200 (OK)
#             response.raise_for_status()

#             # Parse and print the course data (as JSON)
#             courses = response.json()

#             self.list_courses(courses)
            
#         except requests.exceptions.HTTPError as http_err:
#             print(f"HTTP error occurred: {http_err}")
#         except Exception as err:
#             print(f"An error occurred: {err}")

# db.reference("/name").update(name)
# db.reference("/email").update(email)
# db.reference("/token").update(token)

# db.reference("/course_list").transaction(list_courses)


# user = User(name, email, token)
# print(str(user.get_name()) + " " + str(user.get_email()) + " " + user.get_token())

# user.get_courses()