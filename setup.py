from setuptools import setup, find_packages

def build_native(spec):
	build = spec.add_external_build(
		cmd = ['cargo', 'build', '--release'],
		path = "./rust"
	)

	spec.add_cffi_module(
		module_path = 'tetris_learning_environment._native',
		dylib = lambda: build.find_dylib('tetris_learning_environment', in_path = 'target/release'),
		header_filename = lambda: build.find_header('tetris-learning-environment.h', in_path = '.'),
		rtld_flags = ['NOW', 'NODELETE']
	)

setup(
	name = 'tetris_learning_environment',
	author = 'Achille Heraud',
	url = 'https://github.com/aHeraud/tetris-learning-environment-python',
	license = "MIT",
	version = '0.0.1',
	packages = find_packages(),
	include_package_data = True,
	zip_safe = False,
	platforms = 'any',
	install_requires = ['milksnake', 'numpy'],
	milksnake_tasks = [build_native]
)