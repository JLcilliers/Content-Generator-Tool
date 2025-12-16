# SEO Content Brief Generator

An AI-powered Streamlit application that generates professional, validated SEO content briefs with automatic web research, URL validation, and Word document export.

## Features

- **AI-Powered Generation**: Uses OpenAI, Claude, Grok, Perplexity, or Mistral to generate complete content briefs
- **Automatic Web Research**: Scrapes and analyzes target websites for brand voice, services, and audience
- **Smart Internal Link Discovery**: Automatically finds and verifies relevant internal links (HTTP 200)
- **Known Client Detection**: Auto-applies special guidelines for HealthWorks, CellGate, and AIM Companies
- **Strict Validation**: Enforces character limits, heading structure, UK English, and SEO best practices
- **Professional Word Export**: Creates formatted .docx documents ready for use
- **Client Profile Management**: Save and load client profiles via Supabase

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API Keys

Copy `.env.example` to `.env` and add at least one AI provider key:

```bash
cp .env.example .env
```

Edit `.env`:
```
OPENAI_API_KEY=sk-your-key-here
# OR
CLAUDE_API_KEY=your-claude-key-here
```

### 3. Run the Application

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

## Usage

1. **Select AI Provider**: Choose from available providers in the sidebar
2. **Enter Website URL**: The client's website to research
3. **Enter Topic**: What the content should cover
4. **Enter Keywords**: One per line, primary keyword first
5. **Click Generate**: The app will research, generate, and validate the brief
6. **Download**: Get the formatted Word document

## Brief Output Format

Every brief includes:

- **Web Page Structure**: Page type, title (<60 chars), meta description (140-160 chars), URL, H1
- **Internal Linking**: 3 verified URLs from the same domain
- **Writing Guidelines**: Word count, audience, tone, POV, CTA, restrictions
- **Suggested Headings**: H1 + max 4 H2s + max 2 H3s per H2
- **FAQs**: 4-6 questions (no answers)

## Validation Rules

The generator enforces:

1. No years or dates anywhere
2. Page title under 60 characters
3. Meta description 140-160 characters
4. UK English spelling (except AIM Companies)
5. Year 8 reading level
6. Maximum 4 H2 sections
7. Maximum 2 H3s per H2
8. 4-6 FAQ questions only
9. Maximum 5 restrictions
10. No emojis, use hyphens not em dashes

## Known Clients

These domains trigger special guidelines automatically:

| Domain | Client | Special Rules |
|--------|--------|---------------|
| healthworkstx.com | HealthWorks | No pricing, no insurance, include Orthospinology |
| cell-gate.com | CellGate | No direct sales, route to dealers |
| aim-companies.com | AIM Companies | US English, include 4-criteria test |

## Project Structure

```
Content Brief Creator/
├── app.py                      # Main Streamlit application
├── ai_provider.py              # Multi-AI provider abstraction
├── brief_generator.py          # AI-powered brief generation
├── document_formatter.py       # Word document creation
├── web_researcher.py           # Website research & link discovery
├── prompts.py                  # AI system prompts
├── validators.py               # Validation functions
├── client_guidelines.py        # Known client rules
├── supabase_client_manager.py  # Database operations
├── requirements.txt            # Python dependencies
├── supabase_schema.sql         # Database schema
├── .env.example                # Environment template
└── README.md                   # This file
```

## Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| OPENAI_API_KEY | One AI key required | OpenAI API key |
| CLAUDE_API_KEY | One AI key required | Anthropic Claude key |
| GROK_API_KEY | Optional | xAI Grok key |
| PERPLEXITY_API_KEY | Optional | Perplexity API key |
| MISTRAL_API_KEY | Optional | Mistral API key |
| DEFAULT_AI_PROVIDER | Optional | Default provider (openai) |
| SUPABASE_URL | Optional | Supabase project URL |
| SUPABASE_KEY | Optional | Supabase anon key |

### Supabase Setup (Optional)

For client profile storage:

1. Create a Supabase project at [supabase.com](https://supabase.com)
2. Run the SQL in `supabase_schema.sql` in the SQL Editor
3. Add your project URL and anon key to `.env`

## Deployment

### Streamlit Community Cloud (Free)

1. Push to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repository
4. Add API keys in app settings under "Secrets"

### Local Development

```bash
# Run with hot reload
streamlit run app.py

# Run on different port
streamlit run app.py --server.port 8080
```

## Troubleshooting

### "No AI providers available"
- Check that at least one API key is set in `.env` or Streamlit secrets
- Verify the API key format (no quotes, no spaces)

### "Could not fetch website"
- Verify the URL is accessible
- Some sites block automated requests
- Try with a different website

### "Only found X internal links"
- The website may have limited public pages
- Use manual link entry if needed

### Document not generating
- Check that `python-docx` is installed
- Verify write permissions in the output directory

## Dependencies

- **streamlit**: Web application framework
- **python-docx**: Word document generation
- **openai**: OpenAI API client
- **anthropic**: Claude API client
- **supabase**: Database client
- **requests**: HTTP requests
- **beautifulsoup4**: HTML parsing
- **python-dotenv**: Environment variables

## License

Proprietary software for Ghost Rank content production.

## Author

Built for Ghost Rank content production workflow.
