from flask import Flask, request, send_file
from telebot import TeleBot, types
import qrcode
from io import BytesIO
from threading import Thread

BOT_TOKEN = "7991315018:AAE-CxNwnRGYYmufSZJ0tO81RVgrFiHJe7o"
UPI_ID = "darkespytk@ibl"

bot = TeleBot(BOT_TOKEN)
app = Flask(__name__)

@app.route('/generate', methods=['GET'])
def generate_qr():
    amount = request.args.get('amount', default="100", type=str)
    upi_link = f"upi://pay?pa={UPI_ID}&pn=DARKESPYT&am={amount}&tn=Payment for services"
    qr = qrcode.QRCode()
    qr.add_data(upi_link)
    qr.make(fit=True)
    img = qr.make_image(fill="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return send_file(buffer, mimetype="image/png", as_attachment=False, download_name="upi_qr.png")

@bot.inline_handler(lambda query: query.query.strip().isdigit())
def inline_query_handler(inline_query):
    amount = inline_query.query.strip()
    qr_url = f"http://127.0.0.1:5000/generate?amount={amount}"
    results = [
        types.InlineQueryResultPhoto(
            id="1",
            photo_url=qr_url,
            thumbnail_url=qr_url,
            caption=f"Pay ₹{amount} using this QR code."
        )
    ]
    bot.answer_inline_query(inline_query.id, results)

@bot.inline_handler(lambda query: not query.query.strip().isdigit())
def inline_query_invalid_handler(inline_query):
    results = [
        types.InlineQueryResultArticle(
            id="1",
            title="Enter a valid amount",
            input_message_content=types.InputTextMessageContent(
                "Please enter a numeric amount to generate a QR code."
            )
        )
    ]
    bot.answer_inline_query(inline_query.id, results)

def run_flask():
    app.run(host="0.0.0.0", port=5000)

if __name__ == "__main__":
    flask_thread = Thread(target=run_flask)
    flask_thread.start()
    bot.infinity_polling()
