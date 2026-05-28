import time
import logging
from apscheduler.schedulers.blocking import BlockingScheduler
from run_scraper import run_all_tasks

# Configure logging to see scheduler activity
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ScraperScheduler")

def job():
    logger.info("Starting scheduled daily scrape task...")
    try:
        run_all_tasks()
        logger.info("Daily scrape task completed successfully.")
    except Exception as e:
        logger.error(f"Error during daily scrape task: {e}")

if __name__ == "__main__":
    scheduler = BlockingScheduler()
    
    # Schedule the job to run every day at 8:00 AM
    scheduler.add_job(job, 'cron', hour=8, minute=0)
    
    logger.info("Scheduler started. The scraper will run every morning at 8:00 AM.")
    
    # Run once immediately on start
    job()
    
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler stopped.")
