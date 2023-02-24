from pathlib import Path
from sys import argv
from tempfile import TemporaryDirectory

from pywrong.node_project import NodeProject


def serve() -> int:
    args = argv[1:]

    with TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        project = NodeProject(tmpdir_path)
        project.add_package('pyright', unplug=True)
        project.setup()
        process = project.run_binary('pyright-langserver', *args)
        return process.returncode
