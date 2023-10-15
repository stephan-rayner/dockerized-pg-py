up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f

cleanup: down
	docker volume rm dockerized-pg-py_poc-data | true
	docker rmi dockerized-pg-py_app | true
