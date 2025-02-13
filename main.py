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

# Папка для сохранения изображений
DOWNLOADS_FOLDER = 'downloads'

# Метаинформация об изображений в телеграмме
images = dict()


@dispatcher.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    await message.answer('Привет! Пришли мне список фото и я их перемешаю')


@dispatcher.message_handler(content_types=types.ContentTypes.PHOTO)
async def handle_photo(message: types.Message):
    # Создаем папку для сохранения файлов, если её нет
    if not os.path.exists(DOWNLOADS_FOLDER):
        os.makedirs(DOWNLOADS_FOLDER)
    await download_photo(message)
    # Далее можно провести необходимую обработку или отправить ответ пользователю
    mixed_images_path = await mix_up_photos()
    await send_mixed_photos(message, mixed_images_path)


async def download_photo(message: types.Message):
    # Проверяем, есть ли файл в сообщении
    user_id = message.from_user.id

    if message.photo:
        # Получаем информацию о фотографии
        photo_info = message.photo[-1]
        # Получаем объект File для скачивания
        photo_file = await bot.get_file(photo_info.file_id)

        # Загружаем фотографию в локальную папку
        photo_path = os.path.join(DOWNLOADS_FOLDER, f'photo_{message.message_id}.jpg')
        await photo_file.download(photo_path)
        images[message.message_id] = photo_info.file_id


async def mix_up_photos():
    image_paths = [f for f in listdir(DOWNLOADS_FOLDER) if isfile(join(DOWNLOADS_FOLDER, f))]
    random.shuffle(image_paths)
    return image_paths


async def send_mixed_photos(message: types.Message, mixed_images_path):
    media_group = types.MediaGroup()
    for image_path in mixed_images_path:
        message_id = image_path.split("_")[-1].split(".")[0]
        media_group.attach_photo(types.InputFile(os.path.join(DOWNLOADS_FOLDER, image_path), 'Превосходная фотография'))
    await bot.send_media_group(media=media_group, chat_id=message.chat.id)


executor.start_polling(dispatcher)
