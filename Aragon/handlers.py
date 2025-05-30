# handlers.py
from telegram import Update, ReplyKeyboardMarkup, 
KeyboardButton from telegram.ext import 
ContextTypes import pandas as pd import os 
EXCEL_FILE = "data.xlsx" async def 
start_add_record(update: Update, context: 
ContextTypes.DEFAULT_TYPE):
    """شروع اضافه کردن رکورد""" fields = 
    get_current_fields() 
    context.user_data['current_field'] = 0 
    context.user_data['record_data'] = {} 
    context.user_data['fields'] = fields
    
    if not fields: await 
        update.message.reply_text("❌ هیچ فیلدی 
        برای اضافه کردن رکورد وجود ندارد.", 
        reply_markup=get_main_keyboard()) return
    
    field_name = fields[0] await 
    update.message.reply_text(
        f"📝 **اضافه کردن رکورد جدید**\n\n" 
        f"لطفاً **{field_name}** را وارد کنید:", 
        reply_markup=ReplyKeyboardMarkup([[KeyboardButton("❌ 
        لغو")]], resize_keyboard=True)
    ) return ADD_RECORD async def 
process_add_record(update: Update, context: 
ContextTypes.DEFAULT_TYPE):
    """پردازش اضافه کردن رکورد""" if 
    update.message.text == "❌ لغو":
        await update.message.reply_text("عملیات 
        لغو شد.", 
        reply_markup=get_main_keyboard()) return 
        ConversationHandler.END
    
    fields = context.user_data['fields'] 
    current_field_index = 
    context.user_data['current_field'] field_name 
    = fields[current_field_index] value = 
    update.message.text.strip()
    
    context.user_data['record_data'][field_name] 
    = value context.user_data['current_field'] += 
    1
    
    if context.user_data['current_field'] < 
    len(fields):
        next_field = 
        fields[context.user_data['current_field']] 
        progress = 
        context.user_data['current_field'] + 1 
        total = len(fields)
        
        await update.message.reply_text( f"✅ 
            **{field_name}** ثبت شد!\n\n" f"📊 
            پیشرفت: {progress}/{total}\n\n" 
            f"لطفاً **{next_field}** را وارد 
            کنید:"
        ) return ADD_RECORD else:
        # ذخیره رکورد
        try: df = pd.read_excel(EXCEL_FILE) 
            new_record = 
            pd.DataFrame([context.user_data['record_data']]) 
            df = pd.concat([df, new_record], 
            ignore_index=True) 
            save_excel_with_style(df, EXCEL_FILE)
            
            await update.message.reply_text( f"✅ 
                **رکورد با موفقیت ذخیره 
                شد!**\n\n" f"📊 **مجموع 
                رکوردها:** {len(df)}", 
                reply_markup=get_main_keyboard()
            ) except Exception as e: 
            logger.error(f"خطا در ذخیره رکورد: 
            {e}") await 
            update.message.reply_text("❌ خطا در 
            ذخیره رکورد.", 
            reply_markup=get_main_keyboard())
        
        return ConversationHandler.END def 
get_current_fields():
    """دریافت فیلدهای فعلی از فایل Excel""" try: 
        if os.path.exists(EXCEL_FILE):
            df = pd.read_excel(EXCEL_FILE) return 
            list(df.columns)
        else: return [] except Exception as e: 
        print(f"خطا در دریافت فیلدها: {e}") 
        return []
def get_main_keyboard(): """کیبورد اصلی""" 
    keyboard = [
        [KeyboardButton("➕ اضافه کردن رکورد"), 
        KeyboardButton("📋 نمایش همه رکوردها")], 
        [KeyboardButton("✏️ ویرایش رکورد"), 
        KeyboardButton("🗑️ حذف رکورد")], 
        [KeyboardButton("🔍 جستجو رکورد"), 
        KeyboardButton("⚙️ مدیریت فیلدها")], 
        [KeyboardButton("📁 دریافت فایل Excel"), 
        KeyboardButton("🧹 حذف همه رکوردها")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
