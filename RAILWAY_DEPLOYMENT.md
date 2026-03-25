# Railway Deployment Guide

Railway is a modern cloud platform with generous free credits and simplified deployment for background workers. Perfect for your job fetcher scheduler.

## Prerequisites

1. **GitHub Account** - Your code repository must be pushed to GitHub
2. **Railway Account** - Sign up at [railway.app](https://railway.app)
3. **Environment Variables** - Your API keys ready:
   - `JSEARCH_API_KEY`
   - `ADZUNA_APP_ID`
   - `ADZUNA_APP_KEY`
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`

## Step 1: Push Code to GitHub

```bash
cd /Users/gokuljayakumar/Desktop/projects/Job_seek
git add .
git commit -m "Prepare for Railway deployment"
git push origin main
```

## Step 2: Create Railway Project

1. Go to [railway.app](https://railway.app) and sign in with GitHub
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Authorize Railway to access your GitHub account
5. Select `Gokulkrish300520/Job-Seeker` repository
6. Click **"Deploy Now"**

## Step 3: Configure the Worker

Railway will auto-detect Python and install dependencies from `requirements.txt`.

**For the start command:**

1. Go to your Railway project dashboard
2. Click on the **Job-Seeker** service
3. Go to **"Settings"** tab
4. Set **Start Command** to:
   ```
   python scheduler.py
   ```

## Step 4: Add Environment Variables

In your Railway project dashboard:

1. Click on **Job-Seeker** service
2. Go to **"Variables"** section
3. Add the following variables:

| Key                        | Value                              |
| -------------------------- | ---------------------------------- |
| `JSEARCH_API_KEY`          | Your JSearch API key from RapidAPI |
| `ADZUNA_APP_ID`            | Your Adzuna App ID                 |
| `ADZUNA_APP_KEY`           | Your Adzuna App Key                |
| `TELEGRAM_BOT_TOKEN`       | Your Telegram Bot Token            |
| `TELEGRAM_CHAT_ID`         | Your Telegram Chat ID              |
| `SCHEDULER_INTERVAL_HOURS` | `24`                               |
| `PYTHONUNBUFFERED`         | `1`                                |

4. Click **"Deploy"** to apply changes

## Step 5: Verify Deployment

1. Go to **"Deployments"** tab in Railway dashboard
2. Watch for successful build (green checkmark)
3. Check **"Logs"** to see the scheduler starting:
   ```
   🚀 Job scheduler started - jobs will be fetched every 24 hours
   First fetch scheduled at: ...
   ```

## Step 6: Monitor Execution

Railway will keep logs for:

- Job fetch cycles
- Telegram notifications
- Any errors

To view logs:

1. Click on your service in Railway dashboard
2. Go to **"Logs"** tab
3. Logs appear in real-time

You should see a successful fetch every 24 hours with Telegram notifications.

## Important Notes

### Free Tier Benefits

- **5GB of storage** (for logs and data)
- **500 hours/month of execution** (sufficient for your 24-hour scheduler)
- **$5 free monthly credit** to start
- Very affordable after free tier

### Data Persistence

Unlike Render, Railway provides persistent file storage so `seen.json` will survive worker restarts. This means **no duplicate job notifications**.

### Logs

- Railway stores logs automatically
- Can be accessed from dashboard
- Downloadable for archive

### Monitoring

- Real-time logs visible
- Deployment history tracking
- Automatic rebuilds on GitHub push

## Troubleshooting

**Jobs not fetching?**

- Check environment variables in Railway Variables section
- Verify Telegram credentials are correct
- Check logs for API errors

**Worker keeps restarting?**

- Check syntax in `scheduler.py`
- Review Python errors in logs
- Ensure all dependencies in `requirements.txt`

**No Telegram messages?**

- Verify `TELEGRAM_BOT_TOKEN` is correct
- Check if bot is started and has correct chat ID
- Look for API errors in Railway logs

## Deployment Cost

Initially free with $5 credit. After that:

- Background worker: ~$0.29/day (very affordable)
- Railway is one of the cheapest platforms for this use case

For 24-hour scheduling: approximately **$8-10/month** (less expensive than alternatives)

## Next Steps

1. Deploy now and watch the logs
2. First fetch should appear within 5 minutes
3. Subsequent fetches every 24 hours automatically
4. Enjoy hands-free job notifications! 🎉
