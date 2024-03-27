start_docker_and_source_venv:
	@sudo systemctl start docker && source .venv/bin/activate

dev:
	@python manage.py runserver -v2

shell:
	@python manage.py shell_plus --print-sql --ipython

uuid:
	@python -c 'import uuid; print(uuid.uuid4())'

.PHONY: postgres redis
