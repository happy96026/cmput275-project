import pygame, sys, constants, textrect, string
from pygame.locals import *

pygame.init()
DISPLAYSURF = pygame.display.set_mode((1300,1500))
background = pygame.image.load("images/background.jpg").convert_alpha()
r_map = pygame.image.load("images/Risk_Map.png").convert_alpha()
green_bubble = pygame.image.load("images/green_bubble.png").convert_alpha()
red_bubble = pygame.image.load("images/red_bubble.png").convert_alpha()
yellow_bubble = pygame.image.load("images/yellow_bubble.png").convert_alpha()
rect = pygame.image.load("images/round_rect.png").convert_alpha()
text_rect = pygame.Rect((0, 0, 800, 150))
text1 = None
x = 0
y = 0

click = False
TERRITORIES = constants.TERRITORIES	
FONT = pygame.font.Font(None, 35)

# ray casting algorithm
# http://stackoverflow.com/questions/16625507/python-checking-if-point-is-inside-a-polygon
def point_in_poly(x, y, poly):
    n = len(poly)
    inside = False

    p1x,p1y = poly[0]
    for i in range(n+1):
        p2x,p2y = poly[i % n]
        if y > min(p1y,p2y):
            if y <= max(p1y,p2y):
                if x <= max(p1x,p2x):
                    if p1y != p2y:
                        xints = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                    if p1x == p2x or x <= xints:
                        inside = not inside
        p1x,p1y = p2x,p2y

    return inside

# checks if click down and click up
def if_click():
	global click
	if pygame.mouse.get_pressed()[0] == 1:
		click = True
	if click and pygame.mouse.get_pressed()[0] == 0:
		click = False
		return True
	return False


# prints in prompt
def prompt_print(string):
	text = textrect.render_textrect(string, FONT, text_rect, constants.WHITE)
	DISPLAYSURF.blit(text, (60, 800))


def army_size_print(territory):
	if territory["Player"] == 1:
		DISPLAYSURF.blit(green_bubble, territory["Bubble"])
	elif territory["Player"] == 2:
		DISPLAYSURF.blit(red_bubble, territory["Bubble"])
	else:
		DISPLAYSURF.blit(yellow_bubble, territory["Bubble"])
	text = FONT.render(str(territory["Infantry"]), 1, constants.WHITE)
	if territory["Infantry"] < 10:
		DISPLAYSURF.blit(text, (territory["Bubble"][0] + 13, territory["Bubble"][1] + 7))
	else:
		DISPLAYSURF.blit(text, (territory["Bubble"][0] + 7, territory["Bubble"][1] + 7))



# changes color of territory when mouse on territory
def hover_color(territory, color):
	if type(territory["Coordinates"][0]) is tuple:
		pygame.draw.polygon(DISPLAYSURF, color, territory["Coordinates"])
	else:
		for subterritory in territory["Coordinates"]:
			pygame.draw.polygon(DISPLAYSURF, color, subterritory)


# checks if mouse position is on territory 
def in_territory(x, y):
	for territory in TERRITORIES:
		if type(territory["Coordinates"][0]) is tuple:
			if point_in_poly(x, y, territory["Coordinates"]):
				return territory
		else:
			in_subterritory = False
			for subterritory in territory["Coordinates"]:
				if point_in_poly(x, y, subterritory):
					return territory
					break
	return None


# no selection of territory
def selection_screen():
	for territory in TERRITORIES:
		if territory["Player"] == 1:
			hover_color(territory, constants.GREEN)
		elif territory["Player"] == 2:
			hover_color(territory, constants.RED)
		else:
			hover_color(territory, constants.YELLOW)
	for territory in TERRITORIES:
		army_size_print(territory)

# Main loop
def select():
	global x, y
	# selection_screenn_text = None
	while True:
		events = pygame.event.get()
		for event in events:
			if event.type == QUIT:
				pygame.quit()
				sys.exit()
		DISPLAYSURF.blit(background, (0, 0))
		DISPLAYSURF.blit(r_map, (0, 0))
		DISPLAYSURF.blit(rect, (40, 780))
		selection_screen()
		(x, y) = pygame.mouse.get_pos()

		territory = in_territory(x, y)
		if territory is None:
			prompt_print(text1)
		# mouse on territory
		else:
			hover_color(territory, territory["Color"])
			if territory["Name"] == "Brazil":
					army_size_print(TERRITORIES[10])
			else:
				army_size_print(TERRITORIES[36])
			army_size_print(territory)
			prompt_print("The territory is " + territory["Name"])
			if if_click():
				return territory
		pygame.display.update()
		

def refresh():
	global x, y
	events = pygame.event.get()
	for event in events:
		if event.type == QUIT:	
			pygame.quit()
			sys.exit()
	DISPLAYSURF.blit(background, (0, 0))
	DISPLAYSURF.blit(r_map, (0, 0))
	DISPLAYSURF.blit(rect, (40, 780))
	selection_screen()
	(x, y) = pygame.mouse.get_pos()

	territory = in_territory(x, y)
	if territory is not None:
		hover_color(territory, territory["Color"])
		if territory["Name"] == "Brazil":
				army_size_print(TERRITORIES[10])
		else:
			army_size_print(TERRITORIES[36])
		army_size_print(territory)
	prompt_print(text1)
	pygame.display.update()

def get_key():
	''' Based off www.pygame.org/pcr/inputbox
		Credit to Timothy Downs '''
	while True:
		event = pygame.event.poll()
		if event.type == KEYDOWN:
			return event.key
		else:
			pass

def yes_no(question):
	''' Based off www.pygame.org/pcr/inputbox
		Credit to Timothy Downs '''
	while True:
		DISPLAYSURF.blit(background, (0, 0))
		DISPLAYSURF.blit(r_map, (0, 0))
		DISPLAYSURF.blit(rect, (40, 780))
		selection_screen()
		current_string = ""
		prompt_print(question+" (y or n): "+current_string)
		pygame.display.update()
		while True:
			events = pygame.event.get()
			for event in events:
				if event.type == QUIT:
					pygame.quit()
					sys.exit()
			DISPLAYSURF.blit(background, (0, 0))
			DISPLAYSURF.blit(r_map, (0, 0))
			DISPLAYSURF.blit(rect, (40, 780))
			selection_screen()
			(x, y) = pygame.mouse.get_pos()
			
			inkey = get_key()
			if inkey == K_BACKSPACE:
				current_string = current_string[0:-1]
			elif inkey == K_RETURN:
				break
			elif inkey <= 127:
				current_string+=chr(inkey)
			prompt_print(question+" (y or n): "+current_string)
			pygame.display.update()
		
		prompt_print(" ")
		pygame.display.update()
		current_string.lower()
		if current_string == "" or (current_string[0] != 'y' and current_string[0] != 'n'):
			prompt_print("ERROR: Invalid letter!\nOnly enter y or n")
			pygame.display.update()
			pygame.time.delay(1500)
			continue
		elif current_string[0] == 'y':
			return True
		else: # n
			return False

def number(question):
	''' Based off www.pygame.org/pcr/inputbox
		Credit to Timothy Downs '''
	
	DISPLAYSURF.blit(background, (0, 0))
	DISPLAYSURF.blit(r_map, (0, 0))
	DISPLAYSURF.blit(rect, (40, 780))
	selection_screen()
	current_string = ""
	prompt_print(question+": "+current_string)
	pygame.display.update()
	while True:
		events = pygame.event.get()
		for event in events:
			if event.type == QUIT:
				pygame.quit()
				sys.exit()
		DISPLAYSURF.blit(background, (0, 0))
		DISPLAYSURF.blit(r_map, (0, 0))
		DISPLAYSURF.blit(rect, (40, 780))
		selection_screen()
		(x, y) = pygame.mouse.get_pos()
		
		inkey = get_key()
		if inkey == K_BACKSPACE:
			current_string = current_string[0:-1]
		elif inkey == K_RETURN:
			break
		elif inkey <= 127:
			current_string+=chr(inkey)
		prompt_print(question+": "+current_string)
		pygame.display.update()
	
	prompt_print(" ")
	pygame.display.update()
	try:
		num = int(current_string)
	except:
		return 0
	return num
