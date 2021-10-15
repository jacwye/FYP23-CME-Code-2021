import pyrebase
from dotenv import load_dotenv
import os
import re

def uploadFFTFiles(sensor_id, timestamp):
  load_dotenv()

  serviceAccountJson = os.getenv("FIREBASE_SERVICE_ACCOUNT")
  firebase_email = os.getenv("FIREBASE_USERNAME")
  firebase_password = os.getenv("FIREBASE_PASSWORD")

  firebaseConfig = {
    "apiKey": "AIzaSyBl4ZVaBSQcjiwU-yLZ4JZYorVP6Z-gbnM",
    "authDomain": "cms-uoa.firebaseapp.com",
    "databaseURL": "https://cms-uoa.firebaseio.com",
    "projectId": "cms-uoa",
    "storageBucket": "cms-uoa.appspot.com",
    "messagingSenderId": "314758269258",
    "appId": "1:314758269258:web:a742f38723f9eaf5c599b3",
    "measurementId": "G-7L54DZLZNH",
    "serviceAccount": serviceAccountJson
  };

  firebase = pyrebase.initialize_app(firebaseConfig)
  firebase_auth = firebase.auth()
  firebase_storage = firebase.storage()

  firebase_user = firebase_auth.sign_in_with_email_and_password(firebase_email, firebase_password)

  timestamp_formatted = re.sub('[^A-Za-z0-9]+', '', timestamp)
  print(timestamp_formatted)

  graph_path_on_cloud = "fft/" + sensor_id + "/graph/" + timestamp_formatted + ".png"
  graph_path_on_device = "generated\\" + sensor_id + ".png"

  firebase_upload = firebase_storage.child(graph_path_on_cloud).put(graph_path_on_device, firebase_user["idToken"])
  url = firebase_storage.child(graph_path_on_cloud).get_url(firebase_upload['downloadTokens'])
  print("GRAPH URL")
  print(url)

  data_path_on_cloud = "fft/" + sensor_id + "/data/" + timestamp_formatted + ".txt"
  data_path_on_device = "generated\\" + sensor_id + ".txt"

  firebase_upload = firebase_storage.child(data_path_on_cloud).put(data_path_on_device, firebase_user["idToken"])
  url = firebase_storage.child(data_path_on_cloud).get_url(firebase_upload['downloadTokens'])
  print("TEXT FILE URL")
  print(url)






