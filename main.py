# from Interface import Interface
from Camera import Camera
import numpy as np 
# # from User_Interface.Camera import Camera
# if __name__ == "__main__":
#     interface = Interface()
#     interface.run()



#     # cam.add(camera_name="Cam1", camera_url="0")
#     # # cam.remove(camera_id=0)

#     # # cam.edit(1,"edited","2")
    
#     # # cam.edit(camera_id=2,new_name="test02edited", new_url="https2")

#     # all_cams = cam.get_all()
from Camera import Camera
import numpy as np
import multiprocessing
import cv2

if __name__ == "__main__":
    camera_url = "0"  # Use "0" for default camera, or a URL for IP cameras

    if camera_url.isdigit():
        camera_url = int(camera_url)
    cap = cv2.VideoCapture(camera_url)
    ret, frame = cap.read()
    if not ret:
        print("Error: Unable to capture frame.")
        cap.release()
        exit()
    cap.release()

    shape = frame.shape
    shared_memory_size = int(np.prod(shape) * frame.itemsize)

    shared_memory = multiprocessing.Array('b', shared_memory_size)
    stop_event = multiprocessing.Event()

    capture_process = multiprocessing.Process(target=Camera.capture, args=(camera_url, shared_memory, shape, stop_event))
    capture_process.start()

    display_process1 = multiprocessing.Process(target=Camera.display_frames, args=(shared_memory, shape, stop_event, "Display 1"))
    display_process2 = multiprocessing.Process(target=Camera.display_frames, args=(shared_memory, shape, stop_event, "Display 2"))
    display_process1.start()
    display_process2.start()

    display_process1.join()
    display_process2.join()

    stop_event.set()
    capture_process.join()
