import os

import requests


def generate_images(folder_path):
    url = "http://localhost:8000/api/diffusiondiffusion"
    for filename in os.listdir(folder_path):
        if not filename.endswith('.jpg') or not filename.endswith('.png'):  # Add or modify file types
            pass

        file_path = os.path.join(folder_path, filename)
        file_data = open(file_path, 'rb')

        response = requests.post(url, files={'file': file_data})

        file_data.close()

        # Check the response
        if response.status_code == 200:
            print(f"File uploaded successfully. Access link - {response.json()['access_link']}")
        else:
            print('Failed to upload file')


if __name__ == '__main__':
    generate_images('images')
