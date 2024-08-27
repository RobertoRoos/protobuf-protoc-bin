from pathlib import Path
import re
from tempfile import TemporaryDirectory
import shutil
import platform
import urllib.request
import urllib.error

from setuptools import setup
from setuptools.command.install import install


class CustomInstallCommand(install):
    """Download `protoc` binary and install with package."""

    pkg_root: Path

    def run(self):
        install.run(self)  # Avoid `super()` for legacy reasons

        self.pkg_root = Path(__file__).parent.absolute()

        version = self._get_version()

        plat = self._get_platform()

        with TemporaryDirectory() as temp_dir:
            download_dir = Path(temp_dir).absolute()
            zip_file = download_dir / "protoc.zip"
            url = f"https://github.com/protocolbuffers/protobuf/releases/download/v{version}/protoc-{version}-{plat}.zip"
            print(f"Downloading {url}...")
            try:
                urllib.request.urlretrieve(url, zip_file)
            except urllib.error.HTTPError as err:
                raise RuntimeError(
                    f"Failed to download protoc version `{version}`: " + str(err)
                )

            shutil.unpack_archive(zip_file, download_dir)

            filename = "protoc" + (".exe" if "win" in plat.lower() else "")
            protoc_download_path = download_dir / "bin" / filename
            protoc_dest = Path(self.install_scripts).absolute() / filename
            protoc_dest.parent.mkdir(parents=True, exist_ok=True)
            self.copy_file(
                str(protoc_download_path),
                str(protoc_dest),
            )

    def _get_version(self) -> str:
        """Get current package version (or raise exception)."""
        with open(
            self.pkg_root / "src" / "protobuf_protoc_exe" / "_version.py", "r"
        ) as fh:
            re_version = re.compile(r'.*version = [\'"](.*)[\'"]')
            while line := fh.readline():
                if match := re_version.search(line):
                    return match.group(1)

        raise RuntimeError(f"Failed to parse version from pyproject.toml")

    @staticmethod
    def _get_platform() -> str:
        """Detect necessary platform download."""
        system = platform.system().lower()
        arch = [x.lower() if isinstance(x, str) else x for x in platform.architecture()]

        if system == "windows":
            if "64bit" in arch:
                return "win64"
            return "win32"

        if system == "linux":
            if "64bit" in arch:
                return "linux-x86_64"
            return "linux-x86_32"
            # Other Linux types are still ignored

        if system == "darwin":
            if "64bit" in arch:
                return "osx-x86_64"
            return "osx-universal_binary"

        raise RuntimeError(
            f"Could not choose protoc download for system `{system}` ({arch})"
        )


# noinspection PyTypeChecker
setup(
    cmdclass={
        "install": CustomInstallCommand,
    }
)

# Rely on `pyproject.toml` for all other info instead
