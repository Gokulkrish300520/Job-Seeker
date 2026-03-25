"""
Job scheduler for automated job fetching.
Suitable for production deployment.
"""

import logging
import time
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from main import get_all_jobs, notify_jobs_via_telegram
from config import SCHEDULER_INTERVAL_HOURS

# Configure logging
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
        
        logger.info(f"✅ Successfully fetched {len(jobs)} new jobs at {datetime.now()}")
        
        if jobs:
            logger.info(f"\nNew jobs found:")
            for job in jobs[:5]:  # Log first 5
                logger.info(f"  - {job['title']} at {job['company']} ({job['location']})")
            if len(jobs) > 5:
                logger.info(f"  ... and {len(jobs) - 5} more jobs")

            sent = notify_jobs_via_telegram(jobs)
            if sent:
                logger.info("📨 Telegram notification sent")
            else:
                logger.info("ℹ️ Telegram notification skipped or failed")
        else:
            logger.info("No new jobs found in this fetch cycle.")
            
    except Exception as e:
        logger.error(f"❌ Error during job fetch: {str(e)}", exc_info=True)

def start_scheduler(interval_hours=None):
    """Start the background scheduler.
    
    Args:
        interval_hours: How often to run the job fetcher (default: from config)
    """
    if interval_hours is None:
        interval_hours = SCHEDULER_INTERVAL_HOURS
    
    scheduler = BackgroundScheduler()
    
    # Add the job
    scheduler.add_job(
        scheduled_job_fetch,
        trigger=IntervalTrigger(hours=interval_hours),
        id='job_fetcher',
        name='Job Fetcher',
        replace_existing=True
    )
    
    # Start the scheduler
    scheduler.start()
    logger.info(f"🚀 Job scheduler started - jobs will be fetched every {interval_hours} hours")
    logger.info(f"First fetch scheduled at: {scheduler.get_job('job_fetcher').next_run_time}")
    
    return scheduler

if __name__ == "__main__":
    # For testing: run scheduler interactively
    try:
        scheduler = start_scheduler()
        logger.info("Scheduler running. Press Ctrl+C to stop...")
        
        # Keep the scheduler running
        while True:
            time.sleep(1)
            
    except (KeyboardInterrupt, SystemExit):
        logger.info("Shutting down scheduler...")
        scheduler.shutdown()
        logger.info("Scheduler stopped.")
