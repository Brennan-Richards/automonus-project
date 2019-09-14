import logging

from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import register_events, register_job
from django.conf import settings
# Create scheduler to run in a thread inside the application process
scheduler = BackgroundScheduler(settings.SCHEDULER_CONFIG)


def start():
    print("scheduler was started")
    if settings.DEBUG:
        # Hook into the apscheduler logger
        logging.basicConfig()
        logging.getLogger('apscheduler').setLevel(logging.DEBUG)
        pass

    # Adding this job here instead of to crons.
    # This will do the following:
    # - Add a scheduled job to the job store on application initialization
    # - The job will execute a model class method at midnight each day
    # - replace_existing in combination with the unique ID prevents duplicate copies of the job
    scheduler.add_job("analysis:scheduled_jobs.accounts_snapshot.CreateAccountSnapshot", "interval", id="create_accounts_snapshots",
                      seconds=60, replace_existing=True)

    # Add the scheduled jobs to the Django admin interface
    register_events(scheduler)
    scheduler.start()