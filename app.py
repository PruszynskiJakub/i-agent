import asyncio
import os

from dotenv import load_dotenv
from langfuse import Langfuse
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from agent.answer import AgentAnswer
from agent.assistant import Assistant
from agent.execute import AgentExecute
from agent.plan import AgentPlan
from agent.state import StateHolder
from ai.open_ai import OpenAIProvider
from repository.database import Database
from repository.message import MessageRepository
from repository.prompt import PromptRepository
from services.trace import TraceService

# Initialize core services
load_dotenv()
database = Database()
message_repository = MessageRepository(database)
llm = OpenAIProvider(api_key=os.environ["OPENAI_API_KEY"])
langfuse_client = Langfuse(
    public_key=os.environ["LANGFUSE_PUBLIC_KEY"],
    secret_key=os.environ["LANGFUSE_SECRET_KEY"],
    host=os.environ.get("LANGFUSE_HOST", "https://cloud.langfuse.com")
)

# Initialize agent components
agent_plan = AgentPlan(llm)
agent_execute = AgentExecute(llm)
agent_answer = AgentAnswer(llm)

# Initialize Slack app
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))


@app.event("message")
def handle_message(message, say):
    """Handle incoming messages and respond using the agent"""
    try:
        # Initialize state for this conversation
        state = StateHolder(
            conversation_uuid=message.get("thread_ts", message["ts"]),  # Using timestamp as conversation ID
            message_repository=message_repository,
            tools=[
                {
                    "uuid": "a3bb189e-8bf9-4c8b-9beb-5de10a41cf62",
                    "name": "ynab",
                    "description": "responsible for managing budget, transactions etc",
                    "instructions": "",
                }
            ]
        )

        # Add the user's message to state
        state.add_message(content=message["text"], role="user")

        # Initialize and run agent
        assistant = Assistant(
            state=state,
            plan=agent_plan,
            execute=agent_execute,
            answer=agent_answer
        )

        # Get agent's response
        response = asyncio.run(assistant.run())

        # Send response back to Slack
        say(
            text=response,
            thread_ts=message.get("thread_ts", message["ts"])  # Reply in thread
        )

    except Exception as e:
        # Handle errors gracefully
        raise e
        error_message = f"Sorry, I encountered an error: {str(e)}"
        say(
            text=error_message,
            thread_ts=message.get("thread_ts", message["ts"])
        )


# Keep existing command handlers
@app.command("/model")
def handle_model_command(ack, body, respond):
    ack()
    respond("OK, model changed")

@app.event("assistant_thread_started")
def handle_assistant_thread_started(body, ack):
    print(body)
    ack()


if __name__ == "__main__":
    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    handler.start()
