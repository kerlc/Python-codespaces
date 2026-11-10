import random
import math

ACTION_COUNT = 9
DIRECTIONS = {
    0: (0, 0),
    1: (0, -1),
    2: (0, 1),
    3: (-1, 0),
    4: (1, 0),
}

class SimpleAI:
    def __init__(self):
        # The AI remembers its previous position and action.
        self.previous_position = None
        self.previous_action = 0

        # Escape mode helps it get away from walls.
        self.escape_action = None
        self.escape_steps = 0

    def reset(self):
        """Clear memory before starting a new episode."""
        self.__init__()

    def is_blocked(self, action, state):
        """
        Check whether an action points toward a nearby wall.

        State indexes 7-10 contain:
            7 = wall above
            8 = wall below
            9 = wall left
            10 = wall right
        """
        wall_up = state[7]
        wall_down = state[8]
        wall_left = state[9]
        wall_right = state[10]

        wall_threshold = 0.08

        if action == 1:
            return wall_up < wall_threshold
        if action == 2:
            return wall_down < wall_threshold
        if action == 3:
            return wall_left < wall_threshold
        if action == 4:
            return wall_right < wall_threshold

        return False

    def opposite_action(self, action):
        """Return the opposite direction."""
        opposites = {
            1: 2,  # Up -> down
            2: 1,  # Down -> up
            3: 4,  # Left -> right
            4: 3,  # Right -> left
        }

        return opposites.get(action, 0)

    def choose_safest_action(self, state):
        """
        Choose the direction with the most open space.

        max(..., key=...) compares the wall distance values
        and returns the action with the greatest available distance.
        """
        clearances = {
            1: state[7],  # Up
            2: state[8],  # Down
            3: state[9],  # Left
            4: state[10],  # Right
        }

        possible_actions = {
            action: distance
            for action, distance in clearances.items()
            if not self.is_blocked(action, state)
        }

        if not possible_actions:
            return 0

        return max(
            possible_actions,
            key=possible_actions.get,
        )

    def player_is_stuck(self, state):
        """
        Detect whether the player has barely moved.

        Positions are normalized between 0 and 1, so a difference
        below 0.001 is less than about one screen pixel.
        """
        current_position = (state[0], state[1])

        if self.previous_position is None:
            self.previous_position = current_position
            return False

        distance_moved = math.sqrt(
            (current_position[0] - self.previous_position[0]) ** 2
            + (current_position[1] - self.previous_position[1]) ** 2
        )

        self.previous_position = current_position

        return distance_moved < 0.001

    def choose_target_action(self, state):
        """
        Choose a direction toward the nearest coin or finish.
        """
        coin_dx = state[2]
        coin_dy = state[3]
        finish_dx = state[4]
        finish_dy = state[5]
        coins_remaining = state[6]

        if coins_remaining > 0:
            target_dx = coin_dx
            target_dy = coin_dy
        else:
            target_dx = finish_dx
            target_dy = finish_dy

        # Choose the larger difference first.
        if abs(target_dx) > abs(target_dy):
            action = 4 if target_dx > 0 else 3
        else:
            action = 2 if target_dy > 0 else 1

        # If the preferred direction is blocked, try the other axis.
        if self.is_blocked(action, state):
            if action in (3, 4):
                alternative = 2 if target_dy > 0 else 1
            else:
                alternative = 4 if target_dx > 0 else 3

            if not self.is_blocked(alternative, state):
                action = alternative
            else:
                action = self.choose_safest_action(state)

        return action

    def choose_action(self, state):
        """
        Choose one action for the current game state.
        """
        # Continue an escape movement for several frames.
        # This prevents the AI from instantly turning back.
        if self.escape_steps > 0:
            self.escape_steps -= 1
            return self.escape_action

        # If the player has stopped moving, begin escape mode.
        if self.player_is_stuck(state):
            self.escape_action = self.choose_safest_action(state)
            self.escape_steps = 25
            self.previous_action = self.escape_action
            return self.escape_action

        action = self.choose_target_action(state)

        # Do not immediately reverse direction unless necessary.
        opposite = self.opposite_action(self.previous_action)

        if action == opposite and self.is_blocked(self.previous_action, state):
            action = self.choose_safest_action(state)

        self.previous_action = action
        return action