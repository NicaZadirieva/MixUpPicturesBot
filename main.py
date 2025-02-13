from aiogram import Bot, Dispatcher, executor, types
from dotenv import load_dotenv

import os
from os import listdir
from os.path import isfile, join

import random

# загрузка переменных окружения
load_dotenv()
API_TOKEN = os.getenv("MY_TOKEN")
# инициализация бота
bot = Bot(token=API_TOKEN)
dispatcher = Dispatcher(bot)

# Префикс к папке с изображениями
DOWNLOADS_PREFIX = 'img'


# утильная функция. Подставляет префикс к id юзера
def util_get_download_folder(user_id):
    return DOWNLOADS_PREFIX + "_" + str(user_id)


@dispatcher.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    await message.answer('Привет! Пришли мне список фото и я их перемешаю')


@dispatcher.message_handler(content_types=types.ContentTypes.PHOTO)
async def handle_photo(message: types.Message):
    # Создаем папку для сохранения файлов, если её нет
    downloads_folder = util_get_download_folder(message.from_user.id)
    if not os.path.exists(downloads_folder):
        os.makedirs(downloads_folder)
    await download_photo(message)
    # Далее можно провести необходимую обработку или отправить ответ пользователю
    mixed_images_path = await mix_up_photos(message)
    await send_mixed_photos(message, mixed_images_path)


async def download_photo(message: types.Message):
    downloads_folder = util_get_download_folder(message.from_user.id)
    if message.photo:
        # Получаем информацию о фотографии
        photo_info = message.photo[-1]
        # Получаем объект File для скачивания
        photo_file = await bot.get_file(photo_info.file_id)

        # Загружаем фотографию в локальную папку
        photo_path = os.path.join(downloads_folder, f'photo_{message.message_id}.jpg')
        await photo_file.download(photo_path)


async def mix_up_photos(message):
    downloads_folder = util_get_download_folder(message.from_user.id)
    image_paths = [f for f in listdir(downloads_folder) if isfile(join(downloads_folder, f))]
    random.shuffle(image_paths)
    return image_paths


async def send_mixed_photos(message: types.Message, mixed_images_path):
    media_group = types.MediaGroup()
    downloads_folder = util_get_download_folder(message.from_user.id)
    for image_path in mixed_images_path:
        media_group.attach_photo(types.InputFile(os.path.join(downloads_folder, image_path), 'Превосходная фотография'))
    await bot.send_media_group(media=media_group, chat_id=message.chat.id)


executor.start_polling(dispatcher)
