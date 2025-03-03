install:
	python -m venv venv
	bash -c "source venv/bin/activate && pip install -r requirements.txt"
	docker-compose up -d
	python llm-talks.py build-db

rebuild-db:
	python llm-talks.py nuke-db
	python llm-talks.py build-db

clean:
	docker-compose down -v
	source deactivate
	rm -rf venv