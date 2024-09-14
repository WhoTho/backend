from flask import Flask, request
from flask_socketio import SocketIO, emit
import cv2

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret!"
socketio = SocketIO(app, cors_allowed_origins="http://localhost:3000")


@app.route("/")
def hello():
    return "Hello World!"


@socketio.on("connect")
def handle_connect():
    print(f"Client connected: {request.sid}")


@socketio.on("disconnect")
def handle_disconnect():
    print(f"Client disconnected: {request.sid}")


@socketio.on("video_stream")
def video_stream():
    # Start streaming video frames in a background task
    socketio.start_background_task(target=stream_video, sid=request.sid)


def stream_video(sid):
    cap = cv2.VideoCapture(0)
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Perform some OpenCV processing (e.g., draw on frame)
        cv2.putText(
            frame, "Streaming...", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2
        )

        # Encode frame as JPEG
        _, buffer = cv2.imencode(".jpg", frame)
        frame_data = buffer.tobytes()

        try:
            # Emit the processed frame
            socketio.emit("video_frame", frame_data, to=sid)
        except Exception as e:
            print(f"Error emitting frame to {sid}: {e}")
            break

        socketio.sleep(0)  # Yield control to the event loop

    cap.release()
    print(f"Stopped streaming for client: {sid}")


if __name__ == "__main__":
    socketio.run(app, host="127.0.0.1", port=5000)
