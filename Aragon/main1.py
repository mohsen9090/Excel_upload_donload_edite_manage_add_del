
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ربات مدیریت Excel پیشرفته - قسمت اول
نسخه 2.0
"""

import logging
import pandas as pd
import os
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, ConversationHandler, filters

# وارد کردن فایل‌های سیستم
from config import *
from utils import *

# تنظیم لاگینگ
logging.basicConfig(
    filename=LOG_FILE,
    format=LOG_FORMAT,
    level=logging.INFO
)
logger = logging.getLogger(__name__)


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
• تم‌های رنگی متنوع
• خروجی Excel زیبا

از منوی زیر استفاده کنید:"""

    await update.message.reply_text(welcome_msg, reply_markup=get_keyboard())


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

