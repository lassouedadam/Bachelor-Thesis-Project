# Standard dependencies
import cv2
import os
import random
import numpy as np
from matplotlib import pyplot as plt

# TensorFlow Dependencies
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Layer, Conv2D, Dense, MaxPooling2D, Input, Flatten
import tensorflow as tf

import time
import re

import mysql.connector

# DB connexion
mydb = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="Xhh4azsese_",
    database="smartsec2"
)

# Siamese L1 Distance class
class L1Dist(Layer):
    
    def __init__(self, **kwargs):
        super().__init__()
       
    def call(self, input_embedding, validation_embedding):
        return tf.math.abs(input_embedding - validation_embedding)

# Preprocess function    
def preprocess(file_path):
    
    img = cv2.imread(file_path)

    if img is None:
        print("Error: Failed to read image file at", file_path)
        return None

    # Convert image to RGB format
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    #resizing the image to be 100x100x3
    img = cv2.resize(img, (100, 100))

    # Scale image to be between 0 and 1 
    img = img / 255.0

    return img


def verify(model, detection_threshold, verification_threshold):
    results = []
    
    # Get the model name
    model_name = os.path.splitext(os.path.basename(model.filepath))[0]
    
    # Paths : input img + Verification imgs
    input_img_path = os.path.join('application_data', 'input_image', 'input_image.jpg')
    verification_images_path = os.path.join('verification_images', model_name)
    
    for image in os.listdir(verification_images_path):
        input_img = preprocess(input_img_path)
        validation_img = preprocess(os.path.join(verification_images_path, image))
        
        # Make Predictions 
        result = model.predict([np.expand_dims(input_img, axis=0), np.expand_dims(validation_img, axis=0)])
        results.append(result)
    
    # Detection Threshold 
    detection = np.sum(np.array(results) > detection_threshold)
    
    # Verification Threshold
    total_images = len(os.listdir(verification_images_path))
    if total_images == 0:
        return results, False 
    verification = detection / total_images
    verified = verification > verification_threshold

    return results, verified


# Reload model 
def custom_load_model(filepath, custom_objects):
    model = tf.keras.models.load_model(filepath, custom_objects=custom_objects)
    model.filepath = filepath  # Store the filepath as an attribute of the model
    return model

# Argument
import argparse

parser = argparse.ArgumentParser(description='Process IP camera URL.')
parser.add_argument('ip_camera_url', type=str, help='URL for the IP camera')
args = parser.parse_args()

ip_camera_url = args.ip_camera_url

# Load models 
model_paths = [os.path.join('Models', f) for f in os.listdir('Models') if f.endswith('.h5')]

all_models = {}
for path in model_paths:
    # Use your custom_load_model function directly
    all_models[path] = custom_load_model(path, custom_objects={'L1Dist': L1Dist, 'BinaryCrossentropy': tf.losses.BinaryCrossentropy})

# Video Capture object
cap = cv2.VideoCapture(ip_camera_url)

# Load face cascade classifier
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

#Check Camera Zone
def get_zone(ip_camera_url):
    cursor = mydb.cursor()
    cursor.execute(f"SELECT zone FROM zones2 WHERE address ='{ip_camera_url}'")
    result = cursor.fetchone()
    if result:
        return result[0]
zone = get_zone(ip_camera_url)

#Check employee autorisations
def check_autorisation(model_name, zone):
    cursor = mydb.cursor()

    cursor.execute("SELECT {} FROM autorisations2 WHERE employe=%s".format(zone), (model_name,))

    result = cursor.fetchone()

    return result is not None and result[0] == 1


while True:
    # Capture frame-by-frame
    ret, frame = cap.read()

    if not ret:
        print("Error: Failed to capture frame")
        break

    # Convert frame to grayscale for better detection
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Detect faces in the grayscale frame
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=3)

    # Loop through detected faces
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

        # Save the face image
        face_frame = frame[y:y+h, x:x+w]
        filename = os.path.join('application_data', 'input_image', 'input_image.jpg')
        cv2.imwrite(filename, face_frame)

        # Preprocess the saved face image
        preprocessed_face = preprocess(filename)

        for model_path, model in all_models.items():
            
            # Perform verification 
            results, verified = verify(model, 0.5, 0.7)
            person_name = os.path.splitext(os.path.basename(model_path))[0]
            print(f"Employé détecté: {person_name}")
            
            # Control and update
            if verified:
                if check_autorisation(person_name, zone) == False:

                    #UPDATE DB TABLE 
                    sql = f"""
                    UPDATE dashboard2
                    SET {zone} = {zone} + 1
                    WHERE employe = %s
                    """
                    cursor.execute(sql, (person_name,))
                    mydb.commit()
                    cursor = mydb.cursor()
                 
                    sql = f"""
                    UPDATE dashboard2
                    SET detect_non_auto = detect_non_auto + 1
                    WHERE employe = %s
                    """
                    cursor.execute(sql, (person_name,))
                    mydb.commit()

                    # Save the entire frame
                    now = time.strftime("%Y-%m-%d_%H-%M-%S")
                    input_frame = frame

                    # Generate unique filename for frame image
                    filename_frame = os.path.join('application_data', 'input_frame', f"frame_{cap.get(cv2.CAP_PROP_BACKEND)}-{now}.jpg")
                    cv2.imwrite(filename_frame, input_frame)

                    # Update log file
                    with open('verification_log.txt', 'a') as log_file:
                        modelname = os.path.splitext(os.path.basename(model_path))[0]
                        log_file.write(f"Person: {modelname}, Date and Time: {now}, Image: {filename_frame}, Zone: {zone}\n")

                break

# Release the VideoCapture and close all windows
cap.release()
cv2.destroyAllWindows()
