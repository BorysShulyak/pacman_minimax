import random

import numpy as np
import pygame
from Constants import *
from Search import *
vec = pygame.math.Vector2
"""
This is a Player class which help us to draw Hero, moving he and other useful events
"""


class Player:
    def __init__(self, application, pos):
        self.application = application
        self.starting_pos = [pos.x, pos.y]
        self.grid_pos = pos
        self.old_grid_pos = None
        self.pix_pos = self.get_pix_pos()
        self.direction = vec(0, 1)
        self.stored_direction = None
        self.able_to_move = True
        self.current_score = 0
        self.speed = 2
        self.lives = PLAYER_LIVES
        self.destination = DESTINATION
        self.target_coin = None
        self.algo = MINMAX

    def update(self):
        """
        This is a main function to update the Hero. There is a check of eating the coin,
        death from Ghost and some magic with Teleports
        :return:
        """

        if self.able_to_move:
            self.pix_pos += self.direction*self.speed
        if self.is_in_bounds():
            if self.stored_direction is not None:
                self.direction = self.stored_direction
            self.able_to_move = self.is_able_to_move()

        new_pos = [(self.pix_pos[0] - PADDING + self.application.cell_width // 2) // self.application.cell_width + 1,
                        (self.pix_pos[1] - PADDING + self.application.cell_height // 2) // self.application.cell_height + 1]

        if new_pos != self.grid_pos:
            self.old_grid_pos = self.grid_pos
            self.grid_pos = new_pos


        if self.on_coin():
            self.eat_coin()
        if self.on_enemy():
            self.application.remove_life()
        if self.algo == MINMAX:
            self.change_direction(self.min_max())
        elif self.algo == EXPECT:
            self.change_direction(self.expect_max())

    def get_allowed_directions(self, mob):
        if mob == 1:
            directions = [(-1, 0), (1, 0), (0, 1), (0, -1), (0, 0)]
            allowed_directions = []
            for direction in directions:
                if vec(self.grid_pos[0] + direction[0], self.grid_pos[1] + direction[1]) not in self.application.walls:
                    allowed_directions.append(direction)
            return allowed_directions
        else:
            return vec(0, 0)

    def min_max(self):
        DEPTH = 3
        def maximize(game_state, depth, alpha, beta):
            if game_state.is_lose() or game_state.is_win():
                return game_state.get_score()
            allowed_actions = game_state.get_legal_actions(PLAYER)
            best_score = -999999
            temp_score = best_score
            best_action = vec(0, 0)
            for action in allowed_actions:
                new_state = game_state.simulate_state(action, PLAYER)
                temp_score = minimize(new_state, depth, DEFAULT_GHOST, alpha, beta)
                if temp_score > best_score:
                    best_score = temp_score
                    best_action = action
                alpha = max(alpha, best_score)
                if best_score > beta:
                    return best_score

            if depth == 0:
                return vec(best_action)
            else:
                return best_score

        def minimize(state, depth, ghost, alpha,beta):
            if state.is_lose() or state.is_win():
                return state.get_score()
            next_ghost = ghost + 1
            if ghost == state.get_num_agents() - 1:
                next_ghost = PLAYER
            allowed_actions = state.get_legal_actions(ghost)
            best_score = 999999
            score = best_score
            for action in allowed_actions:
                if next_ghost == PLAYER:
                    if depth == DEPTH - 1:
                        score = state.simulate_state(action, ghost).get_score()
                    else:
                        score = maximize(state.simulate_state(action, ghost), depth + 2, alpha, beta)
                else:
                    score = minimize(state.simulate_state(action, ghost), depth - 1, next_ghost, alpha, beta)
                if score < best_score:
                    best_score = score
                beta = min(beta, best_score)
                if best_score < alpha:
                    return best_score
            return best_score

        return maximize(self.application.get_state(), 0, -999999, 999999)

    def expect_max(self):
        DEPTH = 2

        def maximize(state, depth):
            if state.is_lose() or state.is_win():
                return state.get_score()
            actions = state.get_legal_actions(PLAYER)
            best_score = -99999
            score = best_score
            best_action = vec(0, 0)
            for action in actions:
                new_state = state.simulate_state(action, PLAYER)
                score = minimize(new_state, depth, DEFAULT_GHOST)
                if score > best_score:
                    best_score = score
                    best_action = action
            if depth == 0:
                return best_action
            else:
                return best_score

        def minimize(state, depth, ghost):
            if state.is_lose():
                return state.get_score()
            next_ghost = ghost + 1
            if ghost == state.get_num_agents() - 1:
                next_ghost = PLAYER
            actions = state.get_legal_actions(ghost)
            best_score = 99999
            score = best_score
            for action in actions:
                prob = 1.0/len(actions)
                if next_ghost == PLAYER:
                    if depth == DEPTH - 1:
                        score = state.simulate_state(action, ghost).get_score()
                        score += prob * score
                    else:
                        score = maximize(state.simulate_state(action, ghost), depth + 1)
                        score += prob * score
                else:
                    score = minimize(state.simulate_state(action, ghost), depth, next_ghost)
                    score += prob * score
            return score
        return maximize(self.application.get_state(),0)



    def draw(self):
        """
        Draw the Hero
        :return:
        """
        pygame.draw.circle(self.application.screen, PLAYER_COLOUR, (int(self.pix_pos.x),
                                                                    int(self.pix_pos.y)), self.application.cell_width // 2 - 2)

        for x in range(self.lives):
            pygame.draw.circle(self.application.screen, GREEN, (30 + 20 * x, HEIGHT - 15), 7)

    def draw_path(self):

        if self.c is not None:
            for c in self.c[1:-1]:
                pygame.draw.circle(self.application.screen, YELLOW,
                                   (c[1] * self.application.cell_width + 10 + PADDING // 2,
                                    c[0] * self.application.cell_height + 10 + PADDING // 2), 6)

        for p in self.path:
            pygame.draw.circle(self.application.screen, (0, 255, 0),
                               (p[1] * self.application.cell_width + 10 + PADDING // 2,
                                p[0] * self.application.cell_height + 10 + PADDING // 2), 4)


    def on_coin(self):
        """Check is Hero on coin"""
        if self.grid_pos in self.application.coins:
            return True
        return False

    def eat_coin(self):
        """
        Eating the coin
        :return:
        """
        self.application.coins.remove(self.grid_pos)
        self.current_score += 1

    def on_enemy(self):
        """
        Check is Hero on Enemy...
        Should I move this method to Enemy class
        :return:
        """
        for enemy in self.application.enemies:
            if enemy.position == self.grid_pos:
                return True

    def change_direction(self, direction):
        """

        :param direction: Vector(int, int) - direction to move.
        Description: (1,0) - East
                     (-1,0) - West
                     (0, 1) - South
                     (0,-1) - North
        :return:
        """
        self.stored_direction = direction

    def get_pix_pos(self):
        """
        Using grid position to calculate a pixel position on game screen
        :return: vec(x_pixel_position, y_pixel_position)
        """
        return vec((self.grid_pos[0] * self.application.cell_width) + PADDING // 2 + self.application.cell_width // 2,
                   (self.grid_pos[1] * self.application.cell_height) +
                   PADDING // 2 + self.application.cell_height // 2)

    def is_in_bounds(self):
        """
        Checking is Hero inside a cell to avoid Hero clipping in textures
        :return:
        """
        if int(self.pix_pos.x + PADDING // 2) % self.application.cell_width == 0:
            if self.direction == vec(1, 0) or self.direction == vec(-1, 0) or self.direction == vec(0, 0):
                return True
        if int(self.pix_pos.y + PADDING // 2) % self.application.cell_height == 0:
            if self.direction == vec(0, 1) or self.direction == vec(0, -1) or self.direction == vec(0, 0):
                return True

    def is_able_to_move(self):
        """
        Checking next cell considering direction
        :return:
        """
        for wall in self.application.walls:
            if vec(self.grid_pos+self.direction) == wall:
                return False
        return True
