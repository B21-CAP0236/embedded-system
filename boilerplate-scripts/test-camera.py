import time
import picamera

# More on this documentation
# https://picamera.readthedocs.io/en/release-1.13/recipes2.html#rapid-capture-and-processing

with picamera.PiCamera() as camera:
    camera.resolution = (1024, 768)
    camera.framerate = 30
    camera.start_preview()
    time.sleep(2)
    camera.capture_sequence([
        'image1.jpg',
        'image2.jpg',
        'image3.jpg',
        'image4.jpg',
        'image5.jpg',
    ], use_video_port=True)
