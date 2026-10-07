.PHONY: setup test lint run benchmark clean

setup:
	python -m venv .venv
	.venv\Scripts\pip install -r requirements.txt
	python scripts/download_models.py

test:
	pytest tests/ -v --tb=short

lint:
	flake8 lecturelens/ tests/ --max-line-length 120
	black --check lecturelens/ tests/

run:
	streamlit run lecturelens/ui/app.py

benchmark:
	python scripts/benchmark.py --quick

clean:
	rm -rf __pycache__ .pytest_cache logs/*.log
	find . -type d -name __pycache__ -exec rm -rf {} +
