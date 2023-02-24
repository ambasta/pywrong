from typing import Any, Dict, NotRequired, Optional, TypedDict

from requests import get
from typeguard import check_type

from pywrong.utils import to_underscore_case


class Engines(TypedDict):
    node: str


class PackageVersion(TypedDict):
    author: Any
    bin: NotRequired[Any]
    bugs: Any
    description: str
    dev_dependencies: Any
    directories: Any
    display_name: str
    dist: Any
    engines: NotRequired[Engines]
    git_head: NotRequired[Any]
    has_shrinkwrap: bool
    homepage: Any
    id: str
    license: str
    main: Any
    maintainers: Any
    node_version: str
    npm_operational_internal: Any
    npm_user: Any
    npm_version: str
    name: str
    publisher: Any
    repository: Any
    scripts: Any
    version: str


class DistTags(TypedDict):
    latest: str


class PacakgeMeta(TypedDict):
    author: Any
    bugs: Any
    description: Any
    dist_tags: DistTags
    homepage: Any
    id: str
    license: str
    maintainers: Any
    name: str
    readme: str
    readme_filename: str
    repository: Any
    rev: str
    time: Any
    versions: Dict[str, PackageVersion]


class NodePackage:
    __registry: str
    __name: str
    __unplug: bool
    __version: str
    __meta: PacakgeMeta

    def __init__(
        self,
        name: str,
        unplug: bool = False,
        version: Optional[str] = None,
        registry: str = 'https://registry.npmjs.org',
    ):
        self.__name = name
        self.__unplug = unplug
        self.__registry = registry
        self.__populate_metadata()

        if version and version in self.__meta['versions']:
            self.__version = version
        else:
            self.__version = self.__meta['dist_tags']['latest']

    def __populate_metadata(self):
        with get(f'{self.__registry}/{self.__name}') as request:
            request.raise_for_status()
            data = request.json()
            data = to_underscore_case(data)
            check_type(data, PacakgeMeta)
            self.__meta = data

    @property
    def node_version(self) -> str | None:
        return self.__meta['versions'][self.__version].get('engines', {}).get('node')

    @property
    def name(self) -> str:
        return self.__name

    @property
    def unplug(self) -> bool:
        return self.__unplug
