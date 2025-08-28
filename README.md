# Phase1 SERP Intent API

FastAPI service to:
1. Accept 5–10 seed keywords
2. Query [SearchAPI.io](https://www.searchapi.io/docs/google) for top ~30 SERP results
3. Extract exact/semantic terms, action modifiers, disambiguators
4. Generate a concise 2-sentence, gotchas-safe description

## Deploy on Render
1. Push this repo to GitHub
2. Create new Web Service on [Render](https://dashboard.render.com/)
3. Connect repo → Python → Starter plan
4. Build command:
