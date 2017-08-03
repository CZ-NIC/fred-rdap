APP = rdap

.PHONY: default test test-coverage isort check-all check-isort check-flake8 check-doc

default: check-all

test:
	PYTHONPATH='./test_cfg:${PYTHONPATH}' DJANGO_SETTINGS_MODULE='settings' django-admin test rdap

test-coverage:
	PYTHONPATH='./test_cfg:${PYTHONPATH}' DJANGO_SETTINGS_MODULE='settings' coverage run --source=${APP} --branch -m django test ${APP}

isort:
	isort --recursive ${APP}

check-all: check-isort check-flake8 check-doc

check-isort:
	isort --recursive --check-only --diff ${APP}

check-flake8:
	flake8 --config=.flake8 --format=pylint --show-source ${APP}

check-doc:
	pydocstyle ${APP}
