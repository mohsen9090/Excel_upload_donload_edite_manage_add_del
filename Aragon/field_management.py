import pandas as pd import os from telegram 
import Update, ReplyKeyboardMarkup, 
KeyboardButton from telegram.ext import 
ContextTypes, ConversationHandler from config 
import EXCEL_FILE import logging logger = 
logging.getLogger(__name__)
# States
FIELD_MANAGEMENT_MENU, ADD_NEW_FIELD, 
DELETE_FIELD_SELECT = range(400, 403) def 
get_main_keyboard(): ‎ """کیبورد اصلی"""
    keyboard = [ [KeyboardButton("➕ اضافه کردن 
        رکورد"), KeyboardButton("📋 نمایش همه 
        رکوردها")], [KeyboardButton("✏️ ویرایش 
        رکورد"), KeyboardButton("🗑️ حذف رکورد")], 
        [KeyboardButton("🔍 جستجو رکورد"), 
        KeyboardButton("⚙️ مدیریت فیلدها")], 
        [KeyboardButton("📁 دریافت فایل Excel"), 
        KeyboardButton("🧹 حذف همه رکوردها")]
    ] return ReplyKeyboardMarkup(keyboard, 
    resize_keyboard=True)
def get_field_management_keyboard(): ‎ """کیبورد 
مدیریت فیلدها"""
    keyboard = [ [KeyboardButton("📋 نمایش 
        فیلدها"), KeyboardButton("➕ اضافه کردن 
        فیلد")], [KeyboardButton("🗑️ حذف فیلد"), 
        KeyboardButton("🔙 برگشت")]
    ] return ReplyKeyboardMarkup(keyboard, 
    resize_keyboard=True)
async def show_field_management(update: Update, 
context: ContextTypes.DEFAULT_TYPE): ‎ """نمایش 
منوی مدیریت فیلدها"""
    await update.message.reply_text( ‎ "⚙️ مدیریت 
فیلدها\n" ‎ "از گزینه‌های زیر استفاده کنید:",
        reply_markup=get_field_management_keyboard() 
    ) return FIELD_MANAGEMENT_MENU
async def handle_field_management_menu(update: 
Update, context: ContextTypes.DEFAULT_TYPE): ‎ 
"""مدیریت منوی فیلدها"""
    text = update.message.text
    
    if text == "📋 نمایش فیلدها": return await 
        show_fields(update, context)
    elif text == "➕ اضافه کردن فیلد": return 
        await start_add_field(update, context)
    elif text == "🗑️ حذف فیلد": return await 
        start_delete_field(update, context)
    elif text == "🔙 برگشت": await 
        update.message.reply_text(
‎ "بازگشت به منوی اصلی", 
            reply_markup=get_main_keyboard()
        ) return ConversationHandler.END else: 
        await update.message.reply_text(
‎ "لطفاً از گزینه‌های موجود انتخاب کنید:", 
            reply_markup=get_field_management_keyboard()
        ) return FIELD_MANAGEMENT_MENU async def 
show_fields(update: Update, context: 
ContextTypes.DEFAULT_TYPE): ‎ """نمایش فیلدهای 
موجود"""
    try: if not os.path.exists(EXCEL_FILE): ‎ # 
فیلدهای پیش‌فرض
            from main import DEFAULT_FIELDS 
            message = "📋 فیلدهای پیش‌فرض:\n\n" 
            for i, field in 
            enumerate(DEFAULT_FIELDS, 1):
                message += f"{i}. {field}\n" 
        else:
            df = pd.read_excel(EXCEL_FILE) 
            message = "📋 فیلدهای موجود:\n\n" for 
            i, column in enumerate(df.columns, 
            1):
                message += f"{i}. {column}\n"
        
        await update.message.reply_text(message) 
        return FIELD_MANAGEMENT_MENU
        
    except Exception as e: logger.error(f"خطا در 
        نمایش فیلدها: {e}") await 
        update.message.reply_text("خطا در نمایش 
        فیلدها.") return FIELD_MANAGEMENT_MENU
async def start_add_field(update: Update, 
context: ContextTypes.DEFAULT_TYPE): ‎ """شروع 
اضافه کردن فیلد جدید"""
    await update.message.reply_text( ‎ "➕ نام 
فیلد جدید را وارد کنید:\n" ‎ "(یا 'لغو' برای 
برگشت)"
    ) return ADD_NEW_FIELD async def 
add_new_field(update: Update, context: 
ContextTypes.DEFAULT_TYPE): ‎ """اضافه کردن فیلد 
جدید"""
    try: field_name = update.message.text.strip()
        
        if field_name.lower() == 'لغو': await 
            update.message.reply_text(
‎ "❌ اضافه کردن فیلد لغو شد.", 
                reply_markup=get_field_management_keyboard()
            ) return FIELD_MANAGEMENT_MENU
        
        if not field_name: await 
            update.message.reply_text("نام فیلد 
            نمی‌تواند خالی باشد. دوباره تلاش 
            کنید:") return ADD_NEW_FIELD
        
‎ # بررسی وجود فایل و اضافه کردن فیلد if 
        os.path.exists(EXCEL_FILE):
            df = pd.read_excel(EXCEL_FILE)
            
‎ # بررسی وجود فیلد if field_name in df.columns: 
                await update.message.reply_text(
                    f"فیلد '{field_name}' قبلاً 
                    وجود دارد. نام دیگری انتخاب 
                    کنید:"
                ) return ADD_NEW_FIELD
            
‎ # اضافه کردن فیلد جدید df[field_name] = "" else: 
‎ # ایجاد فایل جدید با فیلد جدید
            from main import DEFAULT_FIELDS 
            columns = DEFAULT_FIELDS + 
            [field_name] df = 
            pd.DataFrame(columns=columns)
        
‎ # ذخیره فایل df.to_excel(EXCEL_FILE, 
        index=False)
        
        await update.message.reply_text( f"✅ 
            فیلد '{field_name}' با موفقیت اضافه 
            شد!", 
            reply_markup=get_field_management_keyboard()
        )
        
        return FIELD_MANAGEMENT_MENU
        
    except Exception as e: logger.error(f"خطا در 
        اضافه کردن فیلد: {e}") await 
        update.message.reply_text(
‎ "❌ خطا در اضافه کردن فیلد.", 
            reply_markup=get_field_management_keyboard()
        ) return FIELD_MANAGEMENT_MENU async def 
start_delete_field(update: Update, context: 
ContextTypes.DEFAULT_TYPE): ‎ """شروع حذف فیلد"""
    try: if not os.path.exists(EXCEL_FILE): await 
            update.message.reply_text(
‎ "هیچ فیلدی برای حذف وجود ندارد.", 
                reply_markup=get_field_management_keyboard()
            ) return FIELD_MANAGEMENT_MENU
        
        df = pd.read_excel(EXCEL_FILE)
        
        if df.empty or len(df.columns) == 0: 
            await update.message.reply_text(
‎ "هیچ فیلدی برای حذف وجود ندارد.", 
                reply_markup=get_field_management_keyboard()
            ) return FIELD_MANAGEMENT_MENU
        
        message = "🗑️ فیلدهای قابل حذف:\n\n" for 
        i, column in enumerate(df.columns, 1):
            message += f"{i}. {column}\n"
        
        message += "\nشماره فیلد مورد نظر برای 
        حذف را وارد کنید یا 'لغو' برای برگشت:"
        
       await update.message.reply_text(message) 
        return DELETE_FIELD_SELECT
    except Exception as e: logger.error(f"خطا در 
        شروع حذف فیلد: {e}") await 
        update.message.reply_text(
            "❌ خطا در شروع حذف فیلد.", 
            reply_markup=get_field_management_keyboard()
        ) return FIELD_MANAGEMENT_MENU async def 
delete_field(update: Update, context: 
ContextTypes.DEFAULT_TYPE):
    """حذف فیلد مشخص شده""" try: field_index = 
        update.message.text.strip()
        
        if field_index.lower() == 'لغو': await 
            update.message.reply_text(
                "❌ حذف فیلد لغو شد.", 
                reply_markup=get_field_management_keyboard()
            ) return FIELD_MANAGEMENT_MENU
        
        if not field_index.isdigit(): await 
            update.message.reply_text("لطفاً شماره 
            فیلد را وارد کنید.") return 
            DELETE_FIELD_SELECT
        
        field_index = int(field_index) - 1
        
        df = pd.read_excel(EXCEL_FILE)
        
        if field_index < 0 or field_index >= 
        len(df.columns):
            await 
            update.message.reply_text("شماره فیلد 
            نامعتبر است. دوباره تلاش کنید:") 
            return DELETE_FIELD_SELECT
        
        # حذف فیلد
        deleted_field = df.columns[field_index] 
        df.drop(columns=[deleted_field], 
        inplace=True)
        
        # ذخیره تغییرات
        df.to_excel(EXCEL_FILE, index=False)
        
        await update.message.reply_text( f"✅ 
            فیلد '{deleted_field}' با موفقیت حذف 
            شد!", 
            reply_markup=get_field_management_keyboard()
        )
        
        return FIELD_MANAGEMENT_MENU except 
    Exception as e:
        logger.error(f"خطا در حذف فیلد: {e}") 
        await update.message.reply_text(
            "❌ خطا در حذف فیلد.", 
            reply_markup=get_field_management_keyboard()
        )
        return FIELD_MANAGEMENT_MENU
