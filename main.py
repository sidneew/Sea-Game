import pygame, sys, random

def pixel_collision(mask1, rect1, mask2, rect2):
    offset_x = rect2[0] - rect1[0]
    offset_y = rect2[1] - rect1[1]
    overlap = mask1.overlap(mask2, (offset_x, offset_y))
    return overlap

class Sprite:
    def __init__(self, image):
        self.image = image
        self.rectangle = image.get_rect()
        self.mask = pygame.mask.from_surface(image)

    def set_position(self, new_position):
        self.rectangle.center = new_position

    def draw(self, screen):
        screen.blit(self.image, self.rectangle)

    def is_colliding(self, other_sprite):
        return pixel_collision(self.mask, self.rectangle, other_sprite.mask, other_sprite.rectangle)

class Enemy:
    def __init__(self, image, width, height):
        self.image = image
        self.mask = pygame.mask.from_surface(image)
        self.rectangle = image.get_rect()

        x_position = random.randint(0,width)
        y_position = random.randint(0,height)
        self.rectangle.center = (x_position,y_position)
        vx = random.uniform(3, 3)
        vy = random.uniform(3, 3)
        self.speed = (vx, vy)

    def move(self):
        self.rectangle.move_ip(self.speed)

    def bounce(self, width, height):
        if self.rectangle.left < 0:
            self.speed = (-self.speed[0], self.speed[1])
        if self.rectangle.right > width:
            self.speed = (-self.speed[0], self.speed[1])
        if self.rectangle.top < 0:
            self.speed = (self.speed[0], -self.speed[1])
        if self.rectangle.bottom > height:
            self.speed = (self.speed[0], -self.speed[1])

    def draw(self, screen):
        screen.blit(self.image, self.rectangle)

class PowerUp:
    def __init__(self, image, width, height):
        self.image = image
        self.mask = pygame.mask.from_surface(image)
        self.rectangle = image.get_rect()
        x_pos = random.randint(0,width)
        y_pos = random.randint(0,height)
        self.rectangle.center = (x_pos,y_pos)

    def draw(self, screen):
        # Same as Sprite
        screen.blit(self.image, self.rectangle)

class DropEnemy(Enemy):
    def __init__(self, image,width,height):
        super().__init__(image,width,height)
        self.position = self.rectangle.center

    def move(self):
        x_movement , y_movement = self.speed
        y_movement = y_movement + .1
        self.speed= x_movement, y_movement
        (x,y) = self.position
        x = x + x_movement
        y = y +y_movement
        self.position = (x,y)
        self.rectangle.center = self.position

class PowerUpRotate(PowerUp):
    def __init__(self,image,width,height):
        super().__init__(image,width,height)
        self.angle = 0
        self.original_image = image
    def draw(self, screen):
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        my_center = self.rectangle.center
        self.rectangle = self.image.get_rect()
        self.rectangle.center = my_center
        self.mask = pygame.mask.from_surface(self.image)
        self.angle = self.angle + 5
        super(PowerUpRotate, self).draw(screen)


def main():
    pygame.init()
    # font for printing the lives left on the screen.
    myfont = pygame.font.SysFont('monospace', 24)
    # Define the screen
    width, height = 600, 500
    size = width, height
    screen = pygame.display.set_mode((width, height))

    enemy_image = pygame.image.load("my_shark.png").convert_alpha()
    enemy_image = pygame.transform.smoothscale(enemy_image, (100, 100))

    drop_image = pygame.image.load("the_crab.png").convert_alpha()
    drop_image = pygame.transform.smoothscale(drop_image, (50, 50))
    enemy_sprites = []
    drop_sprites = []
    #making half drop and half original
    for count in range(5):
        my_enemies = Enemy(enemy_image, width, height)
        enemy_sprites.append(my_enemies)
    for count in range(5):
        my_drops = DropEnemy(drop_image, width, height)
        drop_sprites.append(my_drops)
    #storing my drop enemies in the same list
    my_enemies = enemy_sprites + drop_sprites

    player_image = pygame.image.load("turtle.png").convert_alpha()
    player_image = pygame.transform.smoothscale(player_image, (75,70)) #kept the variable name the same on purpose
    player_sprite = Sprite(player_image)
    life = 3

    powerup_image = pygame.image.load("Starfish_1.png").convert_alpha()
    powerup_image = pygame.transform.smoothscale(powerup_image,(50,50))
    #my rotating image
    rotate_image = pygame.image.load("real_octo.png").convert_alpha()
    rotate_image = pygame.transform.smoothscale(rotate_image, (70,70))
    norm_power = []
    rotate_power = []
    #combing them in the same list
    powerups = norm_power + rotate_power

    #Doing a background image
    background_image = pygame.image.load("ocean_back.jpg") #I changed my background image from OG to make colors easier to see
    background_image = pygame.transform.scale(background_image, (width, height))

    # Main part of the game
    is_playing = True
    while is_playing:
        if life <= 0:
            is_playing = False
        # Check for events
        for event in pygame.event.get():
            # Stop loop if click on window close button
            if event.type == pygame.QUIT:
                is_playing = False

        # Make the player follow the mouse
        pos = pygame.mouse.get_pos()
        player_sprite.set_position(pos)

        #This is saying both types of enemies will deduct life points
        for enemy in my_enemies:
            if player_sprite.is_colliding(enemy):
                life = life - 0.25


        #This is saying that both types of my powerups will at 1 life to my life score
        for powerup in powerups:
            if player_sprite.is_colliding(powerup):
                life = life + 1

        powerups = [item for item in powerups if not player_sprite.is_colliding(item)] #This is a change from OG code

        #Letting the enemies move and bounce
        for enemy in my_enemies:
            enemy.move()
            enemy.bounce(width, height)

        # randomly choosing when to add both types of powerups and appending to the same list.
        if random.random() < .01:
            powerups.append(PowerUp(powerup_image,width,height))
        if random.random() < .01:
            powerups.append(PowerUpRotate(rotate_image,width,height))

    #adding the background image
        screen.blit(background_image, (0, 0))

    # Draw the characters
        for enemy in my_enemies:
            enemy.draw(screen)
        for powerup in powerups:
            powerup.draw(screen)
        player_sprite.draw(screen)

        #Life value
        text = "Life: " + str('%.1f'%life)
        label = myfont.render(text, True, (0, 0, 0))
        screen.blit(label, (20, 20))

#This is the clock
        t = pygame.time.get_ticks() /1000
        clock_text = "Time Survived: " + str(t)
        time_label = myfont.render(clock_text, True, (0,0,0))
        screen.blit(time_label, (270,20))

        # Bring all the changes to the screen into view
        pygame.display.update()
        # Pause for a few milliseconds
        pygame.time.wait(20)

    pygame.time.wait(2000)
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()