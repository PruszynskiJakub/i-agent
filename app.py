import asyncio
import json
import os

from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from agent.assistant import agent_run
from utils.state import create_or_restore_state, add_message
from llm.tracing import flush
from logger.logger import log_info, log_exception
from slackk.utils import preprocess_message, get_conversation_id

# Initialize core services
load_dotenv()

# Initialize Slack app
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))


@app.event("message")
def handle_message(message, say):
    """Handle incoming messages and respond using the agent"""
    try:
        conversation_id = get_conversation_id(message)
        # Preprocess the message
        preprocess_message(message, conversation_id)

        # Initialize state for this conversation
        state = create_or_restore_state(conversation_uuid=conversation_id)

        # Log initial state counts
        log_info(
            f"Initial state - Actions: {len(state.action_history)}, Documents: {len(state.documents)}, Messages: {len(state.messages)}")

        state = add_message(state, content=message["text"], role="user")

        response = json.loads(asyncio.run(agent_run(in_state=state)))
        flush()
        # Send response back to Slack
        say(
            text=response['text'],
            blocks = [
              {
                  "type": "section",
                  "text": {
                      "type": "mrkdwn",
                      "text": f"{response['markdown']}"
                  }
              }
            ],
            thread_ts=message.get("thread_ts", message["ts"])  # Reply in thread
        )

    except Exception as e:
        flush()
        # Log the full error with traceback
        log_exception("Error handling Slack message", e)
        
        # Send simplified message to user
        error_message = f"Sorry, I encountered an error: {str(e)}"
        say(
            text=error_message,
            thread_ts=message.get("thread_ts", message["ts"])
        )


# Keep existing command handlers
@app.command("/models")
def handle_model_command(ack, body, respond):
    ack()
    respond("OK, models changed")


@app.event("assistant_thread_started")
def handle_assistant_thread_started(body, ack):
    print(body)
    ack()


if __name__ == "__main__":
    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    handler.start()
