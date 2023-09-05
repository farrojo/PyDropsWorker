import os
from tkinter import Tk, filedialog

# Get the script's execution folder
script_folder = os.path.dirname(os.path.abspath(__file__))

# Choose the directory path using Windows Explorer
root = Tk()
root.withdraw()
directory_path = filedialog.askdirectory(initialdir=script_folder)

# Iterate through all files in the folder
for file_name in os.listdir(directory_path):
    if file_name.endswith("STRAVA.gpx"):
        file_path = os.path.join(directory_path, file_name)

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
    <desc>Created with GOTOES STRAVA TOOLS Version 20.2</desc>
    <time>''',
            '''<?xml version="1.0" encoding="UTF-8"?>
<gpx creator="Strava iPhone App" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd" version="1.1" xmlns="http://www.topografix.com/GPX/1/1">
  <metadata>
    <time>'''
        )

        # Write the updated content back to the file
        with open(file_path, "w") as file:
            file.write(updated_content)

        print(f"Updated file: {file_name}")

print("Replacement complete.")

