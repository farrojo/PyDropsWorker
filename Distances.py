import os
import gpxpy
from geopy.distance import geodesic

def calculate_distance(gpx_file_path):
    gpx_file = open(gpx_file_path, 'r')
    gpx = gpxpy.parse(gpx_file)

    distance = 0.0
    previous_point = None

    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                if previous_point:
                    distance += geodesic(
                        (previous_point.latitude, previous_point.longitude),
                        (point.latitude, point.longitude)
                    ).meters
                previous_point = point

    return distance / 1000

def process_gpx_files(folder_path):
    total_distance = 0.0
    file_count = 0

    for root, dirs, files in os.walk(folder_path):
        for file_name in files:
            if file_name.endswith(".gpx"):
                gpx_file_path = os.path.join(root, file_name)
                distance = calculate_distance(gpx_file_path)
                total_distance += distance
                file_count += 1

                formatted_distance = "{:.2f}".format(distance)
                print(f"File: {gpx_file_path}")
                print(f"Distance: {formatted_distance} Km")
                print("")

    formatted_total_distance = "{:.2f}".format(total_distance)
    print(f"Total Distance: {formatted_total_distance} Km")
    print(f"Number of Files: {file_count}")

# Usage example
# folder_path = input("Enter the path to the main folder: ")
folder_path = ""
process_gpx_files(folder_path)