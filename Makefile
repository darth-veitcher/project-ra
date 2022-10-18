.PHONY: dev

dev:
	docker-compose stop && docker-compose rm -f
	rm -rf data
	mkdir -p data/mariadb
	cp -R home-assistant data/
	docker-compose up --build