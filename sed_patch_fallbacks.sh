#!/bin/bash
# ✅ Append universal_fallback function to end of main2.py
echo '
# Universal Fallback Handler
async def universal_fallback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❌ خطا در درک دستور!\n🏠 بازگشت به منوی اصلی...",
        reply_markup=get_keyboard()
    )
    context.user_data.clear()
    return ConversationHandler.END
' >> /root/aragon/main2.py

# ✅ Add fallback handler to all ConversationHandlers in main2.py
sed -i '/fallbacks=\[/,/\]/s/\]/    MessageHandler(filters.ALL, universal_fallback)\n        ]/' /root/aragon/main2.py
