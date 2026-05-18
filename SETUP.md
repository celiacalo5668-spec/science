# Automated Weekly Content — Setup Guide

Every Friday at noon UTC, GitHub Actions will:
1. Search the web for the best recent articles on all 6 topics
2. Generate 6 new article pages using Claude AI
3. Commit them to GitHub automatically
4. Netlify sees the commit and auto-deploys → live on scienceofwellness.com

Estimated weekly API cost: ~$0.30–0.80 (6 Claude Opus calls with web search).

---

## Step 1 — Create a GitHub Account

Go to **github.com** → Sign Up (free).

---

## Step 2 — Create a Repository

1. Click the **+** icon (top right) → **New repository**
2. Name it: `scienceofwellness`
3. Set to **Public** (required for free GitHub Pages/Actions)
4. Click **Create repository**

---

## Step 3 — Upload Your Site Files

On the new repository page, click **uploading an existing file** (or drag and drop).

Upload the entire `scienceofwellness` folder contents:
- `index.html`
- `css/` folder
- `js/` folder
- `articles/` folder
- `scripts/` folder
- `.github/` folder
- `data/` folder

Click **Commit changes**.

---

## Step 4 — Get an Anthropic API Key

1. Go to **console.anthropic.com**
2. Sign up / log in
3. Click **API Keys** in the sidebar
4. Click **Create Key** → copy it (you won't see it again)

Add a payment method — you get some free credits, and after that it's pay-as-you-go.
Weekly runs cost roughly $0.30–0.80 depending on article length.

---

## Step 5 — Add the API Key as a GitHub Secret

1. Go to your GitHub repository
2. Click **Settings** (top menu)
3. In the left sidebar: **Secrets and variables** → **Actions**
4. Click **New repository secret**
5. Name: `ANTHROPIC_API_KEY`
6. Value: paste your API key
7. Click **Add secret**

---

## Step 6 — Connect Netlify to GitHub (switch from drag-and-drop)

This makes Netlify auto-deploy every time GitHub gets new articles.

1. Log into **netlify.com**
2. Go to your site → **Site configuration** → **Build & deploy**
3. Under **Continuous deployment**, click **Link repository**
4. Choose **GitHub** → authorize → select `scienceofwellness`
5. Build settings:
   - Build command: *(leave empty)*
   - Publish directory: `.`  (just a dot — the root)
6. Click **Deploy**

From now on, every git commit triggers a Netlify rebuild automatically.

---

## Step 7 — Test It (Optional but Recommended)

Don't want to wait until Friday? Trigger it manually:

1. Go to your GitHub repo → **Actions** tab
2. Click **Weekly Content Update** in the left list
3. Click **Run workflow** → **Run workflow**
4. Watch it run — takes 3–5 minutes
5. Check your `articles/` folder for 6 new pages!

---

## What Gets Generated Each Week

Each Friday, the script researches and writes **6 new articles** — one per topic:
- Wim Hof / Cold Therapy
- Breathwork & Pranayama
- Sound Healing
- Iboga & Plant Medicine
- MDMA Therapy
- Fascia & Somatic Healing

After 1 year: **300+ articles** building a deep wellness knowledge base.

---

## Troubleshooting

**Actions tab shows a red X:**
- Click the failed run → read the error log
- Most common cause: API key not set correctly as a secret

**Netlify not auto-deploying:**
- Make sure you linked the GitHub repo in Netlify (Step 6)
- Check Netlify dashboard for deploy logs

**Want to add more topics?**
- Edit `scripts/fetch_articles.py`
- Add a new entry to the `TOPICS` list with `id`, `name`, `queries`, `gradient`, and `related`
