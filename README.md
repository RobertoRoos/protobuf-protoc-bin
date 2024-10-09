# Protobuf Protoc Bin

This Python package is an installer for [protobuf](https://protobuf.dev/)'s `protoc` compiler.

Use this package to install a specific version of `protoc` in your project, without having to figure out the installation externally.

This package is not maintained by or affiliated with the official protobuf group!

This repository does not host any binaries on itself.
Instead, the binaries are downloaded from the official protobuf Github during package built or during source installation.

## How to install

The package is hosted on PyPi at https://pypi.org/project/protobuf-protoc-bin.  
It can be installed via PIP as normal with:
```shell
pip install protobuf-protoc-bin
```

The wheels hosted on PyPi do contain a copy of the protoc releases.
You can also install this package directly from the Github source.
During an installation from source, `protoc` will be downloaded fresh from the official Protobuf releases:
```
pip install "git+https://github.com/RobertoRoos/protobuf-protoc-bin.git@<tag>"
```
(Replacing `<tag>` with a version like `v27.3`.)

## How to require

To require `protoc` only during a build script, include it in your `pyproject.toml` with:
```
[build-system]
requires = [..., "protobuf-protoc-bin==27.3"]
# ...
```

Or make it part of an additional install group in your regular environment (with the Poetry backend):
```
[tool.poetry.group.dev.dependencies]
protobuf-protoc-bin = "27.3"
```

## How to develop

The following concerns only contributors to this package.

### Adding a release

Each `protobuf-protoc-bin` release must correspond one-to-one to a [Protobuf release](https://github.com/protocolbuffers/protobuf/releases).

To trigger a new release, simply push a new tag to the tip of the main branch that matches the protobuf release, including the leading 'v'.
An example of a valid tag is `v27.3`.

This means multiple package releases are made from the same commit.
However, the reference that triggers the CI build will affect the version assigned by `setuptools_scm` and therefor the protobuf release that's being packaged.

### CI

A nightly workflow runs a script that looks for new Protoc releases and copies the tags into here, at the tip of the `main` branch.
So future releases should show up fully automatically.
