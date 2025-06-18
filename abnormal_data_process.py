import matplotlib
matplotlib.use('tkagg')
import matplotlib.pyplot as plt
import csv
import json
import numpy as np
import pandas as pd
from math import ceil
from scipy.spatial.distance import euclidean

# Load video metadata from JSON
with open('processed_data/video_data.json', 'r') as file:
    data = json.load(file)
    data_record_frame = data["DATA_RECORD_FRAME"]       # Total frames processed
    frame_size = data["PROCESSED_FRAME_SIZE"]           # Size of each video frame (width or height)
    vid_fps = data["VID_FPS"]                           # Frames per second of the video
    track_max_age = data["TRACK_MAX_AGE"]               # Max age of a track (how long a track stays alive without detection)

# For safety, define track_max_age explicitly if needed
track_max_age = 3

# Calculate time per step between recorded frames
time_steps = data_record_frame / vid_fps

# Calculate how many frames correspond to "stationary" period
stationary_time = ceil(track_max_age / time_steps)

# Define distance threshold to consider a person "stationary" (1% of frame size)
stationary_distance = frame_size * 0.01

# Read movement tracks from CSV
tracks = []
with open('processed_data/movement_data.csv', 'r') as file:
    reader = csv.reader(file, delimiter=',')
    for row in reader:
        # Check if track has enough data points
        if len(row[3:]) > stationary_time * 2:
            temp = []
            data = row[3:]
            # Convert pairs of coordinates into points
            for i in range(0, len(data), 2):
                temp.append([int(data[i]), int(data[i+1])])
            tracks.append(temp)

print("Tracks recorded: " + str(len(tracks)))

# Filter tracks to separate useful movements by detecting stationary periods
useful_tracks = []
for movement in tracks:
    check_index = stationary_time
    start_point = 0
    track = movement[:check_index]
    while check_index < len(movement):
        for i in movement[check_index:]:
            # If distance moved is greater than threshold, consider movement ongoing
            if euclidean(movement[start_point], i) > stationary_distance:
                track.append(i)
                start_point += 1
                check_index += 1
            else:
                # Movement is stationary; break to start new segment
                start_point += 1
                check_index += 1
                break
        useful_tracks.append(track)
        track = movement[start_point:check_index]

# Calculate energy levels (kinetic energy-like) from speed between positions
energies = []
for movement in useful_tracks:
    for i in range(len(movement) - 1):
        speed = round(euclidean(movement[i], movement[i+1]) / time_steps , 2)
        energy = int(0.5 * speed ** 2)  # Energy = 0.5 * speed^2
        energies.append(energy)

print()
print("Useful movement data points: " + str(len(energies)))

# Convert energies to Pandas Series for statistical analysis
energies = pd.Series(energies)
df = pd.DataFrame({'Energy': energies})

# Print statistical info on energy distribution
print("Kurtosis: " + str(df.kurtosis()[0]))
print("Skewness: " + str(df.skew()[0]))
print("Summary of processed data:")
print(df.describe())

# Calculate acceptable energy level threshold (used for detecting abnormalities)
acceptable_energy_level = int(df.Energy.mean() ** 1.05)
print("Acceptable energy level (mean value ^ 1.05): " + str(acceptable_energy_level))

# Plot histogram of energy levels
bins = np.linspace(int(min(energies)), int(max(energies)), 100)
plt.xlim([min(energies) - 5, max(energies) + 5])
plt.hist(energies, bins=bins, alpha=0.5)
plt.title('Distribution of Energy Levels')
plt.xlabel('Energy Level')
plt.ylabel('Count')
plt.show()

# Remove outliers if skewness is too high to clean data and replot
while df.skew()[0] > 7.5:
    print()
    c = len(energies)
    print("Useful movement data points: " + str(c))
    energies = energies[abs(energies - np.mean(energies)) < 3 * np.std(energies)]
    df = pd.DataFrame({'Energy': energies})
    print("Outliers removed: " + str(c - df.Energy.count()))
    print("Kurtosis: " + str(df.kurtosis()[0]))
    print("Skewness: " + str(df.skew()[0]))
    print("Summary of processed data:")
    print(df.describe())
    acceptable_energy_level = int(df.Energy.mean() ** 1.05)
    print("Acceptable energy level (mean value ^ 1.05): " + str(acceptable_energy_level))

    bins = np.linspace(int(min(energies)), int(max(energies)), 100)
    plt.xlim([min(energies) - 5, max(energies) + 5])
    plt.hist(energies, bins=bins, alpha=0.5)
    plt.title('Distribution of Energy Levels (Outliers Removed)')
    plt.xlabel('Energy Level')
    plt.ylabel('Count')
    plt.show()
