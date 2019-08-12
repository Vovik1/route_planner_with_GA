import urllib.parse, urllib.request
import GeneticAlgorithm
import json
import ssl
import codecs
import csv


api_key = 42
serviceurl = "http://py4e-data.dr-chuck.net/json?"

# # Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

cityList = []
with open('addresses.csv', encoding="utf-8-sig", newline='') as addresses_csv:
  address_reader = csv.DictReader(addresses_csv, delimiter=';')
  additional = {}
  for row in address_reader:
    address = row['Address']
    parms = {}
    parms['address'] = address
    parms['key'] = api_key
    url = serviceurl + urllib.parse.urlencode(parms)
    connection = urllib.request.urlopen(url, context=ctx)
    data = connection.read().decode()
    json_data = json.loads(data)
    lat = json_data['results'][0]['geometry']['location']['lat']
    lng = json_data['results'][0]['geometry']['location']['lng']
    additional[(lat, lng)] = address
    cityList.append(GeneticAlgorithm.City(x=lat, y=lng))

print(additional)

bestRoute = GeneticAlgorithm.geneticAlgorithm(population=cityList, popSize=5, eliteSize=1, mutationRate=0.01, generations=5)

new = {}
for el in bestRoute:
  some_tuple = (el.x, el.y)
  new[some_tuple] = additional[some_tuple]

with codecs.open('where.js', 'w', "utf-8") as js_file:
  js_file.write("myData = [\n")
  count = 0
  for key, value in new.items():
    key = tuple(str(el) for el in key)
    x = ",".join(key)
    str_to_write = "[" + x + ", '" + value + "']"
    count += 1
    if count > 1:
      js_file.write(",\n")

    js_file.write(str_to_write)

  js_file.write("\n];\n")




