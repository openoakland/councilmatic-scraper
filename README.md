municipal-scrapers
==================

source for municipal scrapers

To find out more about the ins and outs of these scrapers, as well as how to create your own, head on over to [docs.opencivicdata.org's scraping page](http://docs.opencivicdata.org/en/latest/scrape/index.html).

Issues?
-------

Issues with the data coming from these scrapers should be filed at the [OCD Data issue tracker](https://sunlight.atlassian.net/browse/DATA/)

All Open Civic Data issues can be browsed and filed at [the Open Civic Data JIRA instance](https://sunlight.atlassian.net/browse/OCD/).

## Development
Requires python3, postgresql

### Setup

The easiest way to get running is with Docker. There is a Docker setup for the scraper here: https://github.com/ekkus93/councilmatic-docker

If you prefer to use VirtualEnv or Anaconda on your machine follow the instructions below.

### Initialization
Assuming that you want to have your database be called `opencivicdata` on your local machine

```bash
pip install -r requirements.txt
createdb opencivicdata
export DATABASE_URL=postgresql:///opencivicdata
pupa dbinit us
pupa init YOUR_CITY_SCRAPER
```

At times, the release of ocd-django on PyPI differs from that of Github. This may cause problems if you need to create and run migrations. Specifically, you might encounter an `ImproperlyConfigured` error that instructs you to do the following:

If you run into additional issues check the troubleshooting guide here:

https://github.com/openoakland/councilmatic-scraper/wiki/Dev-Environment-Setup

```bash
You must either define the environment variable DJANGO_SETTINGS_MODULE or call settings.configure() before accessing settings.
```

Fix the problem by running:

```bash
export DJANGO_SETTINGS_MODULE=pupa.settings
```

Then, you should be able to successfully run:

```bash
django-admin makemigrations
django-admin migrate
```

### Testing
Before submitting a PR, please run `pupa update YOUR_CITY_SCRAPER`

```bash
export DATABASE_URL=postgresql:///opencivicdata
pupa update oakland
```
