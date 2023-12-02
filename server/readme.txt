Handle database migrations through Flask-Migrate:
Initialize
    flask db init
Create Migrations
    flask db migrate -m "Initial migration."
Migrate
    flask db upgrade
Help
    flask db --help