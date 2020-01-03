import codecs
import csv
import json
import ssl
import time
from urllib import parse, request
from GeneticAlgorithm import City, geneticAlgorithm


api_key = 42
service_url = "http://py4e-data.dr-chuck.net/json?"

# # Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

cityList = []
with open('addresses.csv', encoding="utf-8-sig", newline='') as addresses_csv, \
        codecs.open('where.js', 'w', "utf-8") as js_file:
    address_reader = csv.DictReader(addresses_csv, delimiter=';')
    data_dict = {}
    start = time.perf_counter()
    for row in address_reader:
        address = row['Address']
        params = {'address': address, 'key': api_key}
        url = service_url + parse.urlencode(params)
        connection = request.urlopen(url, context=ctx)
        data = connection.read().decode()
        json_data = json.loads(data)
        lat = json_data['results'][0]['geometry']['location']['lat']
        lng = json_data['results'][0]['geometry']['location']['lng']
        data_dict[(str(lat), str(lng))] = address
        cityList.append(City(x=lat, y=lng))

    bestRoute = geneticAlgorithm(population=cityList, popSize=50, eliteSize=10,
                                 mutationRate=0.01, generations=200)

    js_file.write("myData = [\n")
    count = 0
    for coordinates in bestRoute:
        coordinates = tuple(str(data) for data in coordinates)
        x = ",".join(coordinates)
        str_to_write = "[" + x + ", '" + data_dict[coordinates] + "']"
        count += 1
        if count > 1:
            js_file.write(",\n")

        js_file.write(str_to_write)
    js_file.write("\n];\n")


