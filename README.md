# 🤖 Discord-Agentic-Chatbot-Built-With-LangGraph-Custom-Agent

A powerful, modular, and intelligent Discord chatbot powered by [LangGraph](https://www.langgraph.dev/) and a custom-built agent. This bot features agentic behavior, multi-step reasoning, web search, and more — all inside your Discord server.

> 🚧 **This project is under active development. Advanced features like voice-based responses in Discord voice channels will be integrated soon. Stay tuned!**

---

## 🚀 Features (Current)

- 🤝 Discord integration using `discord.py`
- 🧠 Custom LangGraph-based agent with memory and tool usage
- 💬 Natural conversation and code explanation
- 📝 To-do list assistant (Will be integrate later)
- 🔍 Real-time web search
- 📁 File uploads and document understanding (Will be integrate later)
- 🧑‍💻 Code generation and execution
- 🗣️ Voice-to-text support using Whisper (Will be integrate later)
- 📰 Daily news summaries

---

## 🛠️ Tech Stack

- Python 3.10+
- [LangGraph](https://www.langgraph.dev/)
- [LangChain](https://www.langchain.com/)
- [discord.py](https://github.com/Rapptz/discord.py)
- [Whisper](https://github.com/openai/whisper) (for voice input)
- [Groq Cloud](https://console.groq.com/) (for hosted LLM inference)
- Groq LLMs
- Custom tools and agents

---

## 📦 Installation

Follow these steps to set up and run the bot on your local machine:

```bash
# Clone the repository
git clone https://github.com/robin7279/Discord-Agentic-Chatbot-Built-With-LangGraph-Custom-Agent.githttps://github.com/your-username/discord-agentic-chatbot.git
cd Discord Bot

# Create and activate a virtual environment
conda create -p dotbot_env python==3.12 -y

# Install dependencies
pip install -r requirements.txt

# Create a .env file and add the following environment variables
# .env file content:
DISCORD_TOKEN=your_discord_bot_token
GROQ_API_KEY=your_groq_key
TAVILY_API_KEY=your_tavily_key

# Run the bot
python bot.py



---

## 📄 License

This project is licensed under the **MIT License**.  
You are free to use, modify, and distribute this software with proper attribution.

