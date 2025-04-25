import requests
from PIL import Image
import io
import math
import os

def get_lat_lon_offset(lat, zoom, tile_size=640):
    """Calculate proper lat/lon offsets using Google Maps Web Mercator projection."""
    world_size = 256 * (2 ** zoom)
    
    lat_rad = math.radians(lat)
    lat_pixel = (1 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2 * world_size
    
    new_lat_pixel = lat_pixel + tile_size  # Move one tile down
    new_lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * new_lat_pixel / world_size)))
    lat_offset = math.degrees(new_lat_rad) - lat  # Difference in degrees
    
    # Longitude offset is linear
    lon_offset = (tile_size / world_size) * 360

    return lat_offset, lon_offset

def capture_gmap(save_dir, LAT, LON, GRID_SIZE = 4):
    API_KEY = "AIzaSyBoG58gmt5sB4p6dmwZBz40Doa_xn8zkks"

    ZOOM = 19
    MAPTYPE = "satellite"
    TILE_SIZE = 640

    # Get correct offsets for latitude & longitude
    LAT_OFFSET, LON_OFFSET = get_lat_lon_offset(LAT, ZOOM)
    print(f"LAT_OFFSET: {LAT_OFFSET}, LON_OFFSET: {LON_OFFSET}")

    final_image_size = (TILE_SIZE * GRID_SIZE, TILE_SIZE * GRID_SIZE)
    stitched_image = Image.new("RGB", final_image_size)

    # Download and stitch the images
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            # Calculate lat/lon with correct offsets
            lat = round(LAT + (y - GRID_SIZE // 2) * LAT_OFFSET, 6)
            lon = round(LON + (x - GRID_SIZE // 2) * LON_OFFSET, 6)

            url = f"https://maps.googleapis.com/maps/api/staticmap?center={lat},{lon}&zoom={ZOOM}&size={TILE_SIZE}x{TILE_SIZE}&maptype={MAPTYPE}&key={API_KEY}"
            # print(f"Fetching Tile: {url}")

            response = requests.get(url)

            if response.status_code == 200:
                img = Image.open(io.BytesIO(response.content))
                stitched_image.paste(img, (x * TILE_SIZE, y * TILE_SIZE))
            else:
                print(f"Error fetching tile: {lat}, {lon}, Response: {response.text}")

    # Save the final stitched map
    stitched_image.save(f"{save_dir}big_google_map.png")
    print("Saved large stitched map!")



def slice_image(image_path, output_folder, tile_size=304):
    """Slices a large image into smaller square tiles of given size."""
    os.makedirs(output_folder, exist_ok=True)

    img = Image.open(image_path)
    img_width, img_height = img.size

    tile_count_x = img_width // tile_size
    tile_count_y = img_height // tile_size

    print(f"Slicing {img_width}x{img_height} image into {tile_size}x{tile_size} tiles.")

    for x in range(tile_count_x):
        for y in range(tile_count_y):
            left = x * tile_size
            upper = y * tile_size
            right = left + tile_size
            lower = upper + tile_size

            tile = img.crop((left, upper, right, lower))
            tile.save(os.path.join(output_folder, f"tile_{x}_{y}.png"))

    print("Image slicing complete! Tiles saved to:", output_folder)
