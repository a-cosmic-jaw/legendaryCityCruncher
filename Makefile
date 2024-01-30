default:
	python3 src/main.py

clean:
	rm data/allCountries.zip

help:
	python3 src/main.py --help