from tetris_learning_environment._native import ffi, lib
from enum import IntEnum
import numpy


class Key(IntEnum):
	UP = lib.Up
	DOWN = lib.Down
	LEFT = lib.Left
	RIGHT = lib.Right
	B = lib.B
	A = lib.A
	SELECT = lib.Select
	START = lib.Start


class Environment:
	WIDTH = 160
	HEIGHT = 144

	def __init__(self, rom_path: str):
		rom_path_utf8 = rom_path.encode(encoding="UTF-8")
		self.__obj = lib.initialize_environment(rom_path_utf8)
		if self.__obj == ffi.NULL:
			raise Exception("failed to initialize environment (maybe the rom path was incorrect?)")

	def __del__(self):
		# free environment memory
		if self.__obj != ffi.NULL:
			lib.destroy_environment(self.__obj)
		self.__obj = None

	def start_episode(self):
		lib.start_episode(self.__obj)

	def run_frame(self):
		lib.run_frame(self.__obj)

	def is_running(self) -> bool:
		return lib.is_running(self.__obj)

	def set_key_state(self, key: Key, pressed: bool):
		lib.set_key_state(self.__obj, key, pressed)

	def get_score(self) -> int:
		return lib.get_score(self.__obj)

	def get_lines(self) -> int:
		return lib.get_lines(self.__obj)

	def get_pixels(self) -> numpy.ndarray:
		"""
		Returns the contents of the screen as a 160x144 array of RGBA pixel values,
		where each component (R,G,B,A) is 8-bits.
		
		The alpha component is always 255.
		"""
		buffer = ffi.buffer(lib.get_pixels(self.__obj), self.WIDTH * self.HEIGHT * 4)
		return numpy.ndarray((self.HEIGHT, self.WIDTH),
		                      dtype=numpy.uint32,
		                      buffer=buffer,
		                      offset=0,
		                      strides=(self.WIDTH * 4, 4))
