from flask import Flask, Response, render_template, redirect, url_for, request, send_from_directory
import cv2
import os
from datetime import datetime

app = Flask(__name__)

SAVE_DIR = "static/captured_images"
os.makedirs(SAVE_DIR, exist_ok=True)  # Ensure directory exists
cap = None  # Global variable to manage camera

# Generate video frames
def generate_frames():
    global cap
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # Open the camera
    
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        _, buffer = cv2.imencode('.jpg', frame)  # Encode frame as JPEG
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')  # Streaming response format
    
    cap.release()

# Home page
@app.route("/")
def index():
    return render_template("index.html")

# Capture video feed
@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Open camera
@app.route('/open_camera', methods=["POST"])
def open_camera():
    return render_template("open_camera.html")

# Stop camera
@app.route("/stop_camera", methods=["GET", "POST"])
def stop_camera():
    global cap
    if cap is not None:
        cap.release()
        cv2.destroyAllWindows()
    return redirect("/")

# Capture Image
@app.route('/capture')
def capture():
    global cap
    if cap is None or not cap.isOpened():
        return "Camera is not open", 400
    
    success, frame = cap.read()
    if success:
        filename = f"captured_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        img_path = os.path.join(SAVE_DIR, filename)
        cv2.imwrite(img_path, frame)  # Save image
        return filename  # Return image filename
    
    return "Error capturing image", 500

# Serve captured images
@app.route('/static/<filename>')
def get_image(filename):
    return send_from_directory(SAVE_DIR, filename)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
