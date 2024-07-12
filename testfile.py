from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ApplicationBuilder

TOKEN: Final = '7404980400:AAEmi0HLuElXOL6e2YMObr6hRBZvw4fcjPg'

BOT_USERNAME: Final = '@begatis_bot'



async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hello! This is Begati\'s bot!')
    
    
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('You said: ' + update.message.text)

async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('This is a custom command')




def handle_responses(text: str):
    processed: str = text.lower()
    
    if 'hello' in processed:
        return 'Hello! How can I help you?'
    if 'bye' in processed:
        return 'Goodbye!'
    if 'how are you' in processed:
        return 'I am fine, thank you!'
    if 'your name' in processed:
        return 'I am Begati\'s bot!'
    if 'your creator' in processed:
        return 'I was created by Begati!'
    if 'your purpose' in processed:
        return 'I was created to help you!'
    if 'your age' in processed:
        return 'I was created on 2021!'
    
    if text == '/start':
        return start_command
    elif text == '/help':
        return help_command
    elif text == '/custom':
        return custom_command
    else:
        return 'I am sorry, I do not understand that command!'
    
    
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    print (f'User {update.message.from_user.username} sent a message of type {message_type}: {update.message.text}')
    if message_type == 'group':
        if BOT_USERNAME in update.message.text:
            new_text: str = update.message.text.replace(BOT_USERNAME, '').strip()
            response: str = handle_responses(new_text)
        else:
            return
    else:
        response: str = handle_responses(update.message.text)
        await update.message.reply_text(response)
        

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')
    

if __name__ == '__main__':
    
    app = ApplicationBuilder().token(TOKEN).build()    
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('custom', custom_command))
    
    app.add_handler(MessageHandler(filters.Text, handle_responses))
    
    
    #Messages 
    app.add_handler(MessageHandler(filters.Text, handle_message))
    
    #Errors
    app.add_error_handler(error)
    
    #polling
    print('Bot is running!')
    app.run_polling(poll_interval=3)
    
    app.run()
    
