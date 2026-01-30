import os, asyncio, logging, threading
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart
from aiogram.types import FSInputFile
import yt_dlp
from http.server import BaseHTTPRequestHandler, HTTPServer

# --- ВЕБ-СЕРВЕР ДЛЯ KOYEB HEALTH CHECK ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"I am alive")

def run_health_server():
    # Koyeb за замовчуванням шукає порт 8000
    server = HTTPServer(('0.0.0.0', 8000), HealthCheckHandler)
    server.serve_forever()

# --- БОТ ---
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
    await m.answer("Привіт! Бот успішно запущений на Koyeb. Надсилай посилання!")

@dp.message(F.text.startswith("http"))
async def handle(m: types.Message):
    status = await m.answer("⏳ Обробка посилання...")
    try:
        path = await asyncio.to_thread(_download, m.text)
        await m.answer_audio(FSInputFile(path))
        os.remove(path)
        await status.delete()
    except Exception as e:
        await status.edit_text(f"Помилка: {e}")

async def main():
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
    
    # Запускаємо веб-сервер у фоновому потоці
    threading.Thread(target=run_health_server, daemon=True).start()
    
    print("Бот запускається...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
EOF
