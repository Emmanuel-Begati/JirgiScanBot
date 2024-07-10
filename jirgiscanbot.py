from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackContext, ConversationHandler
import requests
from datetime import datetime, timedelta

TELEGRAM_BOT_TOKEN = '7020624033:AAHN3-LcSxSz4yLQ9qppXJqf_n4UoPimxYk'
RAPIDAPI_KEY = '41c04622dfmshd82d138a82f6e0cp140b66jsn6dad2c4c4dce'

# Define conversation states
ORIGIN, DESTINATION, DATE = range(3)

async def start(update: Update, context: CallbackContext):
    await update.message.reply_text('Welcome to Flight Finder Bot! Let\'s start searching for flights. Please enter your origin city:')
    return ORIGIN

async def get_origin(update: Update, context: CallbackContext):
    context.user_data['origin'] = update.message.text
    await update.message.reply_text('Great! Now, please enter your destination city:')
    return DESTINATION

async def get_destination(update: Update, context: CallbackContext):
    context.user_data['destination'] = update.message.text
    await update.message.reply_text('Perfect! Finally, please enter your preferred travel date in YYYY-MM-DD format:')
    return DATE

async def get_date(update: Update, context: CallbackContext):
    context.user_data['date'] = update.message.text
    await update.message.reply_text('Thank you! I\'m now searching for the best flights within a 7-day range. Please wait...')
    
    flight_info = get_flight_info(context.user_data['origin'], context.user_data['destination'], context.user_data['date'])
    await update.message.reply_text(flight_info)
    return ConversationHandler.END

def get_flight_info(origin, destination, date):
    try:
        base_date = datetime.strptime(date, "%Y-%m-%d")
        date_range = [base_date + timedelta(days=i) for i in range(-7, 8)]
        
        cheapest_flight = None
        cheapest_price = float('inf')
        
        for search_date in date_range:
            url = "https://skyscanner44.p.rapidapi.com/search"
            params = {
                "origin": origin,
                "destination": destination,
                "date": search_date.strftime("%Y-%m-%d"),
                "adults": 1,
                "currency": "USD"
            }
            headers = {
                "X-RapidAPI-Key": RAPIDAPI_KEY,
                "X-RapidAPI-Host": "skyscanner44.p.rapidapi.com"
            }
            response = requests.get(url, params=params, headers=headers)
            data = response.json()

            if data.get('quotes'):
                flight = min(data['quotes'], key=lambda x: x['minPrice'])
                if flight['minPrice'] < cheapest_price:
                    cheapest_flight = flight
                    cheapest_price = flight['minPrice']
                    cheapest_date = search_date

        if cheapest_flight:
            carrier = cheapest_flight['carriers'][0]['name']
            return f'Cheapest flight found:\nCarrier: {carrier}\nPrice: ${cheapest_price}\nDate: {cheapest_date.strftime("%Y-%m-%d")}'
        else:
            return 'No flights found within the specified date range.'
    
    except Exception as e:
        return f"An error occurred while searching for flights: {str(e)}"

def main():
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            ORIGIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_origin)],
            DESTINATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_destination)],
            DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_date)],
        },
        fallbacks=[],
    )

    application.add_handler(conv_handler)

    application.run_polling()

if __name__ == '__main__':
    main()