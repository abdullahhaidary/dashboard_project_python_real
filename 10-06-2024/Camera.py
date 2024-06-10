
import tkinter as tk
from tkinter import simpledialog, messagebox
import json
import cv2
import numpy as np
import time
import os
class Camera:

    CAMERA_DATA_FILE = "camera_data.json"
    def add(self, camera_name, camera_url):
        # Check if the file exists and read the data
        try:
            if os.path.exists(self.CAMERA_DATA_FILE):
                with open(self.CAMERA_DATA_FILE, 'r') as file:
                    camera_data = json.load(file)
            else:
                camera_data = []
        except (FileNotFoundError, json.JSONDecodeError):
            camera_data = []

        # Ensure the data is a list
        if not isinstance(camera_data, list):
            camera_data = []

        # Check if the camera name or URL already exists
        for camera in camera_data:
            if camera["camera"] == camera_name or camera["url"] == camera_url:
                print("Error: Camera name or URL already exists.")
                return

        # Determine the new ID
        if camera_data:
            max_id = max(camera["id"] for camera in camera_data)
            new_id = max_id + 1
        else:
            new_id = 0

        # Add the new camera data
        new_camera = {"id": new_id, "camera": camera_name, "url": camera_url}
        camera_data.append(new_camera)

        # Write the updated data back to the JSON file
        with open(self.CAMERA_DATA_FILE, "w") as file:
            json.dump(camera_data, file, indent=4)
        print("Camera added successfully.")

    
    def remove(self, camera_id):
        try:
            # Check if the file exists and read the data
            if os.path.exists(self.CAMERA_DATA_FILE):
                with open(self.CAMERA_DATA_FILE, "r") as file:
                    camera_data = json.load(file)
            else:
                print("The JSON file does not exist.")
                return
        except (FileNotFoundError, json.JSONDecodeError):
            print("Error reading the JSON file.")
            return

        # Ensure the data is a list
        if not isinstance(camera_data, list):
            print("The JSON data is not a list.")
            return

        # Find and remove the camera with the specified ID
        original_length = len(camera_data)
        camera_data = [camera for camera in camera_data if camera.get("id") != camera_id]

        # Check if any camera was removed
        if len(camera_data) == original_length:
            print("Camera ID not found.")
        else:
            # Write the modified data back to the JSON file
            with open(self.CAMERA_DATA_FILE, "w") as file:
                json.dump(camera_data, file, indent=4)
            print("Camera removed successfully.")

    def edit(self, camera_id, new_name, new_url):
        try:
            # Check if the file exists and read the data
            if os.path.exists(self.CAMERA_DATA_FILE):
                with open(self.CAMERA_DATA_FILE, "r") as file:
                    camera_data = json.load(file)
            else:
                print("The JSON file does not exist.")
                return
        except (FileNotFoundError, json.JSONDecodeError):
            print("Error reading the JSON file.")
            return

        # Ensure the data is a list
        if not isinstance(camera_data, list):
            print("The JSON data is not a list.")
            return

        # Find and update the camera with the specified id
        camera_found = False
        for camera in camera_data:
            if camera["id"] == camera_id:
                camera["camera"] = new_name
                camera["url"] = new_url
                camera_found = True
                break

        if not camera_found:
            print("Camera id not found.")
        else:
            # Write the modified data back to the JSON file
            with open(self.CAMERA_DATA_FILE, "w") as file:
                json.dump(camera_data, file, indent=4)
            print("Camera updated successfully.")
    
    def get_all(self):
        try:
            # Check if the file exists and read the data
            if os.path.exists(self.CAMERA_DATA_FILE):
                with open(self.CAMERA_DATA_FILE, "r") as file:
                    camera_data = json.load(file)
            else:
                print("The JSON file does not exist.")
                return None
        except (FileNotFoundError, json.JSONDecodeError):
            print("Error reading the JSON file.")
            return None

        # Ensure the data is a list
        if not isinstance(camera_data, list):
            print("The JSON data is not a list.")
            return None

        # Return the list of camera data
        return camera_data
    
    def remove_all(self):
        try:
            # Open the JSON file in write mode and write an empty list to it
            with open(self.CAMERA_DATA_FILE, "w") as file:
                json.dump([], file)
            print("All data removed successfully.")
        except FileNotFoundError:
            print("The JSON file does not exist.")
        except Exception as e:
            print("An error occurred:", e)


    def show_img(self, url): 
        return 
    

    def stop_img(self,url):
        return
    


    @staticmethod
    def capture(url, shared_memory, shape, stop_event):
        cap = cv2.VideoCapture(url)

        if not cap.isOpened():
            return

        # Get the frame rate of the video or camera
        fps = cap.get(cv2.CAP_PROP_FPS)
        if fps == 0:
            fps = 30  # Default to 30 fps if the camera doesn't provide fps info
        frame_duration = 1.0 / fps
        try:
            while not stop_event.is_set():
                start_time = time.time()
                
                ret, frame = cap.read()

                if not ret:
                    continue

                resized_frame = cv2.resize(frame, (shape[1], shape[0]))

                # Assign the resized frame to shared memory
                np.frombuffer(shared_memory.get_obj(), dtype=np.uint8)[:] = resized_frame.flatten()

                # Calculate the time to wait to match the frame rate
                elapsed_time = time.time() - start_time
                wait_time = frame_duration - elapsed_time
                # Instead of sleeping for the entire wait_time, sleep in small intervals and check the stop_event
                while wait_time > 0 and not stop_event.is_set():
                    sleep_interval = min(0.01, wait_time)
                    time.sleep(sleep_interval)
                    wait_time -= sleep_interval
        finally:
            cap.release()


   