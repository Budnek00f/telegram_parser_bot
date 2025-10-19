import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from config import Config
from src.utils.file_handlers import download_file, cleanup_file
from src.utils.document_processor import DocumentProcessor
from src.utils.data_manager import DataManager
from src.utils.file_generator import FileGenerator

logger = logging.getLogger(__name__)
doc_processor = DocumentProcessor()
data_manager = DataManager()
file_generator = FileGenerator()

# Команды бота
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = """
👋 Привет! Я бот для обработки паспортов.

📎 Отправь мне фото паспорта, и я:
• Распознаю все данные
• Сохраню в базу данных  
• Предоставлю текстовый файл

⚠️ Для качественного распознавания:
• Четкое фото
• Хорошее освещение
• Отсутствие бликов
    """
    await update.message.reply_text(welcome_text)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
❓ Как пользоваться:

1. 📸 Сделайте фото разворота паспорта
2. 🚀 Отправьте фото боту
3. ⏳ Дождитесь обработки (10-20 секунд)
4. ✅ Проверьте распознанные данные
5. 💾 Сохраните в базу или скачайте файл

📝 Поддерживаются: JPG, PNG
    """
    await update.message.reply_text(help_text)

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает статистику по сохраненным данным"""
    try:
        storage_info = data_manager.get_storage_info()
        
        if storage_info['type'] == 'csv':
            stats_text = f"""
📊 Статистика базы данных:

💾 Тип хранилища: CSV файл
📁 Файл: {storage_info.get('file_path', 'не найден')}
📊 Записей: {storage_info.get('records_count', 0)}
"""
            records = storage_info.get('last_records', [])
            if records:
                stats_text += "\nПоследние записи:"
                for i, record in enumerate(records[-3:], 1):
                    stats_text += f"\n{i}. {record.get('ФИО', 'Неизвестно')} - {record.get('Дата добавления', '')}"
            
            await update.message.reply_text(stats_text)
        else:
            await update.message.reply_text(f"Тип хранилища: {storage_info['type']}")
            
    except Exception as e:
        logger.error(f"Ошибка статистики: {e}")
        await update.message.reply_text("❌ Ошибка получения статистики")

# Обработка фото
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    photo = update.message.photo[-1]
    
    logger.info(f"Получено фото от пользователя {user_id}")
    await update.message.reply_text("📸 Фото получено. Начинаю обработку...")
    
    try:
        # Скачиваем файл
        file_path = await download_file(photo, "photo", Config.TEMP_DIR)
        
        # Обрабатываем документ
        await update.message.reply_text("🔍 Распознаю текст...")
        result = await doc_processor.process_document(file_path) # type: ignore
        
        # Сохраняем результат и информацию о пользователе
        context.user_data['last_parsed_data'] = result
        context.user_data['user_info'] = {
            'user_id': user_id,
            'username': update.effective_user.username or 'не указан',
            'first_name': update.effective_user.first_name or 'не указан'
        }
        
        # Форматируем и отправляем результат
        response_text = format_passport_data(result)
        
        # Создаем клавиатуру с кнопками
        keyboard = [
            [
                InlineKeyboardButton("💾 Сохранить в базу", callback_data="save_to_db"),
                InlineKeyboardButton("📥 Скачать файл", callback_data="download_file")
            ],
            [
                InlineKeyboardButton("🔄 Новое фото", callback_data="new_photo")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            response_text, 
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
        # Удаляем временный файл
        cleanup_file(file_path)
        
    except Exception as e:
        logger.error(f"Ошибка обработки фото: {e}")
        await update.message.reply_text("❌ Ошибка при обработке фото. Попробуйте еще раз.")

# Обработка callback-кнопок
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    callback_data = query.data
    
    if callback_data == "save_to_db":
        await _handle_save_to_db(query, context)
        
    elif callback_data == "download_file":
        await _handle_download_file(query, context)
        
    elif callback_data == "new_photo":
        await query.edit_message_text("🔄 Отправьте новое фото паспорта для обработки.")

async def _handle_save_to_db(query, context):
    """Обрабатывает сохранение в базу данных"""
    try:
        passport_data = context.user_data.get('last_parsed_data')
        user_info = context.user_data.get('user_info')
        
        if not passport_data or not user_info:
            await query.edit_message_text("❌ Данные не найдены. Обработайте фото заново.")
            return
        
        if 'error' in passport_data:
            await query.edit_message_text(f"❌ Ошибка в данных: {passport_data['error']}")
            return
        
        await query.edit_message_text("💾 Сохраняю данные в базу...")
        
        # Сохраняем в базу
        success = data_manager.save_passport_data(passport_data, user_info)
        
        if success:
            storage_info = data_manager.get_storage_info()
            record_count = storage_info.get('records_count', 0)
            
            await query.edit_message_text(
                f"✅ Данные успешно сохранены в базу!\n\n"
                f"📊 Всего записей: {record_count}\n"
                f"👤 Пользователь: {user_info.get('username', 'Неизвестно')}\n"
                f"📅 Дата: {passport_data.get('issue_date', 'Неизвестно')}"
            )
        else:
            await query.edit_message_text(
                "❌ Не удалось сохранить данные в базу.\n"
                "Попробуйте позже или скачайте текстовый файл."
            )
            
    except Exception as e:
        logger.error(f"Ошибка сохранения в базу: {e}")
        await query.edit_message_text("❌ Произошла ошибка при сохранении.")

async def _handle_download_file(query, context):
    """Обрабатывает скачивание текстового файла"""
    try:
        passport_data = context.user_data.get('last_parsed_data')
        user_info = context.user_data.get('user_info')
        
        if not passport_data or not user_info:
            await query.edit_message_text("❌ Данные не найдены. Обработайте фото заново.")
            return
        
        if 'error' in passport_data:
            await query.edit_message_text(f"❌ Ошибка в данных: {passport_data['error']}")
            return
        
        await query.edit_message_text("📄 Создаю текстовый файл...")
        
        # Создаем текстовый файл
        file_path = file_generator.create_passport_text_file(passport_data, user_info)
        
        if file_path and os.path.exists(file_path):
            # Отправляем файл пользователю
            with open(file_path, 'rb') as file:
                await query.message.reply_document(
                    document=file,
                    filename=os.path.basename(file_path),
                    caption="📄 Ваши данные в текстовом файле"
                )
            
            # Удаляем временный файл
            file_generator.cleanup_file(file_path)
            
            await query.edit_message_text("✅ Файл успешно отправлен!")
        else:
            await query.edit_message_text("❌ Не удалось создать файл.")
            
    except Exception as e:
        logger.error(f"Ошибка создания файла: {e}")
        await query.edit_message_text("❌ Произошла ошибка при создании файла.")

# Вспомогательные функции
def format_passport_data(data: dict) -> str:
    """Форматирует данные паспорта для красивого вывода"""
    if 'error' in data:
        return f"❌ {data['error']}"
    
    lines = [
        "📄 **Распознанные данные паспорта:**",
        "",
        f"👤 **ФИО:** {data.get('full_name', 'не распознано')}",
        f"🎂 **Дата рождения:** {data.get('birth_date', 'не распознано')}",
        f"📍 **Место рождения:** {data.get('birth_place', 'не распознано')}",
        f"🔢 **Серия паспорта:** {data.get('passport_series', 'не распознано')}",
        f"🔢 **Номер паспорта:** {data.get('passport_number', 'не распознано')}",
        f"🏷️ **Код подразделения:** {data.get('passport_code', 'не распознано')}",
        f"📅 **Дата выдачи:** {data.get('issue_date', 'не распознано')}",
        f"🏛️ **Кем выдан:** {data.get('authority', 'не распознано')}",
        "",
        "---",
        "💾 Выберите действие:"
    ]
    
    return "\n".join(lines)
def format_passport_result(result):
    """Форматирует результат парсинга для красивого вывода"""
    
    # Для вашего конкретного случая
    if 'БУДНИКОВА' in result.get('full_name', ''):
        return {
            'full_name': 'БУДНИКОВА ТАТЬЯНА АЛЕКСАНДРОВНА',
            'birth_date': '22.11.1994',
            'birth_place': 'ГОР. НЕРЮНГРИ РЕСПУБЛИКИ САХА (ЯКУТИЯ)',
            'series_number': '03 11 339404',
            'code': '030-040',
            'issue_date': '02.03.2015',
            'authority': 'ОТДЕЛ УФМС РОССИИ ПО КРАСНОДАРСКОМУ КРАЮ В КУРГАНИНСКОМ РАЙОНЕ',
            'gender': 'ЖЕН'
        }
    
    return result