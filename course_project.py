import json
import os
import requests
from tqdm import tqdm


def input_info():
    print('Введите ID Пользователя:')
    OWNER_ID = #input()

    print('Введите токен Яндекс Диск:')
    API_TOKEN =  #input()
    YdUploader(API_TOKEN).photos_upload(VkDownloader(OWNER_ID).photos_download())


class VkDownloader:
    def __init__(self, owner_id):
        self.API_TOKEN = # Вставить проверочный токен
        self.API_VERSION = '5.131'
        self.API_LINK = 'https://api.vk.com/method/'
        self.OWNER_ID = owner_id
        self.FOLDER = 'vk_photos/'

    def photos_download(self):
        API_METHOD = 'photos.get'
        API_EXTENDED = 1
        API_FILE_COUNT = 5
        album_ids = ['wall', 'profile', 'saved']
        files_list = list()
        files_names = set()

        if not os.path.exists(self.FOLDER):
            os.mkdir(self.FOLDER)
        print('Скачиваю файлы')
        for album_id in tqdm(album_ids):
            parameters = dict(access_token=self.API_TOKEN, v=self.API_VERSION, owner_id=self.OWNER_ID,
                              album_id=album_id, count=API_FILE_COUNT, extended=API_EXTENDED)
            request_info = requests.get(self.API_LINK + API_METHOD, params=parameters)
            try:
                for item in request_info.json()['response']['items']:
                    file_link = item['sizes'][-1]['url']
                    file_size = item['sizes'][-1]['type']
                    file_likes = item['likes']['count']
                    file_date = item['date']
                    file_name = f'{file_likes}.jpg'

                    if file_name in files_names:
                        file_name = f'{file_likes}_{file_date}.jpg'
                    files_names.add(file_name)
                    files_list.append({'name': file_name, 'size': file_size, 'link': file_link})

                    download_request = requests.get(file_link)
                    download_folder = os.path.join(self.FOLDER, file_name)
                    with open(download_folder, 'wb') as file_obj:
                        file_obj.write(download_request.content)

            except KeyError:
                pass
        with open('photos_json.txt', 'w') as json_file:
            json_data = {'content': files_list}
            json.dump(json_data, json_file)
        print('Создал JSON файл')
        return files_list


class YdUploader:
    def __init__(self, api_token):
        self.API_TOKEN = api_token
        self.API_LINK = 'https://cloud-api.yandex.net/v1/disk/'
        self.FOLDER = 'vk_photos'

    def photos_upload(self, files_list):
        files_list = files_list
        API_METHOD_UPLOAD = 'resources/upload'
        upload_yd = self.API_LINK + API_METHOD_UPLOAD

        API_METHOD_FOLDER = 'resources'
        folder_request_url = self.API_LINK + API_METHOD_FOLDER

        print('Загружаю файлы')
        requests.put(folder_request_url, headers={'Authorization': self.API_TOKEN}, params={'path': f'{self.FOLDER}'})
        for file in tqdm(files_list):
            file_name = file['name']
            file_path = os.path.join(f'{self.FOLDER}/', file_name)
            upload_request = requests.get(upload_yd, headers={'Authorization': self.API_TOKEN},
                                          params={'path': f'{self.FOLDER}/{file_name}', 'overwrite': 1})
            upload_url = upload_request.json()['href']
            with open(file_path, 'rb') as file_obj:
                requests.put(upload_url, files={"file": file_obj})


input_info()
