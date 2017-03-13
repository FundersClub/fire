# Introduction

This document details the steps and integrations required to set up and get Fire up and running on a production environment. It assumes it will be running under `company.com`.

Fire depends on the current services/integrations:

* Amazon S3 for storing email attachments
* Sentry for error reporting
* SendGrid for sending and receiving emails
* PostgreSQL for database (although any database Django supports should work)
* Redis for storing background task queue
* GitHub (Fire requires both a GitHub user and a GitHub OAuth application)

In addition Fire needs a machine to run it’s Django application and Celery task queue. We use Heroku, but you can use any provider you feel comfortable with.

# Configuration Summary

By default, Fire’s configuration is handled using environment variables. Below is a summary of the ones Fire needs:

<table>
  <tr>
    <td>Environment Variable</td>
    <td>Purpose</td>
    <td>Example value</td>
  </tr>
  <tr>
    <td>DJANGO_SETTINGS_MODULE</td>
    <td>Controls which settings module Django would use</td>
    <td>firebot.settings.prod</td>
  </tr>
  <tr>
    <td>DJANGO_ADMIN_URL</td>
    <td>The URL to serve Django’s admin from</td>
    <td>admin123
(Would result in admin being served from /admin123/)</td>
  </tr>
  <tr>
    <td>DJANGO_ALLOWED_HOSTS</td>
    <td>Comma-separated list of domains [Django will serve HTTP requests for](https://docs.djangoproject.com/en/1.10/ref/settings/#allowed-hosts)</td>
    <td>company-firebot.herokuapp.com,fire.company.com</td>
  </tr>
  <tr>
    <td>DJANGO_DEBUG</td>
    <td>Enable [Django debug mode](https://docs.djangoproject.com/en/1.10/ref/settings/#debug) (Values: YES/NO)</td>
    <td>NO</td>
  </tr>
  <tr>
    <td>DJANGO_SECRET_KEY</td>
    <td>[Django’s secret key](https://docs.djangoproject.com/en/1.10/ref/settings/#std:setting-SECRET_KEY)</td>
    <td>KZg#{x:Fb+[-*TY,?b~V5;Q.@VJ]76</td>
  </tr>
  <tr>
    <td>MEDIAFILES_AWS_STORAGE_BUCKET_NAME</td>
    <td>S3 bucket name to store email attachments in</td>
    <td>company-fire-media</td>
  </tr>
  <tr>
    <td>MEDIAFILES_AWS_ACCESS_KEY_ID</td>
    <td>AWS Access Key that has read/write permissions to above bucket</td>
    <td></td>
  </tr>
  <tr>
    <td>MEDIAFILES_AWS_SECRET_ACCESS_KEY</td>
    <td>AWS Secret Access Key for the above Access Key</td>
    <td></td>
  </tr>
  <tr>
    <td>DATABASE_URL</td>
    <td>[Database URL](https://github.com/kennethreitz/dj-database-url)</td>
    <td>postgres://master:secretpassword@our-db.amazonaws.com:5432/fire</td>
  </tr>
  <tr>
    <td>REDIS_URL</td>
    <td>Redis URL to be used by the [Celery](www.celeryproject.org) task queue</td>
    <td>redis://user:pass@redis.company.com</td>
  </tr>
  <tr>
    <td>GITHUB_BOT_USERNAME</td>
    <td>The GitHub username the bot would be using</td>
    <td>company-fire</td>
  </tr>
  <tr>
    <td>GITHUB_TOKEN</td>
    <td>A GitHub Personal Access Token for the user mentioned above</td>
    <td></td>
  </tr>
  <tr>
    <td>FIREBOT_BASE_URL</td>
    <td>The main URL used for accessing this Fire’s instance (with no trailing slash!)</td>
    <td>https://fire.company.com</td>
  </tr>
  <tr>
    <td>CONTACT_URL</td>
    <td>Contact URL (displayed on the footer)</td>
    <td>https://company.com/contact/</td>
  </tr>
  <tr>
    <td>PRIVACY_POLICY_URL</td>
    <td>Privacy policy URL (displayed on the footer)</td>
    <td>https://company.com/privacy/</td>
  </tr>
  <tr>
    <td>TERMS_OF_SERVICE_URL</td>
    <td>Terms of Service URL (displayed on the footer)</td>
    <td>https://company.com/tos/</td>
  </tr>
  <tr>
    <td>FIREBOT_EMAIL_DOMAIN</td>
    <td>The domain Fire is accepting emails on</td>
    <td>fire.company.com</td>
  </tr>
  <tr>
    <td>SENDGRID_API_KEY</td>
    <td>SendGrid API key (used for sending outgoing emails)</td>
    <td></td>
  </tr>
  <tr>
    <td>SENDGRID_WEBHOOK_SECRET</td>
    <td>Secret to put in the SendGrid webhook URL. The webhook URL ends up being:
/emails/sendgrid/SECRET/parse/</td>
    <td>SECRET</td>
  </tr>
  <tr>
    <td>SENTRY_DSN</td>
    <td>Sentry’s API key</td>
    <td></td>
  </tr>
</table>


# Setting up Integrations

## Github

For Fire to work, it needs a GitHub user, a Personal Access Token for that user with specific permissions, and an OAuth Application.

1. Register a user on GitHub. This is the user that will get invited to repositories and create issues. Set the GITHUB_BOT_USERNAME environment variable to the username you just created.
2. Go to [https://github.com/settings/tokens](https://github.com/settings/tokens) to create a Personal Access token for this user. Grant it the **repo** and **user** permissions (and everything underneath them). Set the GITHUB_TOKEN environment variable to the token.
3. Go to [https://github.com/settings/developers](https://github.com/settings/developers) and register a new application
4. Give the application a name, and note it’s **Client ID** and **Client Secret**. Those will need to be configured in Django after all integrations are ready.
5. For the Homepage URL, put whatever you’d like
6. For Authorization callback URL put [https://fire.company.com/accounts/github/login/callback/](https://fire.company.com/accounts/github/login/callback/) (replace fire.company.com with the host you’re serving Fire from)

## S3

Fire needs a place to store attachments sent by users so that they could be embedded in the issues it create. We opted to use S3 for this, but since we’re using Django’s file storage API this can be customized if you prefer to use something else.

You’ll need to create an S3 bucket for this purpose, as well as an IAM user and get Access Key and Secret Key for this user. Set the bucket name and keys in the MEDIAFILES_AWS_STORAGE_BUCKET_NAME, MEDIAFILES_AWS_ACCESS_KEY_ID and MEDIAFILES_AWS_SECRET_ACCESS_KEY environment variables.

The user will need Put/Get/Delete access to the bucket. Here’s an example policy that works:

```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::company-fire-media"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:PutObject",
                "s3:PutObjectACL",
                "s3:GetObject",
                "s3:DeleteObject"
            ],
            "Resource": [
                "arn:aws:s3:::company-fire-media/*"
            ]
        }
    ]
}
```


# SendGrid

Fire needs to be able to send and receive emails. We are using SendGrid to do both.

* Create a SendGrid account setup and authorize it to use your email domain.
* Set the FIREBOT_EMAIL_DOMAIN environment variable to this domain.
* Create an API key and give it Full Access to the Mail Send permission. Set this API key in the SENDGRID_API_KEY environment variable.
* Set the SENDGRID_WEBHOOK_SECRET to a random string, and then create a new Inbound Parse endpoint and point it to [https://fire.company.com/emails/sendgrid/](https://fire.company.com/emails/sendgrid/)<your random strong>/parse/

# Running

1. Make sure you have the correct Python requirements installed (`pip install -r py-requirements/prod.txt`)
2. Create the initial database (`./manage.py migrate`)
3. Build the frontend files (`npm run build`)
4. Collect static files (`./manage.py collectstatic`)
5. Get gunicorn to run and serve requests, and Celery to process background tasks (Take a look at the `Procfile` file)
6. Create a superuser (`./manage.py createsuperuser`)
7. Go to [https://fire.company.com/admin/](https://fire.company.com/admin/) (URL might differ depending on your setting of DJANGO_ADMIN_URL).
8. Log in with the super user you created
9. Go to Sites and edit the default site to match your domain name (/admin/sites/site/1/change/)
10. Add a new "Social application" (under /admin/socialaccount/socialapp/add/):
    1. Provider: GitHub
    2. Name: github (lowercase)
    3. Client ID: Use the value you got from GitHub
    4. Secret key: USe the value you got from GitHub
    5. Sites: Add the default (and only) site
11. Everything is now set up! You should be able to invite your fire user to a repository, and if everything works as it should it’ll accept the invite and create the initial issue! Good luck!

