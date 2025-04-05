from decouple import config
ENV = config("ENV", "development")

if ENV == "production":
    from .production import *
elif ENV == "testing":
    from .testing import *
else:
    from .development import *
