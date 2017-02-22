# firebot

This shit is on fire!

### To get set up:
```
git clone git@github.com:FundersClub/firebot.git
cd firebot
python3.6 -m venv venv
. ./venv/bin/activate
pip install -r py-requirements/dev.txt
createdb firebot
```

If you have access to the Heroku app:
```
git remote add herkou https://git.heroku.com/fc-firebot.git
./bin/restore-db
```

Otherwise, you'll need to set up the DB manually. This means:
1) `./manage.py syncdb`
2) `./manage.py createsuperuser`
3) Run the dev server (see below)
4) Go to http://localhost:12000/admin/socialaccount/socialapp/add/ and set up a `github` social app

### Running the dev server
```
./bin/run-dev-server
```

Browse to http://localhost:12000/

### Running tests
```
./manage.py test
```
