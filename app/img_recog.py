import cv2
import face_recognition
import pickle
import numpy as np
import io

# Load the known encodings and IDs from the file
with open("model/Testing/face_recog/EncodeFile.p", 'rb') as file:
    encodeListKnown, studentIds = pickle.load(file)

print("File Loaded")

def findEncodings(image):
    img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # Convert BGR to RGB
    encodings = face_recognition.face_encodings(img_rgb)
    return encodings

def recognize_face(encoding_to_check):
    matches = face_recognition.compare_faces(encodeListKnown, encoding_to_check)
    face_distances = face_recognition.face_distance(encodeListKnown, encoding_to_check)
    best_match_index = np.argmin(face_distances)
    if matches[best_match_index]:
        return studentIds[best_match_index]
    else:
        return "Unknown"
    
def process_image(image_file):
    # Read the image file
    new_image = cv2.imdecode(np.fromstring(image_file.read(), np.uint8), cv2.IMREAD_COLOR)

    # Check if the image was loaded correctly
    if new_image is None:
        raise ValueError("Error: Image could not be loaded.")
    
    # Find encodings for the new image
    print("Encoding new image...")
    new_encodings = findEncodings(new_image)

    # Compare each encoding in the new image with the known encodings
    rgb_image = cv2.cvtColor(new_image, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_image)
    
    for (top, right, bottom, left) in face_locations:
        name = recognize_face(face_recognition.face_encodings(rgb_image, [(top, right, bottom, left)])[0])
        cv2.rectangle(new_image, (left, top), (right, bottom), (0, 255, 0), 2)
        cv2.putText(new_image, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    # Convert the processed image to a byte stream
    _, img_encoded = cv2.imencode('.jpg', new_image)
    return io.BytesIO(img_encoded.tobytes())


