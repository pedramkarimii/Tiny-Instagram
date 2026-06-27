# Tiny Instagram

A Dockerized Django social platform built as a backend portfolio project. It demonstrates custom authentication, social interactions, media handling, PostgreSQL persistence, Redis caching, and a production-oriented Nginx/Gunicorn runtime.

## Highlights

* Custom Django user model with phone-number authentication
* User profiles and profile media
* Follow and unfollow relationships
* Posts with image attachments
* Threaded comments, post votes, and comment likes
* OTP lifecycle utilities
* PostgreSQL for persistent data and Redis-backed caching
* Docker Compose runtime with Django, Gunicorn, PostgreSQL, Redis, and Nginx
* Non-destructive startup: committed migrations are applied; database files and migration files are never deleted
* Health checks and dependency-aware startup ordering
* GitHub Actions CI for Django checks, migrations, tests, dependency auditing, Docker build, and HTTP smoke testing

## Architecture

```text
Browser
  │
  ▼
Nginx
  │
  ▼
Gunicorn / Django
  ├── PostgreSQL
  └── Redis cache
```

## Quick start

```bash
git clone --branch version-6 https://github.com/pedramkarimii/Tiny-Instagram.git
cd Tiny-Instagram

cp .env.example .env
docker compose up --build --wait
```

Open the application:

```text
http://127.0.0.1:8081
```

Stop local services:

```bash
docker compose down
```

Persistent PostgreSQL, Redis, media, and collected static files use Docker named volumes. Remove them only when a clean local environment is intended:

```bash
docker compose down --volumes
```

## Environment configuration

Copy `.env.example` to `.env` and change values for your environment.

Important variables:

```text
DEBUG
SECRET_KEY
ALLOWED_HOSTS
CSRF_TRUSTED_ORIGINS

DB_NAME
DB_USER
DB_PASSWORD
DB_HOST
DB_PORT

REDIS_HOST
REDIS_PORT

NGINX_BIND_ADDRESS
NGINX_HTTP_HOST_PORT
NGINX_HTTPS_HOST_PORT
DOMAIN_NAME
```

Never commit `.env` files or real credentials.

## Local development commands

Install locked dependencies with Poetry:

```bash
poetry install --no-root
```

Regenerate the runtime dependency file after changing `pyproject.toml`:

```bash
poetry lock
poetry export --format requirements.txt --without-hashes --output requirements.txt
```

Run Django validation and tests through Docker:

```bash
docker compose up -d --wait db redis

docker compose run --rm --no-deps \
  --entrypoint sh \
  application \
  -c '
    python -m pip check &&
    python manage.py check &&
    python manage.py makemigrations --check --dry-run &&
    python manage.py migrate --plan &&
    python manage.py test
  '
```

Run a dependency vulnerability audit:

```bash
docker run --rm \
  -v "$(pwd)":/src:ro \
  -w /src \
  python:3.12-slim \
  sh -lc 'python -m pip install --no-cache-dir pip-audit && pip-audit -r requirements.txt'
```

## Quality gates

The CI workflow verifies:

* Python dependency installation and `pip check`
* Django system checks
* Production configuration checks
* Migration drift detection
* Django test suite
* Dependency vulnerability audit with `pip-audit`
* Docker Compose configuration
* Docker image build
* Nginx HTTP smoke test

## Security notes

* Containers run the Django application as a non-root user.
* PostgreSQL and Redis are not published to the host.
* Gunicorn is reachable only inside the Compose network; Nginx is the public entry point.
* Production-only cookie, HTTPS redirect, HSTS, proxy header, and content-type protections are enabled when `DEBUG=false`.
* The local `.env.example` values are placeholders only.

## Domain model

The application includes:

* `User`, `Profile`, and OTP code records
* Follow relationships
* `Post` and image attachments
* `Comment` and threaded replies
* Post votes and comment likes

## Known limitation

`django-ckeditor` currently bundles CKEditor 4, which is flagged by the package as unsupported. The dependency audit passes, but replacing the editor with a supported alternative should be handled as a dedicated compatibility and data-migration task.

## Project status

This repository is maintained as a backend portfolio project. It is suitable for local development, code review, and CI validation. A real production deployment still requires domain-specific environment values, real credentials, backups, monitoring, and a reviewed TLS certificate workflow.
