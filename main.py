import airsim
import os
import numpy as np
import time
import cv2
import pandas as pd
import threading

# Global settings
drones = ['drone0', 'drone1', 'drone2']
client = airsim.MultirotorClient()
client.confirmConnection()

# Setup folders
for drone in drones:
    os.makedirs(f"data/{drone}/images", exist_ok=True)
    pose_file = f"data/{drone}/poses.csv"
    if not os.path.exists(pose_file):
        with open(pose_file, "w") as f:
            f.write("timestamp,x,y,z,qx,qy,qz,qw\n")

def capture_data(client, drone_name, timestamp):
    responses = client.simGetImages([
        airsim.ImageRequest("nadir_cam", airsim.ImageType.Scene, False, False)
    ], vehicle_name=drone_name)

    image = responses[0]
    if image.height == 0 or image.width == 0:
        print(f"[WARNING] Empty image from {drone_name} at {timestamp}")
        return

    img_data = np.frombuffer(image.image_data_uint8, dtype=np.uint8).reshape((image.height, image.width, 3))
    filename = f"data/{drone_name}/images/{timestamp}.png"
    cv2.imwrite(filename, img_data)

    pose = client.simGetVehiclePose(vehicle_name=drone_name)
    pos = pose.position
    ori = pose.orientation
    with open(f"data/{drone_name}/poses.csv", "a") as f:
        f.write(f"{timestamp},{pos.x_val},{pos.y_val},{pos.z_val},{ori.x_val},{ori.y_val},{ori.z_val},{ori.w_val}\n")

def fly_path(drone_name, path, velocity=3, max_images=10):
    client = airsim.MultirotorClient()  # new client per thread
    client.confirmConnection()
    
    print(f"🚁 Starting mission for {drone_name}")
    client.enableApiControl(True, drone_name)
    client.armDisarm(True, drone_name)
    client.takeoffAsync(vehicle_name=drone_name).join()
    time.sleep(1.0)

    captured = 0
    for i, (x, y, z) in enumerate(path):
        if captured >= max_images:
            break

        print(f"{drone_name} → Point {i}: ({x:.2f}, {y:.2f}, {z:.2f})")
        client.moveToPositionAsync(x, y, z, velocity, vehicle_name=drone_name).join()
        time.sleep(0.5)  # Allow stabilization

        timestamp = str(int(time.time() * 1000))
        capture_data(client, drone_name, timestamp)
        captured += 1

    print(f"🛬 {drone_name} captured {captured} images. Landing.")
    client.landAsync(vehicle_name=drone_name).join()
    client.armDisarm(False, drone_name)
    client.enableApiControl(False, drone_name)

# Define simple lawnmower-style paths
paths = {
    "drone0": [(-10, y, -12) for y in range(0, 100, 10)],
    "drone1": [(0, y, -12) for y in range(0, 100, 10)],
    "drone2": [(10, y, -12) for y in range(0, 100, 10)],
}

# Launch drones in parallel
threads = []
for drone in drones:
    t = threading.Thread(target=fly_path, args=(drone, paths[drone], 3, 10))  # velocity=3, max_images=10
    t.start()
    threads.append(t)

for t in threads:
    t.join()

print("✅ All drone missions complete.")
