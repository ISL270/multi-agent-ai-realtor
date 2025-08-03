# AI Real Estate Assistant

A multi-agent real estate AI assistant built using **LangChain**, **LangGraph**, **LangSmith** for observability, and **LangMem** for persistence. Powered by OpenAI’s **GPT-4.1**, the system includes a **Property Finder agent** that parses natural language requests and queries a **Supabase** backend via RPC, and **Calendar Manager agent** responsible for scheduling viewings. Search results are displayed using **Generative UI** in a clean, in-chat interface built with **React** and **Tailwind CSS**.

## Features

- 🏠 **Natural Language Property Search**: Ask for properties in plain English
- 📅 **Smart Calendar Management**: Schedule property viewings with intelligent calendar coordination
- 🎨 **Modern React UI**: Beautiful property carousels with responsive design
- 🤖 **Clean LangGraph Architecture**: Supervisor pattern with specialized sub-agents
- 💾 **Long-Term Memory**: Remembers user preferences and information across conversation threads
- 🗄️ **Supabase Integration**: Real-time property data from PostgreSQL database

## Prerequisites

Before running this project, make sure you have:

- **Python 3.10+** installed
- **Node.js 18+** and **npm** installed
- **OpenAI API Key** ([Get one here](https://platform.openai.com/api-keys))
- **Supabase Project** ([Create one here](https://supabase.com))
- **LangSmith Account** (Optional, for tracing - [Sign up here](https://smith.langchain.com))

## Quick Start

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd real_estate_ai
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -e .
   ```

3. **Install frontend dependencies:**
   ```bash
   cd src/frontend
   npm install
   ```

4. **Build the frontend CSS:**
   ```bash
   npm run dev
   ```

5. **Configure environment variables:**
   ```bash
   # Copy the example file and update it with your actual API keys
   cp .env.example .env
   ```

   Required environment variables:
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `SUPABASE_URL`: Your Supabase project URL
   - `SUPABASE_KEY`: Your Supabase anon key
   - `LANGSMITH_API_KEY`: (Optional) Your LangSmith API key for tracing

6. **Run the application:**
   ```bash
   # From the project root directory
   langgraph dev
   ```

## Usage Examples

Try these natural language queries in the chat interface:

- "Show me 2-bedroom apartments in New Cairo under 5M EGP"
- "Find villas with swimming pools in 6th of October City"
- "I need a 3-bedroom apartment with parking in Maadi"
- "Show me properties under 3 million EGP with gardens"

## Project Structure

```
real_estate_ai/
├── src/
│   ├── agents/                   # LangGraph agent implementations
│   │   ├── supervisor/          # Supervisor agent and state management
│   │   ├── property_finder/     # Property search specialist
│   │   └── calendar_manager/    # Calendar and scheduling specialist
│   ├── frontend/                # React UI components (Tailwind CSS)
│   ├── utils/                   # Shared utilities (Supabase, Google Calendar)
│   └── graph.py                 # Main application entry point
├── langgraph.json               # LangGraph configuration
├── pyproject.toml               # Python dependencies
└── .env                         # Environment variables
```

## Development

### Architecture Overview

The application follows a **clean supervisor-agent pattern** with modular, specialized components:

#### **Core Components:**
- **Supervisor Agent** (`src/agents/supervisor/`): Orchestrates conversation flow, manages user memory, and coordinates UI rendering
- **Property Finder** (`src/agents/property_finder/`): Specialized agent for natural language property search and filtering
- **Calendar Manager** (`src/agents/calendar_manager/`): Handles scheduling, availability checking, and appointment booking
- **React UI Components** (`src/frontend/`): Modern, responsive property carousel with Tailwind CSS
- **Database Integration** (`src/utils/`): Supabase PostgreSQL with property data and RPC functions

#### **Key Design Principles:**
- **🏗️ Modular Architecture**: Each agent is self-contained with its own tools and responsibilities
- **🎯 Separation of Concerns**: Agents focus on domain expertise, supervisor handles orchestration
- **🎨 Centralized UI**: All UI rendering happens at supervisor level using `render_property_carousel`
- **⚡ Stateless Tools**: Tools use Command pattern for clean, predictable state updates
- **🔒 Type Safety**: Full TypeScript/Python type annotations throughout the codebase
- **📦 Clean Imports**: Proper module organization with clear dependency paths

#### **Agent Workflow:**
1. **User Input** → Supervisor analyzes intent and delegates to appropriate agent
2. **Property Search** → Property Finder parses query and searches database
3. **UI Rendering** → Supervisor uses `render_property_carousel` to display results
4. **Appointment Booking** → Calendar Manager handles scheduling when requested

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

MIT
