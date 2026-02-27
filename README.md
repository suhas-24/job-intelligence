# 🌍 Global Job Intelligence Tracker

A free, LLM-orchestrated global job/hiring/layoffs tracker built for OpenClaw.

## ⚡ Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Copy env and configure (optional)
cp .env.example .env
# Edit .env with your API keys

# 3. Run the pipeline
python3 run.py
```

## 📁 Project Structure

```
job-intelligence-tracker/
├── config/
│   ├── sources.yaml       # All 80+ source definitions
│   └── schema.json        # Global unified schema
├── ingest/
│   ├── apis/              # Free API fetchers
│   │   ├── fetch_jobs.py  # RemoteOK, Himalayas, Jobicy, Arbeitnow
│   │   └── jsearch.py     # JSearch (needs API key)
│   └── layoffs/           # Layoff tracker scrapers
├── normalize/
│   └── normalizer.py      # Classification + dedup
├── reports/
│   └── daily_report.py    # Markdown/HTML report generator
├── storage/
│   ├── supabase_client.py # Supabase integration
│   └── notifications.py   # Telegram/Discord/Slack alerts
├── dashboard/
│   └── app.py             # Streamlit dashboard
├── data/                  # Output files
├── openclaw_skill/        # OpenClaw skill wrapper
└── run.py                 # Main runner
```

## 📊 Current Sources (Free)

### Core APIs (No Key Required)
| Source | Regions | Notes |
|--------|---------|-------|
| RemoteOK | Global | Remote jobs |
| Himalayas | US/EU/India | Remote jobs |
| Jobicy | Global | Remote jobs |
| Arbeitnow | EU/US | Remote + local |

### With API Key (Free Tier)
| Source | Free Tier | Regions |
|--------|-----------|---------|
| JSearch | 200/month | India, US, Global |

### Layoff Trackers
| Source | Coverage |
|--------|----------|
| Layoffs.fyi | Global tech |
| TrueUp | Real-time |
| Peerlist | Tech + startups |

## 🔧 Configuration

### Environment Variables

```bash
# JSearch (free: 200 requests/month)
# Get key: https://www.openwebninja.com/api/jsearch
JSEARCH_API_KEY=your_key_here

# Supabase (free: 500MB DB)
# Get from: https://supabase.com > Settings > API
SUPABASE_URL=your_project_url
SUPABASE_KEY=your_anon_key

# Telegram (optional)
TELEGRAM_BOT_TOKEN=xxx
TELEGRAM_CHAT_ID=xxx

# Discord (optional)
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/xxx
```

## 🚀 Deployment

### Local Run
```bash
python3 run.py
```

### Streamlit Dashboard
```bash
pip install streamlit
streamlit run dashboard/app.py
```

### Deploy to Streamlit Cloud (Free)
1. Push to GitHub
2. Go to https://streamlit.io/cloud
3. Connect GitHub repo
4. Deploy!

### OpenClaw Cron (Daily)
```bash
# Set cron to run at 00:00 UTC daily
0 0 * * * cd /path/to/job-intelligence-tracker && python3 run.py
```

## 📈 Output

### JSON (data/unified_output.json)
```json
{
  "run_timestamp": "2026-02-27T12:00:00Z",
  "metrics": {
    "global": {
      "total_events": 1247,
      "hiring_count": 1156,
      "layoffs_count": 91
    },
    "by_market": {
      "US": {"openings": 523, "layoffs": 45},
      "India": {"openings": 312, "layoffs": 23}
    }
  },
  "events": [...]
}
```

### Markdown Report
```markdown
# 📊 Global Job Intelligence Report

| Metric | Count |
|--------|-------|
| Total Events | 1,247 |
| Hiring Openings | 1,156 |
| Layoffs | 91 |
```

## 🔜 Roadmap

- [x] Core APIs (RemoteOK, Himalayas, Jobicy)
- [x] Layoff trackers
- [x] Normalization + dedup
- [x] Reports (MD/HTML)
- [x] JSearch integration
- [x] Supabase storage
- [x] Streamlit dashboard
- [ ] Telegram/Discord alerts
- [ ] India portals (Naukri via Apify)
- [ ] US/EU portal scrapers
- [ ] 70+ company career RSS feeds
- [ ] LLM-based enrichment

## 📝 License

MIT - Built for Suhaz's SRE/AI job search 🚀
