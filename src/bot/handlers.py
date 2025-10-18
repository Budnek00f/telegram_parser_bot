import os
import logging
from telegram import Update
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
5. Подтвердите сохранение в таблицу

📝 Поддерживаемые форматы: JPG, PNG, PDF, TIFF
    """
    await update.message.reply_text(help_text)
    logger.info(f"User {update.effective_user.id} requested help")

# Обработка медиа
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    photo = update.message.photo[-1]  # Берем самое качественное фото
    
    logger.info(f"Received photo from user {user_id}")
    await update.message.reply_text("📸 Фото получено. Начинаю обработку...")
    
    try:
        # Скачиваем файл
        file_path = await download_file(photo, "photo", Config.TEMP_DIR)
        
        # Логируем информацию о файле
        file_size = os.path.getsize(file_path) / 1024  # KB
        logger.info(f"Photo saved: {file_path} ({file_size:.2f} KB)")
        
        # Обрабатываем документ
        await update.message.reply_text("🔍 Распознаю текст...")
        result = await doc_processor.process_document(file_path)
        
        # Форматируем и отправляем результат
        response_text = format_passport_data(result)
        await update.message.reply_text(response_text, parse_mode='Markdown')
        
        # Логируем для отладки
        if 'extracted_text' in result:
            logger.debug(f"Распознанный текст: {result['extracted_text'][:200]}...")
        
        # Удаляем временный файл
        cleanup_file(file_path)
        
    except Exception as e:
        logger.error(f"Error processing photo from user {user_id}: {e}")
        await update.message.reply_text("❌ Ошибка при обработке фото. Попробуйте еще раз.")

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Проверяем, есть ли документ в сообщении
    if not update.message.document:
        await update.message.reply_text("❌ Файл не найден в сообщении.")
        return
        
    document = update.message.document
    
    # Проверяем тип файла
    allowed_types = ['.jpg', '.jpeg', '.png', '.pdf', '.tiff', '.tif']
    file_ext = os.path.splitext(document.file_name)[1].lower() if document.file_name else ''
    
    if file_ext not in allowed_types:
        await update.message.reply_text(
            f"❌ Формат {file_ext} не поддерживается.\n"
            f"📝 Поддерживаемые форматы: {', '.join(allowed_types)}"
        )
        return
    
    logger.info(f"Received document {document.file_name} from user {user_id}")
    await update.message.reply_text("📄 Документ получен. Начинаю обработку...")
    
    try:
        # Скачиваем файл
        file_path = await download_file(document, "document", Config.TEMP_DIR)
        
        file_size = os.path.getsize(file_path) / 1024  # KB
        logger.info(f"Document saved: {file_path} ({file_size:.2f} KB)")
        
        # Обрабатываем документ
        await update.message.reply_text("🔍 Распознаю текст...")
        result = await doc_processor.process_document(file_path)
        
        # Форматируем и отправляем результат
        response_text = format_passport_data(result)
        await update.message.reply_text(response_text, parse_mode='Markdown')
        
        # Удаляем временный файл
        cleanup_file(file_path)
        
    except Exception as e:
        logger.error(f"Error processing document from user {user_id}: {e}")
        await update.message.reply_text("❌ Ошибка при обработке документа. Попробуйте еще раз.")

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
        "🔍 *Для улучшения точности:*",
        "- Убедитесь, что фото содержит страницу с серией и номером",
        "- Серия и номер обычно находятся на другой странице",
        "- Сфотографируйте обе страницы разворота",
        "---",
        "✅ Проверьте данные перед сохранением"
    ]
    
    return "\n".join(lines)