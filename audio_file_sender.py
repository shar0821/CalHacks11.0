import requests

url = 'https://aebe-199-115-241-205.ngrok-free.app/upload_audio'

file_path = 'sample.mp3'
with open(file_path, 'rb') as file:
    files = {'file': (file_path, file, 'audio/mpeg')}
    response = requests.post(url, files=files)

if response.status_code == 200:
    print('File uploaded successfully')
else:
    print(f'Failed to upload file. Status code: {response.status_code}, Response: {response.text}')
