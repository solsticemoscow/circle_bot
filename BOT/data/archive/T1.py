# import time
# from tg_tqdm import tg_tqdm
#
# from BOT.config import TOKEN
#
# for _ in tg_tqdm(range(100), TOKEN, 239203155):
#     time.sleep(0.1)
#
import time, sys

import telebot



from BOT.config import TOKEN, OWNER


# for i in range(101):
#     time.sleep(0.1)
#     update_progress(i/100.0)

bot = telebot.TeleBot(TOKEN)
MSG = bot.send_message(chat_id=OWNER, text='TEST')
print(MSG.message_id)
bot.edit_message_text(chat_id=OWNER, text='TEST222', message_id=MSG.message_id)


# import time
# import sys
#
# toolbar_width = 40
#
# # setup toolbar
# sys.stdout.write("[%s]" % (" " * toolbar_width))
# sys.stdout.flush()
# sys.stdout.write("\b" * (toolbar_width+1))
#
# for i in range(toolbar_width):
#     time.sleep(0.0001)
#     # update the bar
#     sys.stdout.write("-")
#     sys.stdout.flush()
#
# sys.stdout.write("]\n") # this ends the progress bar