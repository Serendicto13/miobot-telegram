import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes
)

TOKEN = "7793377477:AAHyiIlhC9DRUpr8WCc2LndGMJ6tp2RE86w"

reportes = []

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 ¡Hola! Soy MIOBot. Usa /reporte para enviar un aviso y /estado para ver los últimos reportes."
    )

async def reporte(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = ' '.join(context.args)
    if texto:
        reportes.append(texto)
        await update.message.reply_text(f"✅ Reporte recibido: {texto}")
    else:
        await update.message.reply_text("❗ Escribe el mensaje después de /reporte")

async def estado(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if reportes:
        ultimos = '\n- '.join(reportes[-5:])
        await update.message.reply_text(f"📢 Últimos reportes:\n- {ultimos}")
    else:
        await update.message.reply_text("📭 No hay reportes aún.")

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reporte", reporte))
    app.add_handler(CommandHandler("estado", estado))

    print("✅ Bot en línea. Presiona Ctrl+C para detenerlo.")
    app.run_polling()

if __name__ == '__main__':
    main()
