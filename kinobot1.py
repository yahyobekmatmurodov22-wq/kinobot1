import telebot
import os
import json

bot = telebot.TeleBot("7734015917:AAHS3UxZHboCxUcsfjHcaQTQYatQV7gNTE4")
ADMIN = 5437530757
os.makedirs("movies", exist_ok=True)

try: 
    movies = json.load(open("movies.json", encoding='utf-8'))
except: 
    movies = {}

AD_CHANNEL = "@yahyobekuzz"

# Start komandasi
@bot.message_handler(commands=['start'])
def start(m):
    bot.reply_to(m, 
        f"🎬 Salom! Kino kodini yuboring.\n\n"
        f"📢 Kanal: {AD_CHANNEL}\n"
        f"👤 Admin: @yahyobek_04_26")

# Kino qo'shish (admin) - ISHLAYDI
@bot.message_handler(commands=['add'])
def add_movie(m):
    if m.from_user.id != ADMIN: 
        bot.reply_to(m, "❌ Siz admin emassiz!")
        return
    
    if len(m.text.split()) < 2:
        bot.reply_to(m, "❌ Kod kiriting: /add 123")
        return
    
    code = m.text.split()[1]
    bot.reply_to(m, f"📝 Endi {code} kodli video ni yuboring!")
    
    # Keyingi qadamni kutish
    bot.register_next_step_handler(m, process_video, code)

# Video qabul qilish
def process_video(m, code):
    try:
        if m.video:
            # Video faylini olish
            file_id = m.video.file_id
            file_info = bot.get_file(file_id)
            
            # Faylni yuklab olish
            downloaded_file = bot.download_file(file_info.file_path)
            
            # Faylni saqlash
            path = f"movies/{code}.mp4"
            with open(path, "wb") as video_file:
                video_file.write(downloaded_file)
            
            # Ma'lumotlarni saqlash
            movies[code] = {
                "path": path,
                "title": f"Kino {code}",
                "added_date": str(m.date)
            }
            
            with open("movies.json", "w", encoding='utf-8') as f:
                json.dump(movies, f, ensure_ascii=False, indent=2)
            
            bot.reply_to(m, f"✅ Kino saqlandi! Kod: {code}")
            
        else:
            bot.reply_to(m, "❌ Video yuboring!")
            
    except Exception as e:
        bot.reply_to(m, f"❌ Xatolik: {str(e)}")

# Reklama yuborish (admin)
@bot.message_handler(commands=['broadcast'])
def broadcast(m):
    if m.from_user.id != ADMIN: 
        return
    
    if len(m.text.split()) < 2:
        bot.reply_to(m, "📢 Reklama yuborish:\n/broadcast xabar matni")
        return
    
    msg = ' '.join(m.text.split()[1:])
    
    # Foydalanuvchilarni olish
    user_count = 0
    if os.path.exists("users.json"):
        try:
            with open("users.json", "r", encoding='utf-8') as f:
                users_data = json.load(f)
                user_count = len(users_data)
                
                for user_id in users_data.keys():
                    try:
                        bot.send_message(int(user_id), f"📢 {msg}\n\n{AD_CHANNEL}")
                    except:
                        continue
        except:
            pass
    
    bot.reply_to(m, f"✅ Reklama {user_count} foydalanuvchiga yuborildi")

# Foydalanuvchini saqlash
def save_user(user_id, username, first_name):
    try:
        if os.path.exists("users.json"):
            with open("users.json", "r", encoding='utf-8') as f:
                users_data = json.load(f)
        else:
            users_data = {}
        
        users_data[str(user_id)] = {
            "username": username,
            "first_name": first_name
        }
        
        with open("users.json", "w", encoding='utf-8') as f:
            json.dump(users_data, f, ensure_ascii=False, indent=2)
    except:
        pass

# Kino olish
@bot.message_handler(func=lambda m: True)
def get_movie(m):
    # Foydalanuvchini saqlash
    save_user(m.from_user.id, m.from_user.username, m.from_user.first_name)
    
    code = m.text.strip()
    
    if code in movies and os.path.exists(movies[code]["path"]):
        try:
            with open(movies[code]["path"], 'rb') as video_file:
                bot.send_video(m.chat.id, video_file, 
                    caption=f"🎬 Kod: {code}\n📢 {AD_CHANNEL}")
        except Exception as e:
            bot.reply_to(m, f"❌ Video yuborishda xatolik")
    else:
        bot.reply_to(m, f"❌ {code} kodli kino topilmadi")

print("🤖 Bot ishga tushdi...")
print(f"👑 Admin: {ADMIN}")
print(f"📢 Kanal: {AD_CHANNEL}")
# --- avvalgi kod (o'zingiz berilgan kinobot1.py) yuqorida qoladi ---
# ... (telebot import va handlerlar) ...

from flask import Flask
import threading
import os

app = Flask(__name__)

# Soddа health-check endpoint — UptimeRobot shu URLni ping qiladi
@app.route("/", methods=["GET"])
def index():
    return "OK", 200

def run_bot():
    try:
        print("🤖 Bot ishga tushmoqda (fon ipda)...")
        # infinity_polling bloklaydi, shuning uchun uni alohida ipda ishga tushiramiz
        bot.infinity_polling(timeout=60, long_polling_timeout = 60)
    except Exception as e:
        print("Botda xatolik:", e)

if __name__ != "__main__":
    # Agar fayl modul sifatida import qilinsa ham hech narsa qilinmasligi mumkin,
    # lekin Render gunicorn orqali app obyektini import qiladi va __name__ == "kinobot1"
    pass

# Agar fayl to'g'ridan-to'g'ri ishga tushsa (masalan lokal test)
if __name__ == "__main__":
    # Botni fon ipda ishga tushiramiz
    t = threading.Thread(target=run_bot, daemon=True)
    t.start()

    port = int(os.environ.get("PORT", 5000))
    print(f"🌐 Web server 0.0.0.0:{port} da ishlaydi (local).")
    app.run(host="0.0.0.0", port=port)
else:
    # Agar gunicorn orqali import qilingan bo'lsa (Renderda shunday foydalanamiz),
    # birdan botni fon ipda ishga tushiramiz:
    try:
        t = threading.Thread(target=run_bot, daemon=True)
        t.start()
        print("🤖 Bot fon ipda ishga tushirildi (gunicorn/modul import).")
    except Exception as e:
        print("Fon ipni boshlashda xatolik:", e)

# end of file
bot.infinity_polling()