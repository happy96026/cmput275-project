from graph import WeightedUndirectedGraph # We don't actually use the weights at any point, just undirected was necessary
from queue import deque
import random, algorithm
import pygame, sys, constants, textrect, func
from pygame.locals import *

risk_map = WeightedUndirectedGraph()
CARD_VALUES = {} # dictionary mapping each cards to the army face value
CARDS = list() # card deck

filename = "risk-map.txt"
with open(filename) as file:
   for line in file: # Variable 'line' loops over each line in the file
        line = line.strip() # Remove trailing newline character
        # Process the line here
        line = line.split(',')
        if line[0] == 'V': # add vertex
            risk_map.add_vertex(line[1])
            CARD_VALUES[line[1]] = int(line[2])
            CARDS.append(line[1])
        elif line[0] == 'E': # add add_edge
            risk_map.add_edge(line[1], line[2], line[3])



CONTINENT_BONUS = {'Asia':7, 'North America': 5, 'Europe': 5,
                   'Africa': 3, 'Australia': 2, 'South America': 2}

NORTH_AMERICA = {'Alaska', 'Northwest Territories', 'Alberta', 'Ontario',
                 'Eastern Canada', 'Greenland', 'Central America',
                 'Western United States', 'Eastern United States'}

SOUTH_AMERICA = {'Venezuela', 'Brazil', 'Peru', 'Argentina'}

EUROPE = {'Iceland', 'Great Britain', 'Scandinavia', 'Russia',
          'Northern Europe', 'Western Europe', 'Southern Europe'}

ASIA = {'Middle East', 'Afghanistan', 'Ural', 'Siberia', 'Yalutsk',
        'Kamchatka', 'Irkutsk', 'Mongolia', 'Japan', 'China',
        'India', 'Southeast Asia'}

AUSTRALIA = {'Indonesia', 'New Guinea', 'Eastern Australia', 'Western Australia'}

AFRICA = {'North Africa', 'Egypt', 'East Africa', 'Central Africa',
          'South Africa', 'Madagascar'}

Cards = list([set(), set(), set()])
Countries = list([set(), set(), set()])
Traded = 0
player = 2

old_source = None
old_destination = None



def select_territory(param = 'attack'):
    '''
    Allows player to select a territory on the game board
    
    Returns: territory in constants.TERRITORIES
    Params: param - specifies whether we are selecting to attack or 
                    for neutral purposes.
                    (Default attack)
    '''
    if player == 1:
        territory = func.select()
    elif player == 2:
        if param == 'attack':
            territory = algorithm.attack(risk_map, Countries[2])
        elif param == 'place':
            terr = algorithm.positioning(risk_map, Countries[2], player)
            for t in constants.TERRITORIES:
                if t["Name"] == terr:
                    break
            territory = t
    else: # player == 0:
        terr = algorithm.positioning(risk_map, Countries[0], player)
        for t in constants.TERRITORIES:
            if t["Name"] == terr:
                break
        territory = t
    return territory

def select_cards(cards, number):
    '''
    Allows player to select a card to trade in 
   
    Params: cards - set of cards belonging to the player whose turn 
                    it is
            number - specifies the number of cards to select.
                     (normally 3 but may be less for bonus)
    Returns: card list of cards selected from cards
     '''
    global player, risk_map, Cards, Countries, CARD_VALUES
    
    if player is 1:
        card = list()
        cards = sorted(list(cards))
        card_text = ""
        i = 1
        
        for c in cards: # display cards
            card_text += str(i) + ": " + c + " = " + str(CARD_VALUES[c]) + "   "
            i += 1
        text = card_text + "\nPlease select the index of a card"
        for i in range(number): # Pick x cards
            while True:
                index = func.number(text)
                if index == 0 or index > len(cards) or cards[index-1] in card:
                    func.text1 = "ERROR: Invalid index!"
                    func.refresh()
                    pygame.time.delay(1000)
                    continue
                card.append(cards[index-1])
                break
        
    else: # player 2
        uniques = set()
        own = set()
        card = list()
        for c in cards:
            uniques.add(CARD_VALUES[c])
            if c is not 'Wild' and risk_map.owner(c) is player:
                own.add(c)
        if 0 in uniques: # Wild Card Case
            card.append('Wild')
            cards.remove('Wild')
            uniques.remove(0)
            if 'Wild' in cards: # Second Wild Card
                card.append('Wild')
                cards.remove('Wild')
                if own: # If we own a territory in cards
                    card.append(own.pop()) 
                else:
                    card.append(cards.pop()) # No ownership
            elif len(uniques) == 1: # just add 2 cards
                card.append(cards.pop())
                card.append(cards.pop())
            else: # len(uniques) == 2 or len(uniques) == 3:
                c = cards.pop() # add any one card
                card.append(c)
                uniques.remove(CARD_VALUES[c]) # remove that cards value from uniques
                c = cards.pop()
                while CARD_VALUES[c] not in uniques:
                    c = cards.pop() # find another card that is unique
                card.append(c)
        
        else: # No wild Cards
            if len(uniques) == 1: # add three cards, simple
                for i in range(3):
                    card.append(cards.pop())
            elif len(uniques) == 2: # Ex. card values = {1,1,5,5,1}
                occurs = [0,0]
                val1 = uniques.pop()
                val2 = uniques.pop()
                for c in cards: # find what card value happend 3 times
                    if CARD_VALUES[c] is val1:
                        occurs[0] += 1
                    else: # CARD_VALUES[c] is val2:
                        occurs[1] += 1
                if occurs[0] > 2:
                    val = val1 # save that value
                else: # occurs[1] > 2:
                    val = val2
                for c in cards: # append the three cards with value == val
                    if CARD_VALUES[c] is val:
                        card.append(c)
                cards.remove(card[0]) # remove cards from hand
                cards.remove(card[1])
                cards.remove(card[2])
            else: # len(uniques) == 3
                c = cards.pop() # take any one card
                card.append(c)
                uniques.remove(CARD_VALUES[c]) # remove value from uniques
                for i in range(2): # two more cards to add
                    c = cards.pop()
                    while CARD_VALUES[c] not in uniques: # find on with value not already used
                        c = cards.pop()
                    card.append(c)
                    uniques.remove(CARD_VALUES[c])
    
    return card

def place_infantry(infantry, i_type):
    '''
    Allows player to place the specified number of infantry on the board
    
    Returns: None
    Params: infantry - the number of infantry to place
            i_type - specifies whether placing attack or neutral infantry
    '''
    global risk_map, player
    # TODO Player 2 !
    while infantry:
        num = str(infantry)
        func.text1 = "Please place " + num + " infantry.\nSelect a territory" # Prompt user to select terrirory
        terr = select_territory('place')
        if i_type == "allies":
        	if risk_map.owner(terr["Name"]) is not player:
        		func.text1 = "ERROR: You do not own that territory.\n"# Print error message
        		func.refresh()
        		pygame.time.delay(1000)
        		continue
        	else:
        		terr["Infantry"] += 1
        		risk_map.add_army(terr["Name"], 1) # add chosen armies to selected terr
        		infantry -= 1
        else: # neutral
        	if risk_map.owner(terr["Name"]) is not 0:
        		func.text1 = ("ERROR: "+ terr["Name"] +" is not a neutral territory\nPlease select again.")
        		func.refresh()
        		pygame.time.delay(1000)
        		continue
        	else:
        		terr["Infantry"] += 1
        		risk_map.add_army(terr["Name"], 1) # Must add 1
        		infantry -= 1


def setup():
    '''
    Allows players to take turns placing initial infantry on the board
    
    Returns: None
    Params: None
    '''
    global risk_map, Cards, Countries, player
    deck = list()
    for c in CARDS:
        deck.append(c)
    random.shuffle(deck)
    while deck: # deal cards
        Cards[0].add(deck.pop())
        Cards[1].add(deck.pop())
        Cards[2].add(deck.pop())
    
    # assign territories and place 1 infantry in each
    for terr in Cards[0]:
        Countries[0].add(terr)
        risk_map.set_owner(terr, 0)
        risk_map.add_army(terr, 1)
    for terr in Cards[1]:
        Countries[1].add(terr)
        risk_map.set_owner(terr, 1)
        risk_map.add_army(terr, 1)
    for terr in Cards[2]:
        Countries[2].add(terr)
        risk_map.set_owner(terr, 2)
        risk_map.add_army(terr, 1)
    
    for territory in func.TERRITORIES:
    	if risk_map.owner(territory["Name"]) == 1:
    		territory["Color"] = constants.LIGHT_GREEN
    	elif risk_map.owner(territory["Name"]) == 2:
    		territory["Color"] = constants.LIGHT_RED
    	else:
    		territory["Color"] = constants.LIGHT_YELLOW
    	territory["Player"] = risk_map.owner(territory["Name"])
    	territory["Infantry"] = 1
    
    func.text1 = "Initializing..."
    func.refresh()
    pygame.time.delay(1000)
    
    # Each player begins with 40 armies
    # Place one army in each territory
    # Each player places 14 armies to begin with
    # These are placed automatically as below
    # remaining 40-14=26 armies are placed taking turns
    for armies in range(0,26,2):
        func.text1 = "Please place 2 infantry units in your territories"
        func.refresh()
        pygame.time.delay(1500)
        player = 1
        place_infantry(2, "allies")
        func.text1 = "Please select a territory for one neutral army"
        func.refresh()
        pygame.time.delay(1500)
        place_infantry(1, "neutral")
        
        player = 2
        place_infantry(2, "allies") # player 2
        player = 0
        place_infantry(1, "neutral") # neutral armies
        player = 2
        
        # each player placed two each round
    
    # return cards to deck (Empty player hands)
    Cards[0] = set()
    Cards[1] = set()
    Cards[2] = set()
    # add 2 wild cards to deck
    for i in range(2):
        CARDS.append('Wild')
    CARD_VALUES['Wild'] = 0
    random.shuffle(CARDS)


def card_bonus():
    '''
    Returns: Number of armies to be placed due to trading in cards
    
    Params: None
    '''
    global risk_map, Cards, Countries, Traded, player, CARD_VALUES, CARDS
    num_armies = 0
    
    if len(Cards[player]) < 3:
        func.text1 = "Card trading not possible (Less than 3 cards)"
        func.refresh()
        pygame.time.delay(1000)
        return 0
    
    # Check validity of cards
    uniques = set()
    for c in Cards[player]:
        uniques.add(CARD_VALUES[c])
    # if Wild Card or All cards match or All cards Different
    if 0 in uniques or len(uniques) == 1 or len(uniques) == 3 or len(Cards[player]) > 4:  
        # Valid trade exists   
        trade = False
        text = ""
        for c in Cards[player]:
            text += c + ": " + str(CARD_VALUES[c]) + "   "
        text += "\nWould you like to trade cards?"
        if player is 1:
            # Ask player if they want to trade
            if func.yes_no(text):
                trade =  True
        else: # player is 2
            trade = True 
        
        if trade:
            Traded += 1
            selected = set()
            valid = False
            while not valid:
                card = select_cards(Cards[player], 3)
                selected.add(CARD_VALUES[card[0]])
                selected.add(CARD_VALUES[card[1]])
                selected.add(CARD_VALUES[card[2]])
                if ((len(selected) == 1) or
                   (len(selected) == 3) or
                   (0 in selected)):
                    valid = True
                else:
                    func.text1 = "ERROR: Invalid card selections\nPlease select all 3 again" # Print error message 
                    func.refresh()
                    pygame.time.delay(1500)
                    continue
            if Traded < 6:
                num_armies += 2*Traded + 2 # Constant formula from rule book
            else:
                num_armies += 5*Traded - 15 # Constant formula from rule book
            bonus = set()
            if card[0] in Countries[player]:
                bonus.add(card[0])
            if card[1] in Countries[player]:
                bonus.add(card[1])
            if card[2] in Countries[player]:
                bonus.add(card[2])
            if len(bonus) == 1:
                # Default to add to that country in bonus
                terr = bonus.pop()
                for t in constants.TERRITORIES:
                    if t["Name"] == terr:
                        break
                t["Infantry"] += 2
                risk_map.add_army(terr, 2)
                func.text1 = "Bonus of 2 armies added to " + terr # Print message
                func.refresh()
                pygame.time.delay(3000)
            elif bonus:
                # More than 1 country in bonus
                # Player chooses country in bonus cards to place additional
                # two armies on
                if player == 1:
                    func.text1 = "Two or more territories owned on traded cards\nPlease select a card to add a bonus of 2 armies..."
                    func.refresh()
                    pygame.time.delay(3000)
                    b_card = select_cards(bonus, 1)
                    for t in constants.TERRITORIES:
                        if t["Name"] == b_card[0]:
                            break
                    t["Infantry"] += 2
                    risk_map.add_army(b_card[0], 2)
                    func.text1 = "Bonus of 2 armies added to " + b_card[0] # Print message
                    func.refresh()
                    pygame.time.delay(3000)
                else: # player == 2
                    terr = bonus.pop()
                    for t in constants.TERRITORIES:
                        if t["Name"] == terr:
                            break
                    t["Infantry"] += 2
                    risk_map.add_army(terr, 2)
                    func.text1 = "Bonus of 2 armies added to " + terr # Print message
                    func.refresh()
                    pygame.time.delay(3000)
            
            if player == 1:
                # Remove traded cards from player's hand
                Cards[player].remove(card[0])
                Cards[player].remove(card[1])
                Cards[player].remove(card[2])
    
    else: # No valid trade exists
        func.text1 = "Card trading not possible (No valid combinations)"
        func.refresh()
        pygame.time.delay(1000)
    
    return num_armies


def attacking_dice (attacking):
    ''' Determines the number of dice to roll for the attacking player
    Returns the number of dice to be rolled
    Args: attacking - the territory id of the attacking territory
    '''
    global risk_map
    if player is 1:
        while True:
            text = "Please select the number of dice to roll" # Prompt player for number of dice
            text += "\n(Between 1 and " + str(min(3, risk_map.armies(attacking)-1)) + ")"
            num_dice = func.number(text)
            if (num_dice < risk_map.armies(attacking) and
               num_dice < 4 and num_dice > 0):
                break
            func.text1 = "ERROR: Invalid number of dice!" # Print error message
            func.refresh()
            pygame.time.delay(1000)
    else: # player is 2 (roll as many as possible)
        if risk_map.armies(attacking) > 3:
            num_dice = 3
        elif risk_map.armies(attacking) == 3: # risk_map.armies(attacking) == 2:
            num_dice = 2
        else:
            num_dice = 1

    return num_dice


def defending_dice (attacking, defending, attack_rolls):
    ''' Determines the number of dice to roll for the defending player
    Returns: the number of dice to be rolled
    Args: attacking - the territory id of the attacking territory
          defending - the territory id of the defending territory
          attack_rolls - the number of dice the attacker chose to roll'''
    global risk_map
    if player is 1: # then player 2 or neutral defends (roll as many as possible)
        if risk_map.armies(defending) > 1:
            num_dice = 2
        else:
            num_dice = 1
    else: # player is 2 / 0 so player 1 defends:
        while True:
            text = "Player "+ str(risk_map.owner(defending)) + ", " + defending + " is under attack from " + attacking
            text += "\nPlease select the number of dice to roll " # Prompt player for number of dice
            text += "(Between 1 and " + str(min(2, risk_map.armies(defending))) + ")"
            num_dice = func.number(text)
            if (num_dice <= risk_map.armies(defending) and
               num_dice <=2 and num_dice > 0):
                break
            func.text1 = "ERROR: Invalid number of dice!" # Print error message
            func.refresh()
            pygame.time.delay(1000)
    
    return num_dice


def battle (attacking, defending):
    '''Decides the outcome of an attack based on dice rolls
    
    Returns: the outcome of the attack (True if the terriroy is 
             captured, otherwise False)
    Params: attacking - the id of the territory performing the attack
            defending - the id of the territory receiving the attack
    '''
    global risk_map, Cards, Countries, player
    attack_dice = list()
    defend_dice = list()
    
    # Rerieve territories
    for a_terr in constants.TERRITORIES:
        if a_terr["Name"] == attacking:
            break
    for d_terr in constants.TERRITORIES:
        if d_terr["Name"] == defending:
            break
    
    # Attacking Dice
    num_dice = attacking_dice(attacking)
    for i in range(num_dice): # Dice rolls
        attack_dice.append(random.randint(1,6))
    attack_rolls = len(attack_dice)
    
    # Defending Dice
    num_dice = defending_dice(attacking, defending, attack_rolls)
    for i in range(num_dice): # Dice rolls
        defend_dice.append(random.randint(1,6))
    defend_rolls = len(defend_dice)
    
    attack_dice.sort()
    defend_dice.sort()
    
    func.text1 = "Attacker rolled: "
    for i in range(attack_rolls):
        func.text1 += str(attack_dice[i]) + " "
    func.text1 += "\nDefender rolled: " 
    for i in range(defend_rolls):
        func.text1 += str(defend_dice[i]) + " "
    func.refresh()
    pygame.time.delay(750)
    
    for i in range(min(attack_rolls, defend_rolls)):
        if max(attack_dice) > max(defend_dice):
            func.text1 = "Defender lost 1 army!" # Print message
            func.refresh()
            pygame.time.delay(1000)
            d_terr["Infantry"] -= 1
            remaining = risk_map.remove_army(defending, 1)
            if not remaining: # ie conquered the territory
                Countries[risk_map.owner(attacking)].add(defending) # add conquered territory to players owned countries
                Countries[risk_map.owner(defending)].remove(defending) # remove territory from defenders owned countries
                risk_map.set_owner(defending, player) # set ownership
                d_terr["Player"] = player
                func.refresh()
                if player is 1:
                    d_terr["Color"] = constants.LIGHT_GREEN # set colour
                    while True:
                        # Prompt user for number of armies to move into captured territory
                        text = "CONQUERED!\nHow many armies would you like to move?"
                        text += "\n(Between " + str(attack_rolls) + " and " + str(risk_map.armies(attacking)-1) + ")"
                        move_armies = func.number(text)
                        if move_armies < attack_rolls:
                            func.text1 = "ERROR: Too few armies! Must move at least " + str(attack_rolls) # Print error message
                            func.refresh()
                            pygame.time.delay(1000)
                            continue
                        if move_armies >= risk_map.armies(attacking):
                            func.text1 = "ERROR: Too many armies! Must move at most " + str(risk_map.armies(attacking)-1) # Print error message
                            func.refresh()
                            pygame.time.delay(1000)
                            continue
                        break
                else:
                    d_terr["Color"] = constants.LIGHT_RED # set colour
                    func.hover_color(d_terr, constants.RED)
                    move_armies = risk_map.armies(attacking) - 1
                risk_map.add_army(defending, move_armies) # add moved armies to new location
                d_terr["Infantry"] += move_armies
                risk_map.remove_army(attacking, move_armies) # remove moved armies from old location
                a_terr["Infantry"] -= move_armies
                return True # We have conquered the territory. No further rolls are required
        else: # max(defend_dice) >= max(attack_dice)
            func.text1 = "Attacker lost 1 army!" # Print message
            func.refresh()
            pygame.time.delay(1000)
            a_terr["Infantry"] -= 1
            result = risk_map.remove_army(attacking, 1)
        # remove the compared dice from the sets and check the next pair (if applicable)
        attack_dice.remove(max(attack_dice))
        defend_dice.remove(max(defend_dice))
        func.selection_screen()
        func.text1 = "And..." # Print message
        func.refresh()
        pygame.time.delay(500)
    
    return False # if we did not capture the territory


def path_search (source, destination):
    ''' ** Based off breadth_first_search from Jan 21 Lecture **
    Find if there exists a path through the map such that the
    player owns all territories
    
    Returns: True if there exists a path
             False if there does not exist a path
    
    Params:
        source: The vertex where the path starts. 
        destination: The vertex where the path ends.
    '''
    global risk_map, player
    reached = {source} # initialize reached set with source
    
    todo = deque([source]) # list of territories to check
    
    while todo: # while we have territories to check
        if destination in reached: # if we have found a path to dest
            break
        curr = todo.popleft() # remove item from todo list
        
        for succ in risk_map.neighbours(curr): # for each neighbouring territory
            if risk_map.owner(succ) is not player: 
                # if player does not own the terriory a path does not exist 
                continue
            if succ not in reached: # if we haven't already found a path to succ
                reached.add(succ) # add it to the reached set
                todo.append(succ) # add it to the todo list
    
    if destination in reached: # if we found a valid path
        return True
    else:
        return False


def turn():
    '''
    Returns: True if the player has successfully captured all countries
             Otherwise returns False
    
    Params: player - The id of the player whose turn it is
    '''
    global risk_map, Cards, Countries, player
    global CONTINENT_BONUS, NORTH_AMERICA, SOUTH_AMERICA, EUROPE, ASIA, AUSTRALIA, AFRICA
    global old_source, old_destination
    # initialize variables
    new_armies = 0
    
    # determine the territory bonus
    territory_bonus = len(Countries[player])//3
    if territory_bonus < 3: 
        territory_bonus = 3
    new_armies += territory_bonus # add territory bonus to new armies total
    
    # determine if player owns entire continents and add the continent
    # bonus to the new armies total if applicable
    if NORTH_AMERICA < Countries[player]:
        new_armies += CONTINENT_BONUS['North America']
    if SOUTH_AMERICA < Countries[player]:
        new_armies += CONTINENT_BONUS['South America']
    if EUROPE < Countries[player]:
        new_armies += CONTINENT_BONUS['Europe']
    if ASIA < Countries[player]:
        new_armies += CONTINENT_BONUS['Asia']
    if AUSTRALIA < Countries[player]:
        new_armies += CONTINENT_BONUS['Australia']
    if AFRICA < Countries[player]:
        new_armies += CONTINENT_BONUS['Africa']
    
    # determine the card bonus and add to the new armies total
    new_armies += card_bonus()
    
    place_infantry(new_armies, "allies")
    
    # ATTACK PHASE
    conquered = False
    
    while True:
        if player == 1:
            # option to quit attacking
            for c in Countries[1]:
                if risk_map.armies(c) > 1:
                    break
            else:
                func.text1 = "No more attacks are possible!"
                func.refresh()
                pygame.time.delay(1500)
                break
            if not func.yes_no("Would you like to attack an opponent?"): 
                break
        else: # Player is 2
            territories = select_territory()
            if territories is None:
                break
            attacking_territory = territories[0]
            defending_territory = territories[1]
            
        
        attack_success = False
        func.text1 = "Please select a territory to attack from." # Print message to select attacking_territory
        func.refresh()
        pygame.time.delay(750)
        if player == 1:
            territory = select_territory()
            attacking_territory = territory["Name"]
        if risk_map.owner(attacking_territory) is not player:
            func.text1 = "ERROR: You do not own "+attacking_territory+"!" # Print error message
            func.refresh()
            pygame.time.delay(1000)
            continue
        if risk_map.armies(attacking_territory) < 2:
            func.text1 = "ERROR: Too few armies in "+attacking_territory # Print error message
            func.refresh()
            pygame.time.delay(1000)
            continue
        for neigh in risk_map.neighbours(attacking_territory):
            if risk_map.owner(neigh) is not player:
                break
        else:
            func.text1 = "ERROR: No enemy territories bordering "+attacking_territory # Print error message
            func.refresh()
            pygame.time.delay(1000)
            continue
        while True:
            func.text1 = "Please select a neighbouring territory to attack." # Print message to select defending territory
            func.refresh()
            pygame.time.delay(750)
            if player == 1: # already decided for player 2
                territory = select_territory()
                defending_territory = territory["Name"]                
            if risk_map.owner(defending_territory) is player:
                func.text1 = "ERROR: You own "+defending_territory+"!" # Print error message
                func.refresh()
                pygame.time.delay(1000)
                continue
            if risk_map.is_edge(attacking_territory, defending_territory):
                break
            else:
                func.text1 = "ERROR: "+defending_territory+" does not border "+attacking_territory # Print error message
                func.refresh()
                pygame.time.delay(1000)
                continue
        
        conquered = max(conquered, battle(attacking_territory, defending_territory))
        
        # Determine if player has won the game
        if player is 1:
            if not Countries[2]:
                return True
        else:
            if not Countries[1]:
                return True
    
    if conquered: # take a card from the deck
        Cards[player].add(CARDS.pop())
    
    # FORTIFICATION PHASE
    
    # Allow user to change location of armies
    while True:
        # option to quit fortifying
        if player == 1:
            for c in Countries[1]:
                if risk_map.armies(c) > 1:
                    break
            else:
                func.text1 = "No fortification is possible!"
                func.refresh()
                pygame.time.delay(1500)
                break
            if not func.yes_no("Would you like to Fortify your territories?"):
                break
        else: # player == 2
            (source, destination) = algorithm.moving(risk_map, Countries[2], player)
            num_armies = 1
            if source is None or (old_source == destination and old_destination == source):
                break
            old_source = source
            old_destination = destination
            
        func.text1 = "Please select a territory to move armies from" # print message to select source territory
        func.refresh()
        pygame.time.delay(750)
        if player == 1:
            terr = select_territory()
            source = terr["Name"]
        if risk_map.owner(source) is not player:
            func.text1 = "ERROR: You do not own " + source # Print error message
            func.refresh()
            pygame.time.delay(1000)
            continue
        if risk_map.armies(source) == 1:
            func.text1 = "ERROR: Not enough armies to move"
            func.refresh()
            pygame.time.delay(1000)
            continue
        
        func.text1 = "Please select a territory to move armies to" # print message to select destination territory
        func.refresh()
        pygame.time.delay(750)
        if player == 1:
            terr = select_territory()
            destination = terr["Name"]
        if risk_map.owner(destination) is not player:
            func.text1 = "ERROR: You do not own " + destination # Print error message
            func.refresh()
            pygame.time.delay(1000)
            continue
        
        if not path_search(source, destination):
            func.text1 = "ERROR: Path does not exist between " + source + " and " + destination # Print error message
            func.refresh()
            pygame.time.delay(1500)
            continue
        
        text = "Please enter the number of armies to move" # print message to select number of armies to move
        text += "\n(Between 1 and " + str(risk_map.armies(source)-1) + ")"
        if player == 1:
            num_armies = func.number(text)
        if num_armies >= risk_map.armies(source) or num_armies == 0:
            func.text1 = "ERROR: Invalid number of armies!" # Print error message
            func.refresh()
            pygame.time.delay(750)
            continue
        
        # If we reach this point we have a valid move case
        # Rerieve territories
        for s_terr in constants.TERRITORIES:
            if s_terr["Name"] == source:
                break
        for d_terr in constants.TERRITORIES:
            if d_terr["Name"] == destination:
                break
        
        risk_map.remove_army(source, num_armies) # remove armies from source
        s_terr["Infantry"] -= num_armies
        risk_map.add_army(destination, num_armies) # add armies to destination
        d_terr["Infantry"] += num_armies
    
    # Finished player's turn, they did not conquer the entire map.
    return False

def success():
    '''Function to celebrate the specified player's victory'''
    global player
    func.text1 = "CONGRATULATIONS Player " + str(player) + "!\nYou have won the game!!!"
    func.refresh()
    pygame.time.delay(10000)

def main():
    ''' Main funtion for the project.
        Implements turn taking
        
        Returns: None
        Args: None
    '''
    
    global player
    events = pygame.event.get()
    for event in events:
        if event.type == QUIT:	
            pygame.quit()
            sys.exit()
    setup()
    win = False
    while not win:
        if player == 1:
            player = 2
            func.text1 = "Player 2's turn!"
            func.refresh()
            pygame.time.delay(750)
        else:
            player = 1
            func.text1 = "Player 1's turn!"
            func.refresh()
            pygame.time.delay(750)
        win = turn()
    success()

if __name__ == "__main__":
    main()
