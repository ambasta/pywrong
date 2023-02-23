from pathlib import Path
from typing import List, Optional

from semantic_version import SimpleSpec

from pywrong.node_package import NodePackage
from pywrong.node_package_manager import NodePackageManager
from pywrong.nodejs import NodeJS


class NodeProject:
    __node_js: NodeJS
    __cwd: Path
    __packages: List[NodePackage]
    __manager: NodePackageManager

    def __init__(self, cwd: Path) -> None:
        self.__node_js = NodeJS(cwd)
        self.__cwd = cwd

    def add_packages(self, packageNames: List[str]):
        self.__packages = [NodePackage(packageName) for packageName in packageNames]

    def setup(self, manager: Optional[str] = None):
        node_versions = [
            pkg.node_version for pkg in self.__packages if pkg.node_version
        ]
        node_spec = SimpleSpec(','.join(node_versions))
        self.__node_js.setup(node_spec)
        self.__manager = NodePackageManager(
            self.__node_js.binary.parent, self.__cwd, manager
        )
        self.__manager.setup(self.__packages)
