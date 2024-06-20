import urllib.request
from pathlib import Path
from tempfile import TemporaryDirectory
import shutil


def build(*_args):
    """Build script that is run early during the package installation step.

    This script will download a `protoc` binary from the official Github, based on the
    version named in this project's `pyproject.toml`.
    """

    package_dir = Path(__file__).parent.absolute()

    # Get version out of TOML file:
    version_str = None
    with open(package_dir / "pyproject.toml", "r") as fh:
        while line := fh.readline():
            if line.lstrip().startswith("version ="):
                version_str = line[9:].strip().strip('"')
                break

    if version_str is None:
        raise RuntimeError(f"Failed to parse version from pyproject.toml")

    with TemporaryDirectory() as temp_dir:
        download_dir = Path(temp_dir)
        zip_file = download_dir / "protoc.zip"
        url = f"https://github.com/protocolbuffers/protobuf/releases/download/v{version_str}/protoc-{version_str}-win64.zip"
        urllib.request.urlretrieve(url, zip_file)

        shutil.unpack_archive(zip_file, temp_dir)

        protoc_download_file = download_dir / "bin" / "protoc.exe"
        resources_dir = package_dir / "resources"
        if not resources_dir.exists():
            resources_dir.mkdir()
        protoc_dest = resources_dir / protoc_download_file.name
        shutil.move(protoc_download_file, protoc_dest)


if __name__ == "__main__":
    build()
