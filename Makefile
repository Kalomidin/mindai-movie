run:
	@python3 main.py data/movies.csv data/past_screenings.csv data/sample_rules.json
clean:
	@echo "Cleaning cache files"
	@rm -rf __pycache__
	@rm -rf movies.db
	@rm -rf movies_test.db
	@echo "Cache files cleaned"
test:
	python3 memdb_test.py

lint:
	@echo "Running linter"
	@pylint .
	@echo "Linter finished"