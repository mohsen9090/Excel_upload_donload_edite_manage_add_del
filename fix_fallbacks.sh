#!/bin/bash

# 1️⃣ حذف نسخه‌های قبلی universal_fallback
sed -i '/# Universal Fallback Handler/,$d' main2.py

# 2️⃣ اضافه کردن تابع fallback
cat << 'EOU' >> main2.py

# Universal Fallback Handler
async def universal_fallback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❌  خطا در درک دستور!\n🏠  بازگشت به منوی اصلی...",
        reply_markup=get_keyboard()
    )
    context.user_data.clear()
    return ConversationHandler.END
EOU

# 3️⃣ اصلاح fallbackها
sed -i '/fallbacks=\[/ {
    N
    s/\(\[.*\n\)/\1        MessageHandler(filters.ALL, universal_fallback),\n/
}' main2.py

# 4️⃣ حذف خط‌های تکراری universal_fallback
sed -i '/MessageHandler(filters.ALL, universal_fallback),\nMessageHandler(filters.ALL, universal_fallback),/d' main2.py

# 5️⃣ حذف کاماهای دوتایی
sed -i 's/,,/,/g' main2.py

# 6️⃣ اگر بین handlerها کامایی نیست، اضافه کن
sed -i 's/\(MessageHandler([^)]*)\)\( *MessageHandler([^)]*)\)/\1,\2/' main2.py

# 7️⃣ اصلاح MessageHandler بعد از cancel
sed -i 's/cancel) *MessageHandler/cancel), MessageHandler/' main2.py

echo "✅ تموم شد! حالا بزن: python3 main2.py"
