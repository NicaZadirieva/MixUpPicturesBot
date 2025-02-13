import os
import shutil
from os import listdir
from os.path import isfile

from dotenv import load_dotenv, dotenv_values
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import Text, BoundFilter
from os.path import isfile, join
from aiogram.types import ContentType


# загрузка переменных окружения
load_dotenv()
API_TOKEN = os.getenv("MY_TOKEN")
# инициализация бота
bot = Bot(token=API_TOKEN)
dispatcher = Dispatcher(bot)

DOWNLOADS_FOLDER = 'downloads'


class IsPrivate(BoundFilter):
    async def check(self, message: types.Message):
        return types.ChatType.PRIVATE == message.chat.type


@dispatcher.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    await message.answer('Привет! Пришли мне список фото и я их перемешаю')


async def download_photo(message: types.Message):
    # Проверяем, есть ли файл в сообщении
    user_id = message.from_user.id
    if message.photo:
        # Получаем информацию о фотографии
        photo_info = message.photo[-1]
        # Получаем объект File для скачивания
        photo_file = await bot.get_file(photo_info.file_id)
        # Создаем папку для сохранения файлов, если её нет
        if not os.path.exists(DOWNLOADS_FOLDER):
            os.makedirs(DOWNLOADS_FOLDER)

        # Загружаем фотографию в локальную папку
        photo_path = os.path.join(DOWNLOADS_FOLDER, f'photo_{message.message_id}.jpg')
        await photo_file.download(photo_path)

        # Далее можно провести необходимую обработку или отправить ответ пользователю
        await shuffle_photos(message)


async def shuffle_photos(message):
    images = [f for f in listdir(DOWNLOADS_FOLDER) if isfile(join(DOWNLOADS_FOLDER, f))]
    print(images)


@dispatcher.message_handler(content_types=types.ContentTypes.PHOTO)
async def handle_photo(message: types.Message):
    await download_photo(message)


executor.start_polling(dispatcher)
