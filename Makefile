default:
	python3 src/main.py

clean:
	rm -R data/tmp output/

help:
	python3 src/main.py --help