import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes
)
from apscheduler.schedulers.background import BackgroundScheduler
import datetime

TOKEN = "7793377477:AAHyiIlhC9DRUpr8WCc2LndGMJ6tp2RE86w"  # Reemplaza esto con tu token real

reportes = []

# Lista de palabras ofensivas (puedes ampliarla)
palabras_prohibidas = ['grosería1', 'grosería2', 'idiota', 'hp', 'malparido']

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
    if not texto:
        await update.message.reply_text("❗ Escribe el mensaje después de /reporte")
        return

    texto_lower = texto.lower()
    if any(palabra in texto_lower for palabra in palabras_prohibidas):
        await update.message.reply_text("⚠️ Tu reporte contiene lenguaje inapropiado. Intenta escribirlo de forma respetuosa.")
        return

    reportes.append(texto)
    await update.message.reply_text(f"✅ Reporte recibido: {texto}")

async def estado(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if reportes:
        ultimos = '\n- '.join(reportes[-5:])
        await update.message.reply_text(f"📢 Últimos reportes:\n- {ultimos}")
    else:
        await update.message.reply_text("📭 No hay reportes aún.")

def limpiar_reportes():
    print(f"🧹 Limpiando reportes a las {datetime.datetime.now()}")
    reportes.clear()

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reporte", reporte))
    app.add_handler(CommandHandler("estado", estado))

    # Programar limpieza diaria a las 23:59
    scheduler = BackgroundScheduler(timezone="America/Bogota")
    scheduler.add_job(limpiar_reportes, trigger='cron', hour=23, minute=59)
    scheduler.start()

    print("✅ Bot en línea. Presiona Ctrl+C para detenerlo.")
    app.run_polling()

if __name__ == '__main__':
    main()
