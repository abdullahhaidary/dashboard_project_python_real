import cv2


def update_frame(capture):
    ret, frame = capture.read()
    if ret:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return frame
    return None

def update_frame_original(capture):
    ret, frame = capture.read()
    if ret: 
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return rgb_frame
    return None