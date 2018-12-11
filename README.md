<img src="https://cloud.githubusercontent.com/assets/899450/23774315/f3983d3a-04d7-11e7-9ee7-a02e436755cf.png" alt="Fire" width="286" height="150">

# fire

A bot that creates GitHub Issues via email. Read more at https://fire.fundersclub.com/.

To try it out, send an email to fire-test@fire.fundersclub.com and take a look at https://github.com/FundersClub/fire-test/issues

### To get set up:
```
git clone git@github.com:FundersClub/fire.git
cd fire
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
You'll need to run both the backend and the frontend separately. The frontend uses Webpack, which runs its own webserver and is responsible for proxying relevant API calls to the Django backend (see `webpack.dev.js`'s `proxy`). Once both servers are running, navigate to `http://localhost:12001/` to use the app (with hot-reload, etc enabled).

If you'd like to simulate the production environment locally, run `npm run build` to produce the compiled static assets. Then, navigate to `http://localhost:12000/`. The compiled frontend will now be served via Django.

### Running tests
```
./manage.py test
npm test
```
