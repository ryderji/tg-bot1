import asyncio
import logging
import os
import re
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
import yt_dlp

#from dotenv import load_dotenv


BOT_TOKEN = ("8756849498:AAHeMos32AjUNgF1f6P5pJ1_ejyvOnYTZwY")

# =========================
# НАСТРОЙКИ
# =========================
logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Папка для временных файлов
DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# Регулярка для ссылок
URL_REGEX = re.compile(r'(https?://[^\s]+)')


# Проверка поддерживаемых сайтов
def is_supported(url: str) -> bool:
    return any(site in url for site in [
        "tiktok.com",
        "youtube.com/shorts",
        "youtu.be",
        "instagram.com/reel"
    ])


# Скачивание видео через yt-dlp
async def download_video(url: str) -> str | None:
    loop = asyncio.get_event_loop()

    def _download():
        try:
            ydl_opts = {
                'outtmpl': f'{DOWNLOAD_FOLDER}/%(id)s.%(ext)s',
                'format': 'mp4/best',
                'quiet': True,
                'noplaylist': True,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                file_path = ydl.prepare_filename(info)
                return file_path
        except:
            return None

    return await loop.run_in_executor(None, _download)


# Обработка сообщений
@dp.message()
async def handle_message(message: Message):
    text = message.text or ""
    urls = URL_REGEX.findall(text)

    for url in urls:
        if not is_supported(url):
            continue

        file_path = await download_video(url)

        if not file_path or not os.path.exists(file_path):
            await message.answer("Видео недоступно")
            continue

        try:
            video = types.FSInputFile(file_path)
            await message.answer_video(video)
        except:
            await message.answer("Видео недоступно")
        finally:
            # удаляем файл после отправки
            try:
                os.remove(file_path)
            except:
                pass


# =========================
# ЗАПУСК
# =========================
async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())