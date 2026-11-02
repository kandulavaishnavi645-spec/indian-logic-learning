# Deploying to Render

The Render web service in `render.yaml` uses the free web plan. It needs a
PostgreSQL connection from Neon so account, quiz, and shop data survives
restarts. The local SQLite database is intentionally excluded from Git; starter
quiz questions are created by Django migrations.

## One-time setup

1. Install Git for Windows if it is not already installed.
2. In VS Code, open this project and use **Source Control → Initialize
   Repository**, then **Publish to GitHub**. Choose a **private** repository.
   Do not add `db.sqlite3`, `.env`, or secret values; `.gitignore` excludes the
   local database and environment files.
3. Create a free PostgreSQL project at Neon. Copy its pooled connection string
   with SSL enabled. Treat this URL as a password: do not put it in source code
   or send it in chat.
4. In Render, choose **New → Blueprint**, connect the private GitHub repository,
   and approve access when GitHub asks. Render will read `render.yaml`.
5. When Render asks for `DATABASE_URL`, paste the Neon connection string into
   Render's environment-variable field and start the deploy.
6. Wait for the first deployment to finish, then open the `onrender.com` URL
   shown on the Render service page.

The Render web plan may sleep while idle, so the first visit after a quiet
period can take longer. Free-plan limits and availability can change; check the
current provider terms before creating accounts or services.

## After deployment

- Create an administrator with Render's web-service shell by running
  `python manage.py createsuperuser`.
- Add products using `/admin/` if the shop should contain products.
- The local SQLite database is not uploaded. Existing local accounts, orders,
  and shop data therefore need an explicit data migration if they should be
  kept; do not copy the SQLite file to the host.
