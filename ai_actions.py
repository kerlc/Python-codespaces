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
        self.previous_position = None
        self.previous_action = 0
        self.stuck_steps = 0
        self.escape_action = None
        self.escape_steps = 0

    def detect_stuck(self, state):
        current_position = (state[0], state[1])

        if self.previous_position is None:
            self.previous_position = current_position
            return False

        distance_moved = (
        abs(current_position[0] - self.previous_position[0])
        + abs(current_position[1] - self.previous_position[1])
        )
        print(distance_moved)

        self.previous_position = current_position

        if distance_moved < 0.001:
            self.stuck_steps += 1
            print(self.stuck_steps)
        else:
            self.stuck_steps = 0

        return self.stuck_steps >= 10

    def choose_escape_action(self, state):
        wall_up = state[7]
        wall_down = state[8]
        wall_left = state[9]
        wall_right = state[10]

        clearances = {
            1: wall_up,
            2: wall_down,
            3: wall_left,
            4: wall_right,
        }

        return max(clearances, key=clearances.get)

def choose_random_action(state):
    """
    Choose a random movement action.

    This is not intelligent yet. It is only a temporary AI
    used to test whether the game can be controlled without
    keyboard input.

    The state parameter will eventually be used by a trained AI.
    """
    del state

    # randint includes both endpoints, so this returns 0 through 8.
    return random.randint(0, ACTION_COUNT - 1)

def choose_simple_action(state):
    """
    Choose movement based on the current game state.

    State indexes:
        2 = horizontal direction to nearest coin
        3 = vertical direction to nearest coin
        4 = horizontal direction to finish
        5 = vertical direction to finish
        6 = percentage of coins remaining
        7 = dustance to wall up
        8 = distance to wall down
        9 = distance to wall left
        10 = distance to wall right
    """
    coin_dx = state[2]
    coin_dy = state[3]
    finish_dx = state[4]
    finish_dy = state[5]
    coins_remaining = state[6]
    wall_up = state[7]
    wall_down = state[8]
    wall_left = state[9]
    wall_right = state[10]

    if coins_remaining > 0:
        target_dx = coin_dx
        target_dy = coin_dy
    else:
        target_dx = finish_dx
        target_dy = finish_dy

    directions = {
        0: (0, 0),        # Still
        1: (0, -1),       # Up
        2: (0, 1),        # Down
        3: (-1, 0),       # Left
        4: (1, 0),        # Right
        # 5: (-1, -1),      # Up-left
        # 6: (1, -1),       # Up-right
        # 7: (-1, 1),       # Down-left
        # 8: (1, 1),        # Down-right
    }

    threshold = 0.005
    wall_threshold = 0.03

    def action_is_blocked(horizontal, vertical):
        if horizontal == -1 and wall_left < wall_threshold:
            return True

        if horizontal == 1 and wall_right < wall_threshold:
            return True

        if vertical == -1 and wall_up < wall_threshold:
            return True

        if vertical == 1 and wall_down < wall_threshold:
            return True

        return False

    target_lenght = math.sqrt(target_dx ** 2 + target_dy ** 2)

    if target_lenght > 0:
        target_dx /= target_lenght
        target_dy /= target_lenght

    best_action = 0
    best_score = float("-inf")

    for action, (horizontal, vertical) in directions.items():
        if action_is_blocked(horizontal, vertical):
            continue

        target_score = (
            horizontal * target_dx
            + vertical * target_dy
        )

        clearances = []

        if horizontal == -1:
            clearances.append(wall_left)
        elif horizontal == 1:
            clearances.append(wall_right)

        if vertical == -1:
            clearances.append(wall_down)
        elif vertical == 1:
            clearances.append(wall_up)

        if clearances:
            clearance_score = min(clearances)
        else:
            clearance_score = 0

        score = target_score + clearance_score * 0.25

        if action == 0 and target_lenght > 0.02:
            score -= 0.5

        if score > best_score:
            best_score = score
            best_action = action

    return best_action