# edit_record.py
import pandas as pd import os from telegram 
import Update, ReplyKeyboardMarkup, 
KeyboardButton from telegram.ext import 
ContextTypes, ConversationHandler from config 
import EXCEL_FILE import logging logger = 
logging.getLogger(__name__)
# States
SELECT_EDIT_RECORD, SELECT_EDIT_FIELD, 
EDIT_FIELD_VALUE = range(200, 203) def 
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
async def start_edit_record(update: Update, 
context: ContextTypes.DEFAULT_TYPE):
    """شروع فرآیند ویرایش رکورد""" try: if not 
        os.path.exists(EXCEL_FILE):
            await update.message.reply_text("هیچ 
            رکوردی برای ویرایش وجود ندارد.") 
            return ConversationHandler.END
        
        df = pd.read_excel(EXCEL_FILE) if 
        df.empty:
            await update.message.reply_text("هیچ 
            رکوردی برای ویرایش وجود ندارد.") 
            return ConversationHandler.END
        
        # نمایش لیست رکوردها
        message = "✏️ لیست رکوردها برای 
        ویرایش:\n\n" for i in range(len(df)):
            row = df.iloc[i] name = 
            row.get('نام', 'نامشخص') last_name = 
            row.get('نام خانوادگی', '') message 
            += f"{i+1}. {name} {last_name}\n"
        
        message += "\nشماره رکورد مورد نظر برای 
        ویرایش را وارد کنید یا 'لغو' برای برگشت:"
        
        await update.message.reply_text(message) 
        return SELECT_EDIT_RECORD
        
    except Exception as e: logger.error(f"خطا در 
        شروع ویرایش رکورد: {e}") await 
        update.message.reply_text("خطا در 
        بارگذاری رکوردها.") return 
        ConversationHandler.END
async def select_edit_record(update: Update, 
context: ContextTypes.DEFAULT_TYPE):
    """انتخاب رکورد برای ویرایش""" try: 
        user_input = update.message.text.strip()
        
        if user_input.lower() == 'لغو': await 
            update.message.reply_text(
                "❌ عملیات ویرایش لغو شد.", 
                reply_markup=get_main_keyboard()
            ) return ConversationHandler.END
        
        # بررسی صحت شماره وارد شده
        try: record_number = int(user_input) 
        except ValueError:
            await update.message.reply_text("لطفاً 
            شماره معتبر وارد کنید یا 'لغو' تایپ 
            کنید.") return SELECT_EDIT_RECORD
        
        df = pd.read_excel(EXCEL_FILE)
        
        if record_number < 1 or record_number > 
        len(df):
            await 
            update.message.reply_text(f"شماره 
            باید بین 1 تا {len(df)} باشد.") 
            return SELECT_EDIT_RECORD
        
        # ذخیره اطلاعات رکورد انتخاب شده
        context.user_data['edit_record_index'] = 
        record_number - 1 selected_record = 
        df.iloc[record_number - 1]
        
        # نمایش فیلدهای قابل ویرایش
        message = "فیلدهای قابل ویرایش:\n\n" for 
        i, column in enumerate(df.columns, 1):
            current_value = 
            selected_record[column] message += 
            f"{i}. {column}: {current_value}\n"
        
        message += "\nشماره فیلد مورد نظر برای 
        ویرایش را وارد کنید یا 'لغو' برای برگشت:"
        
        await update.message.reply_text(message) 
        return SELECT_EDIT_FIELD
        
    except Exception as e: logger.error(f"خطا در 
        انتخاب رکورد: {e}") await 
        update.message.reply_text("خطا در انتخاب 
        رکورد.") return ConversationHandler.END
async def select_edit_field(update: Update, 
context: ContextTypes.DEFAULT_TYPE):
    """انتخاب فیلد برای ویرایش""" try: 
        user_input = update.message.text.strip()
        
        if user_input.lower() == 'لغو': await 
            update.message.reply_text(
                "❌ عملیات ویرایش لغو شد.", 
                reply_markup=get_main_keyboard()
            ) return ConversationHandler.END
        
        # بررسی صحت شماره وارد شده
        try: field_number = int(user_input) 
        except ValueError:
            await update.message.reply_text("لطفاً 
            شماره معتبر وارد کنید یا 'لغو' تایپ 
            کنید.") return SELECT_EDIT_FIELD
        
        df = pd.read_excel(EXCEL_FILE)
        
        if field_number < 1 or field_number > 
        len(df.columns):
            await 
            update.message.reply_text(f"شماره 
            باید بین 1 تا {len(df.columns)} 
            باشد.") return SELECT_EDIT_FIELD
        
        # ذخیره اطلاعات فیلد انتخاب شده
        selected_field = df.columns[field_number 
        - 1] context.user_data['edit_field_name'] 
        = selected_field
        
        record_index = 
        context.user_data['edit_record_index'] 
        current_value = 
        df.iloc[record_index][selected_field]
        
        await update.message.reply_text( f"مقدار 
            فعلی '{selected_field}': 
            {current_value}\n\n" f"مقدار جدید 
            برای '{selected_field}' را وارد کنید 
            یا 'لغو' برای برگشت:"
        )
        
        return EDIT_FIELD_VALUE
        
    except Exception as e: logger.error(f"خطا در 
        انتخاب فیلد: {e}") await 
        update.message.reply_text("خطا در انتخاب 
        فیلد.") return ConversationHandler.END
async def edit_field_value(update: Update, 
context: ContextTypes.DEFAULT_TYPE):
    """ویرایش مقدار فیلد""" try: user_input = 
        update.message.text.strip()
        
        if user_input.lower() == 'لغو': await 
            update.message.reply_text(
                "❌ عملیات ویرایش لغو شد.", 
                reply_markup=get_main_keyboard()
            ) return ConversationHandler.END
        
        # دریافت اطلاعات ذخیره شده
        record_index = 
        context.user_data['edit_record_index'] 
        field_name = 
        context.user_data['edit_field_name']
        
        # خواندن و ویرایش فایل
        df = pd.read_excel(EXCEL_FILE) old_value 
        = df.iloc[record_index][field_name] 
        df.iloc[record_index, 
        df.columns.get_loc(field_name)] = 
        user_input
        
        # ذخیره فایل
        df.to_excel(EXCEL_FILE, index=False)
        
        await update.message.reply_text( f"✅ 
            ویرایش انجام شد!\n\n" f"فیلد: 
            {field_name}\n" f"مقدار قبلی: 
            {old_value}\n" f"مقدار جدید: 
            {user_input}", 
            reply_markup=get_main_keyboard()
        )
        
        return ConversationHandler.END
        
    except Exception as e: logger.error(f"خطا در 
        ویرایش فیلد: {e}") await 
        update.message.reply_text(
            "❌ خطا در ویرایش رکورد.", 
            reply_markup=get_main_keyboard()
        )
        return ConversationHandler.END
