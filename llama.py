import pygame
import math
import random

DISPLAY = (32*25, 32*15)
DEPTH = 32
FLAGS = 0

# Types of tiles
TOP_LEFT = 'A'
TOP_MIDDLE = 'B'
TOP_RIGHT = 'C'
MIDDLE_LEFT = 'D'
MIDDLE_MIDDLE = 'E'
MIDDLE_RIGHT = 'F'
BOTTOM_LEFT = 'G'
BOTTOM_MIDDLE = 'H'
BOTTOM_RIGHT = 'I'
THIN_LEFT = 'J'
THIN_MIDDLE = 'K'
THIN_RIGHT = 'L'

# Which screen to display
TITLE = 0
HELP = 1
PLAYING = 2
WIN = 3
LOSE = 4

def isRopeValid(x1, y1, x2, y2, level):
	m = float(y2 - y1)/float(x2 - x1)
	b = y1 - (m * x1)
	
	start_y = min(y1, y2)
	end_y = max(y1, y2)
	for y in range(start_y + 32, end_y, 32):
		x = (y - b)/m
		c = int(x/32)
		r = int(y/32)
		if level[r][c] != " " or (x2 > x1 and r >= 1 and level[r - 1][c] != " ") or (x2 < x1 and level[r + 1][c] != " "):
			return False
	
	start_x = min(x1, x2)
	end_x = max(x1, x2)
	for x in range(start_x + 32, end_x, 32):
		y = (m * x) + b
		c = int(x/32)
		r = int(y/32)
		if level[r][c] != " " or (y2 > y1 and level[r][c + 1] != " ") or (y2 < y1 and c >= 1 and level[r][c - 1] != " "):
			return False
	
	return True

def possibleRopes(platforms, player, level):
	left = right = None
	possible_ropes = []
	for p in platforms:
		if p.rect.top == player.rect.bottom:
			if p.rect.right > player.rect.left and p.rect.right < player.rect.right:
				left = p
			elif p.rect.left > player.rect.left and p.rect.left < player.rect.right:
				right = p
			elif p.rect.left == player.rect.left and p.rect.right == player.rect.right:
				left = p
				right = p
	if left is not None and (left.type == TOP_LEFT or left.type == THIN_LEFT):
		possible_ropes += [Rope(left.rect.x, left.rect.y, p.rect.x+32, p.rect.y) for p in platforms if (p.type == TOP_RIGHT or p.type == THIN_RIGHT) and p.rect.right < left.rect.left and isRopeValid(left.rect.x, left.rect.y, p.rect.x+32, p.rect.y, level)]
	if right is not None and (right.type == TOP_RIGHT or right.type == THIN_RIGHT):
		possible_ropes += [Rope(right.rect.x+32, right.rect.y, p.rect.x, p.rect.y) for p in platforms if (p.type == TOP_LEFT or p.type == THIN_LEFT) and p.rect.left > right.rect.right and isRopeValid(right.rect.x+32, right.rect.y, p.rect.x, p.rect.y, level)]
	return possible_ropes

def buildLevel(level):
	global entities, platforms, flagRect, possible_ropes, existing_ropes, placingRope, currentRope, player, left, right
	left = right = False
	player = Player(32, 32)
	
	possible_ropes = []
	existing_ropes = []
	placingRope = False
	currentRope = 0
	entities = pygame.sprite.Group()
	platforms = []
	x = y = 0
	for row in level:
		for col in row:
			if col == "#":
				flagRect = pygame.Rect(x, y, 32, 32)
			elif col != " ":
				p = Platform(x, y, False, col)
				if col == TOP_LEFT or col == TOP_MIDDLE or col == TOP_RIGHT or col == THIN_LEFT or col == THIN_MIDDLE or col == THIN_RIGHT:
					p.hasYarn = random.randint(0,10) > 8
				platforms.append(p)
				entities.add(p)
			x += 32
		y += 32
		x = 0
	
	entities.add(player)

def main():
	global entities, platforms, flagRect, possible_ropes, existing_ropes, placingRope, currentRope, player, levels, currentLevel, screenMode, left, right
	global yarnSound, ropeWalkSound, winSound, loseSound
	pygame.init()
	screen = pygame.display.set_mode(DISPLAY, FLAGS, DEPTH)
	pygame.display.set_caption("Tangle")
	timer = pygame.time.Clock()
	
	screenMode = TITLE
	prevScreen = TITLE
	titleScreen = pygame.image.load("Images\\title.gif")
	titleRect = titleScreen.get_rect()
	winScreen = pygame.image.load("Images\\win_screen.gif")
	winRect = winScreen.get_rect()
	loseScreen = pygame.image.load("Images\\lose_screen.gif")
	loseRect = loseScreen.get_rect()
	helpScreen = pygame.image.load("Images\\instructions.gif")
	helpRect = helpScreen.get_rect()
	
	cancelSound = pygame.mixer.Sound("Sounds\Cancel8-Bit.ogg")
	confirmSound = pygame.mixer.Sound("Sounds\Confirm8-Bit.ogg")
	selectSound = pygame.mixer.Sound("Sounds\Select8-Bit.ogg")
	yarnSound = pygame.mixer.Sound("Sounds\Powerup.ogg")
	ropeWalkSound = pygame.mixer.Sound("Sounds\DownStairs8-Bit.ogg")
	winSound = pygame.mixer.Sound("Sounds\Menu8-Bit.ogg")
	loseSound = pygame.mixer.Sound("Sounds\Fart.ogg")
	
	bg = pygame.image.load("Images\\bg2.gif")
	bgRect = bg.get_rect()
	yarnSprite = pygame.image.load("Images\\yarn2.gif")
	bigYarnSprite = pygame.transform.scale2x(yarnSprite)
	flagSprite = pygame.image.load("Images\\flag2t.gif")
	
	currentLevel = 0
	
	levels = [
		[
		"                         ",
		"                         ",
		"       ABBBBC      JKKKKK",
		"       GHHHHI            ",
		"                         ",
		"               AC        ",
		"           AC  GI       A",
		"BBBC       DF           D",
		"HHHI       GI  ABC      G",
		"               GHI       ",
		"                         ",
		"      AC                 ",
		"BBBBC DF  JKKKKL       # ",
		"EEEEF GI            ABBBB",
		"EEEEF               DEEEE",],
		[
		"                         ",
		"                  JKKKL  ",
		"BBBBC                    ",
		"EEEEF       ABC          ",
		"            DEF  JKL     ",
		"       ABC  GHI          ",
		"  AC   DEF               ",
		"  GI   DEF       AC      ",
		"       GHI  ABC  DF      ",
		"            GHI  DF   AC ",
		"                 GI   GI ",
		"       ABC               ",
		" JKL   GHI           #   ",
		"                    ABBBB",
		"                    DEEEE",],
		[
		"                         ",
		"                JKKKKKL  ",
		" ABC                     ",
		" GHI   ABC               ",
		"       GHI          JL   ",
		"             ABBC        ",
		"             GHHI        ",
		"                         ",
		"       ABC               ",
		"       DEF        JL     ",
		" ABC   DEF               ",
		" DEF   DEF               ",
		" DEF   GHI      AC     # ",
		" GHI            GI  ABBBB",
		"                    DEEEE",],
		[
		"                         ",
		"         ABC             ",
		"         GHI        ABBBB",
		"    AC              GHHHH",
		"    DF          AC       ",
		" AC DF          GI       ",
		" GI DF              ABC  ",
		"    DF  JL   #      GHI  ",
		"    GI      JL           ",
		"                         ",
		"        JL               ",
		"                ABBBBC   ",
		"                GHHHHI   ",
		"BBBBC                    ",
		"EEEEF                    ",],
	]
	# build the level
	buildLevel(levels[0])
	
	while 1:
		timer.tick(60)
		for e in pygame.event.get():
			if e.type == pygame.QUIT: raise SystemExit, "Good-bye!"
			if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE: 
				raise SystemExit, "Good-bye!"
			
			if e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE:
				if screenMode == TITLE:
					screenMode = HELP
					prevScreen = TITLE
				elif screenMode == HELP:
					if prevScreen == TITLE:
						buildLevel(levels[0])
					screenMode = PLAYING
					prevScreen = HELP
				elif screenMode == WIN:
					screenMode = TITLE
					prevScreen = WIN
				elif screenMode == LOSE:
					screenMode = TITLE
					prevScreen = LOSE
			if e.type == pygame.KEYDOWN and e.key == pygame.K_h:
				prevScreen = screenMode
				screenMode = HELP
			if screenMode != PLAYING:
				break
			
			# Movement
			if e.type == pygame.KEYDOWN and e.key == pygame.K_LEFT:
				left = True
			if e.type == pygame.KEYDOWN and e.key == pygame.K_RIGHT:
				right = True
			
			# Rope placing
			if e.type == pygame.KEYDOWN and e.key == pygame.K_z and player.yarn > 0:
				if not placingRope:
					possible_ropes = possibleRopes(platforms, player, levels[currentLevel])
					if len(possible_ropes) > 0:
						placingRope = True
						selectSound.play()
				else:
					placingRope = False
					existing_ropes.append(possible_ropes[currentRope])
					currentRope = 0
					player.yarn -= 1
					confirmSound.play()
			if e.type == pygame.KEYDOWN and placingRope and e.key == pygame.K_c:
				placingRope = False
				currentRope = 0
				cancelSound.play()
			if e.type == pygame.KEYDOWN and placingRope and e.key == pygame.K_UP:
				currentRope = (currentRope + 1) % len(possible_ropes)
				selectSound.play()
			if e.type == pygame.KEYDOWN and placingRope and e.key == pygame.K_DOWN:
				currentRope = (currentRope - 1) % len(possible_ropes)
				selectSound.play()
			
			if e.type == pygame.KEYUP and e.key == pygame.K_LEFT:
				left = False
			if e.type == pygame.KEYUP and e.key == pygame.K_RIGHT:
				right = False
		
		if screenMode == TITLE:
			screen.blit(titleScreen, titleRect)
			pygame.display.flip()
			continue
		if screenMode == HELP:
			screen.blit(helpScreen, helpRect)
			pygame.display.flip()
			continue
		if screenMode == WIN:
			screen.blit(winScreen, winRect)
			pygame.display.flip()
			continue
		if screenMode == LOSE:
			screen.blit(loseScreen, loseRect)
			pygame.display.flip()
			continue
		
		# draw background
		screen.blit(bg, bgRect)
		
		# update player, draw everything else
		if not placingRope:
			player.update(left, right, platforms, existing_ropes, flagRect)
		entities.draw(screen)
		
		for p in platforms:
			if p.hasYarn:
				screen.blit(yarnSprite, p.rect)
		
		screen.blit(flagSprite, flagRect)
		
		if placingRope:
			pygame.draw.line(screen, (255,91,34), (possible_ropes[currentRope].x1, possible_ropes[currentRope].y1), (possible_ropes[currentRope].x2, possible_ropes[currentRope].y2), 2)
		
		for rope in existing_ropes:
			pygame.draw.line(screen, (255,161,104), (rope.x1, rope.y1), (rope.x2, rope.y2), 2)
		
		screen.blit(bigYarnSprite, pygame.Rect(736, 0, 64, 64))
		font = pygame.font.SysFont("Helvetica", 50)
		label = font.render(str(player.yarn)+"x ", 1, (255,91,34))
		screen.blit(label, (736 - font.size(str(player.yarn)+"x ")[0], 0))
		
		pygame.display.flip()

class Entity(pygame.sprite.Sprite):
	def __init__(self):
		pygame.sprite.Sprite.__init__(self)

class Player(Entity):
	def __init__(self, x, y):
		Entity.__init__(self)
		self.xvel = 0
		self.yvel = 0
		self.onGround = False
		self.onRope = False
		self.whichRope = None
		self.image = pygame.image.load("Images\\llama2.gif")
		self.rect = pygame.Rect(x, y, 32, 32)
		self.yarn = 2
		self.facing = 0 # 0 for facing right, 1 for facing left
	
	def update(self, left, right, platforms, ropes, flagRect):
		global levels, currentLevel, screenMode, yarnSound, ropeWalkSound, winSound, loseSound
		# Did we win?
		if self.rect.colliderect(flagRect):
			currentLevel = (currentLevel + 1) % len(levels)
			buildLevel(levels[currentLevel])
			if currentLevel == 0:
				screenMode = WIN
				prevScreen = PLAYING
			winSound.play()
			return
		# Did we lose?
		if self.rect.bottom > 480:
			screenMode = LOSE
			prevScreen = PLAYING
			currentLevel = 0
			loseSound.play()
			return
		if left:
			if not self.onRope:
				self.xvel = -3
			else:
				self.xvel = -3 * math.fabs(math.cos(self.whichRope.slope))
				self.yvel = -3 * math.fabs(math.sin(self.whichRope.slope))
				if ropeWalkSound.get_num_channels() == 0:
					ropeWalkSound.play()
			if self.facing == 0:
				self.facing = 1
				self.image = pygame.transform.flip(self.image, True, False)
		elif right:
			if not self.onRope:
				self.xvel = 3
			else:
				self.xvel = 3 * math.fabs(math.cos(self.whichRope.slope))
				self.yvel = 3 * math.fabs(math.sin(self.whichRope.slope))
				if ropeWalkSound.get_num_channels() == 0:
					ropeWalkSound.play()
			if self.facing == 1:
				self.facing = 0
				self.image = pygame.transform.flip(self.image, True, False)
		else:
			self.xvel = 0
		if not self.onGround and not self.onRope:
			# only accelerate with gravity if in the air
			self.yvel += 0.6
		if self.onRope:
			if not self.whichRope.collidesWith(self.rect):
				self.onRope = False
				self.whichRope = None
				self.onGround = False
		# increment in x direction
		self.rect.left += self.xvel
		# do x-axis collisions
		self.collide(self.xvel, 0, platforms, [])
		# increment in y direction
		self.rect.top += self.yvel
		# assuming we're in the air
		self.onGround = False
		# do y-axis collisions
		self.collide(0, self.yvel, platforms, ropes)
	
	def collide(self, xvel, yvel, platforms, ropes):
		for p in platforms:
			if pygame.sprite.collide_rect(self, p) and not self.onRope:
				if xvel > 0: self.rect.right = p.rect.left
				if xvel < 0: self.rect.left = p.rect.right
				if yvel > 0:
					self.rect.bottom = p.rect.top
					self.onGround = True
					self.onRope = False
					self.yvel = 0
					if p.hasYarn:
						self.yarn += 1
						p.hasYarn = False
						yarnSound.play()
				if yvel < 0: self.rect.top = p.rect.bottom
		for r in ropes:
			if r.collidesWith(self.rect):
				self.onRope = True
				self.whichRope = r
				if r.slope <= 0:
					if r.x2 >= r.x1:
						self.rect.bottom = (r.m * self.rect.right) + r.b
					else:
						self.rect.bottom = (r.m * self.rect.left) + r.b
				else:
					if r.x2 >= r.x1:
						self.rect.bottom = (r.m * self.rect.left) + r.b
					else:
						self.rect.bottom = (r.m * self.rect.right) + r.b
				return

class Platform(Entity):
	def __init__(self, x, y, hasYarn, type):
		Entity.__init__(self)
		if type == 'A':
			self.imageFilename = "Images\\tl.gif"
		elif type == 'B':
			self.imageFilename = "Images\\tm.gif"
		elif type == 'C':
			self.imageFilename = "Images\\tr.gif"
		elif type == 'D':
			self.imageFilename = "Images\\ml.gif"
		elif type == 'E':
			self.imageFilename = "Images\\mm.gif"
		elif type == 'F':
			self.imageFilename = "Images\\mr.gif"
		elif type == 'G':
			self.imageFilename = "Images\\bl.gif"
		elif type == 'H':
			self.imageFilename = "Images\\bm.gif"
		elif type == 'I':
			self.imageFilename = "Images\\br.gif"
		elif type == 'J':
			self.imageFilename = "Images\\l.gif"
		elif type == 'K':
			self.imageFilename = "Images\\m.gif"
		elif type == 'L':
			self.imageFilename = "Images\\r.gif"
		self.image = pygame.image.load(self.imageFilename)
		self.rect = pygame.Rect(x, y, 32, 32)
		self.hasYarn = hasYarn
		self.type = type
	
	def update(self):
		pass

class Rope(Entity):
	def __init__(self, x1, y1, x2, y2):
		Entity.__init__(self)
		self.x1 = x1
		self.y1 = y1
		self.x2 = x2
		self.y2 = y2
		self.rect = pygame.Rect(min(x1, x2), min(y1, y2), abs(x1 - x2), abs(y1 - y2))
		self.slope = math.atan2(float(y2 - y1),float(x2 - x1))
		self.m = float(y2 - y1)/float(x2 - x1)
		self.b = y1 - (self.m * x1)
	def collidesWith(self, rect):
		if self.rect.colliderect(rect):
			start_x = min(self.x1, self.x2)
			end_x = max(self.x1, self.x2)
			for x in range(start_x, end_x, 1):
				y = self.m * x + self.b
				if rect.collidepoint(x, y):
					return True
		return False
	def update(self):
		pass

if(__name__ == "__main__"):
	main()