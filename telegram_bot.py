import os
import requests
import telebot
from telebot import types
from enum import Enum

#Get bot token from environment variable and assign to TeleBot instance
BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)

# Enum to represent bot states
class BotState(Enum):
    CONTEXT_CAPTURING = "context_capturing"     #Bot expects context for question answering
    SENTIMENT = "sentiment_analysis"            #Sentiment analysis of received messages
    QA = "question_answering"                   #Question answering of received messages (based on context)
    CHANGE_MODE = "change_mode"                 #Change mode base on message

# Initial state
current_state = BotState.SENTIMENT

#Global variables
current_context = ""
reset_context = False

#Define buttons to change modes
select_state_markup = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
select_buttons = [
    types.KeyboardButton("QA"),
    types.KeyboardButton("Sentiment"),
    types.KeyboardButton("Context"),
]
select_state_markup.add(*select_buttons)

#Define buttons to change modes
change_state_markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
change_buttons = [
    types.KeyboardButton("Cambiar estado"),
]
change_state_markup.add(*change_buttons)


#Start command handler
@bot.message_handler(commands=['start', 'hola'])
def send_welcome(message):
    bot.send_message(message.chat.id, f"Hola {message.from_user.first_name}! ¿Cómo estás?", reply_markup=change_state_markup)


#Function for sentiment analysis messaging
def sentiment_analysis(message):
    """Send message to sentiment analysis endpoint of API and respond with API response

    Args:
        message (telebot.types.Message): Message sent for sentiment analysis of telebot.types.Message
    """
    #Get user name to include in response
    user_name = str(message.from_user.first_name)

    #Define API call parameters
    url = "http://127.0.0.1:8000/sent_analysis"
    payload = {"name": user_name, "text": message.text}

    #Make API call
    http_response = requests.post(url, json=payload)
    response = http_response.json()

    #Parse results
    score_prcnt = "{:.2f}%".format(response['confidence'] * 100)
    sentiment_dict = {"NEG": "negativo", "NEU": "neutral", "POS":"positivo"}
    sentiment = sentiment_dict[response['classification']]

    #Generate response
    response_message = (f"{response['name']}, estoy {score_prcnt} seguro de que tu mensaje fue {sentiment}")
    bot.reply_to(message, response_message, reply_markup=change_state_markup)


#Function for question answering messaging
def question_answering(message, context: str, change_context: bool):
    """Send message to question answering endpoint of API and respond with API response

    Args:
        message (telebot.types.Message): _description_
        context (str): _description_
        change_context (bool): _description_
    """
    #Access global variable for context reset
    global reset_context

    #Define API parameters
    url = "http://127.0.0.1:8000/qa"
    payload = {"question": message.text, "context": context, "reset_context": change_context}

    #Make API call
    http_response = requests.post(url, json=payload)
    response = http_response.json()

    #Parse results
    score_prcnt = "{:.2f}%".format(response['confidence'] * 100)

    #Set flag to false for next message in case context had been reset
    reset_context = False

    #Generate response
    response_message = (f"{response['answer']} ({score_prcnt} certeza)")
    bot.reply_to(message, response_message, reply_markup=change_state_markup)


#Define message handler
@bot.message_handler(func=lambda msg: True)
def conversation_handler(message):
    """Handler for all mesages sent to bot. Interactions vary depending on current_state. 
    Hits corresponding API endpoints for sentiment analysis and question answering.

    Args:
        message (_type_): _description_
    """
    global current_state
    global reset_context
    global current_context

    #First handle case when current state doesn't matter and we want to change state
    if message.text == "Cambiar estado":
        #Respond with prompt to select new state with the states buttons on screen
        bot.send_message(message.chat.id, "Seleccionar estado", reply_markup=select_state_markup)
        current_state = BotState.CHANGE_MODE

    #Change mode state with case for each selected state
    if current_state == BotState.CHANGE_MODE:
        if message.text == "QA":
            current_state = BotState.QA
            bot.send_message(message.chat.id, "Nuevo estado: *Responder preguntas*", parse_mode='Markdown')

        elif message.text == "Sentiment":
            current_state = BotState.SENTIMENT
            bot.send_message(message.chat.id, "Nuevo estado: *Análisis de sentimiento*", parse_mode='Markdown')

        elif message.text == "Context":
            current_state = BotState.CONTEXT_CAPTURING
            bot.send_message(message.chat.id, "Nuevo estado: *Ingresar nuevo contexto*", parse_mode='Markdown')

        else:
            bot.send_message(message.chat.id, "Estado desconocido, reingrese utilizando botones", reply_markup=select_state_markup, parse_mode='Markdown')

    #QA state, calls relevant function
    elif current_state == BotState.QA:
        question_answering(message=message, context=current_context, change_context=reset_context)

    #Sentiment analysis state, calls relevant function
    elif current_state == BotState.SENTIMENT:
        sentiment_analysis(message=message)

    #Context capture state, reads context and sets flag for question_answering function
    elif current_state == BotState.CONTEXT_CAPTURING:
        current_context = message.text
        reset_context = True
        bot.reply_to(message, "Contexto guardado", reply_markup=change_state_markup)

#Start bot
bot.infinity_polling()