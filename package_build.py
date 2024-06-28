import urllib.request
import urllib.error
from pathlib import Path
from tempfile import TemporaryDirectory
import shutil
import re


def build(*_args):
    """Build script that is run early during the package installation step.

    This script will download a `protoc` binary from the official Github, based on the
    version named in this project's `pyproject.toml`.
    """

    root = Path(__file__).parent.absolute()

    # Get version out of TOML file:
    version_str = None
    with open(root / "src" / "protobuf_protoc_exe" / "__init__.py", "r") as fh:
        re_version = re.compile(r'__version__ = "(.*)"')
        while line := fh.readline():
            if match := re_version.search(line):
                version_str = match.group(1)
                break

    if version_str is None:
        raise RuntimeError(f"Failed to parse version from pyproject.toml")

    with TemporaryDirectory() as temp_dir:
        download_dir = Path(temp_dir)
        zip_file = download_dir / "protoc.zip"
        url = f"https://github.com/protocolbuffers/protobuf/releases/download/v{version_str}/protoc-{version_str}-win64.zip"
        try:
            urllib.request.urlretrieve(url, zip_file)
        except urllib.error.HTTPError as err:
            raise RuntimeError(
                f"Failed to download protoc version `{version_str}`: " + str(err)
            )

        shutil.unpack_archive(zip_file, temp_dir)

        protoc_download_file = download_dir / "bin" / "protoc.exe"
        resources_dir = root / "resources"
        if not resources_dir.exists():
            resources_dir.mkdir()
        protoc_dest = resources_dir / protoc_download_file.name
        shutil.move(protoc_download_file, protoc_dest)


if __name__ == "__main__":
    build()
