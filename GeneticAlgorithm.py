import json
import ssl
from urllib import parse, request
import functools
import numpy as np
import operator
import pandas as pd
import random
import concurrent.futures

api_key = 'AIzaSyDmGpnn3txIZQlDrCKzo53Y8jgXEced3Hg'
service_url = 'https://maps.googleapis.com/maps/api/distancematrix/json?'

# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE


class ElementIterator:
    def __init__(self, lst):
        self.lst = lst
        self.i = 1

    def __next__(self):
        if self.i < len(self.lst):
            self.i += 1
            return self.lst[self.i - 2], self.lst[self.i - 1]
        else:
            raise StopIteration


class Route(list):
    def __iter__(self):
        return ElementIterator(self)


class City:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.lst = [self.x, self.y]

    def __iter__(self):
        for coordinate in self.lst:
            yield coordinate

    def distance(self, city):
        params = {'destinations': str(city.x) + ',' + str(city.y), 'key': api_key}
        url = service_url + 'origins=' + str(self.x) + ',' + str(self.y) + '&' + parse.urlencode(params)
        return self.calculate_distance(url) / 1000

    @functools.lru_cache()
    def calculate_distance(self, url):
        uh = request.urlopen(url, context=ctx)
        data = uh.read().decode()
        try:
            js = json.loads(data)
        except:
            js = None
            if not js or 'status' not in js or js['status'] != 'OK':
                print('==== Failure To Retrieve ====')
                print(data)

        distance = js['rows'][0]['elements'][0]['distance']['value']
        return distance

    def __repr__(self):
        return "(" + str(self.x) + "," + str(self.y) + ")"


class Fitness:
    def __init__(self, route):
        self.route = Route(route)
        self.distance = 0
        self.fitness = 0.0

    def initPopRouteDistance(self):
        if self.distance == 0:
            pathDistance = 0
            with concurrent.futures.ThreadPoolExecutor() as executor:
                results = [executor.submit(point[0].distance, point[1]) for point in self.route]

                for f in concurrent.futures.as_completed(results):
                    pathDistance += f.result()

            self.distance = pathDistance
        return self.distance

    def routeDistance(self):
        if self.distance == 0:
            pathDistance = 0
            for point in self.route:
                fromCity = point[0]
                toCity = point[1]
                pathDistance += fromCity.distance(toCity)
            self.distance = pathDistance
        return self.distance

    def routeFitness(self, init_pop=False):
        if self.fitness == 0:
            if init_pop:
                self.fitness = 1 / float(self.initPopRouteDistance())
            else:
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


def rankRoutes(population, init_pop=False):
    fitnessResults = {}
    for i in range(0, len(population)):
        fitnessResults[i] = Fitness(population[i]).routeFitness(init_pop)
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
        if random.random() < mutationRate:
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
    print("Initial distance: " + str(1 / rankRoutes(pop, init_pop=True)[0][1]))
    for i in range(0, generations):
        pop = nextGeneration(pop, eliteSize, mutationRate)
    print("Final distance: " + str(1 / rankRoutes(pop)[0][1]))
    bestRouteIndex = rankRoutes(pop)[0][0]
    bestRoute = pop[bestRouteIndex]
    return bestRoute
