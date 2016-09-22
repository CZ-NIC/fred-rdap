APP = rdap

.PHONY: default test isort check-isort check-flake8 check-all

default: check-all

test:
	PYTHONPATH='./test_cfg:${PYTHONPATH}' DJANGO_SETTINGS_MODULE='settings' django-admin test rdap

isort:
	isort --recursive ${APP}

cehck_all: check-isort check-flake8

check-isort:
	isort --recursive --check-only --diff ${APP}

check-flake8:
	flake8 --config=.flake8 --format=pylint --show-source ${APP}
