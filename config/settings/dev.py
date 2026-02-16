from .base import *

DEBUG = True

ALLOWED_HOSTS = ["*"]

DATABASES["default"]["HOST"] = os.getenv("DB_HOST", "db")

