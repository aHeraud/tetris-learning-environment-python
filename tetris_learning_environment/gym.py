from typing import Union, Tuple
from enum import IntEnum, Enum
from tetris_learning_environment import Environment, Key

try:
    import numpy as np
    from gym.spaces import Discrete
except ImportError:
    raise Exception('the open ai gym api requires the following packages: \'numpy\', \'gym\'')


class Metric(Enum):
    SCORE = 0
    LINES = 1


class Action(IntEnum):
    NONE = 0
    LEFT = 1
    RIGHT = 2
    DOWN = 3
    ROTATE_RIGHT = 4
    ROTATE_LEFT = 5


def _map_action_to_key(action: Action) -> Union[Key, None]:
    if action == Action.LEFT:
        return Key.LEFT
    elif action == Action.RIGHT:
        return Key.RIGHT
    elif action == Action.DOWN:
        return Key.DOWN
    elif action == Action.ROTATE_RIGHT:
        return Key.A
    elif action == Action.ROTATE_LEFT:
        return Key.B
    else:
        return None


class TetrisEnvironment:
    _action_set = [action for action in Action]
    action_space = Discrete(len(_action_set))

    def __init__(self, rom_path: str, frame_skip=4, reward_type=Metric.SCORE):
        self.env = Environment(rom_path)
        self.last_action = Action.NONE
        self.frame_skip = frame_skip
        self.viewer = None
        self.reward_type = reward_type

    def step(self, action: Action) -> Tuple[np.ndarray, float, bool, dict]:
        """Run 1 frame of the game (~1/60th of a second emulated time)

        # Arguments
            action (object): One of the actions contained in Environment.action_space

        # Returns
            observation (object): A numpy array of RGB pixels representing the contents of the screen.
            reward (float): Difference in score between before and after the frame is emulated, or the number of lines
                            cleared during the frame, depending on the value of reward_type when the environment was
                            created.
            done (boolean): Whether the game has ended.
            info (dict): Contains the current score (key='score')
        """

        old_score = self.env.get_score()
        old_lines = self.env.get_lines()

        # In Tetris holding down either of the rotate buttons doesn't continue to rotate the piece.
        # To perform multiple rotations you must release the rotate key and then press it again in a later frame.
        if action == Action.ROTATE_RIGHT and self.last_action == Action.ROTATE_RIGHT:
            action = Action.NONE
        elif action == Action.ROTATE_LEFT and self.last_action == Action.ROTATE_LEFT:
            action = Action.NONE
        self.last_action = action

        for key in Key:
            self.env.set_key_state(key, False)

        key = _map_action_to_key(action)
        if key is not None:
            self.env.set_key_state(key, True)

        self.env.run_frame()

        for _ in range(self.frame_skip):
            if self.env.is_running():
                self.env.run_frame()

        new_lines = self.env.get_lines()
        new_score = self.env.get_score()

        score_delta = new_score - old_score
        line_delta = old_lines - new_lines

        if self.reward_type == Metric.SCORE:
            reward = max(score_delta, 0)
        elif self.reward_type == Metric.LINES:
            reward = max(line_delta, 0)
        else:
            raise Exception('invalid reward type')

        image = self.env.get_rgb_pixels()

        info = {'score': new_score, 'lines': new_lines}

        return image, reward, self.env.is_running() is not True, info

    def reset(self) -> np.ndarray:
        """Starts a new game of Tetris.
        This will handle randomizing the Gameboys source of PRNG, so you should not call the seed method of the environment.

        # Returns
            observation (object): An array of RGBA pixels representing the contents of the screen.
        """
        self.env.start_episode()
        image = self.env.get_rgb_pixels()
        return image

    def render(self, mode='human', close=False):
        img = self.env.get_rgb_pixels()
        if mode == 'rgb_array':
            return img
        elif mode == 'human':
            from gym.envs.classic_control import rendering
            if self.viewer is None:
                self.viewer = rendering.SimpleImageViewer()
            self.viewer.imshow(img)
        return self.viewer.isopen

    def seed(self, seed=None):
        if seed is not None:
            raise NotImplementedError()

    def close(self):
        if self.viewer is not None:
            self.viewer.close()
            self.viewer = None

    def configure(self, *args, **kwargs):
        raise NotImplementedError()

    def __del__(self):
        self.close()
