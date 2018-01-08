import json
import requests
import schedule
import time
import urllib
from dbhelper import DBHelper
from admincommands import AdminCommands
from messages import Messages
from timeutil import TimeUtil


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

    def send_random_quote(self, chat):
        try:
            random_quote = self.db.get_random_quote()
            self.db.update_last_quote(chat, random_quote)
            self.send_message(random_quote, chat)
        except TypeError:
            self.send_message(Messages.empty, chat)

    def remove_scheduler(self, chat):
        schedule.clear(chat)

    def set_scheduler(self, chat, time_to_send):
        self.db.set_time_to_send(chat, time_to_send)
        schedule.clear(chat)
        schedule.every().day.at(TimeUtil.convert_string_to_time(time_to_send)).do(self.send_random_quote, chat)\
            .tag(chat)

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

            elif text == "/help":
                self.send_message(Messages.help, chat)

            elif text == "/delete":
                quote_to_delete = self.db.get_last_quote(chat)
                if quote_to_delete in self.db.get_quotes():
                    self.db.delete_quote(quote_to_delete)
                    self.send_message(Messages.deleted_last, chat)
                elif quote_to_delete is None:
                    self.send_message(Messages.delete_nothing, chat)
                else:
                    self.send_message(Messages.deleted_before, chat)

            elif text.startswith("/add"):
                new_text = text[5:]
                quotes = self.db.get_quotes()
                if str.lower(new_text).strip() in (quote.lower().strip() for quote in quotes):
                    self.send_message(Messages.duplicate, chat)
                elif str(new_text).__len__() < 3:
                    self.send_message(Messages.no, chat)
                elif str(new_text).__len__() > 255:
                    self.send_message(Messages.too_long, chat)
                else:
                    self.db.add_quote(new_text)
                    self.send_message(Messages.added, chat)
                    self.db.update_last_quote(chat, new_text)

            elif text == "/time":
                self.remove_scheduler(chat)
                self.send_message(Messages.time_removed, chat)

            elif text.startswith("/time"):
                new_time = text[6:]
                if TimeUtil.is_valid_time(new_time):
                    self.set_scheduler(chat, new_time)
                    self.send_message(Messages.time_updated, chat)
                else:
                    self.send_message(Messages.invalid_time, chat)

            # Admin commands
            elif text == AdminCommands.list:
                quotes = self.db.get_quotes()
                message = ""
                for idx, val in enumerate(quotes):
                    message += str(idx)
                    message += ". "
                    message += val
                    message += "\n"
                if message.__len__() > 0:
                    self.send_message(message, chat)
                else:
                    self.send_message(Messages.empty, chat)

            elif text.startswith(AdminCommands.delete):
                try:
                    quote_id_to_delete = int(text[AdminCommands.delete_offset:])
                except ValueError:
                    self.send_message(Messages.invalid_id, chat)
                    return
                if quote_id_to_delete >= 0:
                    quotes = self.db.get_quotes()
                    try:
                        quote_to_delete = quotes[quote_id_to_delete]
                        self.send_message(Messages.deleted_by_id.format(quote_to_delete), chat)
                        self.db.delete_quote(quote_to_delete)
                    except IndexError:
                        self.send_message(Messages.invalid_id, chat)
                else:
                    self.send_message(Messages.invalid_id, chat)

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
        return text, chat_id


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
        time.sleep(0.4)


if __name__ == '__main__':
    main()
