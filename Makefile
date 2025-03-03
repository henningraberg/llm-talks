install:
	python -m venv venv
	. venv/bin/activate
	pip install -r requirements.txt
	docker-compose up -d
	python llm-talks.py build-db

rebuild-db:
	python llm-talks.py nuke-db
	python llm-talks.py build-db

clean:
	docker-compose down -v
	rm -rf venv
	deactivate