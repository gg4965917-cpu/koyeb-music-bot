import os, asyncio, logging
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart
from aiogram.types import FSInputFile
import yt_dlp

# Отримуємо токен зі змінних оточення
BOT_TOKEN = os.getenv("BOT_TOKEN")
logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

def _download(url):
    opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '192'}],
        'noplaylist': True,
        'quiet': True
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info).rsplit('.', 1)[0] + '.mp3'

@dp.message(CommandStart())
async def start(m: types.Message):
    await m.answer("Привіт! Я працюю на Koyeb. Надішли мені посилання на YouTube — я зроблю MP3.")

@dp.message(F.text.startswith("http"))
async def handle(m: types.Message):
    status = await m.answer("⏳ Завантажую аудіо...")
    try:
        path = await asyncio.to_thread(_download, m.text)
        await m.answer_audio(FSInputFile(path))
        os.remove(path)
        await status.delete()
    except Exception as e:
        await status.edit_text(f"Помилка: {e}")

async def main():
    # Створюємо папку для завантажень, якщо її немає
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
