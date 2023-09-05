import os
import glob
import time
import pandas as pd
import xml.etree.ElementTree as ET
import requests
import numpy as np
import tkinter as tk
from tkinter import filedialog, ttk, scrolledtext

# Create the main Tkinter window
window = tk.Tk()
window.title("Creador de elevaciones")
window.geometry("500x600")

# Create a ScrolledText widget for displaying logs
logs_text = scrolledtext.ScrolledText(window, width=60, height=25)
logs_text.pack(pady=10)

# Create a progress bar
progress = ttk.Progressbar(window, length=400, mode="determinate")
progress.pack(pady=10)

# Function to select a folder and process KML files
def process_folder():
    # Reset the logs and progress bar
    logs_text.delete("1.0", tk.END)
    progress["value"] = 0

    current_dir = os.getcwd()

    # Select the folder using a file dialog
    folder_path = filedialog.askdirectory(initialdir=current_dir)
    if not folder_path:
        logs_text.insert(tk.END, "No folder selected.")
        return

    # Get all KML files in the selected folder and its subfolders
    kml_files = glob.glob(os.path.join(folder_path, "**/*.kml"), recursive=True)
    total_files = len(kml_files)

    # Process each KML file
    for i, kml_file in enumerate(kml_files, start=1):
        logs_text.insert(tk.END, f"Processing file {i}/{total_files}: {kml_file}\n")
        logs_text.see(tk.END)

        # Generate the GPX file path
        gpx_file = os.path.splitext(kml_file)[0] + ".gpx"

        # Read the KML file and generate the GPX file
        df = readkml(kml_file)
        generate_gpx(df, gpx_file)

        # Update the progress bar
        progress["value"] = (i / total_files) * 100
        window.update()

    # Complete the progress bar
    progress["value"] = 100
    window.update()

    logs_text.insert(tk.END, "Conversion completed.")
    logs_text.see(tk.END)

# Function to read a KML file and return a DataFrame
def readkml(kml_file):
    # Parse the KML file
    tree = ET.parse(kml_file)
    root = tree.getroot()

    # Namespace dictionary
    ns = {'kml': 'http://www.opengis.net/kml/2.2'}

    # Extract coordinates from Placemark elements
    coordinates = []
    for placemark in root.findall('.//kml:Placemark', ns):
        coordinates_elem = placemark.find('.//kml:coordinates', ns)
        if coordinates_elem is not None:
            coordinates_str = coordinates_elem.text.strip()
            coordinates_list = [c.split(',')[:2] for c in coordinates_str.split()]
            coordinates.extend(coordinates_list)

    # Create a DataFrame from the coordinates
    df = pd.DataFrame(coordinates, columns=['lon', 'lat'])

    df = df[['lat', 'lon']]
    lat = df['lat'].tolist()
    lon = df['lon'].tolist()
    filtered_lat = [elem for i, elem in enumerate(lat) if (i + 1) % 10 == 1]
    filtered_lon = [elem for i, elem in enumerate(lon) if (i + 1) % 10 == 1]

    chunk_size = 100

    lat_chunks = [filtered_lat[i:i + chunk_size] for i in range(0, len(filtered_lat), chunk_size)]
    lon_chunks = [filtered_lon[i:i + chunk_size] for i in range(0, len(filtered_lon), chunk_size)]

    df1_rows = []

    max_retries = 4

    for i in range(len(lat_chunks)):
        lat_chunk = lat_chunks[i]
        lon_chunk = lon_chunks[i]
        retries = 0
        success = False

        while retries < max_retries and not success:
            try:
                # Create the API request URL
                url = f"https://api.open-meteo.com/v1/elevation?latitude={','.join(map(str, lat_chunk))}&longitude={','.join(map(str, lon_chunk))}"

                # Send the API request
                response = requests.get(url, timeout=10)

                # Check if the request was successful
                if response.status_code == 200:
                    json_data = response.json()
                    elevations = json_data['elevation']

                    # Append the data to the list of rows
                    for j in range(len(lat_chunk)):
                        if j > 0:
                            start_val = float(elevations[j - 1])
                            end_val = float(elevations[j])
                            result = np.geomspace(start_val + 0.001, end_val + 0.001, num=10)
                            random_values = np.random.uniform(-0.099, 0.099, size=result.shape)
                            result = np.add(result, random_values)
                            result = np.around(result, decimals=3)
                            for k in range(-9, 0):
                                try:
                                    index = (i * 1000) + k + (j * 10)
                                    df_row = df.iloc[index]
                                    df_row['ele'] = result[k + 9]
                                    df1_rows.append(df_row)
                                except IndexError:
                                    break
                        elevations[j] += np.around(np.random.uniform(-0.049, 0.049), decimals=3)
                        chunk_row = [lat_chunk[j], lon_chunk[j], elevations[j]]
                        df1_rows.append(chunk_row)

                    success = True

            except requests.exceptions.ReadTimeout:
                # Increment the number of retries and print an error message
                retries += 1
                time.sleep(3)
                logs_text.insert(tk.END, f"Request timed out. Retrying ({retries}/{max_retries})...\n")

            except requests.exceptions.ConnectionError:
                # Increment the number of retries and print an error message
                retries += 1
                time.sleep(5)
                logs_text.insert(tk.END, f"Connection Error. Retrying ({retries}/{max_retries})...\n")

    def soften_column(dataframe, column_name, window_size=65):
        dataframe[column_name] = dataframe[column_name].rolling(window_size, center=True, min_periods=1).mean()
        return dataframe

    df1 = pd.DataFrame(df1_rows, columns=["lat", "lon", "ele"])
    soften_column(df1, "ele")
    return df1

def generate_gpx(df, gpx_file):
    gpx_content = '''<?xml version="1.0" encoding="utf-8" standalone="yes"?>
<gpx version="1.1" creator="GPS Visualizer https://www.gpsvisualizer.com/" xmlns="http://www.topografix.com/GPX/1/1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd">
<trk>
  <name>{track_name}</name>
  <trkseg>
    {track_points}
  </trkseg>
</trk>
</gpx>'''

    track_point_template = '<trkpt lat="{lat}" lon="{lon}">\n  <ele>{ele}</ele>\n</trkpt>'

    track_points = []
    for _, row in df.iterrows():
        track_point = track_point_template.format(lat=row['lat'], lon=row['lon'], ele=row['ele'])
        track_points.append(track_point)

    gpx_content = gpx_content.format(track_name="brington -1", track_points='\n'.join(track_points))

    with open(gpx_file, 'w') as f:
        f.write(gpx_content)

# Create a button to select a folder and start the process
select_folder_button = tk.Button(window, text="Seleccionar Folder", command=process_folder)
select_folder_button.pack()

# Start the Tkinter event loop
window.mainloop()
