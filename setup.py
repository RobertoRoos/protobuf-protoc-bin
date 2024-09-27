import stat
from pathlib import Path
import re
import os
from tempfile import TemporaryDirectory
import shutil
import platform
import urllib.request
import urllib.error

from setuptools import setup
from setuptools.command.install import install
from wheel.bdist_wheel import bdist_wheel


class CustomInstallCommand(install):
    """Download `protoc` binary and install with package."""

    PKG_ROOT: Path

    PLATFORM_SUFFIX: str

    @classmethod
    def check(cls):
        """Detect the building platform and choose protoc download type."""
        cls.PKG_ROOT = Path(__file__).parent.absolute()
        cls.PLATFORM_SUFFIX = cls._get_platform()

    def run(self):
        install.run(self)  # Avoid `super()` for legacy reasons

        version = self._get_version()
        plat = self.PLATFORM_SUFFIX

        base_url = "https://github.com/protocolbuffers/protobuf/releases"

        if version == "0.0":  # Typical for un-tagged CI build
            print("Finding latest protoc release...")
            new_url: str = urllib.request.urlopen(f"{base_url}/latest").geturl()
            _, _, new_version = new_url.rpartition("/")
            version = new_version.lstrip("v")

        with TemporaryDirectory() as temp_dir:
            download_dir = Path(temp_dir).absolute()
            zip_file = download_dir / "protoc.zip"
            url = f"{base_url}/download/v{version}/protoc-{version}-{plat}.zip"
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
            # Allow executing of new file:
            os.chmod(
                protoc_dest,
                stat.S_IRUSR
                | stat.S_IWUSR
                | stat.S_IXUSR
                | stat.S_IRGRP
                | stat.S_IXGRP
                | stat.S_IROTH
                | stat.S_IXOTH,  # Set to 755 mode
            )

    def _get_version(self) -> str:
        """Get current package version (or raise exception)."""
        with open(
            self.PKG_ROOT / "src" / "protobuf_protoc_exe" / "_version.py", "r"
        ) as fh:
            re_version = re.compile(r'.*version = [\'"](.*)[\'"]')
            while line := fh.readline():
                if match := re_version.search(line):
                    return match.group(1)

        raise RuntimeError(f"Failed to parse version from pyproject.toml")

    @classmethod
    def _get_platform(cls) -> str:
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


# Execute platform check
CustomInstallCommand.check()


class CustomWheel(bdist_wheel):
    """Custom command to mark our wheel as platform-specific."""

    def get_tag(self):
        plat = CustomInstallCommand.PLATFORM_SUFFIX

        if plat == "osx-universal_binary":
            system = "macosx_10_11_universal2"
        elif plat == "osx-x86_64":
            system = "macosx_10_11_x86_64"
        elif plat == "win64":
            system = "win_amd64"
        elif plat in ["win32", "linux-x86_64", "linux-x86_64"]:
            system = plat.replace("-", "_")  # Same but with underscore
        else:
            raise RuntimeError(f"Failed to detect Python platform tag for `{plat}`")

        return "py2.py3", "none", system


# noinspection PyTypeChecker
setup(
    cmdclass={
        "install": CustomInstallCommand,
        "bdist_wheel": CustomWheel,
    }
)

# Rely on `pyproject.toml` for all other info instead
