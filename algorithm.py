from queue import deque

CONTINENT_BONUS = {'Asia':7, 'North America': 5, 'Europe': 5,
                   'Africa': 3, 'Australia': 2, 'South America': 2}

NORTH_AMERICA = {'Alaska', 'Northwest Territories', 'Alberta', 'Ontario',
                 'Eastern Canada', 'Greenland', 'Central America',
                 'Western United States', 'Eastern United States'}

SOUTH_AMERICA = {'Venezuela', 'Brazil', 'Peru', 'Argentina'}

EUROPE = {'Iceland', 'Great Britain', 'Scandinavia', 'Russia',
          'Northern Europe', 'Western Europe', 'Southern Europe'}

ASIA = {'Middle East', 'Afghanistan', 'Ural', 'Siberia', 'Yakutsk',
        'Kamchatka', 'Irkutsk', 'Mongolia', 'Japan', 'China',
        'India', 'Southeast Asia'}

AUSTRALIA = {'Indonesia', 'New Guinea', 'Eastern Australia', 'Western Australia'}

AFRICA = {'North Africa', 'Egypt', 'East Africa', 'Central Africa',
          'South Africa', 'Madagascar'}

NORTH_AMERICA = {'Alaska', 'Northwest Territories', 'Alberta', 'Ontario',
                 'Eastern Canada', 'Greenland', 'Central America',
                 'Western United States', 'Eastern United States'}


def path_search (source, destination, graph, player):
    ''' ** Based off breadth_first_search from Jan 21 Lecture **
    Find if there exists a path through the map such that the
    player owns all territories
    
    Returns: True if there exists a path
             False if there does not exist a path
    
    Params:
        source: The vertex where the path starts. 
        destination: The vertex where the path ends.
    '''
    reached = {source} # initialize reached set with source
    
    todo = deque([source]) # list of territories to check
    
    while todo: # while we have territories to check
        if destination in reached: # if we have found a path to dest
            break
        curr = todo.popleft() # remove item from todo list
        
        for succ in graph.neighbours(curr): # for each neighbouring territory
            if graph.owner(succ) is not player: 
                # if player does not own the terriory a path does not exist 
                continue
            if succ not in reached: # if we haven't already found a path to succ
                reached.add(succ) # add it to the reached set
                todo.append(succ) # add it to the todo list
    
    if destination in reached: # if we found a valid path
        return True
    else:
        return False


def get_probability(attacker, defender, memo = None):
	'''
	Finds the probability of winning in a battle between two territories
	Probability is determined by calculating the number of outcomes that have
	no defenders remaining divded by the number of all the possible outcomes
	Based on: http://www.datagenetics.com/blog/november22011/

	Returns: the probability of attacker winning

	Params:
		attacker: the number of attackers
		defender: the number of defenders
	'''
	if memo is None:
		memo = {}

	key = str(attacker) + "," + str(defender)

	if key not in memo:
		if attacker >= 3 and defender >= 2:
			probability = (2890/7776)*get_probability(attacker, defender - 2, memo) + (2611/7776)*get_probability(attacker - 1, defender - 1, memo) + (2275/7776)*get_probability(attacker - 2, defender, memo)
		elif attacker >= 3 and defender == 1:
			probability = (855/1296) + (441/1296)*get_probability(attacker - 1, defender, memo)
		elif attacker == 2 and defender >= 2:
			probability = (295/1296)*get_probability(attacker, defender - 2, memo) + (420/1296)*get_probability(attacker - 1, defender - 1, memo)
		elif attacker == 2 and defender == 1:
			probability = (125/216) + (91/216)*get_probability(attacker - 1, defender, memo)
		elif attacker == 1 and defender >= 2:
			probability = (55/216)*get_probability(attacker, defender - 1, memo)
		elif attacker == 1 and defender == 1:
			probability = (15/36)*get_probability(attacker, defender - 1, memo)
		elif defender == 0:
			probability = 1
		else:
			probability = 0

		memo[key] = probability

	return memo[key]


def positioning(graph, countries, player):
	'''
	Finds the most ideal territory to position the infantry from
	the territories owned by player

	Returns: the name of territory as string

	Params:
		graph: the graph in which the risk map is loaded
		countries: a list that contains all the string of countries
					possessed by the designated player
		player: the designated player represented as an integer
				0 - neutral
				2 - computer

	'''
	global NORTH_AMERICA, SOUTH_AMERICA, AFRICA, ASIA, EUROPE, AUSTRALIA

	# Case 1 - choosing territory for player 2 (computer)
	if player == 2:
		min_prob = 1
		continent = None
		min_terr = 0
		territory = None
		north_america = ["NORTH AMERICA", 9]
		south_america = ["SOUTH AMERICA", 4]
		europe = ["EUROPE", 7]
		asia = ["ASIA", 12]
		africa = ["AFRICA", 6]
		australia = ["AUSTRALIA", 4]

		# find the number of territories not possessed by player 2 in each continent
		for country in countries:
			if country in NORTH_AMERICA:
				north_america[1] -= 1
			elif country in SOUTH_AMERICA:
				south_america[1] -= 1
			elif country in EUROPE:
				europe[1] -= 1
			elif country in ASIA:
				asia[1] -= 1
			elif country in AFRICA:
				africa[1] -= 1
			elif country in AUSTRALIA:
				australia[1] -= 1

		# array is sorted such that the first element is the continent that player 2 requires the least amount of territories to gain the continent bonus
		array = sorted([north_america, south_america, europe, asia, africa, australia], key=lambda x: x[1])

		# first determines the number of allies surrounding each enemy territories
		# and finds a territory near enemy territory that has the least possibility of winning over that enemy territory
		for i in range(6):
			continent = array[i]
			if continent[1] == 0:	# if a continent has been conquered, conquer a continent that requires the least territory to obtain
				continue 
			# conquer the continent that is the easiest to conquer according to the most territories possesed in each continent
			if continent[0] is "ASIA":
				for country in ASIA:
					if graph.owner(country) == 2:
						continue
					allies = 0
					enemies = graph.armies(country)
					for neighbour in graph.neighbours(country):
						if graph.owner(neighbour) == 2:
							allies += graph.armies(neighbour) - 1
					probability = get_probability(allies, enemies)
					for neighbour in graph.neighbours(country):
						# get_probability(graph.armies(neighbour), graph.armies(country)) < 0.6 is used to distribute infantry to other surrounding territories
						# probability has a maximum threshold probability of 0.8
						if probability < 0.8 and probability < min_prob and get_probability(graph.armies(neighbour), graph.armies(country)) < 0.6 and graph.owner(neighbour) == 2:
							min_prob = probability
							territory = neighbour
			elif continent[0] is "NORTH AMERICA":
				for country in NORTH_AMERICA:
					if graph.owner(country) == 2:
						continue
					allies = 0
					enemies = graph.armies(country)
					for neighbour in graph.neighbours(country):
						if graph.owner(neighbour) == 2:
							allies += graph.armies(neighbour) - 1
					probability = get_probability(allies, enemies)
					for neighbour in graph.neighbours(country):	
						if probability < 0.8 and probability < min_prob and get_probability(graph.armies(neighbour), graph.armies(country)) < 0.6 and graph.owner(neighbour) == 2:
							min_prob = probability
							territory = neighbour
			elif continent[0] is "EUROPE":
				for country in EUROPE:
					if graph.owner(country) == 2:
						continue
					allies = 0
					enemies = graph.armies(country)
					for neighbour in graph.neighbours(country):
						if graph.owner(neighbour) == 2:
							allies += graph.armies(neighbour) - 1
					probability = get_probability(allies, enemies)
					for neighbour in graph.neighbours(country):
						if probability < 0.8 and probability < min_prob and get_probability(graph.armies(neighbour), graph.armies(country)) < 0.6 and graph.owner(neighbour) == 2:
							min_prob = probability
							territory = neighbour
			elif continent[0] is "AFRICA":
				for country in AFRICA:
					if graph.owner(country) == 2:
						continue
					allies = 0
					enemies = graph.armies(country)
					for neighbour in graph.neighbours(country):
						if graph.owner(neighbour) == 2:
							allies += graph.armies(neighbour) - 1
					probability = get_probability(allies, enemies)
					for neighbour in graph.neighbours(country):
						if probability < 0.8 and probability < min_prob and get_probability(graph.armies(neighbour), graph.armies(country)) < 0.6 and graph.owner(neighbour) == 2:
							min_prob = probability
							territory = neighbour
			elif continent[0] is "AUSTRALIA":
				for country in AUSTRALIA:
					if graph.owner(country) == 2:
						continue
					allies = 0
					enemies = graph.armies(country)
					for neighbour in graph.neighbours(country):
						if graph.owner(neighbour) == 2:
							allies += graph.armies(neighbour) - 1
					probability = get_probability(allies, enemies)
					for neighbour in graph.neighbours(country):
						if probability < 0.8 and probability < min_prob and get_probability(graph.armies(neighbour), graph.armies(country)) < 0.6 and graph.owner(neighbour) == 2:
							min_prob = probability
							territory = neighbour
			elif continent[0] is "SOUTH AMERICA":
				for country in SOUTH_AMERICA:
					if graph.owner(country) == 2:
						continue
					allies = 0
					enemies = graph.armies(country)
					for neighbour in graph.neighbours(country):
						if graph.owner(neighbour) == 2:
							allies += graph.armies(neighbour) - 1
					probability = get_probability(allies, enemies)
					for neighbour in graph.neighbours(country):
						if probability < 0.8 and probability < min_prob and get_probability(graph.armies(neighbour), graph.armies(country)) < 0.6 and graph.owner(neighbour) == 2:
							min_prob = probability
							territory = neighbour
						
			break

		if territory is not None:
			return territory

		# if no territory has been found, find the territory that has the
		# worst probability of winning a battle with minimum threshold probability of 0.05
		# and maximum threshold probability of 0.8
		for country in countries:
			for neighbour in graph.neighbours(country):
				allies = 0
				for a_neighbour in graph.neighbours(neighbour):
					if graph.owner(a_neighbour) == 2:
						allies += graph.armies(a_neighbour)
				probability = get_probability(allies, graph.armies(neighbour))
				if probability > 0.05 and probability < 0.8 and probability < min_prob and get_probability(graph.armies(country), graph.armies(neighbour)) < 0.6:
					min_prob = probability
					territory = country

		# if no territory has still not been found, find territory that has the worst probablity of defending
		if territory not in countries:
			for country in countries:
				for neighbour in graph.neighbours(country):
					probability = 1 - get_probability(graph.armies(neighbour),graph.armies(country))
					if probability < min_prob:
						min_prob = probability
						territory = country


		return territory

	# Case 2 - choosing territory for player 0 (neutral)
	# returns the territory that distracts player 1 from obtaining a continent bonus
	else:
		north_america = ["NORTH AMERICA", 9]
		south_america = ["SOUTH AMERICA", 4]
		europe = ["EUROPE", 7]
		asia = ["ASIA", 12]
		africa = ["AFRICA", 6]
		australia = ["AUSTRALIA", 4]

		# find the number of territories not possessed by player 1 in each continent
		for country in NORTH_AMERICA:
			if graph.owner(country) == 1:
				north_america[1] -= 1
		for country in SOUTH_AMERICA:
			if graph.owner(country) == 1:
				south_america[1] -= 1
		for country in EUROPE:
			if graph.owner(country) == 1:
				europe[1] -= 1
		for country in ASIA:
			if graph.owner(country) == 1:
				asia[1] -= 1
		for country in AFRICA:
			if graph.owner(country) == 1:
				africa[1] -= 1
		for country in AUSTRALIA:
			if graph.owner(country) == 1:
				australia[1] -= 1

		# array is sorted such that the first element is the continent that player 1 requires the least amount of territories to receive the continent bonus
		array = sorted([north_america, south_america, europe, asia, africa, australia], key=lambda x: x[1])

		north_america1 = 0
		south_america1 = 0
		europe1 = 0
		asia1 = 0
		africa1 = 0
		australia1 = 0

		# finds the number of territories possessed by player 0
		for country in countries:
			if country in NORTH_AMERICA:
				north_america1 += 1
			elif country in SOUTH_AMERICA:
				south_america1 += 1
			elif country in EUROPE:
				europe1 += 1
			elif country in ASIA:
				asia1 += 1
			elif country in AFRICA:
				africa1 += 1
			elif country in AUSTRALIA:
				australia1 += 1

		# finds the continent or the ith element of array in which the player 1 
		# requires the least amount of territories and player 0 possesses some territory in that continent
		i = 0
		while True:
			if array[i][0] == "NORTH AMERICA" and north_america1 == 0:
				north_america1 += 1
			elif array[i][0] == "SOUTH AMERICA" and south_america1 == 0:
				south_america1 += 1
			elif array[i][0] == "EUROPE" and europe1 == 0:
				europe1 += 1
			elif array[i][0] == "ASIA" and asia1 == 0:
				asia1 += 1
			elif array[i][0] == "AFRICA" and africa1 == 0:
				africa1 += 1
			elif array[i][0] == "AUSTRALIA" and australia1 == 0:
				australia1 += 1
			else:
				break
			i += 1
		
		# finds some random territory in the continent found above
		while True:
			if array[i][0] == "NORTH AMERICA":
				territory = NORTH_AMERICA.pop()
			elif array[i][0] == "SOUTH AMERICA":
				territory = SOUTH_AMERICA.pop()
			elif array[i][0] == "EUROPE":
				territory = EUROPE.pop()
			elif array[i][0] == "ASIA":
				territory = ASIA.pop()
			elif array[i][0] == "AFRICA":
				territory = AFRICA.pop()
			elif array[i][0] == "AUSTRALIA":
				territory = AUSTRALIA.pop()
			if graph.owner(territory) == 0:
				NORTH_AMERICA = {'Alaska', 'Northwest Territories', 'Alberta', 'Ontario',
								'Eastern Canada', 'Greenland', 'Central America',
								'Western United States', 'Eastern United States'}

				SOUTH_AMERICA = {'Venezuela', 'Brazil', 'Peru', 'Argentina'}

				EUROPE = {'Iceland', 'Great Britain', 'Scandinavia', 'Russia',
						'Northern Europe', 'Western Europe', 'Southern Europe'}

				ASIA = {'Middle East', 'Afghanistan', 'Ural', 'Siberia', 'Yakutsk',
						'Kamchatka', 'Irkutsk', 'Mongolia', 'Japan', 'China',
						'India', 'Southeast Asia'}

				AUSTRALIA = {'Indonesia', 'New Guinea', 'Eastern Australia', 'Western Australia'}

				AFRICA = {'North Africa', 'Egypt', 'East Africa', 'Central Africa',
						'South Africa', 'Madagascar'}

				NORTH_AMERICA = {'Alaska', 'Northwest Territories', 'Alberta', 'Ontario',
						'Eastern Canada', 'Greenland', 'Central America',
						'Western United States', 'Eastern United States'}
				return territory	
			

def moving(graph, countries, player):
	'''
	Finds the source location and destination location to move infantry in order to 
	increase the possibility of winng

	Returns: the name of territory to move infantry from (source)
				and the name of territory to move infantry to (destination)
				as a tuple 
	Params:
		graph: the graph in which the risk map is loaded
		countries: a list that contains all the string of countries
					possessed by the designated player
		player: the designated player represented as an integer
				2 - computer
	'''
	destination = positioning(graph, countries, 2)
	max_prob = 1
	source = None
	for country in countries:
		enemies = 0
		for neighbour in graph.neighbours(country):
			if graph.owner(neighbour) == 1:
				probability = 1 - get_probability(graph.armies(neighbour), graph.armies(country) - 1)
				enemies += graph.armies(neighbour)
			# infantry should be taken from territory such that it is able to defend the territory after one unit has been taken away
			if graph.owner(neighbour) == 1 and probability > 0.7 and max_prob < probability and path_search(country, destination, graph, player):
				max_prob = probability
				source = country
		if enemies == 0 and graph.armies(country) - 1 > 0 and path_search(country, destination, graph, player):	# if country is not surrounded by any enemy, infantry can be taken 
			return (country, destination)

	return (source, destination)


def attack(graph, countries, player = 2):
	'''
	Finds an enemy territory that has the maximum possibility of 
	conquering

	Returns: the name of territory to attack as string
			None if maximum probability is lower than the threshold probability of 0.7 
	Params:
		graph: the graph in which the risk map is loaded
		countries: a list that contains all the string of countries
					possessed by the designated player
		player: the designated player represented as an integer
				2 - computer
	'''
	max_prob = 0
	territory = None
	attack = None
	# finds the success probability of number of surrounding allies attacking
	# the enemy territory
	for country in countries:
		for neighbour in graph.neighbours(country):
			if graph.owner(neighbour) == 2:
				continue
			allies = 0
			for a_neighbour in graph.neighbours(neighbour):
				if graph.owner(a_neighbour) == 2:
					allies += graph.armies(a_neighbour) - 1
			probability = get_probability(allies, graph.armies(neighbour))
			# get_probability(graph.armies(country), graph.armies(neighbour)) > 0.15 is used beacuse
			# ally territory should not risk all of the units to capture the enemy territory
			if probability > max_prob and graph.armies(country) > 1 and get_probability(graph.armies(country), graph.armies(neighbour)) > 0.15:
				max_prob = probability
				territory = country
				attack = neighbour

	if max_prob < 0.7:
		return None
		
	return (territory, attack)
