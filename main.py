import telebot
import os
from rubpy import Client
import requests
import asyncio
from mutagen.id3 import ID3, APIC, TIT2, TPE1, error, TALB
from mutagen.mp3 import MP3
import os
from keep_alive import keep_alive

TOKEN = os.getenv("TOKEN")
DOWNLOAD_DIR = 'downloads'
os.makedirs(DOWNLOAD_DIR, exist_ok=True)
bot = telebot.TeleBot(TOKEN)

auth = os.getenv("AUTH")
key = os.getenv("KEY")
channel = "c0Cknsx046fe22f6032301f7d672870e"

cap_music = """< آهنگ کلیپ | 𝑨𝒉𝒏𝒈 𝑪𝒍𝒊𝒑 >

#موسیقی
#Reza.Lucifer

‹‹ **ریکشن فراموش نشه** ››

@Ahng_Clip_insta"""

cap_video = """< آهنگ کلیپ | 𝑨𝒉𝒏𝒈 𝑪𝒍𝒊𝒑 >

#کلیپ
#Reza.Lucifer"""

def update_mp3_metadata(file_path, title, artist, image_path, album):
	try:
		if not os.path.isfile(file_path):
			print(f"فایل MP3 پیدا نشد: {file_path}")
			return
		if not os.path.isfile(image_path):
			print(f"فایل تصویر پیدا نشد: {image_path}")
			return
		audio = MP3(file_path, ID3=ID3)
		try:
			audio.add_tags()
		except error:
			pass
		audio.tags["TIT2"] = TIT2(encoding=3, text=title)
		audio.tags["TALB"] = TALB(encoding=3, text=album)
		audio.tags["TPE1"] = TPE1(encoding=3, text=artist)
		audio.tags.delall("APIC")
		with open(image_path, "rb") as img:
			img_data = img.read()
			mime = "image/jpeg" if image_path.lower().endswith(".jpg") or image_path.lower().endswith(".jpeg") else "image/png"
			audio.tags.add(
				APIC(
					encoding=3,
					mime=mime,
					type=3,
					desc="Cover",
					data=img_data
				)
			)
		audio.save()
		print("عنوان، هنرمند و کاور با موفقیت اضافه شدند.")
	except Exception as e:
		print(f"خطا: {e}")


async def main(type, file, cap):
	async with Client(name="7914", auth=auth, private_key=key, display_welcome=False) as app:
		print("start rubpy")
		if type == "Music":
			update_mp3_metadata(file,title="< آهنگ کلیپ | 𝑨𝒉𝒏𝒈 𝑪𝒍𝒊𝒑 >",artist="آهنگ کلیپ | 𝑨𝒉𝒏𝒈 𝑪𝒍𝒊𝒑",image_path="image.jpg", album="آهنگ کلیپ | 𝑨𝒉𝒏𝒈 𝑪𝒍𝒊𝒑")
			await app.send_music(channel, file, cap)
		elif type == "Voice":
			await app.send_voice(channel, file)
		elif type == "Photo":
			await app.send_photo(channel, file)
		elif type == "Video":
			await app.send_video(channel, file, cap)

def save_and_upload(file_id, file_name, message, type, cap=None):
	try:
		file_info = bot.get_file(file_id)
		downloaded_file = bot.download_file(file_info.file_path)

		file_path = os.path.join(DOWNLOAD_DIR, file_name)
		with open(file_path, 'wb') as f:
			f.write(downloaded_file)

		bot.reply_to(message, f"فایل ذخیره شد: {file_name}")
		
		# آپلود به روبیکا
		asyncio.run(main(type=type, file=file_path, cap=cap))
		bot.send_message(message.chat.id, f"ارسال شد.")
	except Exception as e:
		bot.reply_to(message, f"خطا: {e}")

@bot.message_handler(content_types=['audio'])
def handle_audio(message):
	name = message.audio.file_name or f"{message.audio.file_id}.mp3"
	save_and_upload(message.audio.file_id, name, message, "Music", cap=cap_music)

@bot.message_handler(content_types=['voice'])
def handle_voice(message):
	name = f"{message.voice.file_id}.ogg"
	save_and_upload(message.voice.file_id, name, message, "Voice")

@bot.message_handler(content_types=['video'])
def handle_video(message):
	name = message.video.file_name or f"{message.video.file_id}.mp4"
	save_and_upload(message.video.file_id, name, message, "Video", cap=cap_video)

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
	photo = message.photo[-1]
	name = f"{photo.file_id}.jpg"
	save_and_upload(photo.file_id, name, message, "Photo")

print("ربات در حال اجراست...")
keep_alive()
bot.infinity_polling()