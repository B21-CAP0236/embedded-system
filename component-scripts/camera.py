import picamera

def capture():
    with picamera.PiCamera() as camera:
        camera.resolution = (1024, 768)
        camera.framerate = 30
        camera.capture_sequence([
            'captured_card.jpg',
        ], use_video_port=True)

if __name__ == "__main__":
    capture()