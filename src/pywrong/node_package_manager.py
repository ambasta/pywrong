from pathlib import Path
from shutil import which
from subprocess import DEVNULL, Popen, run
from typing import List, Literal, Optional, get_args

from pywrong.node_package import NodePackage

Manager = Literal['yarn'] | Literal['npm'] | Literal['pnpm']


def run_command(cmd: Path, cwd: Path, args: List[str | Path]):
    arguments: List[Path | str] = [cmd]

    for arg in list(args):
        arguments.append(arg)

    with Popen(arguments, cwd=cwd, stdout=DEVNULL, stderr=DEVNULL) as process:
        process.wait()


class NodePackageManager:
    __cwd: Path
    __bin_path: Path
    __manager: Optional[str] = None
    __manager_binary: Path

    def __init__(
        self, bin_path: Path, project_root: Path, manager: Optional[str] = None
    ):
        self.__bin_path = bin_path
        self.__cwd = project_root

        if manager:
            self.__manager = manager

    def __detect_managers(self):
        try:
            self.__manager_binary = Path(
                next(
                    manager
                    for literals in get_args(Manager)
                    for manager in get_args(literals)
                    if which(manager, path=self.__bin_path)
                )
            )
            self.__manager = self.__manager_binary.name
        except StopIteration:
            raise RuntimeError(f'No usable package managers found')

    def __setup_yarn(self):
        run_command(self.__manager_binary, self.__cwd, ['init', '-2'])
        run_command(self.__manager_binary, self.__cwd, ['set', 'version', 'canary'])

    def __setup_npmlike(self):
        run_command(self.__manager_binary, self.__cwd, ['init', '-y'])

    def __initialize(self):
        assert self.__manager is not None

        if self.__manager.startswith('yarn'):
            self.__setup_yarn()
        else:
            self.__setup_npmlike()

    def __install(self, packages: List[NodePackage]):
        install_command: str = (
            'add' if self.__manager_binary.name.startswith('yarn') else 'install'
        )
        run_command(
            self.__manager_binary,
            self.__cwd,
            [install_command, *[pkg.name for pkg in packages]],
        )

        unplug_pkgs = list(
            map(lambda pkg: pkg.name, filter(lambda pkg: pkg.unplug, packages))
        )

        run_command(self.__manager_binary, self.__cwd, ['unplug', *unplug_pkgs])
        run_command(self.__manager_binary, self.__cwd, ['install'])

    def setup(self, packages: List[NodePackage]):
        if self.__manager:
            manager_path = which(self.__manager, path=self.__bin_path)

            if manager_path:
                self.__manager_binary = Path(manager_path)
            else:
                self.__detect_managers()
        else:
            self.__detect_managers()

        self.__initialize()
        self.__install(packages)

    def run_binary(self, binary: str, *args):
        return run([self.__manager_binary, binary, *args], cwd=self.__cwd)
