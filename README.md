# Real Estate AI Agent

An AI-powered property inquiry agent for real estate businesses in Egypt, built with LangChain and Supabase.

## Features

- Natural language property search
- Integration with Supabase database
- Support for various property types and filters
- Real-time property availability

## Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd real_estate_ai
   ```

2. Install dependencies:
   ```bash
   pip install -e .
   ```

3. Configure environment variables:
   - Copy `.env.example` to `.env`
   - Update the values with your Supabase and OpenAI API credentials

4. Run the agent:
   ```python
   from real_estate_ai.agents.property_inquiry_agent import PropertyInquiryAgent
   
   agent = PropertyInquiryAgent()
   response = agent.answer_query("Show me 2-bedroom apartments in New Cairo under 5M EGP")
   print(response)
   ```

## Project Structure

```
real_estate_ai/
├── src/
│   └── real_estate_ai/
│       ├── agents/           # Agent implementations
│       ├── db/              # Database client and queries
│       ├── schemas/         # Pydantic models
│       └── utils/           # Utility functions
├── .env                     # Environment variables
├── pyproject.toml           # Project dependencies
└── README.md                # This file
```

## License

MIT
