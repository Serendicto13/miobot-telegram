import logging
import os
import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from apscheduler.schedulers.background import BackgroundScheduler

# Lee el TOKEN desde variable de entorno para mayor seguridad
TOKEN = os.environ.get("TOKEN", "7793377477:AAHyiIlhC9DRUpr8WCc2LndGMJ6tp2RE86w")

# Lista de reportes en memoria (para demo)
reportes = []

# Palabras prohibidas para filtro simple
palabras_prohibidas = ['grosería1', 'grosería2', 'idiota', 'hp', 'malparido']

# Diccionario temporal para almacenar datos por usuario (flujo evento->estación)
user_data = {}

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# --- Handlers ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 ¡Hola! Soy MIOBot.\n"
        "Usa /reporte para enviar un aviso y /estado para ver los últimos reportes."
    )

async def estado(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if reportes:
        ultimos = '\n- '.join(reportes[-5:])
        await update.message.reply_text(f"📢 Últimos reportes:\n- {ultimos}")
    else:
        await update.message.reply_text("📭 No hay reportes aún.")

# Paso 1: Comienza el reporte mostrando botones con eventos
async def reporte(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Retraso", callback_data="evento_retraso")],
        [InlineKeyboardButton("Bloqueo", callback_data="evento_bloqueo")],
        [InlineKeyboardButton("Cierre de estación", callback_data="evento_cierre")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Selecciona el tipo de evento:", reply_markup=reply_markup)

# Paso 2: El usuario selecciona evento -> Pedimos la estación
async def button_evento(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    evento = query.data.replace("evento_", "")
    user_data[user_id] = {"evento": evento}

    await query.edit_message_text("Ahora escribe el nombre de la estación:")

# Paso 3: El usuario escribe la estación, guardamos el reporte completo
async def estacion_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    texto = update.message.text.strip()

    # Filtro de lenguaje
    texto_lower = texto.lower()
    if any(p in texto_lower for p in palabras_prohibidas):
        await update.message.reply_text("⚠️ Tu mensaje contiene lenguaje inapropiado. Por favor sé respetuoso.")
        return

    if user_id not in user_data or "evento" not in user_data[user_id]:
        await update.message.reply_text("Por favor usa /reporte para iniciar un reporte.")
        return

    evento = user_data[user_id]["evento"]
    estacion = texto

    reporte_final = f"{evento.capitalize()} en estación {estacion}"
    reportes.append(reporte_final)

    # Limpiar datos temporales
    user_data.pop(user_id)

    await update.message.reply_text(f"✅ Reporte guardado: {reporte_final}")

# Limpieza diaria de reportes
def limpiar_reportes():
    print(f"🧹 Limpiando reportes a las {datetime.datetime.now()}")
    reportes.clear()

# --- Main ---
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    # Comandos
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("estado", estado))
    app.add_handler(CommandHandler("reporte", reporte))

    # Callback para botones de evento
    app.add_handler(CallbackQueryHandler(button_evento, pattern="^evento_"))

    # Handler para recibir texto con la estación (solo cuando se espera)
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), estacion_handler))

    # Programar limpieza diaria a las 23:59 en Bogotá
    scheduler = BackgroundScheduler(timezone="America/Bogota")
    scheduler.add_job(limpiar_reportes, trigger='cron', hour=23, minute=59)
    scheduler.start()

    # Obtener puerto de Railway (o usar 8080 por defecto)
    PORT = int(os.environ.get("PORT", "8080"))
    print(f"✅ Bot en línea con webhook en puerto {PORT}")

    # URL base de Railway para webhook
    RAILWAY_URL = "https://miobot-telegram-production.up.railway.app"

    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url=f"miobot-telegram-production.up.railway.app/7793377477:AAHyiIlhC9DRUpr8WCc2LndGMJ6tp2RE86w"
    )

if __name__ == '__main__':
    main()
