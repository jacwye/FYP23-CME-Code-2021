import requests

url = 'http://localhost:5001/cms-uoa/us-central1/ingestor/fft/sensor/r8WLiEfSSS6ceYb8N6pN'

files = {"fftImage": open('D:/University Files/Summer Research Scholarship/defaultImage.png', 'rb')}

response = requests.post(url, files=files)
print(response)
