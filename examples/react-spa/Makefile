.PHONY: runserver
runserver:
	docker-compose exec backend sh -c  'python manage.py migrate && python manage.py runserver 0.0.0.0:8000'

.PHONY: shell
shell:
	docker-compose exec backend sh -c  'python manage.py shell'
