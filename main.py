#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" ربات مدیریت Excel پیشرفته با قابلیت آپلود 
فایل نسخه 2.1 - با آپلود فایل Excel دلخواه """ 
import logging import pandas as pd import os from 
datetime import datetime from telegram import 
Update, ReplyKeyboardMarkup, KeyboardButton, 
InlineKeyboardMarkup, InlineKeyboardButton from 
telegram.ext import ApplicationBuilder, 
CommandHandler, MessageHandler, ContextTypes, 
ConversationHandler, filters, 
CallbackQueryHandler
# وارد کردن فایل‌های سیستم
from config import * from utils import *
# State جدید برای آپلود فایل
UPLOAD_FILE = 11
# تنظیم لاگینگ
logging.basicConfig( filename=LOG_FILE, 
    format=LOG_FORMAT, level=logging.INFO
) logger = logging.getLogger(__name__)
# ============================ آپلود فایل Excel 
# ============================
async def upload_file_start(update: Update, 
context: ContextTypes.DEFAULT_TYPE):
    """شروع آپلود فایل Excel""" keyboard = [ 
        [KeyboardButton("🔄 جایگزینی کامل فایل 
        فعلی")], [KeyboardButton("➕ ادغام با 
        فایل موجود")], [KeyboardButton("❌ لغو")]
    ]
    
    msg = """📤 **آپلود فایل Excel** 🔹 **دو 
گزینه داری:** • **🔄 جایگزینی:** فایل فعلی پاک 
شده و فایل جدید جایگزین میشه • **➕ ادغام:** 
رکوردهای فایل جدید به فایل موجود اضافه میشن ⚠️ 
**نکات مهم:** • فایل باید فرمت Excel (.xlsx) باشه 
• سطر اول باید عناوین ستون‌ها باشه • حداکثر حجم: 
20 مگابایت لطفاً روش مورد نظرت رو انتخاب کن:"""
    await update.message.reply_text( msg, 
        reply_markup=ReplyKeyboardMarkup(keyboard, 
        resize_keyboard=True)
    ) return UPLOAD_FILE async def 
upload_file_process(update: Update, context: 
ContextTypes.DEFAULT_TYPE):
    """پردازش آپلود فایل""" text = 
    update.message.text
    
    if text == "❌ لغو": await 
        update.message.reply_text("❌ آپلود فایل 
        لغو شد.", reply_markup=get_keyboard()) 
        return ConversationHandler.END
    
    if text == "🔄 جایگزینی کامل فایل فعلی": 
        context.user_data['upload_mode'] = 
        'replace' mode_text = "🔄 **جایگزینی 
        کامل**"
    elif text == "➕ ادغام با فایل موجود": 
        context.user_data['upload_mode'] = 
        'merge' mode_text = "➕ **ادغام**"
    else: await update.message.reply_text("❌ 
        گزینه نامعتبر است.") return UPLOAD_FILE
    
    await update.message.reply_text( 
        f"{mode_text}\n\n" f"📁 **حالا فایل Excel 
        رو ارسال کن:**\n" f"• فرمت: .xlsx یا 
        .xls\n" f"• حداکثر حجم: 20 مگابایت\n\n" 
        f"📎 فایل رو به عنوان Document ارسال 
        کن..."
    ) return UPLOAD_FILE async def 
handle_uploaded_file(update: Update, context: 
ContextTypes.DEFAULT_TYPE):
    """پردازش فایل آپلود شده""" try: if not 
        update.message.document:
            await update.message.reply_text("❌ 
            لطفاً فایل را به عنوان Document ارسال 
            کنید.") return UPLOAD_FILE
        
        document = update.message.document
        
        # بررسی فرمت فایل
        if not 
        document.file_name.lower().endswith(('.xlsx', 
        '.xls')):
            await update.message.reply_text("❌ 
            فقط فایل‌های Excel (.xlsx، .xls) 
            پذیرفته میشن.") return UPLOAD_FILE
        
        # بررسی حجم فایل (20 مگابایت)
        if document.file_size > 20 * 1024 * 1024: 
            await update.message.reply_text("❌ 
            حجم فایل نباید از 20 مگابایت بیشتر 
            باشه.") return UPLOAD_FILE
        
        await update.message.reply_text("⏳ در 
        حال پردازش فایل...")
        
        # دانلود فایل
        file = await 
        context.bot.get_file(document.file_id) 
        temp_file = 
        f"temp_{update.effective_user.id}_{document.file_name}" 
        await file.download_to_drive(temp_file)
        
        # خواندن فایل Excel
        try: uploaded_df = 
            pd.read_excel(temp_file)
        except Exception as e: 
            os.remove(temp_file) await 
            update.message.reply_text(f"❌ خطا در 
            خواندن فایل Excel:\n{str(e)}") return 
            UPLOAD_FILE
        
        if uploaded_df.empty: 
            os.remove(temp_file) await 
            update.message.reply_text("❌ فایل 
            خالی است!") return UPLOAD_FILE
        
        # پردازش بر اساس نوع آپلود
        upload_mode = 
        context.user_data.get('upload_mode', 
        'replace') user_theme = 
        load_user_theme(update.effective_user.id)
        
        if upload_mode == 'replace':
            # جایگزینی کامل
            result_df = uploaded_df.copy() 
            action_text = "جایگزین شد"
        else:
            # ادغام
            if os.path.exists(EXCEL_FILE) and 
            os.path.getsize(EXCEL_FILE) > 0:
                existing_df = 
                pd.read_excel(EXCEL_FILE)
                
                # بررسی سازگاری ستون‌ها
                existing_cols = 
                set(existing_df.columns) 
                uploaded_cols = 
                set(uploaded_df.columns)
                
                if existing_cols != 
                uploaded_cols:
                    # اگر ستون‌ها متفاوت باشن، از 
                    # اتحاد ستون‌ها استفاده می‌کنیم
                    all_cols = 
                    list(existing_cols.union(uploaded_cols))
                    
                    # تنظیم ستون‌های موجود
                    for col in all_cols: if col 
                        not in 
                        existing_df.columns:
                            existing_df[col] = "" 
                        if col not in 
                        uploaded_df.columns:
                            uploaded_df[col] = ""
                    
                    # مرتب کردن ستون‌ها
                    existing_df = 
                    existing_df[all_cols] 
                    uploaded_df = 
                    uploaded_df[all_cols]
                
                result_df = 
                pd.concat([existing_df, 
                uploaded_df], ignore_index=True) 
                action_text = "ادغام شد"
            else: result_df = uploaded_df.copy() 
                action_text = "اضافه شد"
        
        # ذخیره فیلدهای جدید
        new_fields = list(result_df.columns) 
        save_fields(new_fields)
        
        # ایجاد فایل Excel جدید
        if create_excel(result_df, user_theme): 
            success_msg = f"""✅ **فایل با موفقیت 
            {action_text}!**
📊 **آمار:** • تعداد رکوردهای جدید: 
{len(uploaded_df):,} • تعداد کل رکوردها: 
{len(result_df):,} • تعداد ستون‌ها: 
{len(result_df.columns)} 📋 **ستون‌های موجود:** 
{chr(10).join([f" • {col}" for col in 
result_df.columns[:10]])} {f"... و 
{len(result_df.columns) - 10} ستون دیگر" if 
len(result_df.columns) > 10 else ""} 🎨 **تم 
اعمال شده:** {THEMES[user_theme]['name']}"""
            await 
            update.message.reply_text(success_msg, 
            reply_markup=get_keyboard()) 
            logger.info(f"User 
            {update.effective_user.id} uploaded 
            Excel file: {document.file_name}")
        else: await update.message.reply_text("❌ 
            خطا در ذخیره فایل.", 
            reply_markup=get_keyboard())
        
        # حذف فایل موقت
        os.remove(temp_file)
        
    except Exception as e: logger.error(f"Error 
        in handle_uploaded_file: {e}") await 
        update.message.reply_text("❌ خطا در 
        پردازش فایل.", 
        reply_markup=get_keyboard())
        
        # حذف فایل موقت در صورت خطا
        temp_file = 
        f"temp_{update.effective_user.id}_{update.message.document.file_name}" 
        if os.path.exists(temp_file):
            os.remove(temp_file)
    
    return ConversationHandler.END
# ============================ کیبورد جدید با 
# دکمه آپلود ============================
def get_keyboard(): """کیبورد اصلی با دکمه 
    آپلود""" keyboard = [
        ["➕ اضافه کردن", "📋 نمایش همه", "📁 
        دریافت فایل"], ["✏️ ویرایش", "🗑️ حذف", "🔍 
        جستجو"], ["📤 آپلود فایل Excel", "⚙️ 
        مدیریت فیلدها"], # دکمه جدید اینجاست! 
        ["🎨 تغییر تم", "📊 آمار", "🧹 حذف همه"], 
        ["ℹ️ راهنما"]
    ] return ReplyKeyboardMarkup(keyboard, 
    resize_keyboard=True)
# ============================ بقیه توابع از قبل 
# ============================
async def start(update: Update, context: 
ContextTypes.DEFAULT_TYPE):
    """شروع ربات""" ensure_excel_file() user_name 
    = update.effective_user.first_name
    
    welcome_msg = f"""🤖 **ربات مدیریت Excel 
    پیشرفته**
سلام {user_name}! 👋 📋 امکانات: • 
اضافه/ویرایش/حذف رکورد • جستجو پیشرفته • مدیریت 
فیلدها • 📤 **آپلود فایل Excel دلخواه** (جدید!) • 
تم‌های رنگی متنوع • خروجی Excel زیبا از منوی زیر 
استفاده کنید:"""
    await update.message.reply_text(welcome_msg, 
    reply_markup=get_keyboard())
# Import کردن بقیه توابع از فایل‌های قبلی
from main1 import ( add_record_start, 
    add_record_process, show_all_records, 
    send_excel_file, edit_start, edit_row_select, 
    edit_field_select, edit_value_apply
)
# اضافه کردن توابع حذف، جستجو و... از A7.py
async def delete_start(update: Update, context: 
ContextTypes.DEFAULT_TYPE):
    """شروع حذف رکورد""" try: 
        ensure_excel_file() df = 
        pd.read_excel(EXCEL_FILE)
        
        if df.empty: await 
            update.message.reply_text("📭 هیچ 
            رکوردی برای حذف وجود ندارد.", 
            reply_markup=get_keyboard()) return 
            ConversationHandler.END
        
        msg = "🗑️ **شماره ردیف مورد نظر برای 
        حذف:**\n\n" for i, row in df.iterrows():
            name = clean_value(row.get('نام', 
            f'ردیف {i+1}')) family = 
            clean_value(row.get('نام خانوادگی', 
            '')) if family:
                name += f" {family}" msg += 
            f"{i+1}. {name}\n"
        
        await update.message.reply_text(msg) 
        return DELETE_ROW
    except Exception as e: logger.error(f"Error 
        in delete_start: {e}") await 
        update.message.reply_text("❌ خطا در 
        بارگذاری رکوردها.", 
        reply_markup=get_keyboard()) return 
        ConversationHandler.END
async def delete_confirm(update: Update, context: 
ContextTypes.DEFAULT_TYPE):
    """تأیید و حذف رکورد""" try: row_num = 
        int(update.message.text) - 1 df = 
        pd.read_excel(EXCEL_FILE)
        
        if row_num < 0 or row_num >= len(df): 
            await update.message.reply_text("❌ 
            شماره ردیف نامعتبر است.") return 
            DELETE_ROW
        
        deleted_record = df.iloc[row_num] 
        record_info = f"🗑️ **رکورد حذف شده:**\n" 
        for col in df.columns:
            value = 
            clean_value(deleted_record[col]) if 
            value:
                record_info += f"• {col}: 
                {value}\n"
        
        df = 
        df.drop(row_num).reset_index(drop=True) 
        user_theme = 
        load_user_theme(update.effective_user.id)
        
        if create_excel(df, user_theme): await 
            update.message.reply_text(
                f"✅ **رکورد با موفقیت حذف 
                شد!**\n\n{record_info}", 
                reply_markup=get_keyboard()
            ) logger.info(f"User 
            {update.effective_user.id} deleted a 
            record")
        else: raise Exception("Error creating 
            Excel file")
        
    except ValueError: await 
        update.message.reply_text("❌ لطفاً یک عدد 
        معتبر وارد کنید.") return DELETE_ROW
    except Exception as e: logger.error(f"Error 
        in delete_confirm: {e}") await 
        update.message.reply_text("❌ خطا در حذف 
        رکورد.", reply_markup=get_keyboard())
    
    return ConversationHandler.END
# توابع کمکی برای جستجو، مدیریت فیلدها و...
async def search_start(update: Update, context: 
ContextTypes.DEFAULT_TYPE):
    """شروع جستجو""" fields = load_fields() 
    keyboard = [[KeyboardButton(field)] for field 
    in fields] 
    keyboard.append([KeyboardButton("🔍 جستجو در 
    همه فیلدها")])
    
    await update.message.reply_text( "🔍 **جستجو 
        در کدام فیلد؟**", 
        reply_markup=ReplyKeyboardMarkup(keyboard, 
        resize_keyboard=True)
    ) return SEARCH_FIELD async def 
search_field_select(update: Update, context: 
ContextTypes.DEFAULT_TYPE):
    """انتخاب فیلد جستجو""" field = 
    update.message.text fields = load_fields()
    
    if field == "🔍 جستجو در همه فیلدها": 
        context.user_data['search_field'] = "all" 
        await update.message.reply_text("🔍 
        **کلیدواژه جستجو را وارد کنید:**") return 
        SEARCH_VALUE
    elif field not in fields: await 
        update.message.reply_text("❌ فیلد 
        نامعتبر است.") return SEARCH_FIELD
    
    context.user_data['search_field'] = field 
    await update.message.reply_text(f"🔍 
    **کلیدواژه جستجو در فیلد '{field}':**") 
    return SEARCH_VALUE
async def search_process(update: Update, context: 
ContextTypes.DEFAULT_TYPE):
    """پردازش جستجو""" try: keyword = 
        update.message.text.strip() field = 
        context.user_data['search_field']
        
        ensure_excel_file() df = 
        pd.read_excel(EXCEL_FILE)
        
        if df.empty: await 
            update.message.reply_text("📭 هیچ 
            رکوردی برای جستجو وجود ندارد.", 
            reply_markup=get_keyboard()) return 
            ConversationHandler.END
        
        if field == "all": mask = 
            df.astype(str).apply(lambda x: 
            x.str.contains(keyword, case=False, 
            na=False)).any(axis=1) results = 
            df[mask]
        else: results = 
            df[df[field].astype(str).str.contains(keyword, 
            case=False, na=False)]
        
        message = format_search_results(results, 
        keyword, MAX_SEARCH_RESULTS) await 
        update.message.reply_text(message, 
        reply_markup=get_keyboard())
        
        logger.info(f"User 
        {update.effective_user.id} searched for 
        '{keyword}'")
        
    except Exception as e: logger.error(f"Error 
        in search_process: {e}") await 
        update.message.reply_text("❌ خطا در 
        جستجو.", reply_markup=get_keyboard())
    
    return ConversationHandler.END
# سایر توابع (مدیریت فیلدها، تم، آمار و...)
async def field_management_start(update: Update, 
context: ContextTypes.DEFAULT_TYPE):
    """شروع مدیریت فیلدها""" fields = 
    load_fields()
    
    keyboard = [ [KeyboardButton("➕ اضافه کردن 
        فیلد"), KeyboardButton("🗑️ حذف فیلد")], 
        [KeyboardButton("📋 نمایش فیلدها"), 
        KeyboardButton("🔄 بازگشت به پیش‌فرض")], 
        [KeyboardButton("🏠 بازگشت به منوی 
        اصلی")]
    ]
    
    msg = f"⚙️ **مدیریت فیلدها**\n\n" msg += f"📊 
    تعداد فیلدهای فعلی: {len(fields)}\n" msg += 
    f"📋 فیلدهای موجود:\n" for i, field in 
    enumerate(fields, 1):
        msg += f" {i}. {field}\n"
    
    await update.message.reply_text( msg, 
        reply_markup=ReplyKeyboardMarkup(keyboard, 
        resize_keyboard=True)
    ) return FIELD_MANAGEMENT async def 
change_theme(update: Update, context: 
ContextTypes.DEFAULT_TYPE):
    """تغییر تم رنگی""" current_theme = 
    load_user_theme(update.effective_user.id)
    
    keyboard = [] for key, theme in 
    THEMES.items():
        status = "✅" if key == current_theme 
        else "" 
        keyboard.append([InlineKeyboardButton(f"{theme['name']} 
        {status}", 
        callback_data=f"theme_{key}")])
    
    await update.message.reply_text( f"🎨 
        **انتخاب تم رنگی**\n" f"🔘 تم فعلی: 
        {THEMES[current_theme]['name']}", 
        reply_markup=InlineKeyboardMarkup(keyboard)
    ) async def show_stats(update: Update, 
context: ContextTypes.DEFAULT_TYPE):
    """نمایش آمار سیستم""" try: 
        ensure_excel_file()
        
        record_count = 0 if 
        os.path.exists(EXCEL_FILE) and 
        os.path.getsize(EXCEL_FILE) > 0:
            df = pd.read_excel(EXCEL_FILE) 
            record_count = len(df)
        
        fields = load_fields() field_count = 
        len(fields) user_theme = 
        load_user_theme(update.effective_user.id) 
        size_str = 
        get_file_size_string(EXCEL_FILE)
        
        msg = f"""📊 **آمار سیستم** 📋 
**داده‌ها:**
  • تعداد رکوردها: {record_count:,} • تعداد 
  فیلدها: {field_count} • حجم فایل: {size_str}
🎨 **تنظیمات شما:** • تم فعلی: 
  {THEMES[user_theme]['name']}
⏰ **زمان:** • تاریخ: 
  {datetime.now().strftime('%Y/%m/%d')} • ساعت: 
  {datetime.now().strftime('%H:%M:%S')}
🤖 **سیستم:** • نسخه ربات: 2.1 (با آپلود فایل) 
  • وضعیت: فعال ✅"""
        
        await update.message.reply_text(msg)
        
    except Exception as e: logger.error(f"Error 
        showing stats: {e}") await 
        update.message.reply_text("❌ خطا در 
        نمایش آمار.")
async def show_help(update: Update, context: 
ContextTypes.DEFAULT_TYPE):
    """نمایش راهنما""" help_text = """ℹ️ **راهنمای 
    ربات Excel**
🔹 **عملیات اصلی:** • ➕ اضافه کردن: افزودن 
  رکورد جدید • 📋 نمایش همه: مشاهده تمام رکوردها 
  • ✏️ ویرایش: تغییر اطلاعات موجود • 🗑️ حذف: پاک 
  کردن رکورد خاص • 🔍 جستجو: پیدا کردن رکورد
🔹 **مدیریت فایل:** • 📤 آپلود فایل Excel: 
  بارگذاری فایل دلخواه • 📁 دریافت فایل: دانلود 
  Excel • ⚙️ مدیریت فیلدها: اضافه/حذف ستون‌ها
🔹 **شخصی‌سازی:** • 🎨 تغییر تم: انتخاب رنگ‌بندی 
  Excel • 📊 آمار: نمایش اطلاعات سیستم
🔹 **نکات آپلود فایل:** • 📤 فرمت: .xlsx یا 
  .xls • 📏 حداکثر حجم: 20 مگابایت • 🔄 دو حالت: 
  جایگزینی یا ادغام • 📋 سطر اول باید عناوین ستون 
  باشد
❓ برای سوالات بیشتر با پشتیبانی تماس بگیرید.""" 
    await update.message.reply_text(help_text)
async def handle_main_menu(update: Update, 
context: ContextTypes.DEFAULT_TYPE):
    """مدیریت منوی اصلی""" text = 
    update.message.text
    
    if text == "➕ اضافه کردن": return await 
        add_record_start(update, context)
    elif text == "📋 نمایش همه": await 
        show_all_records(update, context)
    elif text == "📁 دریافت فایل": await 
        send_excel_file(update, context)
    elif text == "✏️ ویرایش": return await 
        edit_start(update, context)
    elif text == "🗑️ حذف": return await 
        delete_start(update, context)
    elif text == "🔍 جستجو": return await 
        search_start(update, context)
    elif text == "📤 آپلود فایل Excel": # دکمه 
    جدید!
        return await upload_file_start(update, 
        context)
    elif text == "⚙️ مدیریت فیلدها": return await 
        field_management_start(update, context)
    elif text == "🎨 تغییر تم": await 
        change_theme(update, context)
    elif text == "📊 آمار": await 
        show_stats(update, context)
    elif text == "ℹ️ راهنما": await 
        show_help(update, context)
    else: await update.message.reply_text( "❌ 
            گزینه نامعتبر است.\nلطفاً از منوی زیر 
            انتخاب کنید:", 
            reply_markup=get_keyboard()
        ) async def cancel(update: Update, 
context: ContextTypes.DEFAULT_TYPE):
    """لغو عملیات در حال انجام""" await 
    update.message.reply_text(
        "❌ **عملیات لغو شد.**\n🏠 بازگشت به منوی 
        اصلی", reply_markup=get_keyboard()
    ) return ConversationHandler.END def main(): 
    """تابع اصلی اجرای ربات""" print("🔧 در حال 
    راه‌اندازی ربات...")
    
    if TOKEN == "YOUR_BOT_TOKEN_HERE": print("❌ 
        خطا: لطفاً توکن ربات را در فایل config.py 
        وارد کنید") return
    
    application = 
    ApplicationBuilder().token(TOKEN).build()
    
    # ConversationHandler برای آپلود فایل (جدید!)
    upload_file_handler = ConversationHandler( 
        entry_points=[MessageHandler(filters.Regex("^📤 
        آپلود فایل Excel$"), upload_file_start)], 
        states={
            UPLOAD_FILE: [ 
                MessageHandler(filters.TEXT & 
                ~filters.COMMAND, 
                upload_file_process), 
                MessageHandler(filters.Document.ALL, 
                handle_uploaded_file)
            ],
        },
        fallbacks=[ CommandHandler("cancel", 
            cancel), 
            MessageHandler(filters.Regex("^❌ 
            لغو$"), cancel)
        ], )
    
    # ConversationHandler برای اضافه کردن رکورد
    add_record_handler = ConversationHandler( 
        entry_points=[MessageHandler(filters.Regex("^➕ 
        اضافه کردن$"), add_record_start)], 
        states={
            ADD_DATA: 
            [MessageHandler(filters.TEXT & 
            ~filters.COMMAND, 
            add_record_process)],
        },
        fallbacks=[CommandHandler("cancel", 
        cancel), 
        MessageHandler(filters.Regex("^❌ لغو$"), 
        cancel)],
    )
    
    # ConversationHandler برای ویرایش رکورد
    edit_record_handler = ConversationHandler( 
        entry_points=[MessageHandler(filters.Regex("^✏️ 
        ویرایش$"), edit_start)], states={
            EDIT_ROW: 
            [MessageHandler(filters.TEXT & 
            ~filters.COMMAND, edit_row_select)], 
            EDIT_FIELD: 
            [MessageHandler(filters.TEXT & 
            ~filters.COMMAND, 
            edit_field_select)], EDIT_VALUE: 
            [MessageHandler(filters.TEXT & 
            ~filters.COMMAND, edit_value_apply)],
        },
        fallbacks=[CommandHandler("cancel", 
        cancel), 
        MessageHandler(filters.Regex("^❌ لغو$"), 
        cancel)],
    )
    
    # ConversationHandler برای حذف رکورد
    delete_record_handler = ConversationHandler( 
        entry_points=[MessageHandler(filters.Regex("^🗑️ 
        حذف$"), delete_start)], states={
            DELETE_ROW: 
            [MessageHandler(filters.TEXT & 
            ~filters.COMMAND, delete_confirm)],
        },
        fallbacks=[CommandHandler("cancel", 
        cancel), 
        MessageHandler(filters.Regex("^❌ لغو$"), 
        cancel)],
    )
    
    # ConversationHandler برای جستجو
    search_handler = ConversationHandler( 
        entry_points=[MessageHandler(filters.Regex("^🔍 
        جستجو$"), search_start)], states={
            SEARCH_FIELD: 
            [MessageHandler(filters.TEXT & 
            ~filters.COMMAND, 
            search_field_select)], SEARCH_VALUE: 
            [MessageHandler(filters.TEXT & 
            ~filters.COMMAND, search_process)],
        },
        fallbacks=[CommandHandler("cancel", 
        cancel), 
        MessageHandler(filters.Regex("^❌ لغو$"), 
        cancel)],
    )
    
    # ConversationHandler برای مدیریت فیلدها
    field_management_handler = 
    ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^⚙️ 
        مدیریت فیلدها$"), 
        field_management_start)], states={
            FIELD_MANAGEMENT: 
            [MessageHandler(filters.TEXT & 
            ~filters.COMMAND, 
            field_management_handle)], ADD_FIELD: 
            [MessageHandler(filters.TEXT & 
            ~filters.COMMAND, 
            add_field_process)], DELETE_FIELD: 
            [MessageHandler(filters.TEXT & 
            ~filters.COMMAND, 
            delete_field_process)],
        },
        fallbacks=[CommandHandler("cancel", 
        cancel), 
        MessageHandler(filters.Regex("^❌ لغو$"), 
        cancel)],
    )
    
    # اضافه کردن handlers
    application.add_handler(CommandHandler("start", 
    start)) 
    application.add_handler(upload_file_handler) 
    # Handler جدید آپلود فایل!
    application.add_handler(add_record_handler) 
    application.add_handler(edit_record_handler) 
    application.add_handler(delete_record_handler) 
    application.add_handler(search_handler) 
    application.add_handler(field_management_handler) 
    application.add_handler(MessageHandler(filters.TEXT 
    & ~filters.COMMAND, handle_main_menu))
    
    # شروع ربات
    print("🤖 ربات Excel مدیریت کامل در حال 
    اجرا...") print("✅ همه عملکردها فعال است:") 
    print(" • اضافه/ویرایش/حذف رکورد") print(" • 
    📤 آپلود فایل Excel (جدید!)") print(" • جستجو 
    پیشرفته") print(" • مدیریت فیلدها") print(" • 
    تم‌های رنگی") print(" • خروجی Excel زیبا") 
    print("📡 منتظر دریافت پیام...")
    
    logger.info("Bot started successfully with 
    upload feature")
    
    try: application.run_polling() except 
    KeyboardInterrupt:
        print("\n🛑 ربات توسط کاربر متوقف شد") 
        logger.info("Bot stopped by user")
    except Exception as e: print(f"❌ خطا در 
        اجرای ربات: {e}") logger.error(f"Bot 
        error: {e}")
# ============================ توابع اضافی مدیریت 
# فیلدها ============================
async def field_management_handle(update: Update, 
context: ContextTypes.DEFAULT_TYPE):
    """مدیریت عملیات فیلدها""" text = 
    update.message.text
    
    if text == "➕ اضافه کردن فیلد": await 
        update.message.reply_text("📝 **نام فیلد 
        جدید را وارد کنید:**") return ADD_FIELD
    elif text == "🗑️ حذف فیلد": return await 
        delete_field_start(update, context)
    elif text == "📋 نمایش فیلدها": return await 
        show_fields(update, context)
    elif text == "🔄 بازگشت به پیش‌فرض": return 
        await reset_fields(update, context)
    elif text == "🏠 بازگشت به منوی اصلی": await 
        update.message.reply_text("🏠 بازگشت به 
        منوی اصلی", reply_markup=get_keyboard()) 
        return ConversationHandler.END
    else: await update.message.reply_text("❌ 
        گزینه نامعتبر") return FIELD_MANAGEMENT
async def add_field_process(update: Update, 
context: ContextTypes.DEFAULT_TYPE):
    """اضافه کردن فیلد جدید""" try: new_field = 
        update.message.text.strip()
        
        if not new_field: await 
            update.message.reply_text("❌ نام 
            فیلد نمی‌تواند خالی باشد:") return 
            ADD_FIELD
        
        fields = load_fields()
        
        if new_field in fields: await 
            update.message.reply_text("❌ این 
            فیلد از قبل موجود است:") return 
            ADD_FIELD
        
        fields.append(new_field)
        
        if save_fields(fields):
            # اضافه کردن ستون جدید به فایل Excel 
            # موجود
            if os.path.exists(EXCEL_FILE) and 
            os.path.getsize(EXCEL_FILE) > 0:
                df = pd.read_excel(EXCEL_FILE) if 
                new_field not in df.columns:
                    df[new_field] = "" user_theme 
                    = 
                    load_user_theme(update.effective_user.id) 
                    create_excel(df, user_theme)
            
            await update.message.reply_text( f"✅ 
                **فیلد '{new_field}' با موفقیت 
                اضافه شد!**", 
                reply_markup=get_keyboard()
            ) logger.info(f"User 
            {update.effective_user.id} added 
            field: {new_field}")
        else: await update.message.reply_text("❌ 
            خطا در ذخیره فیلد.", 
            reply_markup=get_keyboard())
        
    except Exception as e: logger.error(f"Error 
        adding field: {e}") await 
        update.message.reply_text("❌ خطا در 
        اضافه کردن فیلد.", 
        reply_markup=get_keyboard())
    
    return ConversationHandler.END async def 
delete_field_start(update: Update, context: 
ContextTypes.DEFAULT_TYPE):
    """شروع حذف فیلد""" fields = load_fields()
    
    if len(fields) <= 1: await 
        update.message.reply_text("❌ نمی‌توان همه 
        فیلدها را حذف کرد. حداقل یک فیلد باید 
        باقی بماند.") return FIELD_MANAGEMENT
    
    keyboard = [[KeyboardButton(field)] for field 
    in fields] 
    keyboard.append([KeyboardButton("❌ لغو")])
    
    await update.message.reply_text( "🗑️ **کدام 
        فیلد حذف شود؟**\n⚠️ توجه: تمام داده‌های این 
        فیلد پاک خواهد شد!", 
        reply_markup=ReplyKeyboardMarkup(keyboard, 
        resize_keyboard=True)
    ) return DELETE_FIELD async def 
delete_field_process(update: Update, context: 
ContextTypes.DEFAULT_TYPE):
    """حذف فیلد""" try: field_to_delete = 
        update.message.text
        
        if field_to_delete == "❌ لغو": await 
            update.message.reply_text("❌ حذف 
            فیلد لغو شد.", 
            reply_markup=get_keyboard()) return 
            ConversationHandler.END
        
        fields = load_fields()
        
        if field_to_delete not in fields: await 
            update.message.reply_text("❌ فیلد 
            نامعتبر است.") return DELETE_FIELD
        
        if len(fields) <= 1: await 
            update.message.reply_text("❌ نمی‌توان 
            آخرین فیلد را حذف کرد.") return 
            DELETE_FIELD
        
        fields.remove(field_to_delete)
        
        if save_fields(fields):
            # حذف ستون از فایل Excel
            if os.path.exists(EXCEL_FILE) and 
            os.path.getsize(EXCEL_FILE) > 0:
                df = pd.read_excel(EXCEL_FILE) if 
                field_to_delete in df.columns:
                    df = 
                    df.drop(columns=[field_to_delete]) 
                    user_theme = 
                    load_user_theme(update.effective_user.id) 
                    create_excel(df, user_theme)
            
            await update.message.reply_text( f"✅ 
                **فیلد '{field_to_delete}' با 
                موفقیت حذف شد!**", 
                reply_markup=get_keyboard()
            ) logger.info(f"User 
            {update.effective_user.id} deleted 
            field: {field_to_delete}")
        else: await update.message.reply_text("❌ 
            خطا در حذف فیلد.", 
            reply_markup=get_keyboard())
        
    except Exception as e: logger.error(f"Error 
        deleting field: {e}") await 
        update.message.reply_text("❌ خطا در حذف 
        فیلد.", reply_markup=get_keyboard())
    
    return ConversationHandler.END async def 
show_fields(update: Update, context: 
ContextTypes.DEFAULT_TYPE):
    """نمایش فیلدها""" fields = load_fields()
    
    msg = f"📋 **فیلدهای موجود ({len(fields)} 
    فیلد):**\n\n" for i, field in 
    enumerate(fields, 1):
        msg += f" {i}. {field}\n"
    
    await update.message.reply_text(msg) return 
    FIELD_MANAGEMENT
async def reset_fields(update: Update, context: 
ContextTypes.DEFAULT_TYPE):
    """بازگشت به فیلدهای پیش‌فرض""" try: if 
        save_fields(DEFAULT_FIELDS):
            await update.message.reply_text( "🔄 
                **فیلدها به حالت پیش‌فرض بازگشت 
                داده شد!**\n" f"📊 
                {len(DEFAULT_FIELDS)} فیلد پیش‌فرض 
                بارگذاری شد.", 
                reply_markup=get_keyboard()
            ) logger.info(f"User 
            {update.effective_user.id} reset 
            fields to default")
        else:
     
