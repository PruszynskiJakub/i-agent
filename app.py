import os
from typing import Dict

from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_bolt.context import assistant

load_dotenv()

app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

@app.message("hello")
def message_hello(message, say):
    print(message)
    # say() sends a message to the channel where the event was triggered
    say(
        f"Hey there <@{message['user']}>!",
        thread_ts=message["thread_ts"]
    )

@app.event("assistant_thread_started")
def handle_message(message: Dict, say):
    print(message)
    say("Hello")


@app.command("/model")
def handle_model_command(ack, body, respond):
    ack()
    print(body)
    respond("OK, model changed")


if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
