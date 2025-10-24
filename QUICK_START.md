# Quick Start Guide - Local Desktop Use

This guide gets you up and running with the Content Brief Creator on your Windows desktop.

## First Time Setup (5 minutes)

### Step 1: Install Python (if not already installed)

1. Download Python 3.8+ from [python.org/downloads](https://www.python.org/downloads/)
2. **IMPORTANT**: Check "Add Python to PATH" during installation
3. Restart your computer after installation

### Step 2: Set Up Your API Keys

1. Open the project folder in File Explorer
2. Find the file named `.env.example`
3. Make a copy and rename it to `.env` (remove the `.example` part)
4. Open `.env` in Notepad
5. Add at least one AI provider API key:

```
# Add your actual API key here (remove "your_" part)
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxx
# OR
CLAUDE_API_KEY=sk-ant-xxxxxxxxxxxxx
# OR
PERPLEXITY_API_KEY=pplx-xxxxxxxxxxxxx
# OR
MISTRAL_API_KEY=xxxxxxxxxxxxx

# Choose your default provider
DEFAULT_AI_PROVIDER=openai
```

6. Save and close the file

### Step 3: Launch the App

**Double-click** `Launch Brief Creator.bat`

That's it! The app will:
- ✅ Install dependencies automatically (first time only)
- ✅ Check your API keys
- ✅ Open in your browser at `http://localhost:8501`

## Daily Use

1. **Double-click** `Launch Brief Creator.bat`
2. Browser opens automatically
3. Create/load client profiles
4. Generate briefs
5. Download Word documents

**To close**: Press `Ctrl+C` in the command window, or just close the window.

## Where Is Everything Stored?

### Client Profiles
**Location:** `clients/` folder (JSON files)

Each client gets their own file:
- `clients/castle_surveys.json`
- `clients/acme_corp.json`
- etc.

**Backup Tip:** Copy the entire `clients/` folder to backup your client data.

### Generated Briefs
**Location:** Downloads folder (via browser download)

You can also find them in `output_briefs/` if generated via CLI.

### Your API Keys
**Location:** `.env` file (in project root)

**SECURITY:** Never share this file! It contains your private API keys.

## Troubleshooting

### "Python is not installed"
- Install Python from python.org
- Make sure "Add to PATH" was checked
- Restart computer
- Try again

### "ERROR: Failed to install dependencies"
- Open Command Prompt as Administrator
- Navigate to project folder: `cd "C:\path\to\Content Brief Creator"`
- Run: `pip install -r requirements.txt`

### ".env file not found"
- Copy `.env.example` to `.env`
- Add your API keys
- Try again

### "No AI providers available"
- Open `.env` file
- Check that you have at least one API key
- Make sure the key starts with the correct prefix:
  - OpenAI: `sk-proj-` or `sk-`
  - Claude: `sk-ant-`
  - Perplexity: `pplx-`
- Save the file
- Restart the app

### Browser doesn't open automatically
- Manually open your browser
- Go to: `http://localhost:8501`

### "Port already in use"
- Another Streamlit app is running
- Close all command windows
- Try again

## Features

### Client Management
- **Create**: Add new client profiles with all their requirements
- **Load**: Select existing clients from dropdown
- **View**: See complete client details in sidebar
- **Storage**: All data saved locally in `clients/` folder

### Brief Generation
- Choose from 4 AI providers (OpenAI, Claude, Perplexity, Mistral)
- Enter topic, keywords
- Generate complete 12-section brief
- Download formatted Word document

### Offline Work
- Client profiles work offline
- Only need internet when generating briefs (AI API calls)

## Tips

1. **Keep it running**: Leave the command window open while working
2. **Multiple tabs**: Open multiple browser tabs to compare briefs
3. **Backup regularly**: Copy `clients/` folder to your backup location
4. **Update profiles**: Edit JSON files in `clients/` folder directly if needed

## Need Help?

- Check this guide first
- Review `README.md` for detailed documentation
- Check the command window for error messages
- Ensure API keys are valid and have credits

---

**Ready to create briefs!** Just double-click `Launch Brief Creator.bat` and start working.
