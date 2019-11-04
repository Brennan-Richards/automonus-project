import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from django_apscheduler.jobstores import register_events, register_job
from django.conf import settings
# Create scheduler to run in a thread inside the application process
scheduler = BackgroundScheduler(settings.SCHEDULER_CONFIG)


def start():
    if settings.DEBUG:
        # Hook into the apscheduler logger
        logging.basicConfig()
        logging.getLogger('apscheduler').setLevel(logging.DEBUG)
        pass

    # Adding this job here instead of to crons.
    # This will do the following:
    # - Add a scheduled job to the job store on application initialization
    # - The job will execute a model class method each hour of each day
    # - replace_existing in combination with the unique ID prevents duplicate copies of the job
    scheduler.add_job("charts:scheduled_jobs.accounts_snapshot.CreateAccountSnapshot", "cron", id="create_accounts_snapshots",
                      day_of_week='*', hour='*', replace_existing=True)
    scheduler.add_job("charts:scheduled_jobs.user_sec_holding_snapshot.CreateUserSecurityHoldingSnapshot", "cron", id="create_user_security_snapshot",
                      day_of_week='*', hour='*', replace_existing=True)
    scheduler.add_job("charts:scheduled_jobs.student_loan_snapshot.CreateStudentLoanSnapshot", "cron", id="create_student_loan_snapshot",
                      day_of_week='*', hour='*', replace_existing=True)
    scheduler.add_job("charts:scheduled_jobs.credit_card_snapshot.CreateCreditCardSnapshot", "cron", id="create_credit_card_snapshot",
                      day_of_week='*', hour='*', replace_existing=True)
    # Add the scheduled jobs to the Django admin interface
    register_events(scheduler)
    scheduler.start()
