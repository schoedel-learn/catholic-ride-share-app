# Deployment Guide

This guide explains how to keep **all production secrets out of the repository** while still deploying safely with GitHub Actions.

---

## Overview

Secrets live in exactly two places:

| Where | What's stored |
|-------|--------------|
| **GitHub repository secrets** | Credentials needed by the CI/CD pipeline itself (Docker Hub login, SSH key to reach the VPS) |
| **`.env` file on the VPS** | Runtime app secrets that the containers read at start-up (database password, JWT secret, SMTP credentials, Stripe keys, etc.) |

Neither set of secrets ever touches a committed file.

---

## 1. GitHub Repository Secrets (CI/CD Pipeline)

These are used by `.github/workflows/deploy.yml` to build and push Docker images and then SSH into your server.

### Required secrets

| Secret name | What it is | How to get it |
|-------------|-----------|---------------|
| `DOCKERHUB_TOKEN` | Docker Hub access token (not your password) | Log into hub.docker.com → Account Settings → Security → New Access Token |
| `VPS_HOST` | Public IP address or hostname of your production server | From your VPS provider dashboard |
| `VPS_USERNAME` | Linux user on the VPS that the pipeline should SSH in as (e.g. `deploy` or `ubuntu`) | The account you provisioned on the VPS |
| `VPS_SSH_KEY` | Private SSH key whose public half is in `~/.ssh/authorized_keys` on the VPS | Generate with `ssh-keygen -t ed25519 -C "github-actions-deploy"` and copy the **private** key |

### How to add them

1. Go to your repository on GitHub.
2. Click **Settings** → **Secrets and variables** → **Actions**.
3. Click **New repository secret** for each row in the table above.
4. Paste the value and save. The value is never shown again after saving.

> **Tip**: If you want to limit blast radius, create a dedicated `deploy` Linux user on the VPS with only `docker` group membership, and scope the Docker Hub token to `Read & Write` only on the specific image repositories.

---

## 2. Runtime App Secrets on the VPS

The Docker containers read their configuration from a `.env` file that lives **on the server** — never in the repository.

### One-time server setup

1. SSH into your VPS:
   ```bash
   ssh deploy@YOUR_VPS_IP
   ```

2. Create the app directory and copy the template:
   ```bash
   sudo mkdir -p /opt/catholic-ride-share
   sudo chown deploy:deploy /opt/catholic-ride-share
   cd /opt/catholic-ride-share
   ```

3. Create a `.env` file from the template (you can copy the contents of `env.prod.template` from the repo as a starting point):
   ```bash
   nano .env
   ```

4. Fill in every `CHANGE_ME` value. Key secrets to generate:

   ```bash
   # Generate a strong SECRET_KEY (copy the output into .env)
   openssl rand -hex 32

   # Generate a strong POSTGRES_PASSWORD
   openssl rand -base64 24
   ```

5. Restrict file permissions so only your deploy user can read it:
   ```bash
   chmod 600 .env
   ```

### Variables you must set in `.env`

| Variable | Notes |
|----------|-------|
| `SECRET_KEY` | 64-character random hex string; used to sign JWT tokens |
| `POSTGRES_PASSWORD` | Strong random password for the database |
| `DATABASE_URL` | Must use the same password: `postgresql://catholic_user:YOUR_PASSWORD@db:5432/catholic_ride_share` |
| `SMTP_HOST` / `SMTP_PASSWORD` | Required for email verification and password reset |
| `STRIPE_SECRET_KEY` | Required only if accepting donations |
| `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` | Required only if using S3 for profile photos |
| `ALLOWED_ORIGINS` | JSON list of allowed frontend origins, e.g. `["https://yourdomain.com"]` |

Leave optional variables (Firebase, Checkr, OpenAI, etc.) blank unless you're using those features.

---

## 3. How the Pipeline Uses These Secrets

The deploy workflow (`.github/workflows/deploy.yml`) only needs access to the pipeline secrets. The runtime app secrets stay on the VPS and are **never passed through GitHub Actions**:

```
GitHub Actions                   VPS
─────────────────                ──────────────────────────────────
secrets.DOCKERHUB_TOKEN  →  docker pull (new image)
secrets.VPS_SSH_KEY      →  SSH in, run docker compose up -d
                                  ↑
                          /opt/catholic-ride-share/.env  ← only here, never in git
```

---

## 4. Rotating Secrets

- **JWT secret key**: Change `SECRET_KEY` in `.env` on the VPS, then restart containers (`docker compose up -d`). All existing tokens are immediately invalidated — logged-in users will need to log in again.
- **Database password**: Change `POSTGRES_PASSWORD` and `DATABASE_URL` together, then recreate the db container.
- **SSH deploy key**: Generate a new key pair, update `~/.ssh/authorized_keys` on the VPS, update the `VPS_SSH_KEY` GitHub secret, then delete the old key from `authorized_keys`.
- **Docker Hub token**: Revoke the old token in Docker Hub, generate a new one, update the `DOCKERHUB_TOKEN` GitHub secret.

---

## 5. What to Never Commit

The `.gitignore` already excludes these patterns — this is a reminder, not a new rule:

```
.env
.env.*
*.env
env.prod        # fill in values locally but never commit
```

If you accidentally commit a secret, treat it as **compromised immediately**:
1. Revoke/rotate the leaked credential.
2. Remove it from git history with `git filter-repo` or GitHub's secret scanning remediation tool.
3. Force-push the cleaned history.

---

## See Also

- [Architecture](ARCHITECTURE.md)
- [GitHub Security Setup](GITHUB_SECURITY_SETUP.md)
- [Security Policy](../SECURITY.md)
