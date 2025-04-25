import cv2
import os
import shutil
import base64
import numpy as np

from . import droneRgb_genus
from . import droneRgb_species
from . import capture

def encode_image_to_base64_with_size_limit(image):
    scale = 1.0
    max_base64_bytes = 12 * 1024 * 1024

    while True:
        _, buffer = cv2.imencode(".png", image)
        encoded_str = base64.b64encode(buffer).decode("utf-8")

        if len(encoded_str.encode('utf-8')) <= max_base64_bytes:
            return encoded_str

        scale *= 0.9
        new_width = int(image.shape[1] * scale)
        new_height = int(image.shape[0] * scale)

        if new_width < 50 or new_height < 50:
            raise ValueError("Cannot compress image below minimum size limit")

        image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)

def classify(uploaded_file, genus_species, estimate_res):
    # Validate file input
    if uploaded_file is None:
        return {"error": "No file uploaded"}

    # Validate file format
    filename = uploaded_file.filename
    # Check if the request data is properly formatted


    file_format = filename.split('.')[-1].lower() 
    valid_formats = {'jpeg', 'jpg', 'png', 'gif', 'bmp', 'webp', 'tiff'}
    
    if file_format not in valid_formats:
        print(f'ERROR: Unsupported file format: {file_format}')
        return {"error": "Unsupported image format"}

    # Decode base64 image data
    upload_folder = './drone_based_RGB/uploads_drone/'
    output_tile_path = os.path.join(upload_folder, "output_tiles")
    os.makedirs(upload_folder, exist_ok=True)

    # Define file paths
    base_filename = os.path.splitext(filename)[0]
    image_path = os.path.join(upload_folder, f"{base_filename}.{file_format}")
    output_path = os.path.join(upload_folder, f"{base_filename}_scaled.{file_format}")
    result_image_path = os.path.join(upload_folder, f"{base_filename}_result.{file_format}")

    shutil.rmtree(upload_folder, ignore_errors=True)
    os.makedirs(upload_folder, exist_ok=True)

    uploaded_file.save(image_path)
    current_resolution = estimate_res 
    
    if genus_species == "Genus":
        droneRgb_genus.process_image(image_path, output_path, current_resolution)
        droneRgb_genus.slice_image(output_path, output_tile_path)
        label_percentage, shader_grid = droneRgb_genus.reassemble_tiles(output_tile_path, result_image_path, tile_size=304)
    elif genus_species == "Species":
        droneRgb_species.process_image(image_path, output_path, current_resolution)
        droneRgb_species.slice_image(output_path, output_tile_path)
        label_percentage, shader_grid = droneRgb_species.reassemble_tiles(output_tile_path, result_image_path, tile_size=304)


    result_image = cv2.imread(result_image_path) 
    result_img_base64 = encode_image_to_base64_with_size_limit(result_image)

    return {
        "message": "Data received successfully!",
        "result_image": result_img_base64,
        "label_percentage": label_percentage,
        "shader_grid": shader_grid
    }


def classify_coord(genus_species, lat, lon):
    upload_folder = './drone_based_RGB/uploads_drone/'
    output_tile_path = os.path.join(upload_folder, "output_tiles")
    os.makedirs(upload_folder, exist_ok=True)

    GRID_SIZE = 6

    capture.capture_gmap(upload_folder, lat, lon, GRID_SIZE)
    base_filename = "big_google_map.png"
    image_path = f'./drone_based_RGB/uploads_drone/{base_filename}'
    result_image_path = os.path.join(upload_folder, f"{base_filename}_result.png")

    if genus_species == "Genus":
        droneRgb_genus.slice_image(image_path, output_tile_path)
        label_percentage, shader_grid = droneRgb_genus.reassemble_tiles(output_tile_path, result_image_path, tile_size=304)
    elif genus_species == "Species":
        droneRgb_species.slice_image(image_path, output_tile_path)
        label_percentage, shader_grid = droneRgb_species.reassemble_tiles(output_tile_path, result_image_path, tile_size=304)
    
    result_image = cv2.imread(result_image_path) 
    result_img_base64 = encode_image_to_base64_with_size_limit(result_image)

    shutil.rmtree(upload_folder, ignore_errors=True)
    os.makedirs(upload_folder, exist_ok=True)

    return {
        "message": "Data received successfully!",
        "result_image": result_img_base64,
        "label_percentage": label_percentage,
        "shader_grid": shader_grid
    }