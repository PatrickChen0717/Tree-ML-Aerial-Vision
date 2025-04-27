import os
import torch
from werkzeug.datastructures import FileStorage
from flask import Flask, send_from_directory, Blueprint, make_response, request, jsonify
from flask_restx import Api, Resource, reqparse # Added fields for Swagger models
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity

# --- Existing Project Modules ---
# Assuming these imports are correct relative to this file's location
from drone_based_RGB import drone_based_RGB
from users import users
from database import UserDatabase

# --- NEW: Imports for LiDAR Functionality ---
import time
import logging
import uuid # For unique temporary filenames
import numpy as np
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from pathlib import Path
env_path = Path(__file__).resolve().parents[2] / '.env'
load_dotenv(dotenv_path=env_path)

SERVER_IP = os.getenv('SERVER_IP')

# =======================
# Logging Setup (Basic)
# =======================
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')
logger = logging.getLogger('api_server') # Use a specific name

# =======================
# Flask App Initialization
# =======================
app = Flask(__name__)

app.config["JWT_SECRET_KEY"] = "supersecretkey"
app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 7 * 86400
app.config["JWT_COOKIE_CSRF_PROTECT"] = False #SECURITY VULNERABILITY
app.config["JWT_COOKIE_SECURE"] = False
app.config["JWT_COOKIE_HTTPONLY"] = True
app.config["JWT_COOKIE_SAMESITE"] = "Lax"
app.config["JWT_ACCESS_COOKIE_NAME"] = "korotuTL88_cookie"

jwt = JWTManager(app)
CORS(app, resources={
    r"/*": {
        "origins": [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            f"http://{SERVER_IP}",
            "http://0.0.0.0:8000",
            "https://192.222.59.244:443"
        ],
        "supports_credentials": True
    }
})


# --- NEW: Load LiDAR Model Globally ---
LIDAR_MODEL = None
LIDAR_GENUS_NAMES = []
LIDAR_SPECIES_NAMES = []

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu") # Define main device
logger.info(f"Using main compute device: {DEVICE}")

# --- Upload Folder & Static Path Setup ---
app.instance_path = os.path.dirname(os.path.abspath(__file__)) # Path of this script
app.config['UPLOAD_FOLDER'] = os.environ.get('UPLOAD_FOLDER', os.path.join(app.instance_path, 'uploads'))
app.config['MAX_CONTENT_LENGTH'] = int(os.environ.get('MAX_UPLOAD_MB', 500)) * 1024 * 1024
ALLOWED_NPY_EXTENSIONS = {'npy'}
ALLOWED_IMG_EXTENSIONS = {'jpeg', 'jpg', 'png', 'gif', 'bmp', 'webp', 'tiff'}
try:
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    logger.info(f"Upload folder ensured at: {app.config['UPLOAD_FOLDER']}")
except OSError as e:
    logger.error(f"Could not create upload folder '{app.config['UPLOAD_FOLDER']}': {e}")

frontend_path = os.path.abspath(os.path.join(os.getcwd(), "../client/dist"))
app.static_folder = frontend_path

api_bp = Blueprint("api", __name__, url_prefix="/api")
api = Api(api_bp, title="TL88 Server", doc="/docs")
app.register_blueprint(api_bp)

db = UserDatabase()

# --- Request Parsers (Keep Existing) ---
upload_user = reqparse.RequestParser()
upload_user.add_argument("Username", type=str, location="form", required=True, help="Username")
upload_user.add_argument("Password", type=str, location="form", required=True, help="Password")

upload_parser_drone_rgb = reqparse.RequestParser()
upload_parser_drone_rgb.add_argument("file", type=FileStorage, location="files", required=True, help="Upload file")
upload_parser_drone_rgb.add_argument("genus_species", type=str, required=True, help="Genus or Species")
upload_parser_drone_rgb.add_argument("estimate_res", type=float, required=True, help="Estimated Resolution (cm/pixel)") # Changed to float

upload_parser_drone_coord = reqparse.RequestParser()
upload_parser_drone_coord.add_argument("genus_species", type=str, required=True, help="Genus or Species")
upload_parser_drone_coord.add_argument("latitude", type=float, required=True, help="latitude")
upload_parser_drone_coord.add_argument("longitude", type=float, required=True, help="longitude")

# --- History Query Parser ---
history_query_parser = reqparse.RequestParser()
history_query_parser.add_argument('type', type=str, location='args', required=False, help='Filter history by type.')
history_query_parser.add_argument('timestamp', type=float, location='args', required=False, help='Filter history by timestamp (exact match).')


# =======================
# Utility Functions for API
# =======================
def allowed_file(filename, allowed_extensions):
    """Checks if the file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def cleanup_temp_file(filepath):
    """Safely removes a temporary file, logging errors."""
    if filepath and os.path.exists(filepath):
        try:
            os.remove(filepath)
            logger.debug(f"Removed temporary file: {filepath}")
        except OSError as e:
            logger.error(f"Error removing temporary file {filepath}: {e}")

# =======================
# API Resources
# =======================

# --- Authentication Endpoints (Keep Existing) ---
@api.route("/account/create")
class CreateUserResource(Resource):
    @api.expect(upload_user)
    def post(self):

        args = upload_user.parse_args()
        username = args["Username"]
        password = args["Password"]

        result = users.create_account(username, password)

        if result["allow_create"]:
            return result, 200
        return result, 400

@api.route("/login")
class LoginResource(Resource):
    @api.expect(upload_user)
    def post(self):
        args = upload_user.parse_args()
        username = args["Username"]
        password = args["Password"]

        user_data = users.login(username, password)

        if user_data["allow_login"]:
            response = make_response(jsonify({"message": user_data["message"]}))
            response.set_cookie(
                "korotuTL88_cookie", 
                user_data["token"],
                httponly=True,
                secure=False,
                samesite="Lax",
                max_age=7 * 86400,
                path="/"
            )
            
            return response

        return user_data, 401

@api.route("/logout")
class LogoutResource(Resource):
    def post(self):
        return users.logout()

@api.route("/upload/drone/rgb")
class UploadDroneRGBResource(Resource):
    @api.expect(upload_parser_drone_rgb)
    @api.doc(consumes="multipart/form-data")
    @jwt_required(optional=True)
    def post(self):
        try:        
            args = upload_parser_drone_rgb.parse_args()

            uploaded_file = args['file']
            genus_species = args['genus_species']
            estimate_res = args['estimate_res']

            result = drone_based_RGB.classify(uploaded_file, genus_species, estimate_res)

            if "result_image" not in result:
                return result, 400
            
            result["genus_species"] = genus_species
            result["estimate_res"] = estimate_res

            username = get_jwt_identity()
            if username:
                db.add_history_item(username, "drone_rgb", result)

            return result, 200

        except Exception as e:
            import traceback
            traceback.print_exc()
            return {"message": f"Server error: {str(e)}"}, 500   

@api.route('/upload/drone/coord')
class UploadDroneCoordResource(Resource):
    @api.expect(upload_parser_drone_coord)
    @api.doc(consumes="multipart/form-data")
    @jwt_required(optional=True)
    def post(self):
        try: 
            args = upload_parser_drone_coord.parse_args()

            genus_species = args['genus_species']
            lat = float(args['latitude'])
            lon = float(args['longitude'])

            result = drone_based_RGB.classify_coord(genus_species, lat, lon)

            if "result_image" not in result:
                return result, 400
            
            result["genus_species"] = genus_species
            result["coords"] = [lat, lon]

            username = get_jwt_identity()
            if username:
                db.add_history_item(username, "drone_coord", result)

            return result, 200

        except Exception as e:
            return {"message": f"Server error: {str(e)}"}, 500 


# --- History Endpoints (Keep Existing) ---
@api.route('/history')
class HistoryResource(Resource):
    @jwt_required(optional=True)
    @api.expect(history_query_parser)
    def get(self):
        try:
            type = request.args.get('type')
            timestamp = request.args.get('timestamp')
            username = get_jwt_identity()

            if username is None:
                raise Exception('user does not exist')
            
            #if type or timestamp is provided, query database for specific history entry
            if type is not None and timestamp is not None:

                timestamp = float(timestamp)

                if type not in ["ground", "drone_coord", "drone_rgb", "drone_segment"]:
                    raise Exception("type must be one of 'ground', 'drone_coord', drone_segment, or 'drone_rgb'")

                result = db.get_old_classification(username, type, timestamp)

                if not result:
                    result["message"] = "old classification does not exist with type " + str(type) + " and timestamp " + str(timestamp) + "."
                    return result, 404

            else:
                #get list of history from database
                result = db.get_history(username)
                #result = None

                #indicate a lack of history if there is none
                if not result:
                    result["no_history"] = True

            return result, 200
        except Exception as e:
            return {"message": f"server error: {str(e)}"}, 500
        
@api.route('/history/delete_all')
class DeleteAllHistoryResource(Resource):
    @jwt_required()
    def delete(self):
        try:
            username = get_jwt_identity()
            deleted_count = db.delete_all_history(username)

            return {"message": f"Deleted {deleted_count} history items."}, 200

        except Exception as e:
            return {"message": f"Server error: {str(e)}"}, 500

@api.route('/history/delete_one')
class DeleteSingleHistoryResource(Resource):
    @jwt_required()
    @api.expect(history_query_parser)
    def delete(self):
        try:
            username = get_jwt_identity()
            type = request.args.get("type")
            timestamp = request.args.get("timestamp")

            if not type or not timestamp:
                return {"message": "Missing 'type' or 'timestamp' query parameter."}, 400

            try:
                timestamp = float(timestamp)
            except ValueError:
                return {"message": "'timestamp' must be a valid number."}, 400

            deleted_count = db.delete_history_item(username, type, timestamp)

            if deleted_count == 0:
                return {"message": "No matching history item found."}, 404

            return {"message": "History item deleted."}, 200

        except Exception as e:
            return {"message": f"Server error: {str(e)}"}, 500
    
@app.after_request
def after_request(response):
    allowed_origins = ["http://localhost:5173", "http://127.0.0.1:5173", "http://20.151.90.189:8000", "http://0.0.0.0:8000", "http://127.0.0.1:8000", f"http://{SERVER_IP}"]
    request_origin = request.headers.get("Origin")

    if request_origin in allowed_origins:
        response.headers["Access-Control-Allow-Origin"] = request_origin
        
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS, PUT, DELETE"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    
    if "Access-Control-Allow-Credentials" in response.headers:
        del response.headers["Access-Control-Allow-Credentials"]
    
    response.headers["Access-Control-Allow-Credentials"] = "true"
    
    return response

@app.route("/", defaults={"path": ""})
@app.route('/<path:path>')
def catch_all(path):
    if path and path.startswith("api/"):
        return "Not found", 404 
    
    file_path = os.path.join(app.static_folder, path)
    if path and os.path.exists(file_path):
        return send_from_directory(app.static_folder, path)

    return send_from_directory(app.static_folder, "index.html")

@api.route("/hello")
class HelloResource(Resource):
    def get(self):
        return {"message": "Hello from backend!"}
      
@api.route("/auth/check")
class AuthCheckResource(Resource):
    @jwt_required(optional=True)
    def get(self):
        user = get_jwt_identity()
        if user:
            return {"logged_in": True, "user": user}, 200
        return {"logged_in": False, "user": None}, 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)