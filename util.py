import urllib.request
import urllib.error
import base64
import json
from google.cloud import vision, language_v1
from google.cloud.vision import types
from google.cloud.language_v1 import enums
import io
import boto3
import csv

def get_request(url, h):
    request = urllib.request.Request(url, headers=h, method="GET")
    with urllib.request.urlopen(request) as response:
        data = response.read().decode('ascii')
    return data

def post_request(url, h ,b):
    body = urllib.parse.urlencode(b).encode('ascii')
    request = urllib.request.Request(url, data=body, headers=h, method="POST")
    with urllib.request.urlopen(request) as response:
        data = json.loads(response.read().decode('ascii'))
    return data

def read_text_gcv(text):
    client = language_v1.LanguageServiceClient()

    document = {
        "content": text,
        "type": enums.Document.Type.PLAIN_TEXT
    }

    response = client.analyze_sentiment(document, encoding_type=enums.EncodingType.UTF8)

    data = {
        "score": response.document_sentiment.score,
        "magnitude": response.document_sentiment.magnitude
    }

    return data

def read_face_gcv(image_path):
    client = vision.ImageAnnotatorClient()

    with io.open(image_path, "rb") as image:
        data = image.read()
    
    image = types.Image(content=data)
    response = client.face_detection(image)

    faces = response.face_annotations

    try:
        face = faces[0]

        emotions = [
        {
            'Type': 'JOY',
            'Likelihood': face.joy_likelihood
        }, 
        {
            'Type': 'SORROW',
            'Likelihood': face.sorrow_likelihood
        }, 
        {
            'Type': 'ANGER',
            'Likelihood': face.anger_likelihood
        }, 
        {
            'Type': 'SURPRISE',
            'Likelihood': face.surprise_likelihood
        }
    ]

    except:
        emotions = "No face found"

    return emotions

def read_face_aws(image_path):
    client = boto3.client('rekognition')

    with open(image_path, "rb") as image:
        response = client.detect_faces(Image={'Bytes': image.read()}, Attributes=['ALL'])
    
    return response['FaceDetails'][0]['Emotions']

def read_csv(file_path):
    final_data = []
    with open(file_path, "r") as csv_file:
        data = csv.DictReader(csv_file)
        for line in data:
            final_data.append(line)
    
    return final_data

def pull_foods(foods, emotion):
    matches = []

    for food in foods:
        if food['mood'] == emotion:
            matches.append(food)
    
    return matches

def calculate_emotion_image(data):
    print(data)
    high_num = 0
    high_emotion = ''

    for emotion in data:
        if emotion['Likelihood'] > high_num:
            high_num = emotion['Likelihood']
            if emotion['Type'] == "JOY":
                high_emotion = "Happy"
            elif emotion['Type'] == "SORROW":
                high_emotion = "Sad"
            elif emotion['Type'] == "ANGER":
                high_emotion = "Angry"
            elif emotion['Type'] == "SURPRISE":
                high_emotion = "Surprised"
    
    return high_emotion

def calculate_emotion_text(data):
    if data['score'] > 0:
        emotion = "Happy"
    elif data['score'] <= 0:
        emotion = "Sad"

    return emotion
