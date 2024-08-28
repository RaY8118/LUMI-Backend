import cv2
import face_recognition
import pickle
import os


UPLOAD_FOLDER = "model/Testing/faceRecog/images"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


def get_images():
    pathlist = os.listdir(UPLOAD_FOLDER)
    imgList = []
    personIds = []

    for path in pathlist:
        img_path = os.path.join(UPLOAD_FOLDER, path)
        img = cv2.imread(img_path)

        if img is None:
            print(f"Error loading image: {img_path}")
            continue

        imgList.append(img)
        personIds.append(os.path.splitext(path)[0])

    if not imgList:
        print("No valid images loaded.")
    else:
        print(f"Loaded {len(imgList)} images successfully.")

    return imgList, personIds


def find_encodings(imageslist):
    encodeList = []
    for img in imageslist:
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encodings = face_recognition.face_encodings(img_rgb)
        if encodings:
            encodeList.append(encodings[0])
        else:
            print("No faces found in the image.")
    return encodeList


def save_encodings(encodeListKnown, personIds):
    encodeListKnownWithIds = [encodeListKnown, personIds]
    with open("resources/EncodeFile.p", "wb") as file:
        pickle.dump(encodeListKnownWithIds, file)
    print("File saved")
