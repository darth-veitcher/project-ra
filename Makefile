.PHONY: dev docs-dev docs-prod

dev:
	docker-compose stop && docker-compose rm -f
	rm -rf data
	mkdir -p data/mariadb
	cp -R home-assistant data/
	docker-compose up --build

# Deploys based on the `version` inside the pyproject.toml only
# NB: need to double escape `$` signs for bash variables in makefile
docs-dev:
	- VERSION=$$(poetry version -s); mike deploy $${VERSION} develop
	VERSION=$$(poetry version -s); mike deploy --push --update-aliases $${VERSION} develop

# Deploys based on both the version and labels current as `stable` (ensure this referenced in mkdocs.yml)
docs-prod:
	VERSION=$$(poetry version -s); mike deploy --push --update-aliases $${VERSION} stable