import cv2
import multiprocessing
import numpy as np
import os
import json

class Camera:

    CAMERA_DATA_FILE = "camera_data.json"

    def add(self, camera_name, camera_url):
        try:
            if os.path.exists(self.CAMERA_DATA_FILE):
                with open(self.CAMERA_DATA_FILE, 'r') as file:
                    camera_data = json.load(file)
            else:
                camera_data = []
        except (FileNotFoundError, json.JSONDecodeError):
            camera_data = []

        if not isinstance(camera_data, list):
            camera_data = []

        for camera in camera_data:
            if camera["camera"] == camera_name or camera["url"] == camera_url:
                print("Error: Camera name or URL already exists.")
                return

        if camera_data:
            max_id = max(camera["id"] for camera in camera_data)
            new_id = max_id + 1
        else:
            new_id = 0

        new_camera = {"id": new_id, "camera": camera_name, "url": camera_url}
        camera_data.append(new_camera)

        with open(self.CAMERA_DATA_FILE, "w") as file:
            json.dump(camera_data, file, indent=4)
        print("Camera added successfully.")

    def remove(self, camera_id):
        try:
            if os.path.exists(self.CAMERA_DATA_FILE):
                with open(self.CAMERA_DATA_FILE, "r") as file:
                    camera_data = json.load(file)
            else:
                print("The JSON file does not exist.")
                return
        except (FileNotFoundError, json.JSONDecodeError):
            print("Error reading the JSON file.")
            return

        if not isinstance(camera_data, list):
            print("The JSON data is not a list.")
            return

        original_length = len(camera_data)
        camera_data = [camera for camera in camera_data if camera.get("id") != camera_id]

        if len(camera_data) == original_length:
            print("Camera ID not found.")
        else:
            with open(self.CAMERA_DATA_FILE, "w") as file:
                json.dump(camera_data, file, indent=4)
            print("Camera removed successfully.")

    def edit(self, camera_id, new_name, new_url):
        try:
            if os.path.exists(self.CAMERA_DATA_FILE):
                with open(self.CAMERA_DATA_FILE, "r") as file:
                    camera_data = json.load(file)
            else:
                print("The JSON file does not exist.")
                return
        except (FileNotFoundError, json.JSONDecodeError):
            print("Error reading the JSON file.")
            return

        if not isinstance(camera_data, list):
            print("The JSON data is not a list.")
            return

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
            with open(self.CAMERA_DATA_FILE, "w") as file:
                json.dump(camera_data, file, indent=4)
            print("Camera updated successfully.")

    def get_all(self):
        try:
            if os.path.exists(self.CAMERA_DATA_FILE):
                with open(self.CAMERA_DATA_FILE, "r") as file:
                    camera_data = json.load(file)
            else:
                print("The JSON file does not exist.")
                return None
        except (FileNotFoundError, json.JSONDecodeError):
            print("Error reading the JSON file.")
            return None

        if not isinstance(camera_data, list):
            print("The JSON data is not a list.")
            return None

        return camera_data

    def remove_all(self):
        try:
            with open(self.CAMERA_DATA_FILE, "w") as file:
                json.dump([], file)
            print("All data removed successfully.")
        except FileNotFoundError:
            print("The JSON file does not exist.")
        except Exception as e:
            print("An error occurred:", e)

    @staticmethod
    def capture(url, shared_memory, shape, stop_event):
        cap = cv2.VideoCapture(url)

        if not cap.isOpened():
            return

        while not stop_event.is_set():
            ret, frame = cap.read()

            if not ret:
                continue

            np_frame = np.frombuffer(shared_memory.get_obj(), dtype=np.uint8).reshape(shape)
            np.copyto(np_frame, frame)

        cap.release()

    @staticmethod
    def display_frames(shared_memory, shape, stop_event, window_name):
        while not stop_event.is_set():
            np_frame = np.frombuffer(shared_memory.get_obj(), dtype=np.uint8).reshape(shape)
            cv2.imshow(window_name, np_frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                stop_event.set()
                break
        cv2.destroyAllWindows()
