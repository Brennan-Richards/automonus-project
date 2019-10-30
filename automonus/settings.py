"""
Django settings for The Automonus Project (project).

Generated by 'django-admin startproject' using Django 2.2.3.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os
import environ
import dj_database_url

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Getting .env file with environment variables
root = environ.Path(__file__) - 2
env = environ.Env(DEBUG=(bool, False))  # set default values and casting
environ.Env.read_env(".env")  # reading .env file
IS_ON_PROD = env.bool("IS_ON_PROD", default=False)
print("IS_ON_PROD: {}".format(IS_ON_PROD))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env(
    "SECRET_KEY", default="kj8pmlp50a1_)2el%7hgynt5-u!rvzd2z$(b*@0#2n7^joq54h"
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool("DEBUG", True)

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["*"])

#URLs set for login defaults
LOGIN_URL = "/login_signup/"
LOGIN_REDIRECT_URL = "/master_dashboard/"
LOGOUT_REDIRECT_URL = "/"

# Application definition

INSTALLED_APPS = [
    "expenditures.apps.ExpendituresConfig",
    "academy.apps.AcademyConfig",
    "charts.apps.ChartsConfig",
    "payments.apps.PaymentsConfig",
    "accounts.apps.AccountsConfig",
    "income.apps.IncomeConfig",
    "investments.apps.InvestmentsConfig",
    "liabilities.apps.LiabilitiesConfig",
    "django.contrib.admin",
    "django.contrib.sites",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "users",
    "institutions",
    "webhooks",
    # external packages
    "mathfilters",
    "axes",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "crispy_forms",
    "captcha",
    "django_apscheduler",
    "django_otp",
    "django_otp.plugins.otp_totp",
]

MIDDLEWARE = [
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "axes.middleware.AxesMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django_otp.middleware.OTPMiddleware",
]

OTP_TOTP_ISSUER = "Automonus"

ROOT_URLCONF = "automonus.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": ["automonus/templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]

WSGI_APPLICATION = "automonus.wsgi.application"


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = "/static/"
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static", "static_dev")]
STATIC_ROOT = os.path.join(BASE_DIR, "static", "static_prod")


USE_THOUSAND_SEPARATOR = True

AUTHENTICATION_BACKENDS = [
    "axes.backends.AxesBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
    "django.contrib.auth.backends.ModelBackend",
]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

PLAID_ENV = env("PLAID_ENV", default="sandbox")
PLAID_CLIENT_ID = env("PLAID_CLIENT_ID", default="5d37fe8b737a4f001252bfd9")
PLAID_SECRET = env("PLAID_SECRET", default="176040b1d82a9d35dfc9aca8fe9943")
PLAID_PUBLIC_KEY = env("PLAID_PUBLIC_KEY", default="6c5492915411a3645fdd0368516aa9")

"""Replace ngrok server address (it is the string till "/webhooks/webhook-handler/" with your server address"""
PLAID_WEBHOOK_URL = env(
    "PLAID_WEBHOOK_URL", default="http://9d9c1a5a.ngrok.io/webhooks/webhook-handler/"
)

# STRIPE DATA

STRIPE_PUBLIC_KEY = env(
    "STRIPE_PUBLIC_KEY", default="pk_test_Yefm4kQnlPKSvM5W6BW24gk700SThCTQkg"
)
STRIPE_SECRET_KEY = env(
    "STRIPE_SECRET_KEY", default="sk_test_Cm8UAku0L4hL4G2aOpDMIM7r00iBv2frlo"
)

# SendGrid for emails
SENDGRID_API_KEY = os.getenv(
    "SENDGRID_API_KEY",
    default="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",
)

EMAIL_HOST = "smtp.sendgrid.net"
EMAIL_HOST_USER = "apikey"
EMAIL_HOST_PASSWORD = SENDGRID_API_KEY
EMAIL_PORT = 587
EMAIL_USE_TLS = True

# google-recapcha
RECAPTCHA_PUBLIC_KEY = env(
    "RECAPTCHA_PUBLIC_KEY", default="6LekwrkUAAAAAMS9Svgvyd3z14_7MPtWTdkbN-EB"
)
RECAPTCHA_PRIVATE_KEY = env(
    "RECAPTCHA_PRIVATE_KEY", default="6LekwrkUAAAAACDScUoq7VrZSMbmeJV3x8OP7mro"
)

# django-crispy-forms
CRISPY_TEMPLATE_PACK = "bootstrap4"

# django-allauth
ACCOUNT_FORMS = {
    "login": "users.all_auth_forms.CustomLoginForm",
    "signup": "users.all_auth_forms.CustomSignupForm",
    "reset_password": "users.all_auth_forms.CustomResetPasswordForm",
}

SITE_ID = 1
ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_USER_DISPLAY = lambda user: user.email
ACCOUNT_EMAIL_SUBJECT_PREFIX = "Automonus"

# django-axes
AXES_CACHE = "axes_cache"
AXES_COOLOFF_TIME = 3
AXES_LOCK_OUT_AT_FAILURE = True
AXES_ONLY_USER_FAILURES = True
AXES_FAILURE_LIMIT = env("AXES_FAILURE_LIMIT", default=10)
AXES_USERNAME_FORM_FIELD = "username"
AXES_RESET_ON_SUCCESS = True


# for django-apscheduler
SCHEDULER_CONFIG = {
    "apscheduler.jobstores.default": {
        "class": "django_apscheduler.jobstores:DjangoJobStore"
    },
    "apscheduler.executors.processpool": {"type": "threadpool"},
}
SCHEDULER_AUTOSTART = env.bool("SCHEDULER_AUTOSTART", default=False)

if IS_ON_PROD:
    ACH_STRIPE_TEST = env.bool("ACH_STRIPE_TEST", default=False)
    AXES_BEHIND_REVERSE_PROXY = True
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    ALLOWED_HOSTS = env("ALLOWED_HOSTS", default=["automonus-project.herokuapp.com"])
    DEBUG = env.bool("DEBUG", False)
    DATABASES = {"default": dj_database_url.config()}
    STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

    # rollbar (for handling exceptions on prod)
    ROLLBAR_TOKEN = env("ROLLBAR_TOKEN", default="")
    if ROLLBAR_TOKEN:
        ROLLBAR = {
            "access_token": ROLLBAR_TOKEN,
            "environment": "production",
            "branch": "master",
        }
        MIDDLEWARE.insert(
            0, "rollbar.contrib.django.middleware.RollbarNotifierMiddlewareOnly404"
        )
        MIDDLEWARE.append(
            "rollbar.contrib.django.middleware.RollbarNotifierMiddlewareExcluding404"
        )
else:
    ACH_STRIPE_TEST = env.bool("ACH_STRIPE_TEST", default=True)
