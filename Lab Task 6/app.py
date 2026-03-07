from flask import Flask, render_template, request, jsonify
import cv2
import os

app = Flask(__name__)

# Folder to save uploaded images
UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Haar Cascade Models
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)
eye_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_eye.xml"
)


# Home Page
@app.route("/")
def home():
    return render_template("index.html")


# Image Upload & Analysis
@app.route("/upload", methods=["POST"])
def upload():

    file = request.files.get("image")

    if not file:
        return jsonify({"error": "No image uploaded"})

    # Save image
    image_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(image_path)

    # Read Image
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Detect Faces
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    if len(faces) == 0:
        return jsonify({"error": "No face detected"})

    for (x, y, w, h) in faces:

        # Draw face box
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

        roi_gray = gray[y:y + h, x:x + w]
        roi_color = img[y:y + h, x:x + w]

        # Detect Eyes
        eyes = eye_cascade.detectMultiScale(roi_gray)

        for (ex, ey, ew, eh) in eyes:
            cv2.rectangle(roi_color, (ex, ey),
                          (ex + ew, ey + eh), (255, 0, 0), 2)

        # Simple Personality Logic
        if len(eyes) >= 2:
            personality = "Outgoing"
        else:
            personality = "Calm"

        emotion = "Happy" if len(eyes) > 0 else "Neutral"

        profile_text = f"Personality: {personality} | Emotion: {emotion}"

        break  # Only first face

    # Save Result Image
    result_path = os.path.join(UPLOAD_FOLDER, "result_" + file.filename)
    cv2.imwrite(result_path, img)

    return jsonify({
        "image": result_path,
        "profile": profile_text
    })


# Run App
if __name__ == "__main__":
    app.run(debug=True)