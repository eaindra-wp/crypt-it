import math
import random
import logging
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, ConversationHandler)
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)

# # Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

ENCRYPT_CMD, PLAINMSG, DECRYPT_CMD, CIPHERMSG  = range(4)

key_encrypt = ""
key_decrypt = ""

""" start command """
def start(update, context):
    user = update.message.from_user
    update.message.reply_text('Hello, ' + user.first_name + '. Send me \'/encrypt.\' or \'/decrypt\' according to what you want to do.')

def unknown(update, context):
    update.message.reply_text('I couldn\'t understand what you said')


def cancel(bot, update):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('Bye! I hope we can talk again some day.')
    return ConversationHandler.END


""" encryption process"""
def encryptMessage(key, plaintext):
    result = "" 
    key_index = 0
    message_length = float(len(plaintext)) 
    message_list = list(plaintext) 
    key_list = sorted(list(key)) 
    col = len(key) 
    row = int(math.ceil(message_length / col)) 
  
    # leave a space in the empty matrix cell
    fill_null = int((row * col) - message_length) 
    message_list.extend(' ' * fill_null) 
  
    # put characters in the message in the matrix row-wise
    matrix = [message_list[i: i + col]  
              for i in range(0, len(message_list), col)] 
  
    # read matrix column-wise using key 
    for _ in range(col): 
        current_matrix = key.index(key_list[key_index]) 
        result += ''.join([row[current_matrix]  
                          for row in matrix]) 
        key_index += 1
    return result


def encrpyt_command(update, context):
    update.message.reply_text('Send me the key that you are using to encrypt.')
    return ENCRYPT_CMD
   

def getKey_encrypt(update, context):
    key = update.message.text
    has_space = key.split(" ")
    
    if len(has_space) > 1 :
        update.message.reply_text("The key can't have a space. Please send me a new key.")
        return ENCRYPT

    else:
        update.message.reply_text('This key is valid. You need to remember this key to decrypt the message.'
        '\nNow send me your plain message.')
        global key_encrypt 
        key_encrypt = key
        return PLAINMSG


def getPlainMessage(update, context):
    plain_message = update.message.text
    update.message.reply_text('The encrypted message is: ' + encryptMessage(key_encrypt, plain_message) + '.')
    return ConversationHandler.END


""" decryption process """
def decryptMessage(key, message):
    result = ""
    key_index = 0
    message_index = 0
    message_len = float(len(message))
    message_list = list(message) 
  
    col = len(key)
    row = int(math.ceil(message_len / col)) 
    sorted_key = sorted(list(key)) 
  
    dec_cipher = [] 
    for _ in range(row): 
        dec_cipher += [["&"] * col] 
  
    # Arrange the matrix column wise according  
    # to permutation order by adding into new matrix 
    for _ in range(col): 
        current = key.index(sorted_key[key_index]) 
        for j in range(row): 
            dec_cipher[j][current] = message_list[message_index] 
            message_index += 1
        key_index += 1

    # convert decrypted msg matrix into a string 
    try: 
	    result = ''.join(sum(dec_cipher, [])) 
    except TypeError: 
	    raise TypeError("This program cannot handle repeating words.") 

    null_count = result.count('&') 
    if null_count > 0: 
        return result[: -null_count] 
    
    return result 


def decrypt_command(update, context):
    update.message.reply_text('Send me the key to decrypt the message.')
    return DECRYPT_CMD


def getCipher(update, context):
    global key_decrypt
    key_decrypt = update.message.text
    update.message.reply_text('Now send me the message that you want to decrypt.')
    return CIPHERMSG


def getKey_decrypt(update, context):
    message = update.message.text
    update.message.reply_text("The decrypted message is: " + decryptMessage(key_decrypt, message) + '.')
    return ConversationHandler.END


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

# def check_msg(update, context):
#     message =  update.message.text
#     if()

def main():
    updater = Updater("1022827925:AAG7q0ReUZfv7LnL9dCyajUE34Dxh6tScfw", use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))

    encrypt_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('encrypt', encrpyt_command)],
        states={
            ENCRYPT_CMD: [MessageHandler(Filters.text, getKey_encrypt)],
            PLAINMSG: [MessageHandler(Filters.text, getPlainMessage)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    dp.add_handler(encrypt_conv_handler)
    decrypt_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('decrypt', decrypt_command)],
        states={
            DECRYPT_CMD: [MessageHandler(Filters.text, getCipher)],
            CIPHERMSG: [MessageHandler(Filters.text, getKey_decrypt)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    dp.add_handler(decrypt_conv_handler)
    # dp.add_handler(MessageHandler(Filters.text, check_msg))
    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
