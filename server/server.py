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
# from ground_based import ground_based
from users import users
from database import UserDatabase

# from drone_seg.treemonitoring.models import predictor

# --- NEW: Imports for LiDAR Functionality ---
import time
import logging
import uuid # For unique temporary filenames
import numpy as np
from werkzeug.utils import secure_filename
# try:
#     from drone_lidar.processor import (
#         load_point_cloud,
#         segment_and_classify_plot,
#         classify_single_cluster
#         # save_clustered_pcd # Import only if using the save_clusters feature directly here
#     )
#     from drone_lidar.models.pointnet2_cls_ssg import PointNet2HierarchicalCls
# except ImportError as e:
#     # Basic logging setup if imports fail early
#     logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
#     logging.error(f"Failed to import drone_lidar modules: {e}", exc_info=True)
#     logging.error("Ensure drone_lidar module structure exists and is accessible.")
#     PointNet2HierarchicalCls = None
#     load_point_cloud = None
#     segment_and_classify_plot = None
#     classify_single_cluster = None

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
            "http://20.151.90.189:8000",
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
LIDAR_MODEL_CHECKPOINT_PATH = os.environ.get("LIDAR_MODEL_CKPT_PATH", "./drone_lidar/checkpoints/best_model.pt") # Example path
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu") # Define main device
logger.info(f"Using main compute device: {DEVICE}")

# if PointNet2HierarchicalCls is not None: # Check if import succeeded
#     logger.info(f"Attempting to load LiDAR model from: {LIDAR_MODEL_CHECKPOINT_PATH}")
#     if not os.path.exists(LIDAR_MODEL_CHECKPOINT_PATH):
#         logger.error(f"CRITICAL: LiDAR Model checkpoint file not found at '{LIDAR_MODEL_CHECKPOINT_PATH}'. LiDAR endpoints inactive.")
#     else:
#         try:
#             checkpoint = torch.load(LIDAR_MODEL_CHECKPOINT_PATH, map_location=DEVICE)
#             genus_names = checkpoint.get("genus_classes")
#             species_names = checkpoint.get("species_classes")
#             if genus_names is None or species_names is None:
#                 raise KeyError("Checkpoint missing 'genus_classes' or 'species_classes'.")
#             num_genus = len(genus_names)
#             num_species = len(species_names)
#             model_instance = PointNet2HierarchicalCls(num_genus=num_genus, num_species=num_species).to(DEVICE)
#             model_instance.load_state_dict(checkpoint["model_state_dict"])
#             model_instance.eval()
#             LIDAR_MODEL = model_instance
#             LIDAR_GENUS_NAMES = genus_names
#             LIDAR_SPECIES_NAMES = species_names
#             logger.info(f"✅ LiDAR Model loaded ({num_genus} genus, {num_species} species classes).")
#         except KeyError as e:
#             logger.error(f"CRITICAL: LiDAR Checkpoint format error (missing key {e}). LiDAR endpoints inactive.")
#         except Exception as e:
#             logger.error(f"CRITICAL: Unexpected error loading LiDAR model: {e}", exc_info=True)
# else:
#     logger.error("CRITICAL: LiDAR Model class not imported. LiDAR endpoints inactive.")


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

upload_parser_phone = reqparse.RequestParser()
upload_parser_phone.add_argument("file", type=FileStorage, location="files", required=True, help="Upload file")
upload_parser_phone.add_argument("genus", type=str, required=True, help="Genus?")
upload_parser_phone.add_argument("partial", type=str, required=True, help="Partial?")

upload_parser_drone_rgb = reqparse.RequestParser()
upload_parser_drone_rgb.add_argument("file", type=FileStorage, location="files", required=True, help="Upload file")
upload_parser_drone_rgb.add_argument("genus_species", type=str, required=True, help="Genus or Species")
upload_parser_drone_rgb.add_argument("estimate_res", type=float, required=True, help="Estimated Resolution (cm/pixel)") # Changed to float

upload_parser_drone_coord = reqparse.RequestParser()
upload_parser_drone_coord.add_argument("genus_species", type=str, required=True, help="Genus or Species")
upload_parser_drone_coord.add_argument("latitude", type=float, required=True, help="latitude")
upload_parser_drone_coord.add_argument("longitude", type=float, required=True, help="longitude")

upload_parser_drone_seg = reqparse.RequestParser()
upload_parser_drone_seg.add_argument("file", type=FileStorage, location="files", required=True, help="Upload file")
upload_parser_drone_seg.add_argument("scale_factor", type=float, required=True, help="Estimated scale factor")

# --- NEW: LiDAR Parsers ---
DEFAULT_N_POINTS_LIDAR = 2048
DEFAULT_MIN_CLUSTER_POINTS_LIDAR = 50
DEFAULT_GROUND_METHOD_LIDAR = 'simple_z'
DEFAULT_GROUND_PERC_LIDAR = 5.0
DEFAULT_GROUND_OFFSET_LIDAR = 0.5
DEFAULT_DBSCAN_EPS_LIDAR = 0.8
DEFAULT_DBSCAN_MIN_POINTS_LIDAR = 25

upload_parser_lidar_single = reqparse.RequestParser()
upload_parser_lidar_single.add_argument("file", type=FileStorage, location='files', required=True, help='Single tree point cloud (.npy)')
upload_parser_lidar_single.add_argument("n_points", type=int, location='form', default=DEFAULT_N_POINTS_LIDAR, help=f'Number of points to sample (default: {DEFAULT_N_POINTS_LIDAR}).')

upload_parser_lidar_plot = reqparse.RequestParser()
upload_parser_lidar_plot.add_argument("file", type=FileStorage, location='files', required=True, help='Plot point cloud (.npy)')
upload_parser_lidar_plot.add_argument("ground_method", type=str, location='form', default=DEFAULT_GROUND_METHOD_LIDAR, choices=['simple_z', 'none'], help=f'Ground filter (default: {DEFAULT_GROUND_METHOD_LIDAR}).')
upload_parser_lidar_plot.add_argument("ground_perc", type=float, location='form', default=DEFAULT_GROUND_PERC_LIDAR, help=f'Percentile for simple_z (default: {DEFAULT_GROUND_PERC_LIDAR}).')
upload_parser_lidar_plot.add_argument("ground_offset", type=float, location='form', default=DEFAULT_GROUND_OFFSET_LIDAR, help=f'Offset for simple_z (default: {DEFAULT_GROUND_OFFSET_LIDAR}).')
upload_parser_lidar_plot.add_argument("dbscan_eps", type=float, location='form', default=DEFAULT_DBSCAN_EPS_LIDAR, help=f'DBSCAN epsilon (meters, default: {DEFAULT_DBSCAN_EPS_LIDAR}). TUNING REQUIRED.')
upload_parser_lidar_plot.add_argument("dbscan_min_points", type=int, location='form', default=DEFAULT_DBSCAN_MIN_POINTS_LIDAR, help=f'DBSCAN min points (default: {DEFAULT_DBSCAN_MIN_POINTS_LIDAR}). TUNING REQUIRED.')
upload_parser_lidar_plot.add_argument("n_points", type=int, location='form', default=DEFAULT_N_POINTS_LIDAR, help=f'Points per cluster for classifier (default: {DEFAULT_N_POINTS_LIDAR}).')
upload_parser_lidar_plot.add_argument("min_cluster_points", type=int, location='form', default=DEFAULT_MIN_CLUSTER_POINTS_LIDAR, help=f'Min points per cluster to classify (default: {DEFAULT_MIN_CLUSTER_POINTS_LIDAR}).')
# upload_parser_lidar_plot.add_argument("save_clusters", type=bool, location='form', default=False, help='Save clustered PCD file to server?') # Keep optional

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

# @api.route("/upload/phone")
# class UploadPhoneResource(Resource):
#     @jwt_required(optional=True)
#     @api.expect(upload_parser_phone) 
#     def post(self):
#         try:
#             args = upload_parser_phone.parse_args()
#             image_file = args['file']
            
#             genus = args['genus'] == 'Genus'
#             partial = args['partial'] == 'Partial'
            
#             result = ground_based.segment_and_classify(image_file, genus, partial)
            
#             if "predictions" not in result:
#                 return result, 400
              
#             result['genus'] = genus
#             result['partial'] = partial

#             username = get_jwt_identity()
#             if username:
#                 db.add_history_item(username, "ground", result)
            
#             return result, 200
    
#         except Exception as e:
#             return {"message": f"Server error: {str(e)}"}, 500

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

# @api.route("/upload/drone/seg")
# class UploadDroneSegmentResource(Resource):
#     @api.expect(upload_parser_drone_seg)
#     @api.doc(consumes="multipart/form-data")
#     @jwt_required(optional=True)
    
#     def post(self):
#         try:        
#             print("in the drone seg post")
#             args = upload_parser_drone_seg.parse_args()

#             uploaded_file = args['file'] #store the file and feed in the link
#             scale_factor = args['scale_factor'] #determine the crop size by scale_factor * 768

#             if uploaded_file:
#                 save_path = os.path.abspath(os.path.join(os.getcwd(), "drone_seg/uploads"))
#                 file_path = os.path.join(save_path, "predict.png")

#                 if not os.path.exists(save_path):
#                     os.mkdir(save_path)

#                 uploaded_file.save(file_path)

#             result = predictor.predict_drone_segmodel(file_path, scale_factor)

#             """image = cv2.imread(os.path.abspath(os.path.join(os.getcwd(), "drone_seg/predict", "reassembled_image.png")))
#             _, buffer = cv2.imencode('.png', image)
#             if not _:
#                 raise ValueError("Failed to encode image")

#             result_image = base64.b64encode(buffer).decode('utf-8')"""
            
#             if not result:
#                 return None, 400
#             else:
#                 print("returning result image to frontend")

#             username = get_jwt_identity()
#             if username:
#                 db.add_history_item(username, "drone_segment", result)

#             return result, 200
    
#         except Exception as e:
#             return {"message": f"Server error: {str(e)}"}, 500    

# # --- NEW: Drone LiDAR Endpoints ---
# @api.route("/upload/drone/lidar/single_tree")
# class UploadLidarSingleResource(Resource):
#     @jwt_required(optional=True)
#     @api.expect(upload_parser_lidar_single)
#     @api.response(200, 'Classification successful.')
#     @api.response(400, 'Bad request (e.g., invalid file, parameters).')
#     @api.response(500, 'Internal server error.')
#     @api.response(503, 'Service unavailable (LiDAR model not loaded).')
#     def post(self):
#         """Classifies a single pre-segmented tree from LiDAR point cloud upload (.npy)."""
#         start_req_time = time.time()
#         username = get_jwt_identity()
#         logger.info(f"Received /upload/drone/lidar/single_tree from {username or 'Anonymous'}")

#         if LIDAR_MODEL is None:
#             logger.error("LiDAR model is not loaded. Cannot process request.")
#             return {"message": "LiDAR processing service is currently unavailable."}, 503

#         args = upload_parser_lidar_single.parse_args()
#         file = args['file']
#         n_points_sample = args['n_points']

#         if not file or file.filename == '' or not allowed_file(file.filename, ALLOWED_NPY_EXTENSIONS):
#             logger.warning(f"Invalid file provided: {file.filename if file else 'None'}")
#             return {"message": "Invalid or missing file. Must be .npy."}, 400
#         if n_points_sample < 0:
#             logger.warning(f"Invalid n_points parameter: {n_points_sample}")
#             return {"message": "'n_points' parameter must be positive."}, 400
#         if n_points_sample == 0:
#             n_points_sample = 2048

#         temp_filename = None
#         try:
#             # Save temporarily to handle stream correctly with numpy.load
#             safe_filename = secure_filename(file.filename) if file.filename else 'upload.npy'
#             temp_filename = os.path.join(app.config['UPLOAD_FOLDER'], f"{uuid.uuid4()}_{safe_filename}")
#             file.save(temp_filename)
#             logger.debug(f"Saved single tree upload temporarily to {temp_filename}")

#             print('hello --- 1')

#             # --- Process Upload & Classify ---
#             points = load_point_cloud(temp_filename) # Use function from processor

#             print('hello --- 2')

#             # Call function from processor module
#             result = classify_single_cluster(
#                 points, LIDAR_MODEL, DEVICE, n_points_sample, LIDAR_GENUS_NAMES, LIDAR_SPECIES_NAMES
#             )

#             print('hello --- 3')

#             processing_time = time.time() - start_req_time
#             logger.info(f"Drone LiDAR single tree classification successful ({processing_time:.2f}s).")

#             print('hello --- 4')

#             response_data = {
#                 "success": True,
#                 "message": "Classification successful.",
#                 "processing_time_seconds": round(processing_time, 2),
#                 "parameters_used": {"n_points_sample": n_points_sample},
#                 "prediction": result
#             }

#             print('hello --- 5')

#             # Add to history
#             if username:
#                 try:
#                     # Save response data directly to history
#                     db.add_history_item(username, "drone_lidar_single", response_data)
#                     logger.info(f"Added history item 'drone_lidar_single' for user '{username}'.")
#                 except Exception as db_e:
#                     logger.error(f"Failed to save history for user '{username}': {db_e}", exc_info=True)

#             print('hello --- 6')

#             return response_data, 200

#         except (ValueError, IOError, RuntimeError) as e:
#             logger.error(f"Error classifying single LiDAR tree: {e}", exc_info=False) # Less detail for common errors
#             return {"success": False, "message": f"Processing error: {e}"}, 400
#         except Exception as e:
#             logger.error(f"Unexpected server error during single LiDAR tree classification: {e}", exc_info=True)
#             return {"success": False, "message": "Internal server error."}, 500
#         finally:
#             # Clean up temporary file regardless of success/failure
#             cleanup_temp_file(temp_filename)


# @api.route("/drone/lidar/plot")
# class UploadLidarPlotResource(Resource):
#     @jwt_required(optional=True)
#     @api.expect(upload_parser_lidar_plot)
#     @api.response(200, 'Plot processing successful.')
#     @api.response(400, 'Bad request.')
#     @api.response(500, 'Internal server error.')
#     @api.response(503, 'Service unavailable (LiDAR model not loaded).')
#     def post(self):
#         """Segments a LiDAR plot (.npy) and classifies the resulting tree clusters."""
#         start_req_time = time.time()
#         username = get_jwt_identity()
#         logger.info(f"Received /upload/drone/lidar/plot from {username or 'Anonymous'}")

#         if LIDAR_MODEL is None:
#             logger.error("LiDAR model is not loaded. Cannot process plot request.")
#             return {"message": "LiDAR processing service is currently unavailable."}, 503

#         args = upload_parser_lidar_plot.parse_args()
#         file = args['file']

#         if not file or file.filename == '' or not allowed_file(file.filename, ALLOWED_NPY_EXTENSIONS):
#             logger.warning(f"Invalid file provided: {file.filename if file else 'None'}")
#             return {"message": "Invalid or missing file. Must be .npy."}, 400

#         # Validate parameters
#         params_used = { k: v for k, v in args.items() if k != 'file' }
#         try:
#             if args['dbscan_eps'] <= 0: raise ValueError("'dbscan_eps' must be positive.")
#             if args['dbscan_min_points'] <= 0: raise ValueError("'dbscan_min_points' must be positive.")
#             if args['n_points'] <= 0: raise ValueError("'n_points' must be positive.")
#             if args['min_cluster_points'] < 0: raise ValueError("'min_cluster_points' cannot be negative.")
#             if args['ground_method'] not in ['simple_z', 'none']: raise ValueError(f"Invalid 'ground_method'.")
#             logger.info(f"Processing plot with parameters: {params_used}")
#         except ValueError as e:
#             logger.warning(f"Invalid parameter value in request: {e}")
#             return {"message": f"Invalid parameter value: {e}"}, 400

#         temp_filename = None
#         try:
#             safe_filename = secure_filename(file.filename) if file.filename else 'plot.npy'
#             temp_filename = os.path.join(app.config['UPLOAD_FOLDER'], f"{uuid.uuid4()}_{safe_filename}")
#             file.save(temp_filename)
#             logger.info(f"Saved uploaded plot temporarily to {temp_filename}")
#             points = load_point_cloud(temp_filename)

#             # --- Run Segmentation and Classification Pipeline ---
#             classification_results, processed_points, labels = segment_and_classify_plot(
#                 points=points, model=LIDAR_MODEL, device=DEVICE,
#                 genus_names=LIDAR_GENUS_NAMES, species_names=LIDAR_SPECIES_NAMES,
#                 ground_method=args['ground_method'], ground_perc=args['ground_perc'], ground_offset=args['ground_offset'],
#                 dbscan_eps=args['dbscan_eps'], dbscan_min_points=args['dbscan_min_points'],
#                 n_points_sample=args['n_points'], min_cluster_pts_classify=args['min_cluster_points']
#             )

#             # --- Optionally Save Clustered PCD (Server-Side) ---
#             # save_pcd_flag = args.get('save_clusters', False)
#             # if save_pcd_flag and processed_points.shape[0] > 0:
#             #     # Define where to save PCD on the server...
#             #     # ... (logic from previous example using save_clustered_pcd) ...


#             # --- Format and Return Response ---
#             processing_time = time.time() - start_req_time
#             n_found_clusters = len(np.unique(labels[labels >= 0]))
#             message = f"Plot processed. Found {n_found_clusters} potential clusters, classified {len(classification_results)} meeting criteria."
#             if len(classification_results) < n_found_clusters and n_found_clusters > 0:
#                 message += f" ({n_found_clusters - len(classification_results)} clusters below min points)."

#             logger.info(f"Plot processing successful ({processing_time:.2f}s). {message}")
#             response_data = {
#                 "success": True, "message": message,
#                 "processing_time_seconds": round(processing_time, 2),
#                 "parameters_used": params_used,
#                 "predictions": classification_results # List of prediction dicts
#             }

#             # Add to history
#             if username:
#                 try:
#                     # Save response data (which includes parameters and predictions)
#                     db.add_history_item(username, "drone_lidar_plot", response_data)
#                     logger.info(f"Added history item 'drone_lidar_plot' for user '{username}'.")
#                 except Exception as db_e:
#                     logger.error(f"Failed to save history for user '{username}': {db_e}", exc_info=True)

#             return jsonify(response_data), 200

#         except (ValueError, IOError, RuntimeError) as e:
#             logger.error(f"Error processing plot: {e}", exc_info=False)
#             return jsonify({"success": False, "message": f"Processing error: {e}"}), 400
#         except Exception as e:
#             logger.error(f"Unexpected error during plot processing: {e}", exc_info=True)
#             return jsonify({"success": False, "message": "Internal server error during plot processing."}), 500
#         finally:
#             # Clean up temporary file
#             cleanup_temp_file(temp_filename)


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
    allowed_origins = ["http://localhost:5173", "http://127.0.0.1:5173", "http://20.151.90.189:8000", "http://0.0.0.0:8000", "http://127.0.0.1:8000"]
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