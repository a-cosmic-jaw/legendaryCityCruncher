import urllib.request
import os
import pandas as pd
import zipfile
import click
import subprocess


class Glob(object):
    def __init__(self) -> None:
        self.countries_complete_df = None
        self.headers_file = None
        self.population_size = None
        self.print_status = None
        self.country_codes = None

glob = Glob()


def print_status(status):
    global glob
    
    if glob.print_status:
        print(status)


def download_country(country_code):
    zip_filename = country_code + ".zip"
    all_countries_location = "https://download.geonames.org/export/dump/"

    if not os.path.isfile("data/tmp/" + zip_filename):
        print_status("Downloading '" + zip_filename + "'...")    
        urllib.request.urlretrieve(all_countries_location + zip_filename, "data/tmp/" + zip_filename)


def clean_up():
    print_status("Running clean up...")

    #if os.path.exists("data/tmp"):
    #    os.system("rm -R data/tmp")

def setup(verbose, population_size, country_codes):
    global glob
    glob.countries_complete_df = pd.read_json("data/countries_complete.json")
    glob.headers_file = "data/headers.tsv"
    glob.population_size = population_size
    glob.print_status = verbose
    glob.country_codes = country_codes

    if not os.path.isdir("data/tmp"):
        os.makedirs("data/tmp")


def unzip_country(country_code):
    zip_file = country_code + ".zip"

    if os.path.isfile("data/tmp/" + zip_file):
        with zipfile.ZipFile("data/tmp/" + zip_file, 'r') as zip_ref:
            print_status("Extracting '" + zip_file + "'...")
            zip_ref.extractall("data/tmp/")


def remove_country(country_code):
    file_endings = ["txt", "tsv"]
    
    for ending in file_endings:
        filename = "data/tmp/" + country_code + "." + ending
        if os.path.isfile(filename):
            os.remove(filename)


def create_tsv_file(country_code):
    print_status("Creating .tsv file for '" + country_code + "'")
    tsv_filename = country_code + ".tsv"
    txt_filename = country_code + ".txt"

    os.system("cp data/headers.tsv data/tmp/" + tsv_filename)
    os.system("cat data/tmp/" + txt_filename + " >> data/tmp/" + tsv_filename)

    return "data/tmp/" + tsv_filename

def create_dataframe(country_code, tsv_filename):
    df = pd.read_csv(tsv_filename, sep='\t', low_memory=False, dtype='unicode')
    df[["population"]] = df[["population"]].apply(pd.to_numeric)

    df = df.loc[df["feature class"] == "P"] # Sort out only cities
    df = df.loc[df["population"] > glob.population_size] # Sort out on population size

    print_status(country_code + " contains " + str(len(df.index)) + " cities...")

    return df

def get_country_codes():
    global glob
    ret = None
    if not glob.country_codes == None:
        ret = glob.country_codes.split(",")
    else:
        ret = list(glob.countries_complete_df)

    print_status("Analyzing countries: " + str(ret))

    return ret


def crunch():
    print_status("Starting crunch mode...")
    global glob
    
    for country_code in get_country_codes():
        download_country(country_code)
        unzip_country(country_code)
        tsv_filename = create_tsv_file(country_code)
        df = create_dataframe(country_code, tsv_filename)
        print(df)
        remove_country(country_code)

    print_status("Done crunching...")


@click.command("main")
@click.version_option("0.1.0", prog_name="Legendary City Cruncher")
@click.option("-v", "--verbose", is_flag=True)
@click.option("-p", "--population", type=click.INT)
@click.option("-c", "--country_codes", type=click.STRING)
def main(verbose, population, country_codes):
    setup(verbose, population, country_codes)
    
    print_status("Starting Legendary City Cruncher...")
    
    crunch()
    clean_up()

    print_status("Done!")


if __name__ == "__main__":
    main()