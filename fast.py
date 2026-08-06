import os

from werkzeug.middleware.proxy_fix import ProxyFix
from flaskblog import create_app

app = create_app()

# Render (and most PaaS) sit behind a reverse proxy that terminates HTTPS.
# ProxyFix tells Flask to trust the X-Forwarded-* headers so that:
#   - CSRF validation works (Referer / Origin checks use https://)
#   - Session cookies are set with Secure flag correctly
#   - url_for() generates https:// URLs
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)


if __name__ == "__main__":
    debug = os.environ.get("FLASK_DEBUG", "").lower() in ("1", "true", "yes")
    app.run(debug=debug)

