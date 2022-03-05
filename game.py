"""
Platformer Game
"""

#Imports arcade module
import arcade 
#Dimensions of the window
SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 900

SCREEN_TITLE = "Platformer Game" 

CHARACTER_SCALING = 0.7
TILE_SCALING = 1 
COIN_SCALING = 0.5 

#Viewport margins before the screen starts scrolling
LEFT_VIEWPORT_MARGIN = 500 
RIGHT_VIEWPORT_MARGIN = 800
BOTTOM_VIEWPORT_MARGIN = 250
TOP_VIEWPORT_MARGIN = 250

PLAYER_MOVEMENT_SPEED = 7
GRAVITY = 1
PLAYER_JUMP_SPEED = 20 

#Starting position of the character sprite
PLAYER_START_X = 200
PLAYER_START_Y = 500

RIGHT_FACING = 0
LEFT_FACING = 1

SPRITE_PIXEL_SIZE = 32
GRID_PIXEL_SIZE = (SPRITE_PIXEL_SIZE * TILE_SCALING)

TOTAL_LEVELS = 3


def load_texture_pair(filename):
    """Function what loads two verions of the texture for left/right movement"""
    return [
            arcade.load_texture(filename),
            arcade.load_texture(filename, flipped_horizontally=True)
        ]

class PlayerCharacter(arcade.Sprite):
    """ Player Sprite"""
    def __init__(self):

        # Set up parent class
        super().__init__()

        # Sets default direction to right
        self.character_face_direction = RIGHT_FACING

        # The counter for the current active texture of an animation
        self.cur_walk_texture = 0
        self.cur_idle_texture = 0
        self.cur_death_texture = 0

        self.scale = CHARACTER_SCALING

        # Track the state
        self.jumping = False
        self.climbing = False
        self.is_on_ladder = False
        self.dead = False
        self.respawned = False
        self.frames = 0

        # Loads the sprite textures
        main_path = "assets/mob/lion/"


        # Load textures for jumping, falling and the intial standing.
        self.jump_texture_pair = load_texture_pair("{}jump.png".format(main_path))
        self.fall_texture_pair = load_texture_pair("{}fall.png".format(main_path))
        self.inital_texture_pair = load_texture_pair("{}idle0.png".format(main_path))
        
        #Loads the idle animation textures into a list
        self.idle_textures = []
        for i in range(5):
            texture = load_texture_pair("{}idle{}.png".format(main_path,i))
            self.idle_textures.append(texture)

        #Loads the walking animation textures into a list
        self.walk_textures = []
        for i in range(6):
            texture = load_texture_pair("{}run{}.png".format(main_path,i))
            self.walk_textures.append(texture)

        #Loads the death animation textures into a list
        self.death_textures = []
        for i in range(7):
            texture = load_texture_pair("{}death{}.png".format(main_path,i))
            self.death_textures.append(texture)

        # Loads the climbing textures
        self.climbing_textures = []
        texture = arcade.load_texture("{}climb0.png".format(main_path))
        self.climbing_textures.append(texture)
        texture = arcade.load_texture("{}climb1.png".format(main_path))
        self.climbing_textures.append(texture)

        # Set the initial texture
        self.texture = self.inital_texture_pair[0]

    def update_animation(self, delta_time):
        '''Method that sets the texture everytime the game updates'''

        #Updates the current frame
        self.frames += 1

        # Flips the texture depending on the direction of motion
        if self.change_x < 0 and self.character_face_direction == RIGHT_FACING and not self.dead:
            self.character_face_direction = LEFT_FACING
        elif self.change_x > 0 and self.character_face_direction == LEFT_FACING and not self.dead:
            self.character_face_direction = RIGHT_FACING

        # Death Animation
        if self.dead:
            if self.frames % 7 == 0:
                self.cur_death_texture += 1
                if self.cur_death_texture > 6:
                    self.cur_death_texture = 0
                    self.respawned = True
                else:
                    self.texture = self.death_textures[self.cur_death_texture][self.character_face_direction]
            return

        # Climbing animation
        if self.is_on_ladder:
            self.climbing = True
        if not self.is_on_ladder and self.climbing:
            self.climbing = False
        if self.climbing and abs(self.change_y) > 1:
            if self.frames & 1: self.cur_walk_texture += 1 
            if self.cur_walk_texture > 7:
                self.cur_walk_texture = 0
        if self.climbing:
            self.texture = self.climbing_textures[self.cur_walk_texture // 4]
            return

        # Jumping animation, dependant on whether the sprite is on a ladder or not
        if self.change_y > 0 and not self.is_on_ladder:
            self.texture = self.jump_texture_pair[self.character_face_direction]
            return
        elif self.change_y < 0 and not self.is_on_ladder:
            self.texture = self.fall_texture_pair[self.character_face_direction]    
            return

        

        # Idle animation
        if self.change_x == 0:
            if self.frames % 7 == 0:
                self.cur_idle_texture += 1
                if self.cur_idle_texture > 4:
                    self.cur_idle_texture = 0
                self.texture = self.idle_textures[self.cur_idle_texture][self.character_face_direction]
            return

        # Walking animation
        if self.frames % 3 == 0: self.cur_walk_texture += 1
        if self.cur_walk_texture > 5:
            self.cur_walk_texture = 0
        self.texture = self.walk_textures[self.cur_walk_texture][self.character_face_direction]

class EnemyCharacter(arcade.Sprite):
    """ Player Sprite"""
    def __init__(self, mob_type):

        # Set up parent class
        super().__init__()

        # Sets default direction to right
        self.character_face_direction = RIGHT_FACING

        # The counter for the current active texture of an animation
        self.cur_walk_texture = 0
        self.cur_idle_texture = 0

        self.scale = 1

        self.frames = 0

        # Loads the sprite textures depending on which mob type it is
        main_path = "assets/mob/monsters/{}/".format(mob_type)


        #Loads the initial standing texture
        self.inital_texture_pair = load_texture_pair("{}idle0.png".format(main_path))

        #Loads the idle animation textures into a list
        self.idle_textures = []
        for i in range(4):
            texture = load_texture_pair("{}idle{}.png".format(main_path,i))
            self.idle_textures.append(texture)

        #Loads the walking animation textures into a list
        self.walk_textures = []
        for i in range(6):
            texture = load_texture_pair("{}run{}.png".format(main_path,i))
            self.walk_textures.append(texture)

        # Set the initial texture
        self.texture = self.inital_texture_pair[0]
    def update_animation(self, delta_time): 
        '''Method that sets the texture everytime the game updates'''

        #Updates the current frame
        self.frames += 1

        # Flips the texture depending on the direction of motion
        if self.change_x < 0 and self.character_face_direction == LEFT_FACING:
            self.character_face_direction = RIGHT_FACING
        elif self.change_x > 0 and self.character_face_direction == RIGHT_FACING:
            self.character_face_direction = LEFT_FACING

        # Idle animation
        if self.change_x == 0:
            if self.frames % 7 == 0:
                self.cur_idle_texture += 1
                if self.cur_idle_texture > 3:
                    self.cur_idle_texture = 0
                self.texture = self.idle_textures[self.cur_idle_texture][self.character_face_direction]
            return

        # Walking animation
        if self.frames % 5 == 0: self.cur_walk_texture += 1
        if self.cur_walk_texture > 5:
            self.cur_walk_texture = 0
        self.texture = self.walk_textures[self.cur_walk_texture][self.character_face_direction]

  
class GameOverView(arcade.View):
    """ View that shows when game is over """

    def __init__(self):
        """ This is run once when we switch to this view """
        super().__init__()
         #Loads the image that is displayed
        self.texture = arcade.load_texture("assets/game_over.png")

               

    def on_draw(self):
        """ Draws on the screen"""
        arcade.start_render()
        #Draws the image on the screen
        self.texture.draw_sized(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2,
                                SCREEN_WIDTH, SCREEN_HEIGHT)
     

    def on_mouse_press(self, _x, _y, _button, _modifiers):
        """Starts the game on click """
        game_view = MyGame()
        game_view.setup(game_view.level)
        #Reloads the game on the mouse click
        self.window.show_view(game_view)


class InstructionView(arcade.View):
    """ View to show instructions """

    def __init__(self):
        """ This is run once when we switch to this view """
        super().__init__()
         #Loads the image that is displayed
        self.texture = arcade.load_texture("assets/startscreen.png")

               

    def on_draw(self):
        """ Draws on the screen"""
        arcade.start_render()
        #Draws the image on the screen
        self.texture.draw_sized(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2,
                                SCREEN_WIDTH, SCREEN_HEIGHT)
    def on_mouse_press(self, _x, _y, _button, _modifiers):
        """ If the user presses the mouse button, start the game. """
        game_view = MyGame()
        game_view.setup(game_view.level)
        #Reloads the game on the mouse click
        self.window.show_view(game_view)


class MyGame(arcade.View):
    '''The main game'''
    def __init__(self):

        super().__init__()

        #Initialises all the variables
        self.coin_list=None 
        self.wall_list=None 
        self.ladder_list = None
        self.player_list=None 
        self.player_sprite=None
        self.enemy_sprite=None
        self.enemy_sprite=None  
        self.physics_engine=None
        self.view_bottom=0 
        self.view_left=0 
        self.score=0 
        self.foreground_list = None
        self.background_list = None
        self.dont_touch_list = None
        self.end_of_map = None
        self.up_pressed = False
        self.down_pressed = False
        self.left_pressed = False
        self.right_pressed = False
        self.jump_needs_reset = False
        self.level = 1
        self.background = None

    def setup(self, level):
        """ Set up the game here. This is run for each level """

        #Sets up the main lists
        self.player_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList()
        self.coin_list = arcade.SpriteList()
        self.dont_touch_list = arcade.SpriteList()
        self.ladder_list = arcade.SpriteList()
        self.foreground_list = arcade.SpriteList()
        self.background_list = arcade.SpriteList()
        self.foreground_list = arcade.SpriteList()
        
        #Initialises the sprite and position of the character
        self.player_sprite = PlayerCharacter()
        self.player_list.append(self.player_sprite)
        self.player_sprite.center_x = PLAYER_START_X
        self.player_sprite.center_y = PLAYER_START_Y

        self.view_bottom=0 
        self.view_left=0 
        self.score=0
        self.background = arcade.load_texture("assets/background.png")
        self.dont_touch_list = arcade.SpriteList()

        #Sets the layers from the tmx map file
        platforms_layer_name = 'Platforms'
        moving_platforms_layer_name = 'Moving Platforms'
        coins_layer_name = 'Coins'
        foreground_layer_name = 'Foreground'
        background_layer_name = 'Background'
        foreground_layer_name = 'Foreground'
        dont_touch_layer_name = "Don't Touch"       
        moving_enemies_layer_name = 'Moving Enemies'
        ladders_layer_name = "Ladders"

        #Sets the map name based on the current level
        map_name = ("maps/map1_level_{}.tmx".format(level))

        # Read in the tiled map
        my_map = arcade.tilemap.read_tmx(map_name)

        # Calculates the top and right edge of the map
        self.end_of_map = my_map.map_size.width * GRID_PIXEL_SIZE
        self.top_of_map = my_map.map_size.height * GRID_PIXEL_SIZE

        #Adds the map elements into lists

        #Background
        self.background_list = arcade.tilemap.process_layer(my_map,
                                                            background_layer_name,
                                                            TILE_SCALING)
        self.foreground_list = arcade.tilemap.process_layer(my_map,
                                                            foreground_layer_name,
                                                            TILE_SCALING)

        #Foreground
        self.foreground_list = arcade.tilemap.process_layer(my_map,
                                                            foreground_layer_name,
                                                            TILE_SCALING)

        #Platforms
        self.wall_list = arcade.tilemap.process_layer(map_object=my_map,
                                                      layer_name=platforms_layer_name,
                                                      scaling=TILE_SCALING,
                                                      use_spatial_hash=True)
        
        #Moving Platforms
        moving_platforms_list = arcade.tilemap.process_layer(my_map, moving_platforms_layer_name, TILE_SCALING)
        for sprite in moving_platforms_list:
            self.wall_list.append(sprite)                                            

        #Coins
        self.coin_list = arcade.tilemap.process_layer(my_map,
                                                      coins_layer_name,
                                                      TILE_SCALING,
                                                      use_spatial_hash=True)
        #Ladder
        self.ladder_list = arcade.tilemap.process_layer(my_map,
                                                      ladders_layer_name,
                                                      TILE_SCALING,
                                                      use_spatial_hash=True)
        #Don't Touch
        self.dont_touch_list = arcade.tilemap.process_layer(my_map,
                                                            dont_touch_layer_name,
                                                            TILE_SCALING,
                                                            use_spatial_hash=True)
        #Moving Enemies                                                    
        moving_enemies_list = arcade.tilemap.process_layer(my_map, moving_enemies_layer_name, TILE_SCALING)
        for mob in moving_enemies_list:
            self.enemy_sprite = EnemyCharacter(mob.properties['mob_type'])
            self.dont_touch_list.append(self.enemy_sprite)
            #Sets the properties of the enemy to the properties specified in the map file
            self.enemy_sprite.center_x = mob.center_x   
            self.enemy_sprite.center_y = mob.center_y
            self.enemy_sprite.boundary_left = mob.boundary_left
            self.enemy_sprite.boundary_right = mob.boundary_right
            self.enemy_sprite.change_x = mob.change_x

        
        #Initialises the physics engine
        self.physics_engine = arcade.PhysicsEnginePlatformer(self.player_sprite,
                                                            self.wall_list,GRAVITY,
                                                            ladders=self.ladder_list) 


 
    def on_draw(self):
        """ Render the screen. """
        
        arcade.start_render()

        #Draws the background image
        arcade.draw_lrwh_rectangle_textured(0+self.view_left, 0+self.view_bottom,
                                            SCREEN_WIDTH, SCREEN_HEIGHT,
                                            self.background) 
        #Draws all the lists   
        self.background_list.draw()
        self.wall_list.draw()
        self.coin_list.draw()
        self.foreground_list.draw()
        self.ladder_list.draw()
        self.dont_touch_list.draw()
        self.player_list.draw()
        #Draws the score
        score_text=("Score: {}".format(self.score)) 
        arcade.draw_text(score_text, 10 + self.view_left, 10 + self.view_bottom, arcade.csscolor.BLACK, 30) 


    def process_keychange(self):

        # Process up/down 
        if self.up_pressed and not self.down_pressed and not self.player_sprite.dead:
            if self.physics_engine.is_on_ladder():
                self.player_sprite.change_y = PLAYER_MOVEMENT_SPEED
            elif self.physics_engine.can_jump() and not self.jump_needs_reset:
                self.player_sprite.change_y = PLAYER_JUMP_SPEED
                self.jump_needs_reset = True
                
        elif self.down_pressed and not self.up_pressed:
            if self.physics_engine.is_on_ladder():
                self.player_sprite.change_y = -PLAYER_MOVEMENT_SPEED

        # Process up/down when on a ladder and no movement
        if self.physics_engine.is_on_ladder():
            if not self.up_pressed and not self.down_pressed:
                self.player_sprite.change_y = 0
            elif self.up_pressed and self.down_pressed:
                self.player_sprite.change_y = 0

        # Process left/right
        if self.right_pressed and not self.left_pressed:
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED
        elif self.left_pressed and not self.right_pressed and self.player_sprite.left>0:
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
        else:
            self.player_sprite.change_x = 0

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed. """

        if key == arcade.key.UP or key == arcade.key.W:
            self.up_pressed = True
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.down_pressed = True
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = True
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = True
        self.process_keychange()

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key. """

        if key == arcade.key.UP or key == arcade.key.W:
            self.up_pressed = False
            self.jump_needs_reset = False
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.down_pressed = False
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = False
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = False
        self.process_keychange()


    def on_update(self, delta_time):
        self.physics_engine.update()
        # Update animations
        if self.physics_engine.can_jump():
            self.player_sprite.can_jump = False
        else:
            self.player_sprite.can_jump = True

        if self.physics_engine.is_on_ladder() and not self.physics_engine.can_jump():
            self.player_sprite.is_on_ladder = True
            self.process_keychange()
        else:
            self.player_sprite.is_on_ladder = False
            self.process_keychange()

        self.wall_list.update()
    
        # Sees if the wall hit a boundary and needs to reverse direction.
        for wall in self.wall_list:

            if wall.boundary_right and wall.right > wall.boundary_right and wall.change_x > 0:
                wall.change_x *= -1
            if wall.boundary_left and wall.left < wall.boundary_left and wall.change_x < 0:
                wall.change_x *= -1
            if wall.boundary_top and wall.top > wall.boundary_top and wall.change_y > 0:
                wall.change_y *= -1
            if wall.boundary_bottom and wall.bottom < wall.boundary_bottom and wall.change_y < 0:
                wall.change_y *= -1
        
        self.dont_touch_list.update_animation(delta_time)
        self.dont_touch_list.update()

        #Sees if the enemy his a boundary and needs to reverse direction
        for enemy in self.dont_touch_list:

            if enemy.boundary_right and enemy.right > enemy.boundary_right and enemy.change_x > 0:
                enemy.change_x *= -1
            if enemy.boundary_left and enemy.left < enemy.boundary_left and enemy.change_x < 0:
                enemy.change_x *= -1
    
        #calls the update_animation method
        self.player_list.update_animation(delta_time)
        self.foreground_list.update_animation(delta_time)

        # See if we hit any coins, removing duplicates 
        coin_hit_list = list(set(arcade.check_for_collision_with_list(self.player_sprite,self.coin_list)))

        # Loop through each coin we hit (if any) and remove it 
        for coin in coin_hit_list: 
            # Remove the coin 
            coin.remove_from_sprite_lists()
            self.score += coin.properties["Points"]  

        # Track if we need to change the viewport 
        changed = False 

        # See if the played collided with an enemy/water
        if arcade.check_for_collision_with_list(self.player_sprite,self.dont_touch_list):
            self.player_sprite.dead = True
        #Makes the player movement speed 0 if they are dead.    
        if self.player_sprite.dead:
            self.player_sprite.change_x = 0
            self.player_sprite.change_y = 0

        #Respawns the player at the start of the level
        if self.player_sprite.respawned:
            self.player_sprite.center_x = PLAYER_START_X
            self.player_sprite.center_y = PLAYER_START_Y
            self.player_sprite.respawned = False
            self.player_sprite.dead = False
            self.view_left = 0
            self.view_bottom = 0
            changed = True

        
        # Scroll left 
        left_boundary = self.view_left + LEFT_VIEWPORT_MARGIN 
        if self.player_sprite.left < left_boundary and self.view_left>15: 
            self.view_left -= left_boundary - self.player_sprite.left 
            changed = True 
        #Scroll right 
        right_boundary = self.view_left + SCREEN_WIDTH - RIGHT_VIEWPORT_MARGIN 
        if self.player_sprite.right > right_boundary and self.view_left<self.end_of_map - SCREEN_WIDTH: 
            self.view_left += self.player_sprite.right - right_boundary 
            changed = True 
        # Scroll up 
        top_boundary = self.view_bottom + SCREEN_HEIGHT - TOP_VIEWPORT_MARGIN 
        if self.player_sprite.top > top_boundary and self.view_bottom<self.top_of_map - SCREEN_HEIGHT: 
            self.view_bottom += self.player_sprite.top - top_boundary 
            changed = True 
        # Scroll down 
        bottom_boundary = self.view_bottom + BOTTOM_VIEWPORT_MARGIN 
        if self.player_sprite.bottom < bottom_boundary and self.view_bottom>20: 
            self.view_bottom -= bottom_boundary - self.player_sprite.bottom 
            changed = True 

        
        # See if the user got to the end of the level
        if self.player_sprite.center_x >= self.end_of_map:
            # Advance to the next level
            self.level += 1
            # Set the camera to the start
            self.view_left = 0
            self.view_bottom = 0
            changed = True

            if self.level <= TOTAL_LEVELS:
                # Load the next level
                self.setup(self.level)

            else:
                #Calls the game over view method
                view = GameOverView()
                self.window.show_view(view)
        
        #Scrolls the viewport is the viewport has changed
        if changed: 
            self.view_bottom = int(self.view_bottom) 
            self.view_left = int(self.view_left) 
            arcade.set_viewport(self.view_left, (SCREEN_WIDTH + self.view_left), self.view_bottom, (SCREEN_HEIGHT + self.view_bottom)) 


def main():
    """ Main method """
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    start_view = InstructionView()
    window.show_view(start_view)
    arcade.run()
if __name__ == "__main__":
    main()
