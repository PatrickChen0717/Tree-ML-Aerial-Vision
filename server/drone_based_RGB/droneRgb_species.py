import sys
import os
import json
import torch
import time
import cv2
from PIL import Image
import numpy as np
import rasterio
import random
from collections import defaultdict
from PIL import Image, ImageDraw, ImageFont
import torchvision.transforms as transforms
base_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(base_dir, "drone_based_RGB/treesat_benchmark_species"))
import warnings
warnings.filterwarnings("ignore")
from drone_based_RGB.treesat_benchmark_species.TreeSat_Benchmark.trainers.metrics import *
from drone_based_RGB.treesat_benchmark_species.TreeSat_Benchmark.trainers.augmenter import Augmenter
from drone_based_RGB.treesat_benchmark_species.TreeSat_Benchmark.trainers.dataloaders import get_dataloader
from drone_based_RGB.treesat_benchmark_species.TreeSat_Benchmark.models import get_classification_model
from drone_based_RGB.treesat_benchmark_species.TreeSat_Benchmark.trainers.basetrainer import ModelTrainer
from drone_based_RGB.treesat_benchmark_species.TreeSat_Benchmark.trainers.utils import get_class_weights, set_up_unfrozen_weights
from drone_based_RGB.treesat_benchmark_species.TreeSat_Benchmark.trainers.transforms import xform_aer_scratch, xform_aer_3bands_scratch


means = [93.1159469148246, 85.05016794624635, 81.0471576353153]
stds =  [33.59622314610158, 28.000497087051126, 33.683983599997724]

classes = ["Pinus_sylvestris",
            "Fagus_sylvatica",
            "Picea_abies",
            "Cleared",
            "Quercus_robur",
            "Acer_pseudoplatanus",
            "Betula_spec.",
            "Pseudotsuga_menziesii",
            "Fraxinus_excelsior",
            "Quercus_petraea",
            "Alnus_spec.",
            "Quercus_rubra",
            "Larix_kaempferi",
            "Larix_decidua",
            "Abies_alba",
            "Pinus_strobus",
            "Pinus_nigra",
          ]

classes_english = ["Scots pine",
                   "European beech",
                   "Norway spruce",
                   "Cleared",
                   "English oak",
                   "Sycamore maple",
                   "Birch species",
                   "Douglas fir",
                   "European ash",
                   "Sessile oak",
                   "Alder species",
                   "Northern red oak",
                   "Japanese larch",
                   "European larch",
                   "Silver fir",
                   "Eastern white pine",
                   "Black pine"]


path_config = os.path.join(base_dir, "treesat_benchmark_species/configs/aer_only/aerial_cyclic_Families_v8_3Bands_no_NIR_Scratch.json")

with open(path_config) as file:
    config = json.load(file)

model = get_classification_model("Resnet", classes, config)
model.load_state_dict(torch.load(
    os.path.join(base_dir, "..", "models/drone_rgb_model_species.pt"),
    map_location=torch.device('cpu')
))
model.eval()

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device)
model.eval()


COLOR_SHADERS = {
    1: (1.0, 0.0, 0.0),  # Pure Red
    2: (0.0, 1.0, 0.0),  # Pure Green
    3: (0.0, 0.0, 1.0),  # Pure Blue
    4: (1.0, 1.0, 0.0),  # Yellow
    5: (1.0, 0.0, 1.0),  # Magenta
    6: (0.0, 1.0, 1.0),  # Cyan
    7: (1.0, 0.5, 0.0),  # Deep Orange
    8: (0.5, 1.0, 0.0),  # Bright Lime
    9: (0.5, 0.0, 1.0),  # Deep Purple
    10: (0.0, 1.0, 0.5), # Turquoise
    11: (1.0, 0.0, 0.5), # Hot Pink
    12: (0.0, 0.5, 1.0), # Electric Blue
    13: (0.3, 0.3, 0.3), # Dark Gray
    14: (1.0, 0.8, 0.0), # Gold
    15: (0.2, 0.6, 1.0), # Sky Blue
    16: (0.6, 0.2, 1.0), # Vivid Violet
    17: (0.0, 1.0, 0.2)  # Bright Mint
}

def scale_to_resolution(image, current_res_cm, target_res_cm=17):
    scale_factor = current_res_cm / target_res_cm
    new_size = (int(image.shape[1] * scale_factor), int(image.shape[0] * scale_factor))
    
    interpolation = cv2.INTER_AREA if scale_factor < 1 else cv2.INTER_CUBIC
    return cv2.resize(image, new_size, interpolation=interpolation)


def process_image(input_path, output_path, current_res_cm):
    image = cv2.imread(input_path)
    if image is None:
        raise FileNotFoundError(f"Error: Cannot read the image at {input_path}")

    scaled_image = scale_to_resolution(image, current_res_cm)
    height, width, _ = scaled_image.shape
    
    tile_y = int(np.ceil(304 / height))
    tile_x = int(np.ceil(304 / width))

    if tile_y > 1 or tile_x > 1:
        scaled_image = np.tile(scaled_image, (tile_y, tile_x, 1))
        scaled_image = scaled_image[:max(304, height), :max(304, width)]
    
    cv2.imwrite(output_path, scaled_image)
    print(f"Scaled image saved to {output_path}")


def slice_image(image_path, output_folder, tile_size=304):
    """Slices a large image into smaller square tiles of given size."""
    os.makedirs(output_folder, exist_ok=True)

    img = Image.open(image_path)
    img_width, img_height = img.size

    tile_count_x = img_width // tile_size
    tile_count_y = img_height // tile_size

    print(f"✅ Slicing {img_width}x{img_height} image into {tile_size}x{tile_size} tiles.")

    for x in range(tile_count_x):
        for y in range(tile_count_y):
            left = x * tile_size
            upper = y * tile_size
            right = left + tile_size
            lower = upper + tile_size

            tile = img.crop((left, upper, right, lower))
            tile.save(os.path.join(output_folder, f"tile_{x}_{y}.png"))

    print("✅ Image slicing complete! Tiles saved to:", output_folder)


def apply_shader(image, shader_id, alpha=100):
    """Apply a semi-transparent color shader to the tile based on shader_id (1-12)."""
    if shader_id not in COLOR_SHADERS:
        return image 
    
    r_mult, g_mult, b_mult = COLOR_SHADERS[shader_id]
    
    img = image.convert("RGBA")
    
    overlay = Image.new("RGBA", img.size, (int(r_mult * 255), int(g_mult * 255), int(b_mult * 255), alpha))

    blended = Image.alpha_composite(img, overlay)

    return blended.convert("RGB")


def add_tile_index(image, index_text, tile_size):
    """Add a large centered number on the tile."""
    draw = ImageDraw.Draw(image)
    
    font_size = tile_size // 3
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default(font_size)
    
    bbox = draw.textbbox((0, 0), index_text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    text_position = ((tile_size - text_width) // 2, (tile_size - text_height) // 2)

    outline_color = (0, 0, 0)
    text_color = (255, 255, 255) 
    
    for dx, dy in [(-2, -2), (2, -2), (-2, 2), (2, 2)]:
        draw.text((text_position[0] + dx, text_position[1] + dy), index_text, font=font, fill=outline_color)

    draw.text(text_position, index_text, font=font, fill=text_color)

    return image

def reassemble_tiles(input_folder, output_image, tile_size=304):
    """
    Reassemble sliced tiles back into a single image.
    Randomly assign shaders to each tile.
    """
    tile_files = sorted(os.listdir(input_folder))
    tile_positions = []

    for filename in tile_files:
        if filename.startswith("tile_") and filename.endswith(".png"):
            parts = filename.replace(".png", "").split("_")
            x, y = int(parts[1]), int(parts[2])
            tile_positions.append((x, y))

    if not tile_positions:
        print("❌ No tiles found in folder!")
        return

    max_x = max(pos[0] for pos in tile_positions)
    max_y = max(pos[1] for pos in tile_positions)
    grid_width = (max_x + 1) * tile_size
    grid_height = (max_y + 1) * tile_size

    print(f"🔹 Reassembling tiles into {grid_width}x{grid_height} image...")
    square_size = min(grid_width, grid_height)
    grid_width = grid_height = square_size

    print(f"🔹 Reassembling square image of size {grid_width}x{grid_height}...")

    final_image = Image.new("RGB", (grid_width, grid_height))

    # Generate a random shader map
    shader_map = {}
    for pos in tile_positions:
        x, y = pos[0], pos[1]
        predict_index = drone_classify(input_folder, x, y)
        shader_map[(x, y)] = classes.index(predict_index)
    # print(shader_map)

    
    label_counts = defaultdict(int)
    for label in shader_map.values():
        label_counts[label] += 1

    total_tiles = len(shader_map)

    label_percentages = {classes[label]: (count / total_tiles) * 100 for label, count in label_counts.items()}
    for label, percentage in label_percentages.items():
        print(f"Label {label}: {percentage:.2f}%")

    # Load and place tiles
    for x, y in tile_positions:
        tile_path = os.path.join(input_folder, f"tile_{x}_{y}.png")
        tile_img = Image.open(tile_path)
        final_image.paste(tile_img, (x * tile_size, y * tile_size))

    final_image.save(output_image)
    print(f"✅ Saved reassembled image as '{output_image}' 🎉")
    
    max_x = max(x for (x, y) in shader_map.keys())
    max_y = max(y for (x, y) in shader_map.keys())

    shader_grid = [[None for _ in range(max_x + 1)] for _ in range(max_y + 1)]

    for (x, y), label in shader_map.items():
        shader_grid[y][x] = label

    return label_percentages, shader_grid


def classify_droneRGB_in_memory(image_path, model, device):
    """Classifies an image at multiple resolutions and returns the most frequent prediction."""
    with rasterio.open(image_path) as src:
        image = src.read()

    if image.shape[0] == 4: 
        image = image[1:4, :, :]  # Use only RGB channels


    image_scaled = xform_aer_3bands_scratch(image, means, stds).to(device)
    with torch.no_grad():
        output = model(image_scaled.unsqueeze(0))
        _, predicted = torch.max(output, 1)

    return classes[predicted]


def drone_classify(tile_folder, x, y):
    image_file_path = f"{tile_folder}/tile_{x}_{y}.png"

    if not os.path.exists(image_file_path):
        print(f"Warning: File not found: {image_file_path}")
        return

    try:
        predicted_label = classify_droneRGB_in_memory(image_file_path, model, device)
        return predicted_label
    except Exception as e:
        print(f"Error processing file tile_{x}_{y}.png: {e}")
        return

