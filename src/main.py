import urllib.request
import os
import pandas as pd
import zipfile
import click

class Glob(object):
    pass

glob = Glob()
glob.settings = Glob()
glob.data = Glob()

def print_status(status):
    global glob

    if glob.settings.print_status:
        print(status)


def download_allcountries_file():
    global glob

    if not os.path.isfile(glob.data.allcountries_zip):
        print_status("Downloading '" + glob.data.allcountries_zip + "'...")
        all_countries_location = "https://download.geonames.org/export/dump/"
        urllib.request.urlretrieve(all_countries_location + glob.data.allcountries_zip, "data/" + glob.data.allcountries_zip)


def clean_up():
    print_status("Running clean up...")
    global glob

    # Remove allCountries.txt
    if os.path.isfile(glob.data.allcountries_txt):
        print_status("Removing '" + glob.data.allcountries_txt + "'...")
        os.remove(glob.data.allcountries_txt)


def setup(verbose):
    global glob
    glob.settings.print_status = verbose
    glob.data.allcountries_zip = "data/allCountries.zip"
    glob.data.allcountries_txt = "data/allCountries.txt"

    print_status("Running setup...")
    if not os.path.isfile(glob.data.allcountries_zip):
        download_allcountries_file()
    
    with zipfile.ZipFile(glob.data.allcountries_zip, 'r') as zip_ref:
        print_status("Extracting '" + glob.data.allcountries_zip + "'...")
        zip_ref.extractall("data/")


def crunch():
    print_status("Starting crunch mode...")
    countries = True
    print_status("Done crunching...")


@click.command("main")
@click.version_option("0.1.0", prog_name="Legendary City Cruncher")
@click.option("-v", "--verbose", is_flag=True)
def main(verbose):
    setup(verbose)
    print_status("Starting Legendary City Cruncher...")
    crunch()
    clean_up()
    print_status("Done!")


if __name__ == "__main__":
    main()