from appointmentapp import app
from flask import render_template, jsonify, request
import os, json

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/addAvailability')
def addAvailability():
    return render_template("add_availability.html")

@app.route('/viewAvailabilities')
def viewAvailabilities():
    directory = 'data'
    use_names = []
    
    if os.path.exists(directory):
        for filename in os.listdir(directory):
            if filename.endswith('.json'):
                use_names.append(filename.replace('.json', ''))
    else:
        raise Exception(f"The directory {directory} does not exist.")


    return render_template('list_available_users.html', names=use_names)


@app.route('/saveAvailability', methods=['POST'])
def save_availability():
    name = request.form.get('name')
    availabilities = request.form.getlist('availability')  # Assuming availability is an array

    if not name or not availabilities:
        bad_response = {
            'status': 'failed',
            'reason': "'name' and 'availabilites' are required fields for the 'saveAvailability' api."
        }
        return jsonify(bad_response), 400

    file_name = f"data/{name}.json"
    is_file = os.path.isfile(file_name)
    if is_file:
        with open(file_name, 'r') as f:
            data = json.load(f)

        with open(file_name, 'w') as f:
            # we already have a list in the file, so take the 'availabilities' list and add it
            data.extend(availabilities)
            json.dump(data, f)
    else:
        with open(file_name, 'w') as f:
            # availabilities comes as a list so just save it as a json
            json.dump(availabilities, f)

    return render_template("home.html")


@app.route('/getAvailabilityForUser/<username>')
def getAvailabilityForUser(username):
    f_name = f"data/{username}.json"
    with open(f_name, 'r') as f:
        data = json.load(f)

    return render_template('availability_per_person.html', user_name=username, availabilities=data)
