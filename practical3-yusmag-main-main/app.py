from flask import Flask, render_template, request, jsonify
from models import initialize_database, create_user, create_user_profile, update_user_id, update_user_profile, create_user_image, get_user_profile_and_image_id, create_user_with_details, get_users, get_user_details, get_user_by_id, get_user_details_by_id, update_user_profile,delete_user_by_id, delete_user_profiles_by_id, get_user_role_id, create_user_roles_id
from config import Config, DevelopmentConfig, ProductionConfig
from flask_cors import CORS
import os,json 
from extensions import db
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)


#config_class='DevelopmentConfig'
config_class = os.getenv('FLASK_CONFIG', 'DevelopmentConfig')
app.config.from_object(f'config.{config_class}')

# UPLOAD_FOLDER = 'static/images'
app.config['UPLOAD_FOLDER'] = app.config.get('UPLOAD_FOLDER', 'static/images')
# ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

# Upload folder
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db.init_app(app)

with app.app_context():
    initialize_database()

#Hello world
@app.route("/")
def hello():
    return "Hello, World!"

#REGISTER OR CREATE AN USER
@app.route('/register', methods=['POST'])
def register_user():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')  
    email = data.get('email')
    
    try:
        user_id = create_user(username, password, email)
        return jsonify({"message": "User created successfully", "user_id": user_id}), 201
    except Exception as e:
        # Handle errors and conflicts, such as a duplicate username
        return jsonify({"error": "User creation failed", "details": str(e)}), 400

#CREATE AN USER PROFILE WITH USER ID
@app.route('/user_profile/<int:user_id>', methods=['POST'])
def create_user_profile_by_id(user_id):
    data = request.get_json()
    profile_data = data.get('profile')    
    try:
        # Call your model function to create the user with details
        user_id = create_user_profile(user_id, profile_data)
        return jsonify({"message": "User Profile created successfully", "profile_id": user_id}), 201
    except Exception as e:
        # In a real application, you might want to log this error and return a more generic error message
        return jsonify({"error": "Failed to create user", "details": str(e)}), 400

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.split('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#UPLOAD IMAGE FOR USER
@app.route('/user_images', methods=['POST'])
def create_user_image_by_id():
    file = request.files['image']
    if 'image' not in request.files: 
        return jsonify({"error": "No file part"}), 400
    # if user does not select a file, the browser submits an empty file without filename
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file and allowed_file(file.filename):
        filename =secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        image_url = filepath
        user_id = request.form.get('user_id')
        image_name = request.form.get('image_name')

    try: 
        # CALLING FUNCTION IN MODEL TO CREATE IMAGE WITH user_id
        image_id = create_user_image(user_id, image_name, image_url)
        return jsonify({"message":"User Image created successfully", "image_id": image_id,}), 201
    except Exception as e:
        return jsonify({"error":"Failed to create image", "details": str(e)}), 400


@app.route('/images/<int:user_id>', methods=['GET'])
def get_user_profile_image(user_id):
    user = get_user_profile_and_image_id(user_id)
    if user:
        return jsonify(user)
    else:
        return jsonify({"error": "User not found"}), 404


#GET USER WITH USER ID    
@app.route('/user/<int:user_id>', methods=['GET'])
def user_by_id(user_id):
    user = get_user_by_id(user_id)
    if user:
        return jsonify(user)
    else:
        return jsonify({"error": "User not found"}), 404
 
#GET USER DETAILS WITH USER ID
@app.route('/user_details/<int:user_id>', methods=['GET'])
def user_details_by_id(user_id):
    user = get_user_details_by_id(user_id)
    if user:
        return jsonify(user)
    else:
        return jsonify({"error": "User not found"}), 404

#GET USER PROFILES
@app.route('/user_details_id/<int:user_id>', methods=['GET'])
def get_user_details(user_id):
    user = get_user_by_id(user_id), get_user_details_by_id(user_id)
    if user:
        return jsonify(user)
    else:
        return jsonify({"error": "User not found"}), 404

#UPDATE USER WITH USER ID
# Try change code line
@app.route('/user/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.get_json()
    username = data.get('username')
    #password = data.get('password')  
    email = data.get('email')
    user = update_user_id(user_id, username, email)
    if user:
        return jsonify({"message": "User Profile created successfully", "profile_id": user_id}), 201
    else:
        return jsonify({"error": "User not found"}), 404

#UPDATE USER PROFILE WITH USER ID
@app.route('/user_profile/<int:user_id>', methods=['PUT'])
def update_user_details(user_id):
    data = request.get_json()
    profile_data = data.get('profile')  
    user = update_user_profile(user_id, profile_data['first_name'], profile_data['last_name'], profile_data['contact_no'], profile_data['dob'], profile_data['bio'], profile_data['country'])
    if user:
        return jsonify({"message": "User Profile created successfully", "profile_id": user_id}), 201
    else:
        return jsonify({"error": "User not found"}), 404

#GET USERS ROLES
@app.route('/user_roles/<int:user_id>', methods=['GET'])
def get_user_role(user_id):
    user = get_user_role_id(user_id)
    if user:
        return jsonify(user)
    else:
        return jsonify({"error": "User not found"}), 404

#UPDATE USERS ROLES
@app.route('/update_roles/<int:user_id>', methods=['POST'])
def create_user_roles(user_id):
    data = request.get_json()
    name = data.get('role_name')
    description = data.get('role_description')
    user = create_user_roles_id(user_id, name, description)
    if user:
        return jsonify({"message": "User roles updated successfully", "profile_id": user_id}), 201
    else:
        return jsonify({"error": "User not found"}), 404

#DELETE USER WITH USER ID    
@app.route('/user/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = delete_user_by_id(user_id)
    if user:
        return jsonify({"message": "User ID" + str(user['user_id']) + "has deleted successfully",}), 201
    else:
        return jsonify({"error": "User not found"}), 404

#DELETE USER PROFILES WITH USER ID    
@app.route('/delete_details/<int:user_id>', methods=['DELETE'])
def delete_user_details(user_id):
    user = delete_user_profiles_by_id(user_id)
    if user:
        return jsonify({"message": "User Details deleted successfully",}), 201
    else:
        return jsonify({"error": "User not found"}), 404

#DELETE USER PROFILES
@app.route('/delete_profiles/<int:user_id>', methods=['DELETE'])
def delete_user_profiles(user_id):
    user = delete_user_profiles_by_id(user_id), delete_user_by_id(user_id)
    if user:
        return jsonify({"message": "User Profile deleted successfully",}), 201
    else:
        return jsonify({"error": "User not found"}), 404


# @app.route('/images/<int:user_id>', methods=['POST'])
# def upload_image_for_user(user_id):
#     if 'image' not in request.files:
#         return jsonify({"error" : "No file part"}), 400
    
#     file = request.files['image']
#     if file.filename == '':
#         return jsonify({"error" : "No selected part"}), 400
    
#     if file and ALLOWED_EXTENSIONS(file.filename):
#         filename = secure_filename(file.filename)
#         filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#         file.save(filepath)

#         image_url = filepath
#         user_id = request.form.get('user_id')

#     try:
#         image_id = create_image(user_id, image_url)
#         return jsonify({"message": "Image upload successfully", "user_id": user_id}), 201
#     except Exception as e:
#     # Handle errors and conflicts
#         return jsonify({"error": "User creation failed", "details": str(e)}), 400
# def allowed_file(filename):
#     return '.' in filename and \
#         filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1")
