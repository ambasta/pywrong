from typing import Dict, NotRequired, Optional, TypedDict

from requests import get
from typeguard import check_type

from pywrong.utils import to_underscore_case


class Engines(TypedDict):
    node: str


class PackageVersion(TypedDict):
    name: str
    displayName: str
    description: str
    engines: NotRequired[Engines]


class DistTags(TypedDict):
    latest: str


class PacakgeMeta(TypedDict):
    _id: str
    _rev: str
    name: str
    dist_tags: DistTags
    versions: Dict[str, PackageVersion]


class NodePackage:
    __registry: str
    __name: str
    __version: str
    __meta: PacakgeMeta

    def __init__(
        self,
        name: str,
        version: Optional[str] = None,
        registry: str = 'https://registry.npmjs.org',
    ):
        self.__name = name
        self.__registry = registry
        self.__populate_metadata()

        if version and version in self.__meta['versions']:
            self.__version = version
        else:
            self.__version = self.__meta['dist_tags']['latest']

    def __populate_metadata(self):
        with get(f'{self.__registry}/{self.__name}') as request:
            request.raise_for_status()
            data = to_underscore_case(request.json())
            check_type(data, PacakgeMeta)
            self.__meta = data

    @property
    def node_version(self) -> str | None:
        return self.__meta['versions'][self.__version].get('engines', {}).get('node')

    @property
    def name(self) -> str:
        return self.__name
