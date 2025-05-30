#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
فایل تنظیمات ربات Excel
"""

# توکن ربات تلگرام - توکن خود را اینجا وارد کنید
TOKEN = "6677631238:AAFFdIDAUrR9FJEJsXjTYoTZQJ-VAUuDYYw"

# نام فایل های سیستم
EXCEL_FILE = "data.xlsx"
FIELDS_FILE = "fields.json"

# فیلدهای پیش فرض
DEFAULT_FIELDS = [
    "نام",
    "نام خانوادگی", 
    "سن",
    "شغل",
    "کد ملی",
    "شماره تلفن",
    "ایمیل",
    "کد پستی",
    "آدرس منزل",
    "شماره کارت بانکی",
    "تاریخ تولد",
    "وضعیت تاهل"
]

# تم های رنگی برای Excel
THEMES = {
    "blue": {
        "name": "آبی", 
        "header": "1F4E79", 
        "row1": "D9E2F3", 
        "row2": "F2F2F2"
    },
    "green": {
        "name": "سبز", 
        "header": "0D5016", 
        "row1": "E2F0D9", 
        "row2": "F2F2F2"
    },
    "purple": {
        "name": "بنفش", 
        "header": "5B2C87", 
        "row1": "E6D7F0", 
        "row2": "F2F2F2"
    },
    "red": {
        "name": "قرمز", 
        "header": "C5504B", 
        "row1": "F2D7D5", 
        "row2": "F2F2F2"
    },
    "orange": {
        "name": "نارنجی", 
        "header": "D68910", 
        "row1": "FCF3CF", 
        "row2": "F2F2F2"
    }
}

# States برای ConversationHandler
ADD_DATA = 0
EDIT_ROW = 1
EDIT_FIELD = 2
EDIT_VALUE = 3
DELETE_ROW = 4
SEARCH_FIELD = 5
SEARCH_VALUE = 6
FIELD_MANAGEMENT = 7
ADD_FIELD = 8
DELETE_FIELD = 9
CONFIRM_DELETE_ALL = 10

# تنظیمات لاگینگ
LOG_FILE = "bot.log"
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# حداکثر تعداد رکورد برای نمایش
MAX_DISPLAY_RECORDS = 10

# حداکثر تعداد نتایج جستجو
MAX_SEARCH_RESULTS = 5
