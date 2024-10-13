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
current_class = ""
dict_match = {}
good_spots = []


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

        return redirect(url_for('prefLink'))

    return render_template("login.html")

@app.route('/preferences', methods=["GET", "POST"])
def preferences():
    global list
    print("PREFERENCES CALLED")
    if request.method == "POST":
        print("REQUEST METHOD IS POST")
        getPref()
        return redirect(url_for('matches'))
    return render_template("preferences.html", list = list)

@app.route('/preferences')
def prefLink():
    return render_template("preferences.html")

@app.route('/login')
def loginLink():
    return render_template("logßin.html")

@app.route('/matches')
def matches():
    query_emails()
    return render_template("matches.html", dict_match = dict_match)

@app.route('/spots')
def spotsLink():
    suggest_spot()
    print("GOOD SPOTS")
    print(str(len(good_spots)))
    return render_template("spots.html", good_spots = good_spots)



def getPref():
    global safe_email, current_class
    print("getPref function called")  # Debugging
    if request.method == "POST":
        print("Inside POST method of getPref")  # Debugging
        course = request.form.get("class")
        noise = request.form.get("noise")
        size = request.form.get("group")  # Ensure this matches your form
        time = request.form.get("times")

        current_class = course

        # Update preferences in the database
        db.reference("/emails/" + safe_email + "/classes/" + course).update({"noise": noise})
        db.reference("/emails/" + safe_email + "/classes/" + course).update({"time": time})
        db.reference("/emails/" + safe_email + "/classes/" + course).update({"size": size})

        db.reference("/emails/" + safe_email).update({"current": current_class})

        print(f"Class: {course}, Noise Level: {noise}, Preferred Time: {time}, Group Size: {size}")  # Should print on successful update
        return redirect(url_for('preferences'))
    return render_template("matches.html", list = list)


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
                        "noise": "",
                        "time": "",
                        "size": ""
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




def query_emails():
    global dict_match
    emails = db.reference("/emails").get()
    
    for email in emails:
        match_classes(email)
    
    dict_match = dict(sorted(dict_match.items(), key=lambda item: item[1]))
    del dict_match[safe_email]


    # Create a new dictionary with underscores replaced by periods
    dict_match = {k.replace('_', '.'): v for k, v in dict_match.items()}

    dict_match = {k: dict_match[k] for k in reversed(dict_match.keys())}


    
    print(dict_match)
    
            

def match_classes(email):
    global dict_match
    this_class_pref = db.reference(f"/emails/{safe_email}/current").get()
    other_class_pref = db.reference(f"/emails/{email}/current").get()

    #print(f"{safe_email} current class: {this_class_pref}")
    #print(f"{email} current class: {other_class_pref}")

    if this_class_pref is None or other_class_pref is None:
        print(f"No current class found for {safe_email} or {email}.")
        return

    if this_class_pref == other_class_pref:
        dict_match[email] = compare_prefs(email)


# called when classes match
def compare_prefs(email):
    global current_class

    # Fetch preferences for the current user
    this_pref = db.reference(f"/emails/{safe_email}/classes/{current_class}").get()
    other_pref = db.reference(f"/emails/{email}/classes/{current_class}").get()

    # Debugging: Check if preferences are None
    #print(f"Current user preferences: {this_pref}")
    #print(f"Other user preferences for {email}: {other_pref}")

    if this_pref is None or other_pref is None:
        print(f"No preferences found for {safe_email} or {email}.")
        return 0  # Return 0 points if preferences are not found

    # Ensure this_pref and other_pref are dictionaries
    this_noise = this_pref.get("noise")
    this_time = this_pref.get("time")
    this_size = this_pref.get("size")

    other_noise = other_pref.get("noise")
    other_time = other_pref.get("time")
    other_size = other_pref.get("size")

    points = 0

    if this_noise == other_noise:
        points += 2
    if this_time == other_time:
        points += 2
    if this_size == other_size:
        points += 2

    return points
  
def suggest_spot():
    global safe_email, current_class, good_spots
    noise = db.reference(f"/emails/{safe_email}/classes/{current_class}/noise").get()
    size = db.reference(f"/emails/{safe_email}/classes/{current_class}/size").get()

    if noise == "talkative":
        noise = "loud"
    else:
        noise = "quiet"
        
    if size == "less-people":
        size = "small"
    else:
        size = "large"
    

    study_spots = db.reference("/Spots").get()

    for spot in study_spots:
        print("Noise: " + noise + " vs " + str(db.reference("/Spots/" + spot + "/noise").get()) )
        print("Size: " + size + " vs " + str(db.reference("/Spots/" + spot + "/size").get()))
        if str(db.reference("/Spots/" + spot + "/noise").get()) == noise and str(db.reference("/Spots/" + spot + "/size").get()) == size:
            #(study_spots + "/" + spot + "/noise").get()
            print("ADDED SPOT")
            good_spots.append(spot)


    #for i in range(len(study_spots)):
    #    spot = study_spots[i]
    #    print(str(spot.get("noise")))
    #    if str(spot.get("noise")) == noise and str(spot.get("size")) == size:
    #        #(study_spots + "/" + spot + "/noise").get()
    #        good_spots.append(spot)

    #return render_template('spots.html', good_spots = good_spots)      

if __name__ == '__main__':
    app.run(debug=True)
    

        
    