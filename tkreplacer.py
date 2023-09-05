import os, sys
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText

def choose_directory():
    # Get the current working directory
    current_dir = os.getcwd()
    progress['value'] = 0
    # Choose the directory path using Windows Explorer
    directory_path = filedialog.askdirectory(initialdir=current_dir)
    if directory_path:
        update_files(directory_path)

def update_files(directory_path):
    # Get the total number of files to process
    total_files = sum(1 for file_name in os.listdir(directory_path) if file_name.endswith("STRAVA.gpx"))

    total_files = 0
    for root_folder, subfolders, files in os.walk(directory_path):
        for file_name in files:
            if file_name.endswith("STRAVA.gpx"):
                total_files += 1
    # Update the progress bar as files are processed
    progress['maximum'] = total_files
    processed_files = 0

    # Iterate through all files in the folder
    for root_folder, subfolders, files in os.walk(directory_path):
        for file_name in files:
            if file_name.endswith("STRAVA.gpx"):
                file_path = os.path.join(root_folder, file_name)

                # Read the contents of the file
                with open(file_path, "r") as file:
                    content = file.read()

                # Replace the specified content
                updated_content = content.replace(
                '''<?xml version="1.0" encoding="UTF-8"?>
<gpx creator="Strava iPhone App" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd http://www.garmin.com/xmlschemas/GpxExtensions/v3 http://www.garmin.com/xmlschemas/GpxExtensionsv3.xsd http://www.garmin.com/xmlschemas/TrackPointExtension/v1 http://www.garmin.com/xmlschemas/TrackPointExtensionv1.xsd" version="1.1" xmlns="http://www.topografix.com/GPX/1/1" xmlns:gpxtpx="http://www.garmin.com/xmlschemas/TrackPointExtension/v1" xmlns:gpxx="http://www.garmin.com/xmlschemas/GpxExtensions/v3">
  <metadata>
    <link href="https://gotoes.org/strava/Combine_GPX_TCX_FIT_Files.php">
      <text>GOTOES STRAVA TOOLS</text>
    </link>
    <desc>Created with GOTOES STRAVA TOOLS Version 22.3</desc>
    <time>''',
                '''<?xml version="1.0" encoding="UTF-8"?>
<gpx creator="Strava iPhone App" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd" version="1.1" xmlns="http://www.topografix.com/GPX/1/1">
  <metadata>
    <time>'''
            )
                with open(file_path, "w") as file:
                        file.write(updated_content)

                processed_files += 1
                progress['value'] = processed_files
                root.update_idletasks()

                print_text = f"Updated file: {file_path}\n"
                print_area.insert(tk.END, print_text)
                print_area.see(tk.END)

        total_files += len(files)

    print_area.insert(tk.END, "Replacement complete.\n")
    print_area.see(tk.END)

if __name__ == "__main__":
# Create the Tkinter GUI
    root = tk.Tk()
    root.title("Strava Header Replacer")
    root.geometry("500x400")

    # Create the print response area
    print_area = ScrolledText(root, width=60, height=21)
    print_area.pack(pady=10)

    # Create a frame for the bottom section
    bottom_frame = tk.Frame(root)
    bottom_frame.pack(side=tk.BOTTOM, pady=10)

    # Create the "Open Folder" button
    open_button = tk.Button(bottom_frame, text="Seleccionar Carpeta", command=choose_directory)
    open_button.pack(side=tk.LEFT, padx=10)

    # Create the progress bar
    progress = ttk.Progressbar(bottom_frame, length=400, mode='determinate')
    progress.pack(side=tk.LEFT, padx=10)

    # Run the Tkinter event loop
    root.mainloop()
