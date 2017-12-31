import json
import requests
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
        self.last_quote = None
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

    def send_message(self, text, chat_id, reply_markup=None):
        text = urllib.parse.quote_plus(text)
        url = self.url_prefix + "sendMessage?text={}&chat_id={}&parse_mode=Markdown".format(text, chat_id)
        if reply_markup:
            url += "&reply_markup={}".format(reply_markup)
        self.get_url(url)
        self.db.print_tables()

    def handle_updates(self, updates):
        for update in updates["result"]:
            chat = update["message"]["chat"]["id"]
            if chat not in self.db.get_users():
                self.db.add_user(chat)
            try:
                text = update["message"]["text"]
            except KeyError:
                self.send_message(Messages.no, chat)
                return

            if text == "/delete":
                self.db.delete_quote(self.last_quote)
                self.send_message(Messages.deleted_last, chat)
            elif text == "/start":
                self.send_message(Messages.start, chat)
            elif text == AdminCommands.list:
                quotes = self.db.get_quotes()  ##
                message = "\n".join(quotes)
                if message.__len__() > 0:
                    self.send_message(message, chat)
                else:
                    self.send_message(Messages.empty, chat)
            elif text == AdminCommands.clear:
                self.db.clear_all()
                self.send_message(Messages.cleared, chat)
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
            elif text.startswith("/"):
                self.send_message(Messages.no, chat)
            else:
                self.last_quote = "\n".join(self.db.get_random_quote())
                if not self.last_quote == "":
                    self.send_message(self.last_quote, chat)
                else:
                    self.send_message(Messages.empty, chat)

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


def main():
    token_file = open("token.json")
    TOKEN = json.load(token_file)["token"]
    bot = MotiBot("https://api.telegram.org/bot{}/".format(TOKEN))
    last_update_id = None
    while True:
        updates = bot.get_updates(last_update_id)
        if len(updates["result"]) > 0:
            last_update_id = bot.get_last_update_id(updates) + 1
            bot.handle_updates(updates)
        time.sleep(0.33)


if __name__ == '__main__':
    main()
