class init_camera: 
    urls = ['rtsp://admin:Afghan123@192.168.1.64:554/Stream/Channels']
    def __init__(self):
        print("hello from the class init camera")


    def add_camera(self, url):
        self.urls.append(url)


    def camera_list(self): 
        return self.urls