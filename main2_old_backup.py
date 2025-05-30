#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" ربات مدیریت Excel پیشرفته - قسمت دوم نسخه 2.1 
- با قابلیت آپلود فایل Excel کامل """ import 
logging from telegram import Update from 
telegram.ext import ApplicationBuilder, 
CommandHandler, MessageHandler, ContextTypes, 
ConversationHandler, filters, 
CallbackQueryHandler
# وارد کردن فایل‌های سیستم
from config import * from utils import *
# Import کردن همه توابع از main1
from main1 import ( start, get_keyboard, 
    add_record_start, add_record_process, 
    show_all_records, send_excel_file, 
    edit_start, edit_row_select, 
    edit_field_select, edit_value_apply, cancel, 
    upload_file_start, upload_file_process, 
    handle_uploaded_file, logger
)
# States for conversation handlers
ADD_DATA = 1 EDIT_ROW = 2 EDIT_FIELD = 3 
EDIT_VALUE = 4 DELETE_ROW = 5 SEARCH_QUERY = 6 
MANAGE_FIELDS = 7 ADD_FIELD = 8 
DELETE_FIELD_SELECT = 9 CHANGE_THEME = 10 
UPLOAD_FILE = 11
# ============================ حذف رکورد 
# ============================
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
async def delete_row_process(update: Update, 
context: ContextTypes.DEFAULT_TYPE):
    """پردازش حذف رکورد""" try: row_num = 
        int(update.message.text) - 1 df = 
        pd.read_excel(EXCEL_FILE)
        
        if row_num < 0 or row_num >= len(df): 
            await update.message.reply_text("❌ 
            شماره ردیف نامعتبر است.") return 
            DELETE_ROW
        
        deleted_name = 
        clean_value(df.iloc[row_num].get('نام', 
        f'ردیف {row_num+1}')) df = 
        df.drop(df.index[row_num]).reset_index(drop=True)
        
        user_theme = 
        load_user_theme(update.effective_user.id) 
        if create_excel(df, user_theme):
            await update.message.reply_text( f"✅ 
                رکورد **{deleted_name}** با 
                موفقیت حذف شد!", 
                reply_markup=get_keyboard()
            ) logger.info(f"User 
            {update.effective_user.id} deleted 
            record: {deleted_name}")
        else: raise Exception("Error creating 
            Excel file")
            
    except ValueError: await 
        update.message.reply_text("❌ لطفاً یک عدد 
        معتبر وارد کنید.") return DELETE_ROW
    except Exception as e: logger.error(f"Error 
        in delete_row_process: {e}") await 
        update.message.reply_text("❌ خطا در حذف 
        رکورد.", reply_markup=get_keyboard())
    
    return ConversationHandler.END
# ============================ جستجو 
# ============================
async def search_start(update: Update, context: 
ContextTypes.DEFAULT_TYPE):
    """شروع جستجو""" await 
    update.message.reply_text("🔍 **کلمه کلیدی 
    جستجو را وارد کنید:**") return SEARCH_QUERY
async def search_process(update: Update, context: 
ContextTypes.DEFAULT_TYPE):
    """پردازش جستجو""" try: query = 
        update.message.text.strip().lower()
        
        if not query: await 
            update.message.reply_text("❌ لطفاً 
            کلمه کلیدی وارد کنید.") return 
            SEARCH_QUERY
        
        ensure_excel_file() if not 
        os.path.exists(EXCEL_FILE) or 
        os.path.getsize(EXCEL_FILE) == 0:
            await update.message.reply_text("📭 
            هیچ رکوردی برای جستجو وجود ندارد.", 
            reply_markup=get_keyboard()) return 
            ConversationHandler.END
        
        df = pd.read_excel(EXCEL_FILE) results = 
        df[df.astype(str).apply(lambda x: 
        x.str.lower().str.contains(query, 
        na=False)).any(axis=1)]
        
        if results.empty: await 
            update.message.reply_text(f"❌ هیچ 
            نتیجه‌ای برای «{query}» یافت نشد.", 
            reply_markup=get_keyboard())
        else: message = 
            format_record_display(results, 
            MAX_DISPLAY_RECORDS, f"🔍 نتایج جستجو 
            برای «{query}»:") await 
            update.message.reply_text(message, 
            reply_markup=get_keyboard())
        
    except Exception as e: logger.error(f"Error 
        in search_process: {e}") await 
        update.message.reply_text("❌ خطا در 
        جستجو.", reply_markup=get_keyboard())
    
    return ConversationHandler.END
# ============================ مدیریت فیلدها 
# ============================
async def manage_fields_start(update: Update, 
context: ContextTypes.DEFAULT_TYPE):
    """شروع مدیریت فیلدها""" fields = 
    load_fields() keyboard = [
        ["➕ اضافه کردن فیلد جدید"], ["🗑️ حذف فیلد 
        موجود"], ["📋 نمایش فیلدهای فعلی"], ["❌ 
        بازگشت"]
    ]
    
    msg = f"⚙️ **مدیریت فیلدها**\n\n📋 **فیلدهای 
    فعلی:** ({len(fields)} عدد)\n" for i, field 
    in enumerate(fields, 1):
        msg += f"{i}. {field}\n"
    
    from telegram import ReplyKeyboardMarkup 
    await update.message.reply_text(msg, 
    reply_markup=ReplyKeyboardMarkup(keyboard, 
    resize_keyboard=True)) return MANAGE_FIELDS
async def manage_fields_process(update: Update, 
context: ContextTypes.DEFAULT_TYPE):
    """پردازش مدیریت فیلدها""" text = 
    update.message.text
    
    if text == "❌ بازگشت": await 
        update.message.reply_text("🏠 بازگشت به 
        منوی اصلی", reply_markup=get_keyboard()) 
        return ConversationHandler.END
    elif text == "➕ اضافه کردن فیلد جدید": await 
        update.message.reply_text("📝 **نام فیلد 
        جدید را وارد کنید:**") return ADD_FIELD
    elif text == "🗑️ حذف فیلد موجود": fields = 
        load_fields() if len(fields) <= 1:
            await update.message.reply_text("❌ 
            نمی‌توان همه فیلدها را حذف کرد.") 
            return MANAGE_FIELDS
        
        keyboard = [[field] for field in fields] 
        keyboard.append(["❌ لغو"]) from telegram 
        import ReplyKeyboardMarkup await 
        update.message.reply_text(
            "🗑️ **فیلد مورد نظر برای حذف:**", 
            reply_markup=ReplyKeyboardMarkup(keyboard, 
            resize_keyboard=True)
        ) return DELETE_FIELD_SELECT elif text == 
    "📋 نمایش فیلدهای فعلی":
        fields = load_fields() msg = f"📋 
        **فیلدهای فعلی:** ({len(fields)} 
        عدد)\n\n" for i, field in 
        enumerate(fields, 1):
            msg += f"{i}. {field}\n" await 
        update.message.reply_text(msg) return 
        MANAGE_FIELDS
    else: await update.message.reply_text("❌ 
        گزینه نامعتبر است.") return MANAGE_FIELDS
async def add_field_process(update: Update, 
context: ContextTypes.DEFAULT_TYPE):
    """اضافه کردن فیلد جدید""" try: new_field = 
        update.message.text.strip()
        
        if not new_field: await 
            update.message.reply_text("❌ نام 
            فیلد نمی‌تواند خالی باشد.") return 
            ADD_FIELD
        
        fields = load_fields() if new_field in 
        fields:
            await update.message.reply_text("❌ 
            این فیلد قبلاً وجود دارد.") return 
            ADD_FIELD
        
        fields.append(new_field) 
        save_fields(fields)
        
        # اضافه کردن ستون جدید به فایل Excel
        if os.path.exists(EXCEL_FILE) and 
        os.path.getsize(EXCEL_FILE) > 0:
            df = pd.read_excel(EXCEL_FILE) 
            df[new_field] = "" user_theme = 
            load_user_theme(update.effective_user.id) 
            create_excel(df, user_theme)
        
        await update.message.reply_text( f"✅ 
            فیلد **{new_field}** با موفقیت اضافه 
            شد!", reply_markup=get_keyboard()
        ) logger.info(f"User 
        {update.effective_user.id} added field: 
        {new_field}")
        
    except Exception as e: logger.error(f"Error 
        adding field: {e}") await 
        update.message.reply_text("❌ خطا در 
        اضافه کردن فیلد.", 
        reply_markup=get_keyboard())
    
    return ConversationHandler.END async def 
delete_field_process(update: Update, context: 
ContextTypes.DEFAULT_TYPE):
    """حذف فیلد""" try: field_to_delete = 
        update.message.text
        
        if field_to_delete == "❌ لغو": await 
            update.message.reply_text("❌ حذف 
            فیلد لغو شد.", 
            reply_markup=get_keyboard()) return 
            ConversationHandler.END
        
        fields = load_fields() if field_to_delete 
        not in fields:
            await update.message.reply_text("❌ 
            فیلد نامعتبر است.") return 
            DELETE_FIELD_SELECT
        
        if len(fields) <= 1: await 
            update.message.reply_text("❌ نمی‌توان 
            آخرین فیلد را حذف کرد.", 
            reply_markup=get_keyboard()) return 
            ConversationHandler.END
        
        fields.remove(field_to_delete) 
        save_fields(fields)
        
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
            فیلد **{field_to_delete}** با موفقیت 
            حذف شد!", reply_markup=get_keyboard()
        ) logger.info(f"User 
        {update.effective_user.id} deleted field: 
        {field_to_delete}")
        
    except Exception as e: logger.error(f"Error 
        deleting field: {e}") await 
        update.message.reply_text("❌ خطا در حذف 
        فیلد.", reply_markup=get_keyboard())
    
    return ConversationHandler.END
# ============================ تغییر تم 
# ============================
async def change_theme_start(update: Update, 
context: ContextTypes.DEFAULT_TYPE):
    """شروع تغییر تم""" current_theme = 
    load_user_theme(update.effective_user.id) 
    keyboard = []
    
    for theme_key, theme_data in THEMES.items(): 
        status = "✅" if theme_key == 
        current_theme else "⚪" 
        keyboard.append([f"{status} 
        {theme_data['name']}"])
    
    keyboard.append(["❌ لغو"])
    
    msg = f"🎨 **انتخاب تم رنگی:**\n\n🎯 **تم 
    فعلی:** {THEMES[current_theme]['name']}"
    
    from telegram import ReplyKeyboardMarkup 
    await update.message.reply_text(msg, 
    reply_markup=ReplyKeyboardMarkup(keyboard, 
    resize_keyboard=True)) return CHANGE_THEME
async def change_theme_process(update: Update, 
context: ContextTypes.DEFAULT_TYPE):
    """پردازش تغییر تم""" try: text = 
        update.message.text
        
        if text == "❌ لغو": await 
            update.message.reply_text("❌ تغییر 
            تم لغو شد.", 
            reply_markup=get_keyboard()) return 
            ConversationHandler.END
        
        # یافتن تم انتخاب شده
        selected_theme = None for theme_key, 
        theme_data in THEMES.items():
            if theme_data['name'] in text: 
                selected_theme = theme_key break
        
        if not selected_theme: await 
            update.message.reply_text("❌ تم 
            نامعتبر است.") return CHANGE_THEME
        
        # ذخیره تم جدید
        save_user_theme(update.effective_user.id, 
        selected_theme)
        
        # اعمال تم به فایل موجود
        if os.path.exists(EXCEL_FILE) and 
        os.path.getsize(EXCEL_FILE) > 0:
            df = pd.read_excel(EXCEL_FILE) 
            create_excel(df, selected_theme)
        
        await update.message.reply_text( f"✅ تم 
            به 
            **{THEMES[selected_theme]['name']}** 
            تغییر یافت! 🎨", 
            reply_markup=get_keyboard()
        ) logger.info(f"User 
        {update.effective_user.id} changed theme 
        to: {selected_theme}")
        
    except Exception as e: logger.error(f"Error 
        changing theme: {e}") await 
        update.message.reply_text("❌ خطا در 
        تغییر تم.", reply_markup=get_keyboard())
    
    return ConversationHandler.END
# ============================ آمار 
# ============================
async def show_statistics(update: Update, 
context: ContextTypes.DEFAULT_TYPE):
    """نمایش آمار""" try: ensure_excel_file()
        
        if not os.path.exists(EXCEL_FILE) or 
        os.path.getsize(EXCEL_FILE) == 0:
            await update.message.reply_text("📭 
            هیچ داده‌ای برای نمایش آمار وجود 
            ندارد.") return
        
        df = pd.read_excel(EXCEL_FILE) fields = 
        load_fields() user_theme = 
        load_user_theme(update.effective_user.id)
        
        # محاسبه آمار پایه
        total_records = len(df) total_fields = 
        len(fields) file_size = 
        os.path.getsize(EXCEL_FILE) / 1024 # KB
        
        # آمار فیلدها
        field_stats = {} for field in fields: if 
            field in df.columns:
                non_empty = 
                df[field].astype(str).str.strip().ne('').sum() 
                field_stats[field] = {
                    'filled': non_empty, 
                    'percentage': (non_empty / 
                    total_records * 100) if 
                    total_records > 0 else 0
                }
        
        msg = f"""📊 **آمار و اطلاعات** 📋 **آمار 
کلی:** • تعداد رکوردها: {total_records:,} • تعداد 
فیلدها: {total_fields} • حجم فایل: 
{file_size:.1f} کیلوبایت • تم فعال: 
{THEMES[user_theme]['name']} 📈 **آمار 
فیلدها:**"""
        for field, stats in field_stats.items(): 
            percentage = stats['percentage'] 
            filled = stats['filled'] bar = "█" * 
            int(percentage // 10) + "░" * (10 - 
            int(percentage // 10)) msg += f"\n• 
            {field}: {filled}/{total_records} 
            ({percentage:.0f}%) {bar}"
        
        await update.message.reply_text(msg)
        
    except Exception as e: logger.error(f"Error 
        showing statistics: {e}") await 
        update.message.reply_text("❌ خطا در 
        نمایش آمار.")
# ============================ حذف همه رکوردها 
# ============================
async def delete_all_records(update: Update, 
context: ContextTypes.DEFAULT_TYPE):
    """حذف همه رکوردها""" try: 
        ensure_excel_file()
        
        if not os.path.exists(EXCEL_FILE) or 
        os.path.getsize(EXCEL_FILE) == 0:
            await update.message.reply_text("📭 
            هیچ رکوردی برای حذف وجود ندارد.") 
            return
        
        keyboard = [ ["✅ بله، همه را حذف کن"], 
            ["❌ لغو"]
        ]
        
        from telegram import ReplyKeyboardMarkup 
        await update.message.reply_text(
            "⚠️ **هشدار!**\n\n" "آیا مطمئن هستید 
            که می‌خواهید **همه رکوردها** را حذف 
            کنید؟\n" "این عمل غیرقابل بازگشت 
            است!", 
            reply_markup=ReplyKeyboardMarkup(keyboard, 
            resize_keyboard=True)
        )
        
    except Exception as e: logger.error(f"Error 
        in delete_all_records: {e}") await 
        update.message.reply_text("❌ خطا در 
        دسترسی به فایل.")
async def confirm_delete_all(update: Update, 
context: ContextTypes.DEFAULT_TYPE):
    """تایید حذف همه رکوردها""" try: text = 
        update.message.text
        
        if text == "❌ لغو": await 
            update.message.reply_text("❌ حذف همه 
            رکوردها لغو شد.", 
            reply_markup=get_keyboard()) return
        elif text == "✅ بله، همه را حذف کن":
            # ایجاد فایل خالی با فیلدهای موجود
            fields = load_fields() empty_df = 
            pd.DataFrame(columns=fields) 
            user_theme = 
            load_user_theme(update.effective_user.id)
            
            if create_excel(empty_df, 
            user_theme):
                await update.message.reply_text( 
                    "✅ همه رکوردها با موفقیت حذف 
                    شدند! 🧹", 
                    reply_markup=get_keyboard()
                ) logger.info(f"User 
                {update.effective_user.id} 
                deleted all records")
            else: raise Exception("Error creating 
                empty Excel file")
        else: await update.message.reply_text("❌ 
            گزینه نامعتبر است.")
            
    except Exception as e: logger.error(f"Error 
        in confirm_delete_all: {e}") await 
        update.message.reply_text("❌ خطا در حذف 
        رکوردها.", reply_markup=get_keyboard())
# ============================ راهنما 
# ============================
async def show_help(update: Update, context: 
ContextTypes.DEFAULT_TYPE):
    """نمایش راهنما""" help_text = """ℹ️ **راهنمای 
    کامل ربات**
🔧 **عملیات اصلی:** • **➕ اضافه کردن:** افزودن 
رکورد جدید • **📋 نمایش همه:** مشاهده تمام 
رکوردها • **📁 دریافت فایل:** دانلود فایل Excel ✏️ 
**ویرایش و مدیریت:** • **✏️ ویرایش:** تغییر 
اطلاعات رکورد • **🗑️ حذف:** حذف رکورد منتخب • **🔍 
جستجو:** یافتن رکوردهای مشخص 📤 **آپلود فایل 
(جدید!):** • آپلود فایل Excel دلخواه • دو حالت: 
جایگزینی یا ادغام • پشتیبانی از فرمت .xlsx و .xls 
⚙️ **تنظیمات پیشرفته:** • **⚙️ مدیریت فیلدها:** 
اضافه/حذف ستون‌ها • **🎨 تغییر تم:** انتخاب 
رنگ‌بندی Excel • **📊 آمار:** مشاهده اطلاعات آماری 
• **🧹 حذف همه:** پاک کردن تمام داده‌ها 💡 **نکات 
مفید:** • فایل‌های Excel با رنگ‌بندی زیبا تولید 
می‌شوند • تمام عملیات لاگ می‌شوند • امکان جستجو در 
تمام فیلدها • پشتیبانی کامل از زبان فارسی ❓ 
**سوال دارید؟** از /start شروع کنید!"""
    await update.message.reply_text(help_text)
# ============================ Universal Fallback 
# Handler ============================
async def universal_fallback(update: Update, 
context: ContextTypes.DEFAULT_TYPE):
    """Fallback handler برای خروج از هر state 
    گیرکرده""" await update.message.reply_text(
        "❌ **خطا در درک دستور!**\n\n" "🏠 بازگشت 
        به منوی اصلی...\n" "💡 لطفاً از دکمه‌های 
        زیر استفاده کنید:", 
        reply_markup=get_keyboard()
    )
    # پاک کردن تمام user_data
    context.user_data.clear() return 
    ConversationHandler.END
# ============================ مدیریت پیام‌های 
# متنی ============================
async def handle_text_messages(update: Update, 
context: ContextTypes.DEFAULT_TYPE):
    """مدیریت پیام‌های متنی که مطابق با دکمه‌ها 
    هستند""" text = update.message.text
    
    # بررسی دقیق متن‌های آپلود فایل
    if text in ["📤 آپلود فایل Excel"]: await 
        upload_file_start(update, context)
    elif text in ["➕ اضافه کردن"]: await 
        add_record_start(update, context)
    elif text in ["📋 نمایش همه"]: await 
        show_all_records(update, context)
    elif text in ["📁 دریافت فایل"]: await 
        send_excel_file(update, context)
    elif text in ["✏️ ویرایش"]: await 
        edit_start(update, context)
    elif text in ["🗑️ حذف"]: await 
        delete_start(update, context)
    elif text in ["🔍 جستجو"]: await 
        search_start(update, context)
    elif text in ["⚙️ مدیریت فیلدها"]: await 
        manage_fields_start(update, context)
    elif text in ["🎨 تغییر تم"]: await 
        change_theme_start(update, context)
    elif text in ["📊 آمار"]: await 
        show_statistics(update, context)
    elif text in ["🧹 حذف همه"]: await 
        delete_all_records(update, context)
    elif text in ["ℹ️ راهنما"]: await 
        show_help(update, context)
    elif text in ["✅ بله، همه را حذف کن", "❌ 
    لغو"]:
        await confirm_delete_all(update, context) 
    else:
        await update.message.reply_text( "❌ 
            دستور نامعتبر است.\n💡 از منوی زیر 
            استفاده کنید:", 
            reply_markup=get_keyboard()
        )
# ============================ راه‌اندازی ربات 
# ============================
def main(): """تابع اصلی راه‌اندازی ربات"""
    
    print("🚀 راه‌اندازی ربات Excel مدیریت کامل با 
    آپلود فایل...") print("📤 قابلیت جدید: آپلود 
    فایل Excel دلخواه!") print("✅ آماده برای 
    شروع!")
    
    # ایجاد Application
    application = 
    ApplicationBuilder().token(BOT_TOKEN).build()
    
    print("🔧 در حال راه‌اندازی ربات...")
    # ConversationHandler برای اضافه کردن رکورد
    add_conversation = ConversationHandler( 
        entry_points=[
            MessageHandler(filters.Regex("^➕ 
            اضافه کردن$"), add_record_start)
        ], states={ ADD_DATA: 
            [MessageHandler(filters.TEXT & 
            ~filters.COMMAND, 
            add_record_process)]
        },
        fallbacks=[ CommandHandler("cancel", 
            cancel), MessageHandler(filters.ALL, 
            universal_fallback)
        ] )
    # ConversationHandler برای آپلود فایل
    upload_conversation = ConversationHandler( 
        entry_points=[
            MessageHandler(filters.Regex("^📤 
            آپلود فایل Excel$"), 
            upload_file_start)
        ], states={ UPLOAD_FILE: [ 
                MessageHandler(filters.TEXT & 
                ~filters.COMMAND, 
                upload_file_process), 
                MessageHandler(filters.Document.ALL, 
                handle_uploaded_file)
            ]
        },
        fallbacks=[ CommandHandler("cancel", 
            cancel), MessageHandler(filters.ALL, 
            universal_fallback)
        ] )
    # ConversationHandler برای ویرایش
    edit_conversation = ConversationHandler( 
        entry_points=[
            MessageHandler(filters.Regex("^✏️ 
            ویرایش$"), edit_start)
        ], states={ EDIT_ROW: 
            [MessageHandler(filters.TEXT & 
            ~filters.COMMAND, edit_row_select)], 
            EDIT_FIELD: 
            [MessageHandler(filters.TEXT & 
            ~filters.COMMAND, 
            edit_field_select)], EDIT_VALUE: 
            [MessageHandler(filters.TEXT & 
            ~filters.COMMAND, edit_value_apply)]
        },
        fallbacks=[ CommandHandler("cancel", 
            cancel), MessageHandler(filters.ALL, 
            universal_fallback)
        ] )
    # ConversationHandler برای حذف
    delete_conversation = ConversationHandler( 
        entry_points=[
            MessageHandler(filters.Regex("^🗑️ 
            حذف$"), delete_start)
        ], states={ DELETE_ROW: 
            [MessageHandler(filters.TEXT & 
            ~filters.COMMAND, 
            delete_row_process)]
        },
        fallbacks=[ CommandHandler("cancel", 
            cancel), MessageHandler(filters.ALL, 
            universal_fallback)
        ] )
    # ConversationHandler برای جستجو
    search_conversation = ConversationHandler( 
        entry_points=[
            MessageHandler(filters.Regex("^🔍 
            جستجو$"), search_start)
        ], states={ SEARCH_QUERY: 
            [MessageHandler(filters.TEXT & 
            ~filters.COMMAND, search_process)]
        },
        fallbacks=[ CommandHandler("cancel", 
            cancel), MessageHandler(filters.ALL, 
            universal_fallback)
        ] )
    # ConversationHandler برای مدیریت فیلدها
    manage_fields_conversation = 
    ConversationHandler(
        entry_points=[ 
            MessageHandler(filters.Regex("^⚙️ 
            مدیریت فیلدها$"), 
            manage_fields_start)
        ], states={ MANAGE_FIELDS: 
            [MessageHandler(filters.TEXT & 
            ~filters.COMMAND, 
            manage_fields_process)], ADD_FIELD: 
            [MessageHandler(filters.TEXT & 
            ~filters.COMMAND, 
            add_field_process)], 
            DELETE_FIELD_SELECT: 
            [MessageHandler(filters.TEXT & 
            ~filters.COMMAND, 
            delete_field_process)]
        },
        fallbacks=[ CommandHandler("cancel", 
            cancel), MessageHandler(filters.ALL, 
            universal_fallback)
        ] )
    # ConversationHandler برای تغییر تم
    theme_conversation = ConversationHandler( 
        entry_points=[
            MessageHandler(filters.Regex("^🎨 
            تغییر تم$"), change_theme_start)
        ], states={ CHANGE_THEME: 
            [MessageHandler(filters.TEXT & 
            ~filters.COMMAND, 
            change_theme_process)]
        },
        fallbacks=[ CommandHandler("cancel", 
            cancel), MessageHandler(filters.ALL, 
            universal_fallback)
        ] )
    # اضافه کردن تمام handler ها
    application.add_handler(CommandHandler("start", 
    start))
    
    # ConversationHandler ها - ترتیب مهم است!
    application.add_handler(upload_conversation) 
    # اول آپلود
    application.add_handler(add_conversation) # 
    بعد اضافه کردن 
    application.add_handler(edit_conversation) # 
    ویرایش 
    application.add_handler(delete_conversation) 
    # حذف
    application.add_handler(search_conversation) 
    # جستجو
    application.add_handler(manage_fields_conversation) 
    # مدیریت فیلدها
    application.add_handler(theme_conversation) # 
    تغییر تم
    # MessageHandler های تکی برای عملیات ساده
    application.add_handler(MessageHandler(filters.Regex("^📋 
    نمایش همه$"), show_all_records)) 
    application.add_handler(MessageHandler(filters.Regex("^📁 
    دریافت فایل$"), send_excel_file)) 
    application.add_handler(MessageHandler(filters.Regex("^📊 
    آمار$"), show_statistics)) 
    application.add_handler(MessageHandler(filters.Regex("^🧹 
    حذف همه$"), delete_all_records)) 
    application.add_handler(MessageHandler(filters.Regex("^ℹ️ 
    راهنما$"), show_help))
    
    # Handler کلی برای پیام‌های متنی (آخرین 
    # handler)
    application.add_handler(MessageHandler(filters.TEXT 
    & ~filters.COMMAND, handle_text_messages))
    # راه‌اندازی ربات
    print("🤖 ربات Excel مدیریت کامل در حال 
    اجرا...") print("✅ همه عملکردها فعال است:") 
    print(" • اضافه/ویرایش/حذف رکورد") print(" • 
    📤 آپلود فایل Excel") print(" • جستجو 
    پیشرفته") print(" • مدیریت فیلدها") print(" • 
    تم‌های رنگی") print(" • خروجی Excel زیبا") 
    print("📡 منتظر دریافت پیام...")
    
    try: 
    application.run_polling(drop_pending_updates=True) 
    except KeyboardInterrupt:
        print("\n⏹️ ربات متوقف شد.") except 
    Exception as e:
        print(f"❌ خطا در راه‌اندازی: {e}") 
        logger.error(f"Bot startup error: {e}")
if __name__ == "__main__":
    main()
