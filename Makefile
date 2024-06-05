start_docker_and_source_venv:
	@sudo systemctl start docker && source .venv/bin/activate

dev:
	@python manage.py runserver -v2

shell:
	@python manage.py shell_plus --print-sql --ipython

uuid:
	@python -c 'import uuid; print(uuid.uuid4())'

check_trial_ended:
	@python manage.py check_trial_ended

send_geolite2_country_files:
	@sudo ssh -i ~/.ssh/zap_ass.pem ubuntu@54.235.38.100 "rm -rf /home/ubuntu/fully-featured-backend/GeoLite2-Country/*" && scp -i ~/.ssh/zap_ass.pem ~/Projects/fully-featured-backend/GeoLite2-Country/* ubuntu@54.235.38.100:/home/ubuntu/fully-featured-backend/GeoLite2-Country/

.PHONY: postgres redis
