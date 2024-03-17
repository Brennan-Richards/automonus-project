# Purpose of this project
This project is a Django application with an extensive feature set for managing personal finances. The application includes integrations into Plaid, which enables access and storage of users' personal financial data and useful downstream analyses and visualizations. Additionally, an integration into Stripe enables users to send and receive money from within the application.

# List of context variables
IS_ON_PROD  # set True on production

SECRET_KEY  # set some different key on production, but the same length as the initial one

ALLOWED_HOSTS  # a list of available hosts

DEBUG  # set False for production

PLAID_ENV  # set to the needed production value (it is "sandbox" for development)

PLAID_CLIENT_ID

PLAID_SECRET

PLAID_PUBLIC_KEY

PLAID_WEBHOOK_URL  # on production it should be like this https://yourdomain.com/webhooks/webhook-handler/

RECAPTCHA_PUBLIC_KEY  # from google captcha settings

RECAPTCHA_PRIVATE_KEY  # from google captcha settings

AXES_FAILURE_LIMIT  # limit of failed attempts login attempts before temporary blocking account (for django-axes package)

SCHEDULER_AUTOSTART  # set to True if you need to switch on the scheduler

ROLLBAR_TOKEN  # set the value of token from rollbar

ACH_STRIPE_TEST *-IF TRUE USE TEST ACH ACCOUNT NUMBER, USING FOR DEV *

STRIPE_PUBLIC_KEY

STRIPE_SECRET_KEY
