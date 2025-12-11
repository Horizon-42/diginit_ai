# Dignit AI — Frontend

A small React (Vite) frontend providing a chat UI to help immigrants and refugees with legal and insurance questions. This project includes a mock response engine by default. Optional OpenAI integration is supported for prototype/testing (NOT recommended in production without a backend proxy).

Quick start

1. Install dependencies

```bash
cd frontend
npm install
```

2. (Optional) Add an OpenAI key for prototypes

Create a `.env` file in `frontend/` with:

```text
VITE_OPENAI_API_KEY=your_openai_api_key_here
```

Warning: any key placed in frontend env files will be bundled into the client and can be discovered by users. For production, create a backend endpoint that stores the API key server-side and forwards requests.

3. Run dev server

```bash
npm run dev
```

Notes and next steps

- The app runs in mock mode out-of-the-box. If you set `VITE_OPENAI_API_KEY` the client will attempt to call OpenAI's chat completions API.
- Add a backend service for secure AI usage and to implement logging, rate limits, and safety filters.
- This frontend includes a clear disclaimer that it does not provide legal advice. Integrate local resource links and accredited organizations for each target country.
