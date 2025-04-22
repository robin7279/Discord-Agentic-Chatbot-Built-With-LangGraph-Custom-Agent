import os
import asyncio
import discord
from discord.ext import commands
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.graph.message import add_messages
from typing import Annotated, Literal, TypedDict
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode
from langchain_groq import ChatGroq
from langchain_community.tools.tavily_search import TavilySearchResults
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY")
DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")

# Initialize Discord bot with command prefix and intents
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='$', intents=intents)

# Define bot class
class Dotbot:
    def __init__(self):
        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0,
            api_key=GROQ_API_KEY,
        )

        self.system_prompt = """
        You are a Llama Dotbot built by Robin, a friendly and helpful Discord bot designed to assist users in a server. 
        Your role is to provide accurate, concise, and engaging responses to user queries. 
        Use a casual, conversational tone suitable for a Discord community, and incorporate humor or emojis where appropriate 😄. 
        If a user asks for real-time information, use the provided search tools to fetch relevant data. 
        Always be respectful, avoid sensitive topics, and adhere to Discord's community guidelines. 
        When responding, consider the context of a Discord server, such as mentioning users with '@' or referencing channels if relevant.
        """
    
    def tool_call(self):
        tool = TavilySearchResults(max_results=2, api_key=TAVILY_API_KEY)
        tools = [tool]
        self.tool_node = ToolNode(tools=[tool])
        self.llm_with_tool = self.llm.bind_tools(tools)
                
    def model_call(self, state: MessagesState):
        messages = state['messages']
        system_message = SystemMessage(content=self.system_prompt)
        full_message = [system_message] + messages
        try:
            response = self.llm_with_tool.invoke(full_message)
            return {"messages": [response]}
        except Exception as e:
            error = AIMessage(content=f"Error in LLM invocation: {str(e)}")
            return {"messages": [error]}
    
    def router_function(self, state: MessagesState) -> Literal["tools", END]:
        messages = state['messages']
        last_message = messages[-1]
        if last_message.tool_calls:
            return "tools"
        return END
    
    def __call__(self):
        self.tool_call()
        builder = StateGraph(MessagesState)
        builder.add_node("agent", self.model_call)
        builder.add_node("tools", self.tool_node)
        builder.add_edge(START, "agent")
        builder.add_conditional_edges(
            "agent",
            self.router_function,
            {"tools": "tools", END: END}
        )
        builder.add_edge("tools", "agent")
        memory = MemorySaver()
        self.app = builder.compile(checkpointer=memory)
        return self.app
    
# Initialize bot
dotbot = Dotbot()
dotbot()  # Initialize the LangGraph app

# Discord Event Handlers
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.command()
async def hello(ctx):
    """Responds with a friendly greeting."""
    await ctx.send(f"Hello, {ctx.author.mention}! How can I assist you? 😄")

bot.remove_command('help')
@bot.command()
async def help(ctx):
    """Shows all available commands."""
    await ctx.send(
        "Available commands\n\n"
        "$help 📜        – Show all commands\n\n"
        "$hello 👋       – Greet the Bot\n\n"
        "$ask ❓         – Smart AI Response via Agent\n\n"
        "$search 🔎      – Quick Web Lookup\n\n"
        "$info ℹ️        – Bot info & stats\n\n"
        "You can also chat with me directly without commands!"
    )

@bot.command()
async def info(ctx):
    """Shows bot information and stats."""
    await ctx.send(
        f"I'm a Llama Dotbot powered by Robin\n"
        "Built with LangChain and LangGraph for smart conversations.\n"
        f"Prefix: {bot.command_prefix}\n"
        "Use $help to see all commands!"
    )

@bot.command()
async def ask(ctx, *, question):
    """Asks a question to the Groq LLM via the agent."""
    await process_agent_message(ctx, question)

@bot.command()
async def search(ctx, *, query):
    """Asks a question to the Groq LLM via the agent."""
    await process_agent_message(ctx, query)

async def process_agent_message(ctx_or_message, message):
    """Helper function to process a message using the LangGraph agent."""
    try:
        # Determine if input is Context (from commands) or Message (from on_message)
        is_context = isinstance(ctx_or_message, commands.Context)
        author = ctx_or_message.author
        mention = author.mention
        send_method = ctx_or_message.send if is_context else ctx_or_message.channel.send

        user_input = HumanMessage(content=message)
        thread_id = f"discord_{ctx_or_message.channel.id}_{author.id}"

        # Use dotbot.app.invoke
        response = await asyncio.to_thread(
            dotbot.app.invoke,
            {"messages": [user_input]},
            {"configurable": {"thread_id": thread_id}}
        )

        last_message = response["messages"][-1]
        answer = last_message.content if hasattr(last_message, 'content') else str(last_message)

        # Log response for debugging
        print(f"Agent response: {answer}")

        # Ensure response fits within Discord's 2000-character limit
        if len(answer) > 1990:
            answer = answer[:1990] + '...'

        await send_method(f'{mention} {answer}')

    except Exception as e:
        import traceback
        print(f"Error in process_agent_message: {str(e)}\n{traceback.format_exc()}")
        await send_method(f'{mention} Sorry, an agent error occurred: {str(e)}')

@bot.event
async def on_message(message):
    """Handle all incoming messages."""
    if message.author == bot.user:
        return
    
    if message.content.startswith(bot.command_prefix):
        await bot.process_commands(message)
    else:
        await process_agent_message(message, message.content)

# Run the bot
bot.run(DISCORD_TOKEN)