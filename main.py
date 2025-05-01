import pygame
from math import*
from random import*
import sys
sys.path.append("./bin")

from assets import Assets # type: ignore


class Game:
    def __init__(self):
        pygame.init()

        self.assets = Assets()
        self.sprites = self.assets.sprites

        self.grid_width = 12
        self.grid_height = 12
        self.mine_n = 15

        # options: [0] right+left uncovering? // [1] auto-uncover (flags become strict decision)
        self.options = [0, 1]

        self.SCREEN_WIDTH = self.grid_width*15
        self.SCREEN_HEIGHT = self.grid_height*15
        self.SCREEN_WIDTH = pygame.display.Info().current_w
        self.SCREEN_HEIGHT = pygame.display.Info().current_h
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.toggle_fullscreen()
        self.clock = pygame.time.Clock()
        self.run = True
        self.make_grid(0)
        self.initialized_game = 0
        self.quit = 0
        self.fps_cap = pygame.display.get_current_refresh_rate()
        self.highlighted_cells_to_uncover = []

    def make_grid(self, call):
        if call == 0:
            self.grid = []
            self.uncovered = []
            for i in range (0, self.grid_width*self.grid_height):
                self.grid.append("")
                self.uncovered.append(0)

        else:
            self.grid = []
            self.uncovered = []

            # make an empty grid
            for i in range (0, self.grid_width*self.grid_height):
                self.grid.append("")
                self.uncovered.append(0)
            
            for item in self.spared_initial_cells:
                self.uncovered[item] = 1


            # add mines to the grid randomly
            mine_pos = []
            for i in range (self.mine_n):
                # add mine position and make sure to not repeat positions
                new_mine_position = randint(0, self.grid_width*self.grid_height-1)
                while new_mine_position in mine_pos or new_mine_position in self.spared_initial_cells:
                    new_mine_position = (new_mine_position + 1) % len(self.grid)
                mine_pos.append(new_mine_position)
                self.grid[mine_pos[i]] = "mine"
            self.mine_pos = mine_pos

            # assign numbers to cells (only check cells that are around a mine, and don't check cells more than once)
            checked_cells = []

            # for every mine in the grid
            for i in range (self.mine_n):
                # get the positions around the mine
                check_positions_around_mine = self.assign_numbers(mine_pos[i])
                # for every position around the mine
                for items in check_positions_around_mine:
                    # if that cell wasn't already checked
                    if items not in checked_cells and self.grid[items] != "mine":
                        # get list of positions around cell
                        check_positions_around_cell = self.assign_numbers(items)
                        # check mines at every position, assign number to cell
                        self.grid[items] = self.check_mines_around_cell(items, check_positions_around_cell)
                        # register that the cell has been checked
                        checked_cells.append(items)

            # uncover initial blanks
            self.uncovered_already = []

            for item in self.spared_initial_cells:
                self.uncover_blanks_in_vicinity(item)


    def uncover_blanks_in_vicinity(self, n, condition=None):
        positions_to_uncover = self.assign_numbers(n)
        for item in positions_to_uncover:
            if self.grid[item] != "mine" and item not in self.uncovered_already:
                if condition == None or (condition == "only_check_for_blanks" and self.grid[item] == ""):
                    self.uncovered[item] = 1
                    self.uncovered_already.append(item)
                    if self.grid[item] == "":
                        self.uncover_blanks_in_vicinity(item)


    def check_mines_around_cell(self, n, positions_to_check):
        number = 0
        for items in positions_to_check:
            if self.grid[items] == "mine":
                number += 1
        return number
    
    def uncover_highlighted(self, n, auto_uncover=None):
        surrounding = self.assign_numbers(n)

        if auto_uncover == "auto_uncover":
            valid = self.mouse_c[0]
        else:
            if self.options[0] == True:
                valid = self.mouse_jc[2]
            else:
                valid = True
        
         # this way, if both right and left are clicked:
        if valid == True:

            # check all marked cells around:
            idx = 0
            surrounding_without_marked = []
            for items in surrounding:
                if self.uncovered[items] == "marked":
                    idx += 1
                elif self.uncovered[items] == 0:
                    surrounding_without_marked.append(items)
            
            # uncover surrounding non-marked cells (if the number of marked cells corresponds to the cell value):
            print(idx, self.grid[n])
            if idx == self.grid[n]:
                self.highlighted_cells_to_uncover = surrounding_without_marked
                return surrounding_without_marked
            # if the number of cell doesn't correspond to the number of flagged cells around and you're on auto, return an empty list to indicate there's nothing to uncover
            elif auto_uncover == "auto_uncover":
                return []
    

        return surrounding
            

    def assign_numbers(self, n):
        w = self.grid_width
        positions_to_check = []
        pos_list = [n-w-1, n-w, n-w+1, n-1, n+1, n+w-1, n+w, n+w+1]
        cell_line = floor(n/self.grid_width)
        line_list = [cell_line-1, cell_line-1, cell_line-1, cell_line, cell_line, cell_line+1, cell_line+1, cell_line+1]
        # only include positions that aren't out of the grid (and that are the intended ones)
        idx = -1
        for items in pos_list:
            idx += 1
            try:
                position = self.grid[items]
            except:
                pass
            else:
                # check whether it's on the intended line, if so add it to the list of positions to check around the cell
                if items >= 0:
                    if floor(items/self.grid_width) == line_list[idx]:
                        positions_to_check.append(items)

        return positions_to_check


    def check_mouse(self, x, y, xw, yw):
        x = round(x)
        xw = round(xw)
        y = round(y)
        yw = round(yw)
        val = ""
        if self.mouse_pos[0] in range (x, x+xw) and self.mouse_pos[1] in range (y, y+yw):
            if self.mouse_jr[0] == True: # uncover
                val += "clicked, "
            elif self.mouse_c[0] == True: # clicking
                val += "clicking, " # clicking
            if self.mouse_jc[2] == True: # mark
                val += "mark, "
        return val

    def click_conditions(self, n):
        self.uncovered[n] = 1
        # if this is the first uncovering:
        if self.initialized_game == 0:
            self.initialized_game = 1
            self.spared_initial_cells = [n]
            self.quit = 1
        # if this is not the first uncovering
        else:
            if self.grid[n] == "":
                self.uncover_blanks_in_vicinity(n)
            elif self.grid[n] != "mine":
                self.uncover_blanks_in_vicinity(n, "only_check_for_blanks")
            else:
                # if mine clicked, uncover every mine
                for mine in self.mine_pos:
                    self.uncovered[mine] = 1

    def uncover_near_marked(self, n):
        positions = self.assign_numbers(n)
        to_uncover = []
        for position in positions:
            # if the cell is uncovered:
            if self.uncovered[position] == 1:
                # find surrounding cells to uncover if marked_cells_around == cell_value:
                cell_result = self.uncover_highlighted(position, "auto_uncover")
                # add them all to the end result
                for cell in cell_result:
                    to_uncover.append(cell)
        return to_uncover


    def run_grid(self):
        # initialize grid info
        cell_sprite_factor = 4
        cell_size_in_pixels = int(round(self.sprites["cell_1"].get_width()*cell_sprite_factor))
        grid_xoffs = (self.SCREEN_WIDTH-self.grid_width*cell_size_in_pixels)/2
        grid_yoffs = (self.SCREEN_HEIGHT-self.grid_height*cell_size_in_pixels)/2

        # run and render cells
        for i in range (0, self.grid_height):
            for n in range (0, self.grid_width):
                position = i*self.grid_width+n

                x = grid_xoffs
                y = grid_yoffs
                x += i*cell_size_in_pixels
                y += n*cell_size_in_pixels

                # if cell uncovered:
                if self.uncovered[position] == 1:
                    # assign image based on cell value
                    cell_val = self.grid[position]
                    if cell_val == 0 or cell_val == "":
                        img = "cell_uncovered"
                    elif cell_val == "mine":
                        img = "cell_mine"
                    else:
                        img = "cell_" + str(cell_val)
                    
                    # if clicked, highlight cells around it
                    check_mouse = self.check_mouse(x, y, cell_size_in_pixels, cell_size_in_pixels)
                    if check_mouse == "clicking":
                        self.cells_highlighted = self.uncover_highlighted(position)

                # if cell covered:
                else:
                    check_mouse = self.check_mouse(x, y, cell_size_in_pixels, cell_size_in_pixels)
                    # if self.options[1] == True:
                    #     if self.mouse_jc[2] == True: # shouldn't it be "clicking?" // I THINK ITS WHEN MARKING
                    #         self.uncover_near_marked(position)

                    # if clicked:
                    if "clicked" in check_mouse and self.options[1] == False:
                        img = "cell_hidden_clicked"
                        self.click_conditions(position)

                    # if not uncover-click:
                    else:
                        # mark click:
                        if "mark" in check_mouse:
                            if self.uncovered[position] == "marked":
                                self.uncovered[position] = 0
                            elif self.uncovered[position] == 0:
                                self.uncovered[position] = "marked"
                                if self.options[1] == True:
                                    self.highlighted_cells_to_uncover = self.uncover_near_marked(position)
                                    # self.cells_highlighted = self.uncover_near_marked(position)

                        elif "clicked" in check_mouse and self.options[1] == True:
                            img = "cell_hidden_clicked"
                            self.click_conditions(position)
                            
                        # left-click held:
                        if "clicking" in check_mouse:
                            img = "cell_hidden_clicked"
                            self.cells_highlighted = []
                        
                        # no click:
                        else:
                            # display marked cell:
                            if self.uncovered[position] == "marked": 
                                img = "cell_marked"
                                

                            # display non-marked cell:
                            else:
                                if position in self.cells_highlighted:
                                    img = "cell_hidden_clicked"
                                else:
                                    img = "cell_hidden"
                                
                                # if highlighted cell to uncover, uncover:
                                if position in self.highlighted_cells_to_uncover:
                                    self.uncovered[position] = 1
                                    self.click_conditions(position)

                self.screen.blit(pygame.transform.scale_by(self.sprites[img], cell_sprite_factor), (x, y))
                check_mouse = self.check_mouse(x, y, cell_size_in_pixels, cell_size_in_pixels)


    def game_run(self):
        while self.run:

            # reset grid (after initial click)
            if self.quit == 1:
                self.make_grid(1)
                self.quit = 0
            elif self.quit == 2:
                self.make_grid(0)
                self.initialized_game = 0
                self.quit = 0

            self.clock.tick(self.fps_cap)
            self.key = pygame.key.get_just_pressed()
            self.key_held = pygame.key.get_pressed()
            self.mouse_jr = pygame.mouse.get_just_released()
            self.mouse_c = pygame.mouse.get_pressed()
            self.mouse_jc = pygame.mouse.get_just_pressed()
            self.mouse_pos = pygame.mouse.get_pos()

            self.screen.fill((255,255,255))

            # reset highlighted cells if no left click
            if self.mouse_c[0] == False:
                self.cells_highlighted = []

            if self.key[pygame.K_SPACE] == True:
                self.quit = 2

            self.run_grid()
            print(f"to uncover = {self.highlighted_cells_to_uncover}")

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.run = False
            pygame.display.update()

Game().game_run()