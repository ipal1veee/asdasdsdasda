import telebot
import subprocess
import os
import re
import tempfile
from telebot import types
import sys

# Токен твоего бота
TOKEN = '6'

# Твой Telegram ID (это нужно указать)
AUTHORIZED_USER_ID = 

# Создаём объект бота
bot = telebot.TeleBot(TOKEN)

# Переменная для хранения текущего пути загрузки
current_upload_path = os.getcwd()

def strip_ansi_codes(text: str) -> str:
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)

def get_system_info():
    """Получение информации о системе через shell команды"""
    global current_upload_path
    try:
        # CPU информация
        cpu_info = subprocess.check_output(['bash', '-c', 'lscpu | grep -E "(Model name|CPU\(s\)):" | head -2']).decode('utf-8')
        cpu_usage = subprocess.check_output(['bash', '-c', "top -bn1 | grep 'Cpu(s)' | awk '{print $2}'"]).decode('utf-8').strip()
        
        # Память
        memory_info = subprocess.check_output(['bash', '-c', 'free -h | grep Mem']).decode('utf-8')
        memory_parts = memory_info.split()
        
        # Диск
        disk_info = subprocess.check_output(['bash', '-c', 'df -h / | tail -1']).decode('utf-8')
        disk_parts = disk_info.split()
        
        # Uptime
        uptime_info = subprocess.check_output(['bash', '-c', 'uptime -p']).decode('utf-8').strip()
        
        info = f"""
🖥️ **Системная информация:**

**Процессор:**
{cpu_info.strip()}
• Использование: {cpu_usage}%

**Память:**
• Всего: {memory_parts[1]}
• Использовано: {memory_parts[2]} ({memory_parts[4]})

**Диск:**
• Всего: {disk_parts[1]}
• Использовано: {disk_parts[2]} ({disk_parts[4]})

**Время работы:** {uptime_info}

**📁 Текущий путь загрузки:**
`{current_upload_path}`
"""
        return info
    except Exception as e:
        return f"Ошибка получения информации о системе: {str(e)}"

def get_running_processes():
    """Получение списка запущенных процессов через top"""
    try:
        processes = subprocess.check_output(['bash', '-c', 'top -bn1 | head -20']).decode('utf-8')
        return f"🏃 **Топ процессов:**\n\n```\n{processes}\n```"
    except Exception as e:
        return f"Ошибка получения процессов: {str(e)}"

def get_network_info():
    """Получение сетевой информации через shell команды"""
    try:
        # Сетевая статистика
        net_io = subprocess.check_output(['bash', '-c', 'cat /proc/net/dev | grep -E "(eth|wlan|enp|wlp)" | head -3']).decode('utf-8')
        
        # IP адреса
        ip_info = subprocess.check_output(['bash', '-c', 'ip a | grep "inet " | grep -v "127.0.0.1" | head -3']).decode('utf-8')
        
        info = f"""
🌐 **Сетевая информация:**

**Сетевая статистика:**
{net_io}

**IP адреса:**
{ip_info}
"""
        return info
    except Exception as e:
        return f"Ошибка получения сетевой информации: {str(e)}"

def get_directory_info(path="."):
    """Получить информацию о директории"""
    try:
        result = subprocess.check_output(['bash', '-c', f'ls -la "{path}" | head -20']).decode('utf-8')
        return f"📁 Содержимое `{path}`:\n```\n{result}\n```"
    except Exception as e:
        return f"❌ Ошибка чтения директории: {str(e)}"

def get_main_keyboard():
    """Создаем основную клавиатуру с кнопками внизу"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    buttons = [
        types.KeyboardButton("📊 Статус системы"),
        types.KeyboardButton("🏃 Процессы"),
        types.KeyboardButton("🌐 Сеть"),
        types.KeyboardButton("💾 Диск"),
        types.KeyboardButton("📁 Файлы"),
        types.KeyboardButton("⏰ Uptime"),
        types.KeyboardButton("🔄 Обновить"),
        types.KeyboardButton("📷 Скриншот"),
        types.KeyboardButton("📤 Загрузить файл"),
        types.KeyboardButton("❓ Помощь"),
        types.KeyboardButton("⚙️ Shell"),
        types.KeyboardButton("/start")
    ]
    markup.add(*buttons)
    return markup

def get_shell_keyboard():
    """Клавиатура для shell команд"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    buttons = [
        types.KeyboardButton("📊 Neofetch"),
        types.KeyboardButton("📈 Top"),
        types.KeyboardButton("📂 LS"),
        types.KeyboardButton("🌐 Ping"),
        types.KeyboardButton("🔙 Назад"),
        types.KeyboardButton("❓ Помощь"),
        types.KeyboardButton("/start")
    ]
    markup.add(*buttons)
    return markup

def get_file_keyboard():
    """Клавиатура для работы с файлами"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    buttons = [
        types.KeyboardButton("📁 Домашняя"),
        types.KeyboardButton("📁 Корневая"),
        types.KeyboardButton("📁 Текущая"),
        types.KeyboardButton("📂 Список файлов"),
        types.KeyboardButton("📤 Загрузить файл"),
        types.KeyboardButton("🔙 Назад"),
        types.KeyboardButton("/start")
    ]
    markup.add(*buttons)
    return markup

# === ОБРАБОТКА КОМАНД ===
@bot.message_handler(commands=['start'])
def send_welcome(message):
    if message.from_user.id == AUTHORIZED_USER_ID:
        # Главное меню только для тебя
        markup = types.InlineKeyboardMarkup(row_width=2)
        buttons = [
            types.InlineKeyboardButton("📊 Neofetch", callback_data="neofetch"),
            types.InlineKeyboardButton("📈 Uptime", callback_data="uptime"),
            types.InlineKeyboardButton("💾 Disk usage", callback_data="disk"),
            types.InlineKeyboardButton("🖥️ System Info", callback_data="system_info"),
            types.InlineKeyboardButton("🏃 Processes", callback_data="processes"),
            types.InlineKeyboardButton("🌐 Network", callback_data="network"),
            types.InlineKeyboardButton("📁 Files", callback_data="files"),
            types.InlineKeyboardButton("⚙ Shell", callback_data="shell"),
            types.InlineKeyboardButton("📷 Screenshot", callback_data="screenshot"),
            types.InlineKeyboardButton("📤 Upload", callback_data="upload"),
            types.InlineKeyboardButton("🔁 Restart Bot", callback_data="restart_bot")
        ]
        markup.add(*buttons)
        
        # Отправляем основную клавиатуру
        main_keyboard = get_main_keyboard()
        bot.send_message(message.chat.id, "🔐 Привет, админ!\nВыбирай действие:", 
                        reply_markup=main_keyboard)
        bot.send_message(message.chat.id, "📋 Или используй инлайн кнопки:", 
                        reply_markup=markup)
    else:
        # Для остальных — только айди
        bot.reply_to(message, f"Твой Telegram ID: {message.from_user.id}")

@bot.message_handler(commands=['help'])
def send_help(message):
    if message.from_user.id == AUTHORIZED_USER_ID:
        help_text = """
🤖 **Доступные команды:**

/start - Главное меню
/help - Эта справка
/shell <команда> - Выполнить команду в shell
/status - Статус системы
/processes - Список процессов
/network - Сетевая статистика
/upload - Загрузить файл на сервер

**📋 Основные кнопки:**
• Статус системы - Информация о системе
• Процессы - Запущенные процессы
• Сеть - Сетевая информация
• Диск - Использование диска
• Файлы - Работа с файлами
• Uptime - Время работы
• Скриншот - Сделать скриншот
• Загрузить файл - Отправить файл на сервер
• Shell - Командная строка
• /start - Главное меню

**⚡ Быстрые команды:**
• Neofetch - Информация о системе
• Top - Просмотр процессов
• LS - Список файлов
• Ping - Проверка сети

**📤 Загрузка файлов:**
Просто отправь любой файл боту и он сохранится на сервере!
"""
        bot.reply_to(message, help_text, parse_mode="Markdown")
    else:
        bot.reply_to(message, "У вас нет доступа к этой команде.")

@bot.message_handler(commands=['status'])
def send_status(message):
    if message.from_user.id == AUTHORIZED_USER_ID:
        info = get_system_info()
        bot.reply_to(message, info, parse_mode="Markdown")
    else:
        bot.reply_to(message, "❌ У тебя нет прав!")

@bot.message_handler(commands=['processes'])
def send_processes(message):
    if message.from_user.id == AUTHORIZED_USER_ID:
        processes = get_running_processes()
        bot.reply_to(message, processes, parse_mode="Markdown")
    else:
        bot.reply_to(message, "❌ У тебя нет прав!")

@bot.message_handler(commands=['network'])
def send_network(message):
    if message.from_user.id == AUTHORIZED_USER_ID:
        network_info = get_network_info()
        bot.reply_to(message, network_info, parse_mode="Markdown")
    else:
        bot.reply_to(message, "❌ У тебя нет прав!")

@bot.message_handler(commands=['upload'])
def ask_upload_path(message):
    if message.from_user.id != AUTHORIZED_USER_ID:
        bot.reply_to(message, "❌ У тебя нет прав!")
        return
    
    global current_upload_path
    bot.reply_to(message, f"📁 Текущий путь загрузки: `{current_upload_path}`\n"
                         f"Отправь мне файл и он будет сохранен в эту директорию.\n"
                         f"Или используй кнопки для смены пути.", 
                parse_mode="Markdown")

# === ОБРАБОТКА ФАЙЛОВ ===
@bot.message_handler(content_types=['document', 'photo', 'video', 'audio'])
def handle_file_upload(message):
    if message.from_user.id != AUTHORIZED_USER_ID:
        bot.reply_to(message, "❌ У тебя нет прав для загрузки файлов!")
        return
    
    global current_upload_path
    
    try:
        # Создаем директорию если её нет
        os.makedirs(current_upload_path, exist_ok=True)
        
        file_info = None
        file_name = ""
        
        if message.document:
            file_info = bot.get_file(message.document.file_id)
            file_name = message.document.file_name
        elif message.photo:
            file_info = bot.get_file(message.photo[-1].file_id)
            file_name = f"photo_{message.message_id}.jpg"
        elif message.video:
            file_info = bot.get_file(message.video.file_id)
            file_name = message.video.file_name or f"video_{message.message_id}.mp4"
        elif message.audio:
            file_info = bot.get_file(message.audio.file_id)
            file_name = message.audio.file_name or f"audio_{message.message_id}.mp3"
        
        if file_info and file_name:
            # Скачиваем файл
            downloaded_file = bot.download_file(file_info.file_path)
            
            # Сохраняем файл
            file_path = os.path.join(current_upload_path, file_name)
            
            # Если файл уже существует, добавляем номер
            counter = 1
            original_file_name = file_name
            while os.path.exists(file_path):
                name, ext = os.path.splitext(original_file_name)
                file_name = f"{name}_{counter}{ext}"
                file_path = os.path.join(current_upload_path, file_name)
                counter += 1
            
            with open(file_path, 'wb') as new_file:
                new_file.write(downloaded_file)
            
            # Получаем информацию о файле
            file_size = os.path.getsize(file_path)
            file_size_mb = round(file_size / (1024 * 1024), 2)
            
            bot.reply_to(message, f"✅ Файл успешно загружен!\n"
                                 f"📁 Путь: `{file_path}`\n"
                                 f"📄 Имя: {file_name}\n"
                                 f"📊 Размер: {file_size_mb} MB\n"
                                 f"💾 На сервере: {current_upload_path}",
                        parse_mode="Markdown")
        else:
            bot.reply_to(message, "❌ Не удалось обработать файл")
            
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка при загрузке файла: {str(e)}")

# === ОБРАБОТКА ТЕКСТОВЫХ СООБЩЕНИЙ (КНОПКИ) ===
@bot.message_handler(func=lambda message: True)
def handle_text_messages(message):
    if message.from_user.id != AUTHORIZED_USER_ID:
        bot.reply_to(message, f"Твой Telegram ID: {message.from_user.id}")
        return
    
    text = message.text
    
    if text == "/start":
        send_welcome(message)
        return
    
    text_lower = text.lower()
    
    if text_lower == "📊 статус системы" or text == "Статус системы":
        info = get_system_info()
        bot.reply_to(message, info, parse_mode="Markdown")
    
    elif text_lower == "🏃 процессы" or text == "Процессы":
        processes = get_running_processes()
        bot.reply_to(message, processes, parse_mode="Markdown")
    
    elif text_lower == "🌐 сеть" or text == "Сеть":
        network_info = get_network_info()
        bot.reply_to(message, network_info, parse_mode="Markdown")
    
    elif text_lower == "💾 диск" or text == "Диск":
        run_and_send(message, "df -h")
    
    elif text_lower == "📁 файлы" or text == "Файлы":
        file_keyboard = get_file_keyboard()
    
        bot.reply_to(message, f"📁 Работа с файлами\n"
                             f"Текущий путь: `{current_upload_path}`\n"
                             f"Используй кнопки для навигации или отправь файл для загрузки.",
                    reply_markup=file_keyboard, parse_mode="Markdown")
    
    elif text_lower == "📂 список файлов" or text == "Список файлов":
        dir_info = get_directory_info(current_upload_path)
        bot.reply_to(message, dir_info, parse_mode="Markdown")
    
    elif text_lower == "📁 домашняя" or text == "Домашняя":
    
        current_upload_path = os.path.expanduser("~")
        bot.reply_to(message, f"📁 Установлен домашний путь: `{current_upload_path}`", 
                    parse_mode="Markdown")
    
    elif text_lower == "📁 корневая" or text == "Корневая":
        
        current_upload_path = "/"
        bot.reply_to(message, f"📁 Установлен корневой путь: `{current_upload_path}`", 
                    parse_mode="Markdown")
    
    elif text_lower == "📁 текущая" or text == "Текущая":
        
        current_upload_path = os.getcwd()
        bot.reply_to(message, f"📁 Установлен текущий путь: `{current_upload_path}`", 
                    parse_mode="Markdown")
    
    elif text_lower == "📤 загрузить файл" or text == "Загрузить файл":
        ask_upload_path(message)
    
    elif text_lower == "⏰ uptime" or text == "Uptime":
        run_and_send(message, "uptime -p")
    
    elif text_lower == "🔄 обновить" or text == "Обновить":
        bot.reply_to(message, "♻️ Обновляю информацию...")
        info = get_system_info()
        bot.reply_to(message, info, parse_mode="Markdown")
    
    elif text_lower == "📷 скриншот" or text == "Скриншот":
        take_screenshot(message)
    
    elif text_lower == "❓ помощь" or text == "Помощь":
        send_help(message)
    
    elif text_lower == "⚙️ shell" or text == "Shell":
        shell_keyboard = get_shell_keyboard()
        bot.reply_to(message, "💻 Выбери команду или напиши свою:", 
                    reply_markup=shell_keyboard)
    
    elif text == "📊 Neofetch":
        run_and_send(message, "neofetch")
    
    elif text == "📈 Top":
        run_and_send(message, "top -bn1 | head -20")
    
    elif text == "📂 LS":
        run_and_send(message, "ls -la")
    
    elif text == "🌐 Ping":
        run_and_send(message, "ping -c 4 google.com")
    
    elif text_lower == "🔙 назад" or text == "Назад":
        main_keyboard = get_main_keyboard()
        bot.reply_to(message, "🔙 Возвращаемся в главное меню", 
                    reply_markup=main_keyboard)
    
    elif text.startswith("/"):
        # Неизвестная команда
        bot.reply_to(message, "❌ Неизвестная команда. Используй /help для справки.")
    
    else:
        # Если это не команда и не кнопка, пробуем выполнить как shell команду
        if len(text.split()) <= 3:  # Простые команды
            run_and_send(message, text)
        else:
            bot.reply_to(message, "💡 Напиши /shell перед командой или используй кнопки")

# === ОБРАБОТКА INLINE-КНОПОК ===
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.from_user.id != AUTHORIZED_USER_ID:
        bot.answer_callback_query(call.id, "❌ У тебя нет доступа!")
        return

    if call.data == "neofetch":
        run_and_send(call.message, "neofetch")
    elif call.data == "uptime":
        run_and_send(call.message, "uptime -p")
    elif call.data == "disk":
        run_and_send(call.message, "df -h")
    elif call.data == "system_info":
        info = get_system_info()
        try:
            bot.edit_message_text(chat_id=call.message.chat.id, 
                                 message_id=call.message.message_id,
                                 text=info, 
                                 parse_mode="Markdown")
        except:
            bot.send_message(call.message.chat.id, info, parse_mode="Markdown")
    elif call.data == "processes":
        processes = get_running_processes()
        try:
            bot.edit_message_text(chat_id=call.message.chat.id, 
                                 message_id=call.message.message_id,
                                 text=processes, 
                                 parse_mode="Markdown")
        except:
            bot.send_message(call.message.chat.id, processes, parse_mode="Markdown")
    elif call.data == "network":
        network_info = get_network_info()
        try:
            bot.edit_message_text(chat_id=call.message.chat.id, 
                                 message_id=call.message.message_id,
                                 text=network_info, 
                                 parse_mode="Markdown")
        except:
            bot.send_message(call.message.chat.id, network_info, parse_mode="Markdown")
    elif call.data == "files":
        file_keyboard = get_file_keyboard()
        global current_upload_path
        bot.send_message(call.message.chat.id, 
                        f"📁 Работа с файлами\nТекущий путь: `{current_upload_path}`",
                        reply_markup=file_keyboard, parse_mode="Markdown")
    elif call.data == "shell":
        shell_keyboard = get_shell_keyboard()
        bot.send_message(call.message.chat.id, 
                        "💻 Выбери команду или напиши свою:", 
                        reply_markup=shell_keyboard)
    elif call.data == "screenshot":
        take_screenshot(call.message)
    elif call.data == "upload":
        ask_upload_path(call.message)
    elif call.data == "restart_bot":
        restart_bot(call.message)

def take_screenshot(message):
    """Сделать скриншот"""
    try:
        # Попробуем разные команды для скриншота
        commands = [
            "import -window root screenshot.png",
            "scrot screenshot.png",
            "gnome-screenshot -f screenshot.png",
            "xwd -root -out screenshot.xwd && convert screenshot.xwd screenshot.png"
        ]
        
        success = False
        for cmd in commands:
            try:
                subprocess.run(["bash", "-c", cmd], check=True, timeout=10, 
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                success = True
                break
            except:
                continue
        
        if success and os.path.exists("screenshot.png"):
            with open("screenshot.png", "rb") as photo:
                bot.send_photo(message.chat.id, photo, caption="📷 Скриншот системы")
            os.remove("screenshot.png")
        else:
            bot.reply_to(message, "❌ Не удалось сделать скриншот. Установите scrot или imagemagick")
    
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка при создании скриншота: {str(e)}")

def restart_bot(message):
    """Перезапуск бота"""
    try:
        bot.reply_to(message, "🔄 Перезапуск бота...")
        python = sys.executable
        os.execl(python, python, *sys.argv)
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка при перезапуске: {str(e)}")

# === /SHELL ДЛЯ ТЕБЯ ===
@bot.message_handler(commands=['shell'])
def handle_shell_command(message):
    if message.from_user.id != AUTHORIZED_USER_ID:
        bot.reply_to(message, "❌ У тебя нет прав на выполнение этой команды.")
        return
    
    command = message.text[7:].strip()
    if not command:
        bot.reply_to(message, "⚠ Ты не написал команду для выполнения!")
        return

    # Защита от опасных команд
    dangerous_commands = ['rm -rf /', 'dd if=', ':(){:|:&};:', 'mkfs', 'fdisk', 'shutdown', 'reboot', 'halt']
    if any(danger_cmd in command for danger_cmd in dangerous_commands):
        bot.reply_to(message, "🚫 Опасная команда заблокирована!")
        return

    run_and_send(message, command)

# === ВСПОМОГАТЕЛЬНАЯ ФУНКЦИЯ ===
def run_and_send(message, command):
    try:
        # Ограничение времени выполнения команды
        result = subprocess.check_output(
            ['bash', '-c', command], 
            stderr=subprocess.STDOUT,
            timeout=30  # 30 секунд таймаут
        )
        output = result.decode('utf-8')
        output = strip_ansi_codes(output)
        
        # Обрезаем слишком длинные выводы
        if len(output) > 4000:
            output = output[:4000] + "\n... (вывод обрезан)"
        
        if not output.strip():
            output = "(пустой вывод)"
        
        bot.reply_to(message, f"💻 Команда: `{command}`\n```\n{output}\n```", parse_mode="Markdown")
    
    except subprocess.TimeoutExpired:
        bot.reply_to(message, f"⏰ Команда `{command}` превысила время выполнения (30 секунд)", parse_mode="Markdown")
    
    except subprocess.CalledProcessError as e:
        error_text = strip_ansi_codes(e.output.decode('utf-8'))
        if len(error_text) > 4000:
            error_text = error_text[:4000] + "\n... (вывод обрезан)"
        bot.reply_to(message, f"❌ Команда: `{command}`\n```\n{error_text}\n```", parse_mode="Markdown")
    
    except Exception as e:
        bot.reply_to(message, f"⚠ Не удалось выполнить команду: {str(e)}")

# === ЗАПУСК БОТА ===
if __name__ == "__main__":
    print("🤖 Бот запущен...")
    print("📋 Доступные кнопки:")
    print("• 📊 Статус системы")
    print("• 🏃 Процессы") 
    print("• 🌐 Сеть")
    print("• 💾 Диск")
    print("• 📁 Файлы")
    print("• 📤 Загрузить файл")
    print("• ⏰ Uptime")
    print("• 📷 Скриншот")
    print("• ⚙️ Shell")
    print("• /start - Главное меню")
    print("📤 Просто отправь файл боту для загрузки на сервер!")
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        bot.polling(none_stop=True)
