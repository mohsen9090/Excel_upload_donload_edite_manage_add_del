# search_record.py
import pandas as pd import os from telegram 
import Update, ReplyKeyboardMarkup, 
KeyboardButton from telegram.ext import 
ContextTypes, ConversationHandler from config 
import EXCEL_FILE import logging logger = 
logging.getLogger(__name__)
# States
SEARCH_TERM = 300 def get_main_keyboard(): 
    """کیبورد اصلی""" keyboard = [
        [KeyboardButton("➕ اضافه کردن رکورد"), 
        KeyboardButton("📋 نمایش همه رکوردها")], 
        [KeyboardButton("✏️ ویرایش رکورد"), 
        KeyboardButton("🗑️ حذف رکورد")], 
        [KeyboardButton("🔍 جستجو رکورد"), 
        KeyboardButton("⚙️ مدیریت فیلدها")], 
        [KeyboardButton("📁 دریافت فایل Excel"), 
        KeyboardButton("🧹 حذف همه رکوردها")]
    ] return ReplyKeyboardMarkup(keyboard, 
    resize_keyboard=True)
async def start_search_record(update: Update, 
context: ContextTypes.DEFAULT_TYPE):
    """شروع فرآیند جستجو رکورد""" try: if not 
        os.path.exists(EXCEL_FILE):
            await update.message.reply_text("هیچ 
            رکوردی برای جستجو وجود ندارد.") 
            return ConversationHandler.END
        
        df = pd.read_excel(EXCEL_FILE) if 
        df.empty:
            await update.message.reply_text("هیچ 
            رکوردی برای جستجو وجود ندارد.") 
            return ConversationHandler.END
        
        await update.message.reply_text( "🔍 کلمه 
            کلیدی برای جستجو را وارد کنید:\n" 
            "(جستجو در تمام فیلدها انجام 
            می‌شود)\n\n" "یا 'لغو' برای برگشت:"
        )
        
        return SEARCH_TERM
        
    except Exception as e: logger.error(f"خطا در 
        شروع جستجو: {e}") await 
        update.message.reply_text("خطا در شروع 
        جستجو.") return ConversationHandler.END
async def search_term(update: Update, context: 
ContextTypes.DEFAULT_TYPE):
    """جستجوی رکورد بر اساس کلمه کلیدی""" try: 
        user_input = update.message.text.strip()
        
        if user_input.lower() == 'لغو': await 
            update.message.reply_text(
                "❌ جستجو لغو شد.", 
                reply_markup=get_main_keyboard()
            ) return ConversationHandler.END
        
        df = pd.read_excel(EXCEL_FILE)
        
        # جستجو در تمام فیلدها
        search_results = [] for index, row in 
        df.iterrows():
            row_matched = False for column in 
            df.columns:
                cell_value = 
                str(row[column]).lower() if 
                user_input.lower() in cell_value:
                    if not row_matched: 
                        search_results.append((index, 
                        row)) row_matched = True
                    break
        
        if not search_results: await 
            update.message.reply_text(
                f"❌ هیچ رکوردی با کلمه کلیدی 
                '{user_input}' یافت نشد.", 
                reply_markup=get_main_keyboard()
            ) return ConversationHandler.END
        
        # نمایش نتایج جستجو
        message = f"🔍 نتایج جستجو برای 
        '{user_input}':\n" message += f"تعداد 
        رکوردهای یافت شده: 
        {len(search_results)}\n\n"
        
        for i, (original_index, row) in 
        enumerate(search_results[:10]): # نمایش 
        حداکثر 10 نتیجه
            message += f"🔹 رکورد {i+1}:\n" for 
            column in df.columns:
                cell_value = str(row[column])
                # هایلایت کلمه جستجو شده
                if user_input.lower() in 
                cell_value.lower():
                    message += f" • {column}: 
                    *{cell_value}*\n"
                else: message += f" • {column}: 
                    {cell_value}\n"
            message += "\n"
        
        if len(search_results) > 10: message += 
            f"... و {len(search_results) - 10} 
            رکورد دیگر"
        
        await update.message.reply_text( message, 
            reply_markup=get_main_keyboard(), 
            parse_mode='Markdown'
        )
        
        return ConversationHandler.END
        
    except Exception as e: logger.error(f"خطا در 
        جستجو: {e}") await 
        update.message.reply_text(
            "❌ خطا در جستجو.", 
            reply_markup=get_main_keyboard()
        )
        return ConversationHandler.END
