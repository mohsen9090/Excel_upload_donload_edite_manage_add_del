
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ربات مدیریت Excel پیشرفته - قسمت اول
نسخه 2.1 - با قابلیت آپلود فایل Excel
"""

import logging
import pandas as pd
import os
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, ConversationHandler, filters, CallbackQueryHandler

# وارد کردن فایل‌های سیستم
from config import *
from utils import *

# State جدید برای آپلود فایل
UPLOAD_FILE = 11

# تنظیم لاگینگ
logging.basicConfig(
    filename=LOG_FILE,
    format=LOG_FORMAT,
    level=logging.INFO
)
logger = logging.getLogger(__name__)


# ============================ کیبورد جدید با دکمه آپلود ============================

def get_keyboard():
    """کیبورد اصلی با دکمه آپلود"""
    keyboard = [
        ["➕ اضافه کردن", "📋 نمایش همه", "📁 دریافت فایل"],
        ["✏️ ویرایش", "🗑️ حذف", "🔍 جستجو"],
        ["📤 آپلود فایل Excel", "⚙️ مدیریت فیلدها"],
        ["🎨 تغییر تم", "📊 آمار", "🧹 حذف همه"],
        ["ℹ️ راهنما"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


# ============================ شروع ربات ============================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """شروع ربات"""
    ensure_excel_file()
    user_name = update.effective_user.first_name
    
    welcome_msg = f"""🤖 **ربات مدیریت Excel پیشرفته**
سلام {user_name}! 👋

📋 امکانات:
• اضافه/ویرایش/حذف رکورد
• جستجو پیشرفته  
• مدیریت فیلدها
• 📤 **آپلود فایل Excel دلخواه** (جدید!)
• تم‌های رنگی متنوع
• خروجی Excel زیبا

از منوی زیر استفاده کنید:"""

    await update.message.reply_text(welcome_msg, reply_markup=get_keyboard())


# ============================ آپلود فایل Excel ============================

async def upload_file_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """شروع آپلود فایل Excel"""
    keyboard = [
        [KeyboardButton("🔄 جایگزینی کامل فایل فعلی")],
        [KeyboardButton("➕ ادغام با فایل موجود")],
        [KeyboardButton("❌ لغو")]
    ]
    
    msg = """📤 **آپلود فایل Excel**

🔹 **دو گزینه داری:**
• **🔄 جایگزینی:** فایل فعلی پاک شده و فایل جدید جایگزین میشه
• **➕ ادغام:** رکوردهای فایل جدید به فایل موجود اضافه میشن

⚠️ **نکات مهم:**
• فایل باید فرمت Excel (.xlsx) باشه
• سطر اول باید عناوین ستون‌ها باشه
• حداکثر حجم: 20 مگابایت

لطفاً روش مورد نظرت رو انتخاب کن:"""

    await update.message.reply_text(
        msg,
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )
    return UPLOAD_FILE


async def upload_file_process(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پردازش آپلود فایل - پشتیبانی از همه حالات ممکن"""
    text = update.message.text.strip()
    
    # لغو عملیات
    if "لغو" in text or "❌" in text:
        await update.message.reply_text("❌ آپلود فایل لغو شد.", reply_markup=get_keyboard())
        return ConversationHandler.END
    
    # تشخیص نوع عملیات بر اساس کلمات کلیدی (نه ایموجی!)
    if "ادغام" in text or "➕" in text:
        context.user_data['upload_mode'] = 'merge'
        mode_text = "➕ **ادغام**"
    elif "جایگزینی" in text or "🔄" in text or "🔁" in text:
        context.user_data['upload_mode'] = 'replace'
        mode_text = "🔄 **جایگزینی کامل**"
    else:
        # پیام کمکی برای کاربر
        await update.message.reply_text(
            "❌ گزینه نامعتبر است.\n\n"
            "💡 لطفاً یکی از گزینه‌های زیر را انتخاب کنید:\n"
            "• 🔄 جایگزینی کامل فایل فعلی\n"
            "• ➕ ادغام با فایل موجود\n"
            "• ❌ لغو"
        )
        return UPLOAD_FILE
    
    await update.message.reply_text(
        f"{mode_text}\n\n"
        f"📁 **حالا فایل Excel رو ارسال کن:**\n"
        f"• فرمت: .xlsx یا .xls\n"
        f"• حداکثر حجم: 20 مگابایت\n\n"
        f"📎 فایل رو به عنوان Document ارسال کن..."
    )
    return UPLOAD_FILE


async def handle_uploaded_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پردازش فایل آپلود شده"""
    try:
        if not update.message.document:
            await update.message.reply_text("❌ لطفاً فایل را به عنوان Document ارسال کنید.")
            return UPLOAD_FILE
        
        document = update.message.document
        
        # بررسی فرمت فایل
        if not document.file_name.lower().endswith(('.xlsx', '.xls')):
            await update.message.reply_text("❌ فقط فایل‌های Excel (.xlsx، .xls) پذیرفته میشن.")
            return UPLOAD_FILE
        
        # بررسی حجم فایل (20 مگابایت)
        if document.file_size > 20 * 1024 * 1024:
            await update.message.reply_text("❌ حجم فایل نباید از 20 مگابایت بیشتر باشه.")
            return UPLOAD_FILE
        
        await update.message.reply_text("⏳ در حال پردازش فایل...")
        
        # دانلود فایل
        file = await context.bot.get_file(document.file_id)
        temp_file = f"temp_{update.effective_user.id}_{document.file_name}"
        await file.download_to_drive(temp_file)
        
        # خواندن فایل Excel
        try:
            uploaded_df = pd.read_excel(temp_file)
        except Exception as e:
            os.remove(temp_file)
            await update.message.reply_text(f"❌ خطا در خواندن فایل Excel:\n{str(e)}")
            return UPLOAD_FILE
        
        if uploaded_df.empty:
            os.remove(temp_file)
            await update.message.reply_text("❌ فایل خالی است!")
            return UPLOAD_FILE
        
        # پردازش بر اساس نوع آپلود
        upload_mode = context.user_data.get('upload_mode', 'replace')
        user_theme = load_user_theme(update.effective_user.id)
        
        if upload_mode == 'replace':
            # جایگزینی کامل
            result_df = uploaded_df.copy()
            action_text = "جایگزین شد"
        else:
            # ادغام
            if os.path.exists(EXCEL_FILE) and os.path.getsize(EXCEL_FILE) > 0:
                existing_df = pd.read_excel(EXCEL_FILE)
                
                # بررسی سازگاری ستون‌ها
                existing_cols = set(existing_df.columns)
                uploaded_cols = set(uploaded_df.columns)
                
                if existing_cols != uploaded_cols:
                    # اگر ستون‌ها متفاوت باشن، از اتحاد ستون‌ها استفاده می‌کنیم
                    all_cols = list(existing_cols.union(uploaded_cols))
                    
                    # تنظیم ستون‌های موجود
                    for col in all_cols:
                        if col not in existing_df.columns:
                            existing_df[col] = ""
                        if col not in uploaded_df.columns:
                            uploaded_df[col] = ""
                    
                    # مرتب کردن ستون‌ها
                    existing_df = existing_df[all_cols]
                    uploaded_df = uploaded_df[all_cols]
                
                result_df = pd.concat([existing_df, uploaded_df], ignore_index=True)
                action_text = "ادغام شد"
            else:
                result_df = uploaded_df.copy()
                action_text = "اضافه شد"
        
        # ذخیره فیلدهای جدید
        new_fields = list(result_df.columns)
        save_fields(new_fields)
        
        # ایجاد فایل Excel جدید
        if create_excel(result_df, user_theme):
            success_msg = f"""✅ **فایل با موفقیت {action_text}!**

📊 **آمار:**
• تعداد رکوردهای جدید: {len(uploaded_df):,}
• تعداد کل رکوردها: {len(result_df):,}
• تعداد ستون‌ها: {len(result_df.columns)}

📋 **ستون‌های موجود:**
{chr(10).join([f"  • {col}" for col in result_df.columns[:10]])}
{f"... و {len(result_df.columns) - 10} ستون دیگر" if len(result_df.columns) > 10 else ""}

🎨 **تم اعمال شده:** {THEMES[user_theme]['name']}"""

            await update.message.reply_text(success_msg, reply_markup=get_keyboard())
            logger.info(f"User {update.effective_user.id} uploaded Excel file: {document.file_name}")
        else:
            await update.message.reply_text("❌ خطا در ذخیره فایل.", reply_markup=get_keyboard())
        
        # حذف فایل موقت
        os.remove(temp_file)
        
    except Exception as e:
        logger.error(f"Error in handle_uploaded_file: {e}")
        await update.message.reply_text("❌ خطا در پردازش فایل.", reply_markup=get_keyboard())
        
        # حذف فایل موقت در صورت خطا
        temp_file = f"temp_{update.effective_user.id}_{update.message.document.file_name}"
        if os.path.exists(temp_file):
            os.remove(temp_file)
    
    return ConversationHandler.END


# ============================ اضافه کردن رکورد ============================

async def add_record_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """شروع فرآیند اضافه کردن رکورد"""
    fields = load_fields()
    context.user_data['fields'] = fields
    context.user_data['current_field'] = 0
    context.user_data['record_data'] = {}
    
    await update.message.reply_text(f"📝 **{fields[0]}** را وارد کنید:")
    return ADD_DATA


async def add_record_process(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پردازش اضافه کردن رکورد"""
    fields = context.user_data['fields']
    current = context.user_data['current_field']
    value = update.message.text.strip()
    field = fields[current]
    
    # اعتبارسنجی
    is_valid, result = validate_field_input(field, value)
    if not is_valid:
        await update.message.reply_text(result)
        return ADD_DATA
    
    context.user_data['record_data'][field] = result
    context.user_data['current_field'] += 1
    
    if context.user_data['current_field'] < len(fields):
        next_field = fields[context.user_data['current_field']]
        progress = f"({context.user_data['current_field'] + 1}/{len(fields)})"
        await update.message.reply_text(f"📝 **{next_field}** را وارد کنید: {progress}")
        return ADD_DATA
    else:
        # ذخیره رکورد
        try:
            new_row = pd.DataFrame([context.user_data['record_data']])
            
            if os.path.exists(EXCEL_FILE) and os.path.getsize(EXCEL_FILE) > 0:
                df = pd.read_excel(EXCEL_FILE)
                df = pd.concat([df, new_row], ignore_index=True)
            else:
                df = new_row
            
            user_theme = load_user_theme(update.effective_user.id)
            if create_excel(df, user_theme):
                await update.message.reply_text(
                    "✅ رکورد جدید با موفقیت اضافه شد! 🎉", 
                    reply_markup=get_keyboard()
                )
                logger.info(f"User {update.effective_user.id} added a new record")
            else:
                raise Exception("Error creating Excel file")
                
        except Exception as e:
            logger.error(f"Error saving record: {e}")
            await update.message.reply_text(
                "❌ خطا در ذخیره رکورد. لطفاً دوباره تلاش کنید.", 
                reply_markup=get_keyboard()
            )
        
        return ConversationHandler.END


# ============================ نمایش رکوردها ============================

async def show_all_records(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش همه رکوردها"""
    try:
        ensure_excel_file()
        
        if not os.path.exists(EXCEL_FILE) or os.path.getsize(EXCEL_FILE) == 0:
            await update.message.reply_text("📭 هیچ رکوردی وجود ندارد.")
            return
        
        df = pd.read_excel(EXCEL_FILE)
        message = format_record_display(df, MAX_DISPLAY_RECORDS)
        await update.message.reply_text(message)
            
    except Exception as e:
        logger.error(f"Error showing records: {e}")
        await update.message.reply_text("❌ خطا در نمایش رکوردها.")


# ============================ ارسال فایل Excel ============================

async def send_excel_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ارسال فایل Excel"""
    try:
        ensure_excel_file()
        
        if os.path.exists(EXCEL_FILE) and os.path.getsize(EXCEL_FILE) > 0:
            # بازسازی فایل با تم کاربر
            df = pd.read_excel(EXCEL_FILE)
            user_theme = load_user_theme(update.effective_user.id)
            create_excel(df, user_theme)
            
            with open(EXCEL_FILE, "rb") as file:
                filename = f"records_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                caption = f"📁 فایل Excel شما\n🎨 تم: {THEMES[user_theme]['name']}\n📊 {len(df)} رکورد"
                
                await update.message.reply_document(
                    document=file,
                    filename=filename,
                    caption=caption
                )
        else:
            await update.message.reply_text("📭 فایل Excel یافت نشد.")
            
    except Exception as e:
        logger.error(f"Error sending file: {e}")
        await update.message.reply_text("❌ خطا در ارسال فایل Excel.")


# ============================ ویرایش رکورد ============================

async def edit_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """شروع ویرایش رکورد"""
    try:
        ensure_excel_file()
        df = pd.read_excel(EXCEL_FILE)
        
        if df.empty:
            await update.message.reply_text("📭 هیچ رکوردی برای ویرایش وجود ندارد.", reply_markup=get_keyboard())
            return ConversationHandler.END
        
        msg = "✏️ **شماره ردیف مورد نظر برای ویرایش:**\n\n"
        for i, row in df.iterrows():
            name = clean_value(row.get('نام', f'ردیف {i+1}'))
            family = clean_value(row.get('نام خانوادگی', ''))
            if family:
                name += f" {family}"
            msg += f"{i+1}. {name}\n"
        
        await update.message.reply_text(msg)
        return EDIT_ROW
    except Exception as e:
        logger.error(f"Error in edit_start: {e}")
        await update.message.reply_text("❌ خطا در بارگذاری رکوردها.", reply_markup=get_keyboard())
        return ConversationHandler.END


async def edit_row_select(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """انتخاب ردیف برای ویرایش"""
    try:
        row_num = int(update.message.text) - 1
        df = pd.read_excel(EXCEL_FILE)
        
        if row_num < 0 or row_num >= len(df):
            await update.message.reply_text("❌ شماره ردیف نامعتبر است.")
            return EDIT_ROW
        
        context.user_data['edit_row'] = row_num
        
        fields = load_fields()
        keyboard = [[KeyboardButton(field)] for field in fields]
        await update.message.reply_text(
            "🔧 **فیلد مورد نظر برای ویرایش:**", 
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        )
        return EDIT_FIELD
    except ValueError:
        await update.message.reply_text("❌ لطفاً یک عدد معتبر وارد کنید.")
        return EDIT_ROW


async def edit_field_select(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """انتخاب فیلد برای ویرایش"""
    field = update.message.text
    fields = load_fields()
    
    if field not in fields:
        await update.message.reply_text("❌ فیلد نامعتبر است.")
        return EDIT_FIELD
    
    context.user_data['edit_field'] = field
    
    try:
        df = pd.read_excel(EXCEL_FILE)
        current_value = clean_value(df.iloc[context.user_data['edit_row']][field])
        if not current_value:
            current_value = "خالی"
        
        await update.message.reply_text(
            f"📝 **فیلد:** {field}\n"
            f"🔍 **مقدار فعلی:** {current_value}\n\n"
            f"✏️ **مقدار جدید را وارد کنید:**",
            reply_markup=ReplyKeyboardMarkup([["❌ لغو"]], resize_keyboard=True)
        )
    except Exception:
        await update.message.reply_text("✏️ **مقدار جدید را وارد کنید:**")
    
    return EDIT_VALUE


async def edit_value_apply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """اعمال مقدار جدید"""
    try:
        value = update.message.text.strip()
        
        if value == "❌ لغو":
            await update.message.reply_text("❌ ویرایش لغو شد.", reply_markup=get_keyboard())
            return ConversationHandler.END
        
        field = context.user_data['edit_field']
        row = context.user_data['edit_row']
        
        # اعتبارسنجی
        is_valid, validated_value = validate_field_input(field, value)
        if not is_valid:
            await update.message.reply_text(validated_value)
            return EDIT_VALUE
        
        df = pd.read_excel(EXCEL_FILE)
        old_value = clean_value(df.at[row, field])
        df.at[row, field] = validated_value
        
        user_theme = load_user_theme(update.effective_user.id)
        if create_excel(df, user_theme):
            await update.message.reply_text(
                f"✅ **ویرایش موفق!**\n"
                f"🔧 فیلد: {field}\n"
                f"🔄 از: {old_value}\n"
                f"➡️ به: {validated_value}",
                reply_markup=get_keyboard()
            )
            logger.info(f"User {update.effective_user.id} edited field {field}")
        else:
            raise Exception("Error creating Excel file")
        
    except Exception as e:
        logger.error(f"Error in edit_value_apply: {e}")
        await update.message.reply_text("❌ خطا در ویرایش رکورد.", reply_markup=get_keyboard())
    
    return ConversationHandler.END


# ============================ لغو عملیات ============================

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """لغو عملیات در حال انجام"""
    await update.message.reply_text(
        "❌ **عملیات لغو شد.**\n🏠 بازگشت به منوی اصلی",
        reply_markup=get_keyboard()
    )
    return ConversationHandler.END

