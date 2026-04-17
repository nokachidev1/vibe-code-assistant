# Vibe Code Assistant 🤖✨

A unified coding assistant that seamlessly integrates Claude, OpenAI, Grok, and Gemini AI models in one place.

## Features

- Multi-AI support (Claude, OpenAI, Grok, Gemini)
- Interactive mode for per-session AI selection
- CLI support for direct AI specification
- Simple .env-based configuration

## Requirements

### OS-level
- Python 3.8 or higher

### Python Dependencies
- anthropic
- openai
- google-generativeai

## Installation

1. Clone the repository
2. Install Python dependencies:
   ```bash
   pip install anthropic openai google-generativeai
   ```

## Setup

Create a `.env` file in the project root with your API keys:

```env
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
XAI_API_KEY=xai-...
GEMINI_API_KEY=AIza...
```

For detailed instructions on obtaining these keys:
- [Anthropic (Claude)](https://console.anthropic.com/)
- [OpenAI](https://platform.openai.com/account/api-keys)
- [xAI (Grok)](https://console.x.ai/)
- [Google (Gemini)](https://ai.google.dev/)

## Usage

### Interactive Mode
Run the assistant and select your preferred AI each session:
```bash
python vibe-code-assistant.py
```

### Direct AI Selection
Specify which AI to use:
```bash
python vibe-code-assistant.py --ai claude
python vibe-code-assistant.py --ai openai
python vibe-code-assistant.py --ai grok
python vibe-code-assistant.py --ai gemini
```

## Troubleshooting

- **Missing API Key Error**: Ensure all required keys are set in `.env`
- **Module Not Found**: Run `pip install anthropic openai google-generativeai`

## License

[Add your license here]

## Contributing

[Add contribution guidelines here]