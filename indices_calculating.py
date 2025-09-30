import os
import numpy as np
import rasterio
from rasterio import plot
from rasterio.enums import Resampling
import pandas as pd

# Function to sanitize the index names and ensure valid filenames
def sanitize_filename(name):
    name = name.replace('+', '_plus_')
    name = name.replace('-', '_minus_')
    name = name.replace('*', '_times_')
    name = name.replace('/', '_slash_')
    name = name.replace('(', '_')  # Remove opening parenthesis
    name = name.replace(')', '_')  # Remove closing parenthesis
    name = ''.join(c if c.isalnum() or c == '_' else '_' for c in name)
    return name

# Function to identify bands based on reflectance
def identify_bands(raster_stack):
    band_means = [np.mean(raster_stack.read(i)) for i in range(1, raster_stack.count + 1)]
    band_order = np.argsort(band_means)[::-1]
    return [f'Band {i+1}' for i in band_order]

# Function to compute an index based on an expression
def compute_index(index_expr, bands):
    expr = index_expr
    expr = expr.replace("B1", f"bands[0]")
    expr = expr.replace("B2", f"bands[1]")
    expr = expr.replace("B3", f"bands[2]")
    expr = expr.replace("B4", f"bands[3]")
    
    # Evaluate the expression dynamically
    return eval(expr)

# Path to input/output directories and index file
input_dir = "D:/sdm/new papers/idea/Remote sensing/flower/rapseed mapping/USA/composite/mask"
output_dir = "D:/sdm/new papers/idea/Remote sensing/flower/rapseed mapping/USA/composite/mask/indices/"
index_file = "D:/sdm/new papers/idea/Remote sensing/flower/Andong paper/all_indices.csv"

# Read the CSV with indices
df = pd.read_csv(index_file)

# List all Sentinel composite TIF files in the input directory
sentinel_files = [os.path.join(input_dir, f) for f in os.listdir(input_dir) if f.endswith(".tif")]

# Loop through each index and each Sentinel composite
for index_name in df['Index']:
    sanitized_index_name = sanitize_filename(index_name)
    
    # Create a folder for each index
    index_folder = os.path.join(output_dir, sanitized_index_name)
    os.makedirs(index_folder, exist_ok=True)
    
    for sentinel_file in sentinel_files:
        # Open the Sentinel raster stack (4 bands)
        with rasterio.open(sentinel_file) as src:
            # Read the raster bands into a stack
            raster_stack = src.read([1, 2, 3, 4])  # Assuming 4 bands (NIR, Red, Green, Blue)
            
            # Identify the bands based on reflectance values
            band_names = identify_bands(src)
            print(f"File: {os.path.basename(sentinel_file)}")
            print(f"Band 1 is {band_names[0]}")
            print(f"Band 2 is {band_names[1]}")
            print(f"Band 3 is {band_names[2]}")
            print(f"Band 4 is {band_names[3]}")
            
            # Assign the bands to a list (band 1 to 4)
            bands = [raster_stack[0], raster_stack[1], raster_stack[2], raster_stack[3]]
            
            # Calculate the index for this Sentinel image
            result = compute_index(index_name, bands)
            
            # Extract the file name (without extension) to use as raster file name
            sentinel_file_name = os.path.splitext(os.path.basename(sentinel_file))[0]
            
            # Sanitize the raster file name (in case it has special characters)
            sanitized_raster_name = sanitize_filename(sentinel_file_name)
            
            # Save the resulting raster with the index in the appropriate folder
            output_file = os.path.join(index_folder, f"{sanitized_raster_name}.tif")
            
            # Write the resulting raster to a new file
            with rasterio.open(output_file, 'w', driver='GTiff', count=1, dtype='float32', 
                               width=src.width, height=src.height, crs=src.crs, transform=src.transform) as dst:
                dst.write(result, 1)

print("All indices calculated and saved successfully!")
