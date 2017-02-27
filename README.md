# firebot

This shit is on fire!

### To get set up:
```
git clone git@github.com:FundersClub/firebot.git
cd firebot
python3.6 -m venv venv
. ./venv/bin/activate
pip install -r py-requirements/dev.txt
npm install
createdb firebot
```

If you have access to the Heroku app:
```
git remote add herkou https://git.heroku.com/fc-firebot.git
./bin/restore-db
```

Otherwise, you'll need to set up the DB manually. This means:

1. `./manage.py syncdb`
2. `./manage.py createsuperuser`
3. Run the dev server (see below)
4. Go to http://localhost:12001/admin/socialaccount/socialapp/add/ and set up a `github` social app

### Running the dev servers
```
./bin/run-dev-server (to run backend at http://localhost:12000/)
npm start (to run frontend at http://localhost:12001/)
```

### Running tests
```
./manage.py test
npm test
```

### GitHub intergration notes
 - Locally, `GITHUB_TOKEN` is a personal access token for @firebot-test-local
 - On Heroku, `GITHUB_TOKEN` is a personal access token for @firebot-test

### Frontend build notes
Right now, the frontend can publish a compiled/linked frontend to `dist-frontend` by running `npm run build`. This isn't terribly useful right now.
