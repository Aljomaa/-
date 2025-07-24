import asyncio
from pyrogram import Client
from pytgcalls import PyTgCalls
from pytgcalls.types.input_stream import InputStream
from pytgcalls.types.input_stream.input_audio_stream import InputAudioStream
import logging
import os

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID"))

AUDIO_STREAM_URL = "https://qurango.net/radio/yasser_aldosari"

logging.basicConfig(level=logging.INFO)

app = Client("quran_radio_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
voice = PyTgCalls(app)

async def start_stream():
    await app.start()
    await voice.start()
    logging.info("✅ البوت يعمل وتم الاتصال")

    while True:
        try:
            await voice.join_group_call(
                CHAT_ID,
                InputStream(InputAudioStream(AUDIO_STREAM_URL)),
                stream_type="local_stream"
            )
            logging.info("🎧 بدأ البث بصوت ياسر الدوسري")
            while True:
                await asyncio.sleep(30)
        except Exception as e:
            logging.warning(f"❌ حدث خطأ: {e}")
            logging.info("🔁 إعادة المحاولة بعد 10 ثوانٍ")
            await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(start_stream())
