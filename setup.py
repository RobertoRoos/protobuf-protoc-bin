import os
import platform
import re
import shutil
import stat
import sysconfig
import urllib.error
import urllib.request
from pathlib import Path
from tempfile import TemporaryDirectory

from setuptools import setup
from setuptools.command.install import install
from wheel.bdist_wheel import bdist_wheel


class CustomInstallCommand(install):
    """Download `protoc` binary and install with package."""

    PKG_ROOT = Path(__file__).parent.absolute()

    BASE_URL = "https://github.com/protocolbuffers/protobuf/releases"

    def run(self):
        install.run(self)  # Avoid `super()` for legacy reasons

        version = self._get_version()
        plat = self._get_platform()

        if version == "0.0":  # Typical for un-tagged CI build
            print("Finding latest protoc release...")
            new_url: str = urllib.request.urlopen(f"{self.BASE_URL}/latest").geturl()
            _, _, new_version = new_url.rpartition("/")
            version = new_version.lstrip("v")

        with TemporaryDirectory() as temp_dir:
            download_dir = Path(temp_dir).absolute()
            zip_file = download_dir / "protoc.zip"
            url = self._get_url(plat, version)
            print(f"Downloading {url}...")
            try:
                urllib.request.urlretrieve(url, zip_file)
            except urllib.error.HTTPError as err:
                raise RuntimeError(
                    f"Failed to download protoc version `{version}`: " + str(err)
                )

            shutil.unpack_archive(zip_file, download_dir)

            # Copy binary:
            bin_filename = "protoc" + (".exe" if "win" in plat.lower() else "")
            protoc_download_path = download_dir / "bin" / bin_filename
            protoc_dest = Path(self.install_scripts).absolute() / bin_filename
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

            # Copy 'include' directory als well
            # But protoc requires its include/ to be in the folder adjacent to the
            # binary, not in a regular system include/ folder
            include_download_path = download_dir / "include"
            # The 'google' directory will be created in here:
            include_dest = protoc_dest.parent / "include"
            include_dest.mkdir(parents=True, exist_ok=True)
            self.copy_tree(str(include_download_path), str(include_dest))

    def _get_url(self, plat: str, version: str) -> str:
        """Get URL to the archive for Protoc.

        There are some discrepancies in version string formatting to cover.
        """
        # Check if the version is like `v1.0rc1`, `v1.0-rc-1`, etc.
        rc_match = re.match(r"^(.+)-?rc-?(.+)$", version)
        if rc_match:
            ver1 = "v" + rc_match.group(1) + "-rc" + rc_match.group(2)
            ver2 = rc_match.group(1) + "-rc-" + rc_match.group(2)
        else:
            ver1 = "v" + version
            ver2 = version

        # ver1 does have the `v` prefix, the other doesn't
        return f"{self.BASE_URL}/download/{ver1}/protoc-{ver2}-{plat}.zip"


    def _get_version(self) -> str:
        """Get current package version (or raise exception)."""
        with open(
            self.PKG_ROOT / "src" / "protobuf_protoc_bin" / "_version.py", "r"
        ) as fh:
            re_version = re.compile(r'.*version = [\'"](.*)[\'"]')
            while line := fh.readline():
                if match := re_version.search(line):
                    return match.group(1)

        raise RuntimeError(f"Failed to parse version from pyproject.toml")

    @staticmethod
    def _get_platform() -> str:
        """Detect necessary platform tag for protoc download.

        See available tags from https://github.com/protocolbuffers/protobuf/releases/latest
        """
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


class CustomWheel(bdist_wheel):
    """Custom command to mark our wheel as platform-specific.

    Without this, all wheels are marked as `None` and are considered platform
    independent, which is not true as we included a specific `protoc` binary.

    The tag produced here is different from the tag used for `protoc` in
    :meth:`CustomInstallCommand._get_platform`.
    """

    def get_tag(self):
        """

        See https://packaging.python.org/en/latest/specifications/platform-compatibility-tags/
        """
        impl_tag = "py2.py3"  # Same wheel across Python versions
        abi_tag = "none"  # Same wheeel across ABI versions (not a C-extension)
        # But we need to differentiate on the platform for the compiled adslib:
        plat_tag = sysconfig.get_platform().replace("-", "_").replace(".", "_")

        if plat_tag.startswith("linux_"):
            # But the basic Linux prefix is deprecated, use new scheme instead:
            plat_tag = "manylinux_2_24" + plat_tag[5:]

        # MacOS platform tags area already okay

        # We also keep Windows tags in place, instead of using `any`, to prevent an
        # obscure Linux platform to getting a wheel without adslib source

        return impl_tag, abi_tag, plat_tag


# noinspection PyTypeChecker
setup(
    cmdclass={
        "install": CustomInstallCommand,
        "bdist_wheel": CustomWheel,
    }
)

# Rely on `pyproject.toml` for all other info instead
