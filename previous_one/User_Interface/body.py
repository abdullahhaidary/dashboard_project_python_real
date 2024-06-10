from User_Interface.body_sections import left_frame, right_frame
from User_Interface.body_sections.sidebar import create_sidebar
from User_Interface.body_sections.camera_functions import show_camera_feed

def on_camera_change(camera_name, camera_url, label):
    show_camera_feed(camera_url, label)

def create_body_frames(parent_frame):
    left_frame.create_left_frame(parent_frame)
    right_frame.create_right_frame(parent_frame)
    create_sidebar(parent_frame, on_camera_change,left_frame)
