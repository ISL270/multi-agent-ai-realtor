# Real Estate AI Agent

An AI-powered property search agent built with LangGraph, featuring a modern React UI for displaying property results. The agent uses natural language processing to understand property search queries and returns interactive property carousels.

## Features

- 🏠 **Natural Language Property Search**: Ask for properties in plain English
- 🎨 **Modern React UI**: Beautiful property cards with images and details
- 🔄 **Interactive Carousel**: Browse through property results with navigation
- 🗄️ **Supabase Integration**: Real-time property data from PostgreSQL database
- 🤖 **LangGraph Architecture**: Supervisor agent managing specialized sub-agents
- 📱 **Responsive Design**: Works on desktop and mobile devices

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
│   │   ├── appointment_booking/   # Appointment booking agent
│   │   │   ├── tools/            # Booking-specific tools
│   │   │   │   ├── find_available_slots.py
│   │   │   │   └── schedule_viewing.py
│   │   │   └── appointment_booking_agent.py
│   │   └── property_finder/       # Property search agent
│   │       ├── parse_query/      # Query parsing module
│   │       │   ├── parse_query_node.py
│   │       │   └── property_search_filters.py
│   │       ├── query_supabase/   # Database query module
│   │       │   ├── property.py
│   │       │   └── query_supabase_node.py
│   │       └── property_finder.py
│   ├── frontend/                  # React UI components
│   │   ├── ui.tsx                # Main property carousel component
│   │   ├── ui.css                # Tailwind CSS source
│   │   ├── output.css            # Compiled CSS (generated)
│   │   ├── carousel.tsx          # Carousel component
│   │   ├── button.tsx            # Button component
│   │   ├── utils.ts              # Utility functions
│   │   ├── package.json          # Frontend dependencies
│   │   └── tailwind.config.js    # Tailwind configuration
│   ├── utils/                     # Shared utilities
│   │   ├── google_calendar.py    # Google Calendar integration
│   │   └── supabase.py           # Database client
│   ├── main.py                    # Main supervisor agent
│   ├── standard_state.py          # Shared state definition
│   └── user_profile.py            # User profile model
├── .env                           # Environment variables
├── .env.example                   # Environment template
├── langgraph.json                 # LangGraph configuration
├── pyproject.toml                 # Python dependencies
└── README.md                      # This file
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

- **Supervisor Agent**: Orchestrates the conversation and delegates to specialized agents
- **Property Finder Agent**: Handles property search queries using natural language
- **UI Components**: React components that render property results in an interactive carousel
- **Database**: Supabase PostgreSQL with property data and amenities

### Adding New Features

1. **New Agent**: Create in `src/agents/`
2. **New Tool**: Add to `src/tools/`
3. **New UI Component**: Add to `src/frontend/`
4. **Database Changes**: Update `src/supabase.py`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

MIT
