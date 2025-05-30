# delete_record.py
import pandas as pd import os from telegram 
import Update, ReplyKeyboardMarkup, 
KeyboardButton from telegram.ext import 
ContextTypes, ConversationHandler from config 
import EXCEL_FILE import logging logger = 
logging.getLogger(__name__)
# States
SELECT_DELETE_RECORD = 100 def 
get_main_keyboard():
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
async def start_delete_record(update: Update, 
context: ContextTypes.DEFAULT_TYPE):
    """شروع فرآیند حذف رکورد""" try: if not 
        os.path.exists(EXCEL_FILE):
            await update.message.reply_text("هیچ 
            رکوردی برای حذف وجود ندارد.") return 
            ConversationHandler.END
        
        df = pd.read_excel(EXCEL_FILE) if 
        df.empty:
            await update.message.reply_text("هیچ 
            رکوردی برای حذف وجود ندارد.") return 
            ConversationHandler.END
        
        # نمایش لیست رکوردها
        message = "🗑️ لیست رکوردها برای حذف:\n\n" 
        for i in range(len(df)):
            row = df.iloc[i] name = 
            row.get('نام', 'نامشخص') last_name = 
            row.get('نام خانوادگی', '') message 
            += f"{i+1}. {name} {last_name}\n"
        
        message += "\nشماره رکورد مورد نظر برای 
        حذف را وارد کنید یا 'لغو' برای برگشت:"
        
        await update.message.reply_text(message) 
        return SELECT_DELETE_RECORD
        
    except Exception as e: logger.error(f"خطا در 
        شروع حذف رکورد: {e}") await 
        update.message.reply_text("خطا در 
        بارگذاری رکوردها.") return 
        ConversationHandler.END
async def select_delete_record(update: Update, 
context: ContextTypes.DEFAULT_TYPE):
    """انتخاب رکورد برای حذف""" try: user_input 
        = update.message.text.strip()
        
        if user_input.lower() == 'لغو': await 
            update.message.reply_text(
                "❌ عملیات حذف لغو شد.", 
                reply_markup=get_main_keyboard()
            ) return ConversationHandler.END
        
        # بررسی صحت شماره وارد شده
        try: record_number = int(user_input) 
        except ValueError:
            await update.message.reply_text("لطفاً 
            شماره معتبر وارد کنید یا 'لغو' تایپ 
            کنید.") return SELECT_DELETE_RECORD
        
        df = pd.read_excel(EXCEL_FILE)
        
        if record_number < 1 or record_number > 
        len(df):
            await 
            update.message.reply_text(f"شماره 
            باید بین 1 تا {len(df)} باشد.") 
            return SELECT_DELETE_RECORD
        
        # حذف رکورد
        record_to_delete = df.iloc[record_number 
        - 1] df = df.drop(df.index[record_number 
        - 1])
        
        # ذخیره فایل
        df.to_excel(EXCEL_FILE, index=False)
        
        name = record_to_delete.get('نام', 
        'نامشخص') last_name = 
        record_to_delete.get('نام خانوادگی', '')
        
        await update.message.reply_text( f"✅ 
            رکورد '{name} {last_name}' با موفقیت 
            حذف شد!", 
            reply_markup=get_main_keyboard()
        )
        
        return ConversationHandler.END
        
    except Exception as e: logger.error(f"خطا در 
        حذف رکورد: {e}") await 
        update.message.reply_text(
            "❌ خطا در حذف رکورد.", 
            reply_markup=get_main_keyboard()
        )
        return ConversationHandler.END
