import requests
import json
import feedparser
from config import JSEARCH_API_KEY
from config import ADZUNA_APP_ID, ADZUNA_APP_KEY
from config import LINKEDIN_RSS_FEEDS, QUERIES
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, SCHEDULER_INTERVAL_HOURS

def load_seen_jobs():
    """Load the set of job IDs that have already been seen."""
    try:
        with open("seen.json", "r") as f:
            content = f.read().strip()
            if not content:
                return set()
            return set(json.loads(content))
    except (FileNotFoundError, json.JSONDecodeError):
        return set()

def save_seen_jobs(seen_ids):
    """Save the set of seen job IDs to seen.json."""
    with open("seen.json", "w") as f:
        json.dump(list(seen_ids), f)

def is_relevant(job):
    title = (
        job.get("title")
        or job.get("job_title")
        or ""
    ).lower()

    fresher_keywords = [
        "fresher", "intern", "junior", "entry",
        "trainee", "graduate", "beginner",
        "associate", "sde 1", "engineer i"
    ]

    role_keywords = [
        "software", "developer", "engineer",
        "ai", "ml", "data", "web",
        "frontend", "backend", "full stack",
        "python", "java"
    ]

    has_role = any(r in title for r in role_keywords)
    has_level = any(f in title for f in fresher_keywords)

    return has_role and (has_level or "intern" in title)

def get_apply_link(job):
    """Extract the apply link based on job_apply_is_direct flag and apply_options."""
    if job.get("job_apply_is_direct"):
        # If direct apply link exists, use it
        return job.get("job_apply_link")
    else:
        # If not direct, get from apply_options list
        apply_options = job.get("apply_options", [])
        if apply_options:
            # Prefer direct links, then return first available
            for option in apply_options:
                if option.get("is_direct"):
                    return option.get("apply_link")
            # If no direct link in options, return first option
            return apply_options[0].get("apply_link")
        # Fallback to job_apply_link
        return job.get("job_apply_link")

def get_jsearch_jobs(query="developer jobs in india", seen_ids=None, page=1, num_pages=1):
    """Fetch jobs from JSearch API for India and filter out already seen jobs."""
    if seen_ids is None:
        seen_ids = set()
    
    url = "https://jsearch.p.rapidapi.com/search"
    
    querystring = {
        "query": query,
        "page": str(page),
        "num_pages": str(num_pages),
        "date_posted": "all",
        "country": "in",
        "language": "en"
    }

    headers = {
        "X-RapidAPI-Key": JSEARCH_API_KEY,
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)
    data = response.json()

    new_jobs = []
    
    for job in data.get("data", []):
        job_id = job.get("job_id")
        
        # Skip if we've already seen this job
        if job_id in seen_ids:
            continue
        
        # Check if job is relevant
        if not is_relevant(job):
            continue
        
        seen_ids.add(job_id)
        
        new_jobs.append({
            "id": job_id,
            "title": job.get("job_title"),
            "company": job.get("employer_name"),
            "employment_type": job.get("job_employment_type_text"),
            "is_direct": job.get("job_apply_is_direct"),
            "apply_link": get_apply_link(job),
            "apply_options": job.get("apply_options", []),
            "location": job.get("job_location"),
            "is_remote": job.get("job_is_remote"),
            "salary_min": job.get("job_min_salary"),
            "salary_max": job.get("job_max_salary"),
            "salary_currency": job.get("job_salary_currency"),
            "posted_at": job.get("job_posted_human_readable"),
            "description": (job.get("job_description") or "")[:500],
            "benefits": job.get("job_benefits", [])
        })

    return new_jobs


def get_adzuna_jobs(query="developer jobs in india", seen_ids=None, page=1, results_per_page=10):
    """Fetch jobs from Adzuna API for India and filter out already seen jobs."""
    if seen_ids is None:
        seen_ids = set()
    
    location = "in"  # India location code for Adzuna
    
    url = f"https://api.adzuna.com/v1/api/jobs/{location}/search/{page}"

    params = {
        "app_id": ADZUNA_APP_ID,
        "app_key": ADZUNA_APP_KEY,
        "results_per_page": results_per_page,
        "what": query.replace(" jobs in ", " ").replace(" jobs", "")  # Clean up query
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
    except Exception as e:
        print(f"Error fetching from Adzuna: {e}")
        return []

    new_jobs = []
    
    for job in data.get("results", []):
        job_id = job.get("id")
        
        # Skip if we've already seen this job
        if job_id in seen_ids:
            continue
        
        # Check if job is relevant
        if not is_relevant(job):
            continue
        
        seen_ids.add(job_id)
        
        # Parse salary if available
        salary_min = None
        salary_max = None
        salary_currency = None
        
        if job.get("salary_min"):
            salary_min = int(job.get("salary_min"))
        if job.get("salary_max"):
            salary_max = int(job.get("salary_max"))
        if job.get("salary_currency"):
            salary_currency = job.get("salary_currency")
        
        new_jobs.append({
            "id": job_id,
            "title": job.get("title"),
            "company": job.get("company", {}).get("display_name") if isinstance(job.get("company"), dict) else job.get("company"),
            "employment_type": None,
            "is_direct": True,
            "apply_link": job.get("redirect_url"),
            "apply_options": [],
            "location": job.get("location", {}).get("display_name") if isinstance(job.get("location"), dict) else job.get("location"),
            "is_remote": False,
            "salary_min": salary_min,
            "salary_max": salary_max,
            "salary_currency": salary_currency,
            "posted_at": job.get("created"),
            "description": (job.get("description") or "")[:500],
            "benefits": []
        })

    return new_jobs


def get_linkedin_rss_jobs(seen_ids=None):
    """Fetch jobs from LinkedIn RSS feeds and filter out already seen jobs."""
    if seen_ids is None:
        seen_ids = set()
    
    new_jobs = []
    
    for feed_url in LINKEDIN_RSS_FEEDS:
        try:
            print(f"Fetching from LinkedIn RSS: {feed_url[:80]}...")
            feed = feedparser.parse(feed_url)
            
            for entry in feed.entries:
                # LinkedIn RSS entries use a unique ID format
                job_id = entry.get("id", entry.get("link", ""))
                
                # Skip if we've already seen this job
                if job_id in seen_ids:
                    continue
                
                # Parse job details from RSS entry
                title = entry.get("title", "")
                summary = entry.get("summary", "")
                link = entry.get("link", "")
                published = entry.get("published", "")
                
                # Create a temporary job object for relevance check
                temp_job = {"title": title}
                
                # Check if job is relevant
                if not is_relevant(temp_job):
                    continue
                
                seen_ids.add(job_id)
                
                # Extract company name from summary
                company = extract_company_from_summary(summary)
                
                new_jobs.append({
                    "id": job_id,
                    "title": title,
                    "company": company,
                    "employment_type": None,
                    "is_direct": True,
                    "apply_link": link,
                    "apply_options": [],
                    "location": "India",
                    "is_remote": None,
                    "salary_min": None,
                    "salary_max": None,
                    "salary_currency": None,
                    "posted_at": published,
                    "description": (summary or "")[:500],
                    "benefits": []
                })
        except Exception as e:
            print(f"Error fetching LinkedIn RSS feed: {e}")
            continue
    
    return new_jobs


def extract_company_from_summary(summary):
    import re
    import html

    clean = html.unescape(summary)
    clean = re.sub(r'<[^>]+>', '', clean)

    # Try pattern: "Company: XYZ"
    match = re.search(r'Company[:\-]\s*(.+)', clean, re.IGNORECASE)
    if match:
        return match.group(1).strip()

    # Fallback: first meaningful line
    for line in clean.split("\n"):
        line = line.strip()
        if 2 < len(line) < 60:
            return line

    return "Unknown"


def send_telegram_message(message):
    """Send a plain text message to Telegram. Returns True on success."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "disable_web_page_preview": True
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.status_code == 200
    except Exception:
        return False


def notify_jobs_via_telegram(jobs, jobs_per_message=10):
    """Send all jobs via Telegram using multiple messages."""
    if not jobs:
        return False

    total_jobs = len(jobs)
    total_chunks = (total_jobs + jobs_per_message - 1) // jobs_per_message
    all_sent = True

    for chunk_idx in range(total_chunks):
        start = chunk_idx * jobs_per_message
        end = min(start + jobs_per_message, total_jobs)
        batch = jobs[start:end]

        lines = [
            f"🚀 {total_jobs} new jobs found",
            f"📦 Batch {chunk_idx + 1}/{total_chunks}",
            ""
        ]

        for idx, job in enumerate(batch, start + 1):
            title = job.get("title") or "Untitled"
            company = job.get("company") or "Unknown"
            location = job.get("location") or "Unknown"
            apply_link = job.get("apply_link") or ""
            lines.append(f"{idx}. {title} - {company} ({location})")
            if apply_link:
                lines.append(apply_link)
            lines.append("")

        message = "\n".join(lines).strip()
        sent = send_telegram_message(message)
        if not sent:
            all_sent = False

    return all_sent


def get_all_jobs(jsearch_pages=1, adzuna_results=10):
    """Fetch jobs from JSearch, Adzuna, and LinkedIn RSS feeds combined for India.
    
    Loads seen jobs once at start, passes through all functions, saves once at end.
    """
    all_jobs = []
    
    # Load seen job IDs ONCE at the beginning
    seen_ids = load_seen_jobs()
    
    # Fetch from multiple queries
    for query in QUERIES:
        print(f"\n{'='*70}")
        print(f"Searching for: {query}")
        print(f"{'='*70}")
        
        # JSearch
        print(f"  → Fetching from JSearch...")
        jsearch_jobs = get_jsearch_jobs(query=query, seen_ids=seen_ids, page=1, num_pages=jsearch_pages)
        all_jobs.extend(jsearch_jobs)
        print(f"    Found {len(jsearch_jobs)} new jobs from JSearch")
        
        # Adzuna
        print(f"  → Fetching from Adzuna...")
        adzuna_jobs = get_adzuna_jobs(query=query, seen_ids=seen_ids, page=1, results_per_page=adzuna_results)
        all_jobs.extend(adzuna_jobs)
        print(f"    Found {len(adzuna_jobs)} new jobs from Adzuna")
    
    # Fetch from LinkedIn RSS feeds (once, not per query)
    print(f"\n{'='*70}")
    print(f"Fetching from LinkedIn RSS feeds")
    print(f"{'='*70}")
    linkedin_jobs = get_linkedin_rss_jobs(seen_ids=seen_ids)
    all_jobs.extend(linkedin_jobs)
    print(f"Found {len(linkedin_jobs)} new jobs from LinkedIn RSS")
    
    # Save seen job IDs ONCE at the end
    save_seen_jobs(seen_ids)
    
    return all_jobs


def print_jobs(jobs):
    """Pretty print job results."""
    print(f"\n{'='*70}")
    print(f"SUMMARY: Found {len(jobs)} total new jobs from all sources")
    print(f"{'='*70}\n")
    
    for idx, job in enumerate(jobs, 1):
        print(f"{idx}. {job['title']} at {job['company']}")
        print(f"   Location: {job['location']} (Remote: {job['is_remote']})")
        if job['employment_type']:
            print(f"   Type: {job['employment_type']}")
        if job['salary_min'] and job['salary_max']:
            currency = job['salary_currency'] or "INR"
            print(f"   Salary: {currency} {job['salary_min']} - {job['salary_max']}")
        print(f"   Apply: {job['apply_link']}")
        print()


if __name__ == "__main__":
    import sys
    
    # Check if running in scheduler mode
    if '--scheduler' in sys.argv or '-s' in sys.argv:
        # Production mode: start background scheduler
        print(f"Starting Job Fetcher in PRODUCTION mode (scheduled every {SCHEDULER_INTERVAL_HOURS} hours)...")
        from apscheduler.schedulers.background import BackgroundScheduler
        from apscheduler.triggers.interval import IntervalTrigger
        import logging
        import time
        
        # Configure logging for production
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('job_fetcher.log'),
                logging.StreamHandler()
            ]
        )
        logger = logging.getLogger(__name__)
        
        def scheduled_job_fetch():
            """Fetch jobs and handle errors gracefully."""
            try:
                logger.info("🔄 Starting scheduled job fetch...")
                jobs = get_all_jobs(jsearch_pages=1, adzuna_results=10)
                logger.info(f"✅ Successfully fetched {len(jobs)} new jobs")
                if jobs:
                    logger.info("New jobs found:")
                    for job in jobs[:5]:  # Log first 5
                        logger.info(f"  - {job['title']} at {job['company']}")

                    sent = notify_jobs_via_telegram(jobs)
                    if sent:
                        logger.info("📨 Telegram notification sent")
                    else:
                        logger.info("ℹ️ Telegram notification skipped or failed")
            except Exception as e:
                logger.error(f"❌ Error during job fetch: {str(e)}", exc_info=True)
        
        scheduler = BackgroundScheduler()
        scheduler.add_job(
            scheduled_job_fetch,
            trigger=IntervalTrigger(hours=SCHEDULER_INTERVAL_HOURS),
            id='job_fetcher',
            name='Job Fetcher',
            replace_existing=True
        )
        scheduler.start()
        logger.info(f"🚀 Job scheduler started - fetching every {SCHEDULER_INTERVAL_HOURS} hours")
        
        try:
            while True:
                time.sleep(1)
        except (KeyboardInterrupt, SystemExit):
            logger.info("Shutting down scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler stopped.")
    else:
        # Development mode: fetch once and display
        print("Starting Job Fetcher in DEVELOPMENT mode (single fetch)...")
        jobs = get_all_jobs(jsearch_pages=1, adzuna_results=10)
        print_jobs(jobs)
        if jobs:
            sent = notify_jobs_via_telegram(jobs)
            if sent:
                print("📨 Telegram notification sent")
            else:
                print("ℹ️ Telegram notification skipped or failed")