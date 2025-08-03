# AI Real Estate Assistant

A sophisticated AI-powered real estate assistant built with LangGraph, featuring a clean supervisor-agent architecture and modern React UI. The system uses natural language processing to understand property searches and manage calendar appointments with interactive property carousels.

## Features

- 🏠 **Natural Language Property Search**: Ask for properties in plain English
- 📅 **Smart Calendar Management**: Schedule property viewings with intelligent calendar coordination
- 🎨 **Modern React UI**: Beautiful property carousels with responsive design
- 🔄 **Interactive Property Display**: Browse through search results with smooth navigation
- 🗄️ **Supabase Integration**: Real-time property data from PostgreSQL database
- 🤖 **Clean LangGraph Architecture**: Supervisor pattern with specialized agents
- 💾 **User Memory Management**: Remembers user preferences and information
- 📱 **Responsive Design**: Works seamlessly on desktop and mobile devices

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
   Keep this running in a separate terminal to watch for CSS changes.

5. **Configure environment variables:**
   ```bash
   # Copy the example file
   cp .env.example .env
   
   # Edit .env with your actual API keys
   nano .env  # or use your preferred editor
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

7. **Open the application:**
   - API: http://127.0.0.1:2024
   - Studio UI: https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024
   - API Docs: http://127.0.0.1:2024/docs

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
│   ├── agents/                    # LangGraph agent implementations
│   │   ├── supervisor/           # Supervisor agent and configuration
│   │   │   ├── tools/           # Supervisor-level tools
│   │   │   │   └── render_property_carousel.py
│   │   │   ├── app_state.py     # Application state schema
│   │   │   ├── supervisor.py    # Supervisor agent factory
│   │   │   └── user_profile.py  # User profile model
│   │   ├── property_finder/     # Property search specialist
│   │   │   ├── tools/          # Property search tools
│   │   │   │   ├── parse_property_search_query/
│   │   │   │   │   ├── parse_property_search_query.py
│   │   │   │   │   └── property_search_filters.py
│   │   │   │   └── search_properties/
│   │   │   │       ├── search_properties.py
│   │   │   │       └── property.py
│   │   │   └── property_finder_agent.py
│   │   └── calendar_manager/    # Calendar and scheduling specialist
│   │       ├── tools/          # Calendar management tools
│   │       │   ├── find_available_slots.py
│   │       │   └── schedule_viewing.py
│   │       └── calendar_manager.py
│   ├── frontend/                 # React UI components
│   │   ├── ui.tsx               # Main property carousel component
│   │   ├── ui.css               # Tailwind CSS source
│   │   ├── output.css           # Compiled CSS (generated)
│   │   ├── carousel.tsx         # Carousel component
│   │   ├── button.tsx           # Button component
│   │   ├── utils.ts             # Utility functions
│   │   ├── package.json         # Frontend dependencies
│   │   └── tailwind.config.js   # Tailwind configuration
│   ├── utils/                    # Shared utilities
│   │   ├── google_calendar.py   # Google Calendar integration
│   │   └── supabase.py          # Database client
│   └── graph.py                  # Main application entry point
├── .env                          # Environment variables
├── .env.example                  # Environment template
├── langgraph.json                # LangGraph configuration
├── pyproject.toml                # Python dependencies
└── README.md                     # This file
```

## Troubleshooting

### Frontend CSS Not Loading
If the UI doesn't look right, make sure you've built the CSS:
```bash
cd src/frontend
npm run dev
```

### Port Already in Use
If you get "Address already in use" error:
```bash
# Kill existing LangGraph processes
pkill -f "langgraph dev"

# Then restart
langgraph dev
```

### Missing Dependencies
If you get import errors:
```bash
# Reinstall Python dependencies
pip install -e .

# Reinstall frontend dependencies
cd src/frontend
npm install
```

### Environment Variables
Make sure your `.env` file contains all required variables:
- `OPENAI_API_KEY`
- `SUPABASE_URL`
- `SUPABASE_KEY`

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

### Adding New Features

#### **New Agent:**
1. Create agent directory in `src/agents/new_agent/`
2. Implement agent in `new_agent.py` using `create_react_agent`
3. Add agent to supervisor's agents list in `supervisor.py`
4. Update supervisor prompt with delegation instructions

#### **New Agent Tool:**
1. Create tool in `src/agents/agent_name/tools/`
2. Use `@tool(parse_docstring=True)` decorator
3. Return `Command` objects for state updates
4. Add to agent's tools list

#### **New Supervisor Tool:**
1. Create tool in `src/agents/supervisor/tools/`
2. Import and add to supervisor's tools list
3. Update supervisor prompt with usage instructions

#### **New UI Component:**
1. Add React component to `src/frontend/`
2. Export from `ui.tsx`
3. Update Tailwind CSS if needed
4. Test responsive design

#### **Database Changes:**
1. Update RPC functions in Supabase
2. Modify `src/utils/supabase.py` client
3. Update relevant property/data models

#### **Development Guidelines:**
- **Naming**: Use descriptive names ending in "-er" for agents (e.g., `property_finder`, `calendar_manager`)
- **Tools**: Keep stateless, return `Command` objects, use proper type annotations
- **State**: Use `AppState` for shared state, avoid direct state mutation
- **Imports**: Use relative imports within modules, absolute from project root
- **Documentation**: Update README and add docstrings for new components

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

MIT
