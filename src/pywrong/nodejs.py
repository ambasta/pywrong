from pathlib import Path
from platform import machine
from shutil import which
from subprocess import check_output
from sys import maxsize, platform
from sysconfig import get_config_var
from tarfile import open
from typing import List, Literal, TypedDict

from requests import get
from semantic_version import SimpleSpec, Version
from typeguard import check_type

from pywrong.utils import to_underscore_case

Platform = Literal['armv6l'] | Literal['armv7l']


class NodeVersion(TypedDict):
    version: str


class NodeJS:
    __working_dir: Path
    __node_path: Path
    __src_proto = 'https'
    __src_host = 'nodejs.org'
    __src_host_prefix = ''
    __src_path = 'download/release'

    def __init__(self, cwd: Path):
        self.__working_dir = cwd

        if self.__is_musl:
            self.__src_host_prefix = 'unofficial-builds.'

    def setup(self, spec: SimpleSpec):
        if not self.__detect_system_node(spec):
            maximum_supported_version = next(
                version
                for version in self.__fetch_remote_versions()
                if spec.match(Version(version['version']))
            )
            uri = f"{self.__src_uri}/{maximum_supported_version}/{self.node_variant}.tar.gz"

            with get(uri, stream=True) as rx, open(
                fileobj=rx.raw, mode='r:gz'
            ) as handle:
                handle.extractall(path=self.__working_dir / "node")
            bin_path = which('node', path=self.__working_dir / "node")

            if bin_path is None:
                raise RuntimeError()
            self.__node_path = Path(bin_path)

    @property
    def __src_uri(self):
        return f'{self.__src_proto}://{self.__src_host_prefix}{self.__src_host}/{self.__src_path}'

    @property
    def __is_musl(self) -> bool:
        return 'musl' in get_config_var('HOST_GNU_TYPE')

    @property
    def __is_linux(self) -> bool:
        return 'linux' in platform

    @property
    def __is_64bit(self) -> bool:
        return maxsize > 2**32

    @property
    def __is_arm(self) -> bool:
        return 'aarch64' in machine().lower() or 'arm' in machine().lower()

    @property
    def __is_ppc(self) -> bool:
        return 'ppc' in machine().lower()

    @property
    def binary(self) -> Path:
        return self.__node_path

    def node_variant(self) -> str:
        suffix: str = 'x'

        if not self.__is_linux:
            raise Exception('Unsupported platform')

        if not self.__is_64bit:
            raise Exception('Unsupported architecture')

        if self.__is_arm:
            suffix = 'arm'
        elif self.__is_ppc:
            suffix = 'ppc'

        suffix = f'{suffix}64'

        if self.__is_musl:
            suffix = f'{suffix}-musl'

        return f'linux-{suffix}'

    def __detect_system_node(self, spec: SimpleSpec):
        node_bin_path = which('node') or which('nodejs')

        if node_bin_path:
            node_bin_version = check_output([node_bin_path, '--version'])[:-1].decode()

            if spec.match(node_bin_version):
                self.__node_path = Path(node_bin_path)
                return True
        return False

    def __fetch_remote_versions(self) -> List[NodeVersion]:
        with get(f'{self.__src_uri}/index.json') as request:
            request.raise_for_status()
            data = to_underscore_case(request.json())
            check_type(
                data,
                List[NodeVersion],
            )
            return data
