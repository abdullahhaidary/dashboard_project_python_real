import cv2

# Open the video file
cap = cv2.VideoCapture('C:\\Users\\PC\\PycharmProjects\\UserInterface\\dashboard\\video.mp4')

# Check if the video opened successfully
if not cap.isOpened():
    print("Error: Could not open video file.")
else:
    while True:
        # Read a frame from the video
        ret, frame = cap.read()

        # Check if frame is read successfully
        if not ret:
            print("Error: Could not read frame.")
            break

        # Display the frame or do processing
        cv2.imshow('Frame', frame)

        # Exit if 'q' key is pressed
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break

    # Release the video capture object and close all windows
    cap.release()
    cv2.destroyAllWindows()
