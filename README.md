# Job Fetcher - Automated Job Search Engine for India

A Python-based job aggregator that scrapes freshers & junior developer positions from multiple sources including JSearch API, Adzuna, and LinkedIn RSS feeds. Designed for automated deployment with 4-hour interval fetching.

## Features

✅ **Multi-Source Job Aggregation**

- JSearch API (RapidAPI)
- Adzuna Job Board
- LinkedIn RSS Feeds (5 curated feeds)

✅ **Smart Job Filtering**

- Fresher/Junior level positions only
- Software engineer, Developer, ML, Data science roles
- India-based or Remote jobs
- Automatic duplicate detection

✅ **Automated Scheduling**

- Fetch jobs every 4 hours automatically
- Background scheduler with APScheduler
- Detailed logging with timestamps

✅ **Production Ready**

- Docker & Docker Compose support
- Environment variable configuration
- Persistent job deduplication (seen.json)
- Error handling and retry logic

## Installation

### Prerequisites

- Python 3.9+
- Required API keys:
  - JSearch API key from [RapidAPI](https://rapidapi.com/laimoon/api/jsearch)
  - Adzuna API credentials from [Developer Portal](https://developer.adzuna.com/)

### Local Setup

1. **Clone the repository**

   ```bash
   cd Job_seek
   ```

2. **Create virtual environment**

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure credentials**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   nano .env  # or use your preferred editor
   ```

## Usage

### Development Mode (Manual Fetch)

Run a single job fetch cycle and display results:

```bash
python main.py
```

Output example:

```
===========================================================================
Searching for: software engineer fresher india
===========================================================================
  → Fetching from JSearch...
    Found 12 new jobs from JSearch
  → Fetching from Adzuna...
    Found 8 new jobs from Adzuna

===========================================================================
Fetching from LinkedIn RSS feeds
===========================================================================
Found 5 new jobs from LinkedIn RSS

===========================================================================
SUMMARY: Found 25 total new jobs from all sources
===========================================================================

1. Software Engineer (Fresher) at TechCorp
   Location: Bangalore, India (Remote: True)
   Type: Full-time
   Salary: INR 400000 - 600000
   Apply: https://...

2. Junior Python Developer at StartupXYZ
   ...
```

### Production Mode (Automated Scheduling)

Run with automatic 4-hour interval fetching:

```bash
python main.py --scheduler
# or
python main.py -s
```

Features in production mode:

- Runs infinitely in background
- Fetches jobs every 4 hours automatically
- Logs all activity to `job_fetcher.log`
- Graceful shutdown with Ctrl+C

Example log output:

```
2024-01-15 14:23:00 - __main__ - INFO - 🚀 Job scheduler started - fetching every 4 hours
2024-01-15 14:23:00 - __main__ - INFO - 🔄 Starting scheduled job fetch...
2024-01-15 14:23:45 - __main__ - INFO - ✅ Successfully fetched 25 new jobs
2024-01-15 14:23:45 - __main__ - INFO - New jobs found:
2024-01-15 14:23:45 - __main__ - INFO -   - Software Engineer Fresher at TechCorp
...
2024-01-15 18:23:00 - __main__ - INFO - 🔄 Starting scheduled job fetch...
```

## Docker Deployment

### Using Docker Compose (Recommended)

1. **Set up environment**

   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   nano .env
   ```

2. **Deploy**

   ```bash
   docker-compose up -d
   ```

3. **View logs**

   ```bash
   docker-compose logs -f job-fetcher
   ```

4. **Stop service**
   ```bash
   docker-compose down
   ```

### Using Docker Directly

1. **Build image**

   ```bash
   docker build -t job-fetcher:latest .
   ```

2. **Run container**

   ```bash
   docker run -d \
     --name job-fetcher \
     --env-file .env \
     -v $(pwd)/data:/app/data \
     -v $(pwd)/seen.json:/app/seen.json \
     -v $(pwd)/job_fetcher.log:/app/job_fetcher.log \
     job-fetcher:latest
   ```

3. **View logs**
   ```bash
   docker logs -f job-fetcher
   ```

## Configuration

### Job Search Queries

Edit the `QUERIES` list in `config.py` to customize what jobs you're searching for:

```python
QUERIES = [
    "software engineer fresher india",
    "machine learning intern india",
    "frontend developer fresher india",
    "backend developer junior india",
    "data scientist intern india"
]
```

### LinkedIn RSS Feeds

Customize the `LINKEDIN_RSS_FEEDS` list in `config.py` to target specific roles or locations.

### Scheduler Interval

Change fetching frequency via `.env`:

```env
SCHEDULER_INTERVAL_HOURS=2  # Fetch every 2 hours instead of 4
```

### API Parameters

In `main.py`, adjust these parameters in the `get_all_jobs()` call:

- `jsearch_pages`: Number of pages to fetch from JSearch (default: 1, max: 10)
- `adzuna_results`: Number of results per query from Adzuna (default: 10, max: 50)

## File Structure

```
Job_seek/
├── main.py              # Core job fetching logic
├── config.py            # Configuration & API credentials
├── scheduler.py         # Standalone scheduler script
├── requirements.txt     # Python dependencies
├── .env.example        # Template for environment variables
├── .env                # Local environment variables (git-ignored)
├── Dockerfile          # Production Docker image
├── docker-compose.yml  # Docker Compose configuration
├── seen.json           # Persistent job ID tracker
├── job_fetcher.log     # Application logs (production mode)
└── README.md           # This file
```

## Job Deduplication

The system uses `seen.json` to track job IDs and prevent duplicates:

- Jobs are tracked by unique ID from each source
- `seen.json` persists across runs
- If a job is in `seen.json`, it won't be displayed again
- To reset and see all jobs again, delete `seen.json`

```bash
rm seen.json  # WARNING: Will show all previously seen jobs again
```

## Error Handling

The application gracefully handles:

- API timeouts and connection errors
- Empty JSON files
- Missing or invalid API keys
- RSS feed parsing errors
- Network interruptions in scheduler mode

Errors are logged with full stack traces in `job_fetcher.log`.

## Filtering Logic

Jobs must pass BOTH filters:

1. **Level Keywords** (fresher, junior, intern, etc.)
2. **Role Keywords** (software, developer, ML, data, etc.)

Example: "Software Engineer Fresher" ✅ passes both
Example: "Senior Manager" ❌ fails (no role keyword)
Example: "Developer" ❌ fails (no fresher keyword)

## API Quotas & Limits

- **JSearch**: 100 requests/month (RapidAPI free tier) → ~8 per day
- **Adzuna**: 10,000 requests/month free → ~333 per day
- **LinkedIn RSS**: No limits, but content may vary

## Troubleshooting

### No jobs found

- Check that API credentials in `.env` are correct
- Verify internet connection
- Check `job_fetcher.log` for errors
- Try running `python main.py` once to see detailed output

### Duplicate jobs showing

- Delete `seen.json` to reset tracking
- Check that both functions are receiving same `seen_ids` set

### Docker container keeps restarting

- Check logs: `docker-compose logs job-fetcher`
- Verify `.env` file exists and has valid credentials
- Check volume permissions for `/app/data`

### High memory usage

- Reduce `jsearch_pages` or `adzuna_results` parameters
- Docker compose limits memory to 512MB (configurable in `docker-compose.yml`)

## Performance Tips

1. **Optimize for your needs**
   - Reduce `QUERIES` list to fewer searches
   - Lower `jsearch_pages` and `adzuna_results` if fetching too often
   - Increase `SCHEDULER_INTERVAL_HOURS` if 4 hours is too frequent

2. **Parallel execution**
   - Multiple query searches run sequentially for stability
   - LinkedIn RSS fetches happen once (not per query)

3. **Caching**
   - Job deduplication means later fetches are very quick
   - Results are only returned if they're new

## Email Notifications (Future Feature)

Email configuration is ready in `.env`:

```env
EMAIL=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
RECEIVER=recipient@gmail.com
```

Integration coming soon to notify when new jobs are found.

## Contributing

To enhance this job fetcher:

1. Add more job boards (e.g., Indeed, Monster, AngelList)
2. Implement email notifications
3. Build web interface to view jobs
4. Add job recommendations based on profile
5. Create resume-to-job matching system

## License

MIT License - Feel free to use and modify

## Support

For issues or questions:

1. Check `job_fetcher.log` for error details
2. Verify all API keys are valid
3. Ensure internet connectivity
4. Check the Troubleshooting section above

---

**Last Updated**: 2024-01-15
**Status**: Production Ready ✅
