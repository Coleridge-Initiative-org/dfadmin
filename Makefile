PYTHON=python2.7

db-migrate:
	docker-compose exec web $(PYTHON) manage.py migrate
	docker-compose exec web $(PYTHON) manage.py runscript setup_database

db-prepare: db-migrate
	docker-compose exec web $(PYTHON) manage.py runscript load_cdf_staff
	docker-compose exec web $(PYTHON) manage.py runscript load_cdf_users

# This command drop the schema and recreate it. It should run on dev only.
dev-db-clear:
	docker-compose exec db psql -U postgres -c 'DROP SCHEMA public CASCADE; CREATE SCHEMA public; GRANT ALL ON SCHEMA public TO postgres;'

dev-db-restore: dev-db-clear db-restore db-migrate
	docker-compose exec web $(PYTHON) manage.py runscript init_dev_database
	echo 'Database reset done.'

dev-up:
	docker-compose up -d
	make dev-db-restore

dev-makemigrations:
	docker-compose exec web $(PYTHON) manage.py makemigrations

dev-web-rebuild:
	docker-compose up -d --build web

bash:
	docker-compose exec web bash

shell:
	docker-compose exec web $(PYTHON) manage.py shell_plus

code-check:
	pylint --load-plugins pylint_django data_facility data_facility_admin

test:
	docker-compose exec web coverage run --source='.' manage.py test --noinput -v2 --parallel 2
	docker-compose exec web coverage xml
	docker-compose exec web coverage report

codacy-report: test
	# docker-compose exec web pytest --cov=data_facility --cov=data_facility_admin --cov=scripts --cov-report=xml:coverage.xml
	docker-compose exec web python-codacy-coverage -r coverage.xml

ci: dev-web-rebuild test codacy-report

db-psql:
	docker-compose exec db psql -U postgres

db-start:
	docker-compose start db

db-restore:
	docker-compose exec db psql -U postgres -f /code/db/pg-bkp.sql

db-dump:
	docker-compose exec db pg_dump -c -U postgres > db/pg-bkp.sql

db-up:
	docker-compose up -d db

start:
	docker-compose start


up: git-submodules-init
	docker-compose up -d
	make db-migrate

git-submodules-init:
	git submodule update --init --recursive

check-qa:
	flake8 --exclude venv/ --ignore=E501

deploy-build-latest:
	docker build -f Dockerfile.prod -t datafacility:latest .

deploy-rebuild-latest:
	docker-compose -f deploy/docker-compose.yml down --rmi local
	docker build -f Dockerfile.prod -t datafacility:latest .
	docker-compose -f deploy/docker-compose.yml up -d

deploy-up:
	docker-compose -f deploy/docker-compose.yml up -d
	docker-compose -f deploy/docker-compose.yml ps

ldap_import:
	docker-compose exec web $(PYTHON) manage.py runscript import_from_ldap

docs:
	docker-compose exec web python manage.py graph_models data_facility_admin data_facility_metadata -o documentation/current_class_diagram.png -g --exclude-models 'Historical*' #--layout fdp

check:
	docker-compose exec web python -Wall manage.py check