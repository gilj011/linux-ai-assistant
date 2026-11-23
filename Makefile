# Makefile para gerenciamento e automacao do kored

.PHONY: all test install uninstall deb clean

all: test

test:
	python3 -m unittest discover -s tests

install:
	bash scripts/install.sh

uninstall:
	bash scripts/uninstall.sh

deb:
	bash scripts/build_deb.sh

clean:
	rm -rf dist build .pytest_cache
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
