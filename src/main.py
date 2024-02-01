import urllib.request
import os
import pandas as pd
import zipfile
import click
import json


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
    
    if not os.path.isdir("output/"):
        os.makedirs("output/")


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
    global glob
    df = pd.read_csv(tsv_filename, sep='\t', low_memory=False, dtype='unicode')
    df[["population"]] = df[["population"]].apply(pd.to_numeric)

    cities = df.loc[df["feature class"] == "P"] # Sort out only cities
    if glob.population_size:
        cities = cities.loc[cities["population"] > glob.population_size] # Sort out on population size

    states = df.loc[df["feature code"] == "ADM1"] # Sort out only states
    print_status(country_code + " contains " + str(len(cities.index)) + " cities of the right size...")
    print_status(country_code + " contains " + str(len(states.index)) + " states...")

    return cities, states


def get_country_codes():
    global glob
    ret = None

    if not glob.country_codes == None:
        ret = glob.country_codes.split(",")
    else:
        ret = list(glob.countries_complete_df)

    print_status("Analyzing countries: " + str(ret))

    return ret


def print_city(city):
    print("GeonameId: " + str(city["geonameid"]))
    print("Name: " + str(city["name"]))
    print("ASCII name: " + str(city["asciiname"]))
    print("Alternative names: " + str(city["alternatenames"]))
    print("Latitude: " + str(city["latitude"]))
    print("Longitude: " + str(city["longitude"]))
    print("Feature class:" + str(city["feature class"]))
    print("Feature code: " + str(city["feature code"]))
    print("Country code: " + str(city["country code"]))
    print("Alternate country codes: " + str(city["cc2"]))
    print("Admin code: ")
    print("\t1: " + str(city["admin1 code"]))
    print("\t2: " + str(city["admin2 code"]))
    print("\t3: " + str(city["admin3 code"]))
    print("\t4: " + str(city["admin4 code"]))
    print("Population: " + str(city["population"]))
    print("Elevation: " + str(city["elevation"]))
    print("Digital elevation model: " + str(city["dem"]))
    print("Timezone: " + str(city["timezone"]))
    print("Modification date: " + str(city["modification date"]))


def dataframe_to_json(country_code, cities_df, states_df):
    ret = []
    for index, row in cities_df.iterrows():
        city = {"name": row["name"], "state": None, "data": []}
        state = states_df.loc[states_df["admin1 code"] == row["admin1 code"]]
        city["state"] = state.name.to_string(index=False).replace(" County", "")
        ret.append(city)

    return ret


def save_to_file(country_code, json_data):
    print_status("Writing JSON file for '" + country_code + "'...")

    with open("output/" + country_code + ".json", "w") as json_file:
        json_file.write(
            json.dumps(json_data, indent=4, ensure_ascii=False)
        )


def crunch(country_code):
    print_status("Starting crunch mode for '" + country_code + "'...")
    global glob

    download_country(country_code)
    unzip_country(country_code)
    tsv_filename = create_tsv_file(country_code)
    cities_df, states_df = create_dataframe(country_code, tsv_filename)
    json_data = dataframe_to_json(country_code, cities_df, states_df)
    save_to_file(country_code, json_data)
    remove_country(country_code)

    print_status("Done crunching '" + country_code + "'...")


@click.command("main")
@click.version_option("0.1.0", prog_name="Legendary City Cruncher")
@click.option("-v", "--verbose", is_flag=True)
@click.option("-p", "--population", type=click.INT)
@click.option("-c", "--country_codes", type=click.STRING)
def main(verbose, population, country_codes):
    setup(verbose, population, country_codes)
    
    print_status("Starting Legendary City Cruncher...")
    
    for country_code in get_country_codes():
        crunch(country_code)
    
    clean_up()

    print_status("Done!")


if __name__ == "__main__":
    main()