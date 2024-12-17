# AI Web Server

A simple web server with a centered text input interface built using Flask.

![Screenshot of the application](screenshot.png)

## Prerequisites

- Python 3.11 or higher
- Git
- OpenAI API key

## Setup Instructions

1. Clone the repository
```bash
git clone <repository-url>
cd ai-web-server
```

2. Install uv (if not already installed)
```bash
pip install uv
```

3. Create a virtual environment
```bash
uv venv
```

4. Activate the virtual environment
```bash
# MacOS
source .venv\scripts\activate

# Windows:
.venv\Scripts\activate
```

5. Install dependencies
```bash
uv pip install -e .
```

6. Set up your OpenAI API key:

   a. Get your API key:
   - Go to [OpenAI's website](https://platform.openai.com/signup)
   - Sign up for an account if you don't have one
   - Navigate to [API Keys](https://platform.openai.com/api-keys)
   - Click "Create new secret key"
   - Copy your API key (make sure to save it as it won't be shown again)

   b. Add your API key to the `.env` file in the project root:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

   Note: Replace `your_api_key_here` with your actual OpenAI API key

7. Run the server
```bash
uv run -m ai_web_server.app
```

## Accessing the Application

Once the server is running, open your web browser and navigate to `http://127.0.0.1:5000`

## Important Notes

- Never commit your `.env` file to version control
- Keep your API key secret and secure
- The free tier of OpenAI's API has rate limits and usage limits
- Monitor your API usage on OpenAI's dashboard to avoid unexpected charges

## Troubleshooting

If you encounter "Authentication Error" or similar:
1. Double-check your API key in the `.env` file
2. Ensure the `.env` file is in the correct location (project root)
3. Make sure you activated the virtual environment
4. Try restarting the server

For more information about OpenAI API:
- [OpenAI API Documentation](https://platform.openai.com/docs/introduction)
- [API Keys Management](https://platform.openai.com/api-keys)
- [Usage and Limits](https://platform.openai.com/docs/guides/rate-limits)
