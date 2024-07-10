from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackContext, ConversationHandler
import requests
from datetime import datetime, timedelta

TELEGRAM_BOT_TOKEN = '7020624033:AAHN3-LcSxSz4yLQ9qppXJqf_n4UoPimxYk'
RAPIDAPI_KEY = '41c04622dfmshd82d138a82f6e0cp140b66jsn6dad2c4c4dce'

# Define conversation states
ORIGIN, DESTINATION, DATE = range(3)

async def start(update: Update, context: CallbackContext):
    await update.message.reply_text('Welcome to Jirgi Scan Bot! Let\'s start searching for flights. Please enter your origin city:')
    return ORIGIN

async def get_origin(update: Update, context: CallbackContext):
    origin = update.message.text
    entity_id = get_entity_id(origin)
    if entity_id:
        context.user_data['origin'] = entity_id
        await update.message.reply_text('Great! Now, please enter your destination city:')
        return DESTINATION
    else:
        await update.message.reply_text('Sorry, I couldn\'t find that city. Please try again:')
        return ORIGIN

async def get_destination(update: Update, context: CallbackContext):
    destination = update.message.text
    entity_id = get_entity_id(destination)
    if entity_id:
        context.user_data['destination'] = entity_id
        await update.message.reply_text('Perfect! Finally, please enter your preferred travel date in YYYY-MM-DD format:')
        return DATE
    else:
        await update.message.reply_text('Sorry, I couldn\'t find that city. Please try again:')
        return DESTINATION

async def get_date(update: Update, context: CallbackContext):
    date = update.message.text
    try:
        datetime.strptime(date, "%Y-%m-%d")
        context.user_data['date'] = date
        await update.message.reply_text('Thank you! I\'m now searching for flights within a 7-day range before and after your specified date. Please wait...')
        flight_info = get_flight_info(context.user_data['origin'], context.user_data['destination'], context.user_data['date'])
        await update.message.reply_text(flight_info)
        return ConversationHandler.END
    except ValueError:
        await update.message.reply_text('Invalid date format. Please enter the date in YYYY-MM-DD format:')
        return DATE

def get_entity_id(city):
    url = "https://sky-scanner3.p.rapidapi.com/autocomplete"
    querystring = {"query": city}
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": "sky-scanner3.p.rapidapi.com"
    }
    response = requests.get(url, headers=headers, params=querystring)
    data = response.json()
    # Check if data is not empty before attempting to access the first element
    if data and 'Places' in data and len(data['Places']) > 0:
        return data['Places'][0]['PlaceId']
    return None

def get_flight_info(origin, destination, date):
    try:
        base_date = datetime.strptime(date, "%Y-%m-%d")
        date_range = [base_date + timedelta(days=i) for i in range(-7, 8)]
        
        all_flights = []
        
        for search_date in date_range:
            url = "https://sky-scanner3.p.rapidapi.com/flights/price-calendar-web"
            params = {
                "fromEntityId": origin,
                "toEntityId": destination,
                "yearMonth": search_date.strftime("%Y-%m"),
            }
            headers = {
                "x-rapidapi-key": RAPIDAPI_KEY,
                "x-rapidapi-host": "sky-scanner3.p.rapidapi.com"
            }
            response = requests.get(url, params=params, headers=headers)
            data = response.json()
            print (data)
            if data.get('data') and data['data'].get('quotes'):
                for quote in data['data']['quotes']:
                    all_flights.append({
                        'date': quote['outboundLeg']['departureDateTime'].split('T')[0],
                        'price': quote['price'],
                        'carrier': quote['carriers'][0]['name']
                    })
            

        if all_flights:
            all_flights.sort(key=lambda x: x['price'])
            flight_info = "Flights found (sorted from cheapest to most expensive):\n\n"
            for flight in all_flights[:10]:  # Limiting to top 10 flights to avoid very long messages
                flight_info += f"Date: {flight['date']}, Carrier: {flight['carrier']}, Price: ${flight['price']}\n"
            return flight_info
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