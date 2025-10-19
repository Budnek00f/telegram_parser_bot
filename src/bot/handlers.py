import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from config import Config
from src.utils.file_handlers import download_file, cleanup_file
from src.utils.document_processor import DocumentProcessor

logger = logging.getLogger(__name__)
doc_processor = DocumentProcessor()

# Команды бота
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = """
👋 Привет! Я бот для обработки документов.

📎 Отправь мне фото или файл документа (паспорта), и я извлеку из него текст.

⚠️ Для работы мне нужно:
- Четкое фото документа
- Хорошее освещение
- Отсутствие бликов
    
🛡️ Ваши данные защищены и обрабатываются в соответствии с политикой конфиденциальности.
    """
    await update.message.reply_text(welcome_text)
    logger.info(f"User {update.effective_user.id} started the bot")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
❓ Как пользоваться ботом:

1. Сделайте четкое фото документа или загрузите сканы
2. Отправьте фото/файл боту
3. Дождитесь обработки
4. Проверьте распознанные данные

📝 Поддерживаемые форматы: JPG, PNG, PDF
    """
    await update.message.reply_text(help_text)
    logger.info(f"User {update.effective_user.id} requested help")

# Обработка медиа
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    photo = update.message.photo[-1]
    
    logger.info(f"Received photo from user {user_id}")
    await update.message.reply_text("📸 Фото получено. Начинаю обработку...")
    
    try:
        # Скачиваем файл
        file_path = await download_file(photo, "photo", Config.TEMP_DIR)
        file_size = os.path.getsize(file_path) / 1024
        logger.info(f"Photo saved: {file_path} ({file_size:.2f} KB)")
        
        # Обрабатываем документ
        await update.message.reply_text("🔍 Распознаю текст...")
        result = await doc_processor.process_document(file_path)
        
        # Сохраняем результат в контекст
        context.user_data['last_parsed_data'] = result
        
        # Форматируем и отправляем результат
        response_text = format_passport_data(result)
        
        # Создаем клавиатуру с кнопками
        keyboard = [
            [InlineKeyboardButton("✅ Данные верны", callback_data="data_correct")],
            [InlineKeyboardButton("🔄 Новое фото", callback_data="new_photo")]
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
        logger.error(f"Error processing photo: {e}")
        await update.message.reply_text("❌ Ошибка при обработке фото. Попробуйте еще раз.")

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if not update.message.document:
        await update.message.reply_text("❌ Файл не найден.")
        return
        
    document = update.message.document
    
    # Проверяем тип файла
    allowed_types = ['.jpg', '.jpeg', '.png', '.pdf']
    file_ext = os.path.splitext(document.file_name)[1].lower() if document.file_name else ''
    
    if file_ext not in allowed_types:
        await update.message.reply_text(
            f"❌ Формат {file_ext} не поддерживается.\nПоддерживаемые: {', '.join(allowed_types)}"
        )
        return
    
    logger.info(f"Received document {document.file_name} from user {user_id}")
    await update.message.reply_text("📄 Документ получен. Обрабатываю...")
    
    try:
        # Скачиваем файл
        file_path = await download_file(document, "document", Config.TEMP_DIR)
        file_size = os.path.getsize(file_path) / 1024
        logger.info(f"Document saved: {file_path} ({file_size:.2f} KB)")
        
        # Обрабатываем документ
        await update.message.reply_text("🔍 Распознаю текст...")
        result = await doc_processor.process_document(file_path)
        
        # Сохраняем результат в контекст
        context.user_data['last_parsed_data'] = result
        
        # Форматируем и отправляем результат
        response_text = format_passport_data(result)
        
        # Создаем клавиатуру с кнопками
        keyboard = [
            [InlineKeyboardButton("✅ Данные верны", callback_data="data_correct")],
            [InlineKeyboardButton("🔄 Новый файл", callback_data="new_photo")]
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
        logger.error(f"Error processing document: {e}")
        await update.message.reply_text("❌ Ошибка при обработке документа.")

# Обработка callback-кнопок
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    callback_data = query.data
    
    logger.info(f"Button callback from user {user_id}: {callback_data}")
    
    if callback_data == "data_correct":
        await query.edit_message_text("✅ Данные подтверждены! (Функция сохранения в таблицу будет добавлена)")
        
    elif callback_data == "new_photo":
        await query.edit_message_text("🔄 Отправьте новое фото или документ для обработки.")

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
        "✅ Проверьте данные и нажмите кнопку ниже"
    ]
    
    return "\n".join(lines)