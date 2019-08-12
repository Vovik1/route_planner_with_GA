import numpy as np, random, operator, pandas as pd
import urllib.request, urllib.parse, urllib.error
import json
import ssl

api_key = 'AIzaSyDmGpnn3txIZQlDrCKzo53Y8jgXEced3Hg'
serviceurl = 'https://maps.googleapis.com/maps/api/distancematrix/json?'

# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE


class City:
  def __init__(self, x, y):
    self.x = x
    self.y = y

  def distance(self, city):
    parms = {}
    parms['destinations'] = str(city.x)+','+str(city.y)
    parms['key'] = api_key
    url = serviceurl + 'origins=' + str(self.x) + ',' + str(self.y) + '&' + urllib.parse.urlencode(parms)
    uh = urllib.request.urlopen(url, context=ctx)
    data = uh.read().decode()
    try:
      js = json.loads(data)

    except:
      js = None
    if not js or 'status' not in js or js['status'] != 'OK':
      print('==== Failure To Retrieve ====')
      print(data)

    distance = js['rows'][0]['elements'][0]['distance']['value']
    return distance/1000

  def __repr__(self):
    return "(" + str(self.x) + "," + str(self.y) + ")"

class Fitness:
  def __init__(self, route):
    self.route = route
    self.distance = 0
    self.fitness = 0.0

  def routeDistance(self):
    if self.distance == 0:
      pathDistance = 0
      for i in range(0, len(self.route)):
        fromCity = self.route[i]
        toCity = None
        if i + 1 < len(self.route):
          toCity = self.route[i + 1]
        else:
          break
        pathDistance += fromCity.distance(toCity)
      self.distance = pathDistance
    return self.distance

  def routeFitness(self):
    if self.fitness == 0:
      self.fitness = 1 / float(self.routeDistance())
    return self.fitness

def createRoute(cityList):
  route = random.sample(cityList, len(cityList))
  return route


def initialPopulation(popSize, cityList):
  population = []

  for i in range(0, popSize):
    population.append(createRoute(cityList))
  return population


def rankRoutes(population):
  fitnessResults = {}
  for i in range(0, len(population)):
    fitnessResults[i] = Fitness(population[i]).routeFitness()
  return sorted(fitnessResults.items(), key=operator.itemgetter(1), reverse=True)


def selection(popRanked, eliteSize):
  selectionResults = []
  df = pd.DataFrame(np.array(popRanked), columns=["Index", "Fitness"])
  df['cum_sum'] = df.Fitness.cumsum()
  df['cum_perc'] = 100 * df.cum_sum / df.Fitness.sum()

  for i in range(0, eliteSize):
    selectionResults.append(popRanked[i][0])
  for i in range(0, len(popRanked) - eliteSize):
    pick = 100 * random.random()
    for i in range(0, len(popRanked)):
      if pick <= df.iat[i, 3]:
        selectionResults.append(popRanked[i][0])
        break
  return selectionResults


def matingPool(population, selectionResults):
  matingpool = []
  for i in range(0, len(selectionResults)):
    index = selectionResults[i]
    matingpool.append(population[index])
  return matingpool

def breed(parent1, parent2):
  child = []
  childP1 = []
  childP2 = []
  geneA = int(random.random() * len(parent1))
  geneB = int(random.random() * len(parent1))
  startGene = min(geneA, geneB)
  endGene = max(geneA, geneB)
  for i in range(startGene, endGene):
    childP1.append(parent1[i])
  childP2 = [item for item in parent2 if item not in childP1]
  child = childP1 + childP2
  return child

def breedPopulation(matingpool, eliteSize):
  children = []
  length = len(matingpool) - eliteSize
  pool = random.sample(matingpool, len(matingpool))
  for i in range(0, eliteSize):
    children.append(matingpool[i])
  for i in range(0, length):
    child = breed(pool[i], pool[len(matingpool) - i - 1])
    children.append(child)
  return children

def mutate(individual, mutationRate):
  for swapped in range(len(individual)):
    if (random.random() < mutationRate):
      swapWith = int(random.random() * len(individual))
      city1 = individual[swapped]
      city2 = individual[swapWith]
      individual[swapped] = city2
      individual[swapWith] = city1
  return individual

def mutatePopulation(population, mutationRate):
  mutatedPop = []
  for ind in range(0, len(population)):
    mutatedInd = mutate(population[ind], mutationRate)
    mutatedPop.append(mutatedInd)
  return mutatedPop

def nextGeneration(currentGen, eliteSize, mutationRate):
  popRanked = rankRoutes(currentGen)
  selectionResults = selection(popRanked, eliteSize)
  matingpool = matingPool(currentGen, selectionResults)
  children = breedPopulation(matingpool, eliteSize)
  nextGeneration = mutatePopulation(children, mutationRate)
  return nextGeneration

def geneticAlgorithm(population, popSize, eliteSize, mutationRate, generations):
  pop = initialPopulation(popSize, population)
  print("Initial distance: " + str(1 / rankRoutes(pop)[0][1]))

  for i in range(0, generations):
    pop = nextGeneration(pop, eliteSize, mutationRate)

  print("Final distance: " + str(1 / rankRoutes(pop)[0][1]))
  bestRouteIndex = rankRoutes(pop)[0][0]
  bestRoute = pop[bestRouteIndex]
  return bestRoute