# Protobuf Protoc Exe

This Python package is a wrapper for [protobuf](https://protobuf.dev/)'s `protoc` compiler.

Use this package to install a specific version of `protoc` in your project.

This repository does not contain any binaries on itself!
Instead, the binaries are downloaded from the official protobuf Github upon installation,  you don't have to trust this package much.

## Registry

This package is currently not hosted on a registry like PyPi.
You can install it directly from Github though.

## How to use

To install it directly (pinning a specific version with `@...`):
```
pip install "git+https://github.com/RobertoRoos/protobuf-protoc-exe.git@v27.1"
```

To require `protoc` only during a build script, include it in your `pyproject.toml` with:
```
[build-system]
requires = ["poetry-core", "protobuf-protoc-exe @ git+https://github.com/RobertoRoos/protobuf-protoc-exe.git@v27.1"]
# ...
```

Or make it part of an additional install group in your regular environment:
```
[tool.poetry.group.dev.dependencies]
protobuf-protoc-exe = {git = "https://github.com/RobertoRoos/protobuf-protoc-exe.git", tag = "v27.1"}
```
