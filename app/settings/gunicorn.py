
MODE = "development"


wsgi_app = "main:app"

loglevel = "DEBUG"
errorlog = 'api-error.log'

bind = f"{"localhost" if MODE == "production" else "0.0.0.0"}:5000"
workers = 1
worker_class = "eventlet"
