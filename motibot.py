import datetime
import json
import requests
import schedule
import time
import urllib
from dbhelper import DBHelper
from admincommands import AdminCommands
from messages import Messages


class MotiBot:

    def __init__(self, url_prefix):
        self.url_prefix = url_prefix
        self.db = DBHelper()
        self.db.setup()
        return

    def get_json_from_url(self, url):
        content = self.get_url(url)
        js = json.loads(content)
        return js

    def get_updates(self, offset=None):
        url = self.url_prefix + "getUpdates?timeout=100"
        if offset:
            url += "&offset={}".format(offset)
        js = self.get_json_from_url(url)
        return js

    def send_message(self, text, chat_id):
        text = urllib.parse.quote_plus(text)
        url = self.url_prefix + "sendMessage?text={}&chat_id={}&parse_mode=Markdown".format(text, chat_id)
        self.get_url(url)
        self.db.print_tables()

    def send_random_quote(self, chat):
        random_quote = self.db.get_random_quote()
        if not random_quote == "":
            self.db.update_last_quote(chat, random_quote)
            self.send_message(random_quote, chat)
        else:
            self.send_message(Messages.empty, chat)

    def set_scheduler(self, chat, time_to_send):
        self.db.set_time_to_send(chat, time_to_send)
        schedule.clear(chat)
        schedule.every().day.at(time_to_send[0:2] + ':' + time_to_send[2:]).do(self.send_random_quote, chat).tag(chat)

    def handle_updates(self, updates):
        for update in updates["result"]:
            chat = update["message"]["chat"]["id"]
            self.db.add_user(chat)
            try:
                text = str(update["message"]["text"]).strip()
            except KeyError:
                self.send_message(Messages.no, chat)
                return

            # User commands
            if text == "/start":
                self.send_message(Messages.start, chat)
                self.set_scheduler(chat, "2100")

            elif text == "/delete":
                quote_to_delete = self.db.get_last_quote(chat)
                if quote_to_delete in self.db.get_quotes():
                    self.db.delete_quote(quote_to_delete)
                    self.send_message(Messages.deleted_last, chat)
                else:
                    self.send_message(Messages.deleted_before, chat)

            elif text.startswith("/add"):
                new_text = text[5:]
                quotes = self.db.get_quotes()  ##
                if str.lower(new_text).strip() in (quote.lower().strip() for quote in quotes):
                    self.send_message(Messages.duplicate, chat)
                elif str.__len__(new_text) < 5:
                    self.send_message(Messages.no, chat)
                else:
                    self.db.add_quote(new_text)  ##
                    self.send_message(Messages.added, chat)

            elif text.startswith("/time"):
                new_time = text[6:]
                if self.is_valid_time(new_time):
                    self.set_scheduler(chat, new_time)
                    # self.db.set_time_to_send(chat, str(new_time))
                    self.send_message(Messages.time_updated, chat)
                else:
                    self.send_message(Messages.invalid_time, chat)

            # Admin commands
            elif text == AdminCommands.list:
                quotes = self.db.get_quotes()  ##
                message = "\n".join(quotes)
                if message.__len__() > 0:
                    self.send_message(message, chat)
                else:
                    self.send_message(Messages.empty, chat)

            elif text.startswith(AdminCommands.delete):
                quote_id_to_delete = int(text[AdminCommands.delete_offset]) - 1
                if quote_id_to_delete > 0:
                    quotes = self.db.get_quotes()  ##
                    try:
                        quote_to_delete = quotes[quote_id_to_delete]
                        self.send_message(Messages.deleted_by_id.format(quote_to_delete), chat)
                        self.db.delete_quote(quote_to_delete)
                    except IndexError:
                        self.send_message(Messages.invalid_id, chat)
                else:
                    self.send_message(Messages.invalid_id, chat)

            elif text == AdminCommands.clear:
                self.db.clear_all_quotes()
                self.send_message(Messages.cleared, chat)

            # Fall-through input
            elif text.startswith("/"):
                self.send_message(Messages.no, chat)

            else:
                self.send_random_quote(chat)

    @staticmethod
    def get_url(url):
        response = requests.get(url)
        content = response.content.decode("utf8")
        return content

    @staticmethod
    def get_last_update_id(updates):
        update_ids = []
        for update in updates["result"]:
            update_ids.append(int(update["update_id"]))
        return max(update_ids)

    @staticmethod
    def get_last_chat_id_and_text(updates):
        num_updates = len(updates["result"])
        last_update = num_updates - 1
        text = updates["result"][last_update]["message"]["text"]
        chat_id = updates["result"][last_update]["message"]["chat"]["id"]
        return (text, chat_id)

    @staticmethod
    def is_valid_time(time_to_check):
        try:
            int(time_to_check)
            if not str.strip(time_to_check).__len__() == 4:
                return False
            if int(time_to_check[0:2]) > 23 or int(time_to_check[0:2]) < 0:
                return False
        except ValueError:
            return False

        return True

    @staticmethod
    def convert_time_to_string(hour, minute):
        return str(MotiBot.pad_to_two_digits(hour)) + str(MotiBot.pad_to_two_digits(minute))

    @staticmethod
    def pad_to_two_digits(arg):
        if str(arg).__len__() < 2:
            return "0" + str(arg)
        else:
            return str(arg)


def main():
    token_file = open("token.json")
    token = json.load(token_file)["token"]
    bot = MotiBot("https://api.telegram.org/bot{}/".format(token))
    last_update_id = None
    while True:
        schedule.run_pending()
        updates = bot.get_updates(last_update_id)
        if len(updates["result"]) > 0:
            last_update_id = bot.get_last_update_id(updates) + 1
            bot.handle_updates(updates)
        time.sleep(0.33)


if __name__ == '__main__':
    main()
