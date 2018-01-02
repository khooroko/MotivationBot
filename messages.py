class Messages:

    start = "Hi! Welcome to the community-run bot that sends you a daily motivation reminder! You do not have to do " \
            "anything else, the bot will send you a message at 9pm (GMT+8) by default. To change the time this " \
            "happens, enter \'/time HHMM\' where HH and MM are hours and minutes in the 24h format respectively (in " \
            "GMT+8). You can also send anything to receive a random message.\n\n" \
            "To contribute, enter \'/add \' followed by your message. You can add motivational quotes, cheerful " \
            "messages, or even uplifting stories :)\n\n" \
            "Do note that the first message you send may take quite some time to process. Please be patient if this " \
            "happens as the bot takes some time to wake up. " \
            "Enter \'/help\' to see more commands."
    help = "/add <message>: Add your own message in the database.\n" \
           "e.g. \'/add JUST DO IT\'\n\n" \
           "/delete: Delete the last message the was sent to you by the bot, or the last message you added, " \
           "whichever is more recent.\n" \
           "e.g. \'/delete\'\n\n" \
           "/time HHMM: Change the time in GMT+8 for the daily message to be sent.\n" \
           "e.g. \'/time 2300\'\n" \
           "To disable the daily message, just send \'/time\'."
    duplicate = "That already exists"
    no = "Please do not do that."
    deleted_last = "Last quote deleted"
    deleted_before = "This quote has already been deleted"
    delete_nothing = "Nothing to delete! Try adding a message with \'/add <message>\'"
    deleted_by_id = "'{}' has been removed"
    invalid_id = "The provided index is invalid"
    invalid_time = "The provided time is invalid. Please enter \'/time\' followed by a time in the 24h format. " \
                   "For example, \'/time 1200\' will set the scheduler to 12pm if you are in Singapore, and 8pm if " \
                   "you are in California."
    added = "Message successfully added! If you want to remove the message, please enter \'/delete\' before sending " \
            "anything else or receiving the daily message"
    cleared = "All quotes have been cleared"
    empty = "No quotes available"
    time_updated = "Time to send daily message updated"
    time_removed = "Daily messages stopped. To receive daily messages again, send \'/time HHMM\' where HH and MM " \
                   "are hours and minutes in the 24h format respectively (in GMT+8)."
