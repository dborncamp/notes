# Python Packaging

Python recently changed their packaging structure from what I am used to.
[https://packaging.python.org/en/latest/tutorials/packaging-projects](https://packaging.python.org/en/latest/tutorials/packaging-projects) shows a tutorial of the new structure.

## File Structure

The file structure has changed to have an `src` and `tests` directory.
The build is managed by the `pyproject.toml` file instead of a setup.py.

```txt
packaging_tutorial/
├── LICENSE
├── pyproject.toml
├── README.md
├── src/
│   └── example_package_YOUR_USERNAME_HERE/
│       ├── __init__.py
│       └── example.py
└── tests/
```

## Build Tools

There is a concept of "_backend_" and "_frontend_" build tools.
Frontend build tools are package managers like `pip` and `build` that manage the distribution of the project.
Backend tools are things that create a distribution to be managed.
This includes several [projects listed on the PyPA site](https://packaging.python.org/en/latest/key_projects).

### pyproject.toml

The distribution and build is managed by the `pyproject.toml` file.
It is the thing that tells the front end packages which backend tools that are used to create the distribution.

Key pieces of the file:

| Field | Description |
|-------|-------------|
| Requires | A list of packages needed to build the package |
| build-backend | Object that frontends will use to build |

The metadata is similar to wha we would find in a setup.py file:

| Field | Description |
|-------|-------------|
| name | Name of the project |
| version | Version number |
| authors | Who wrote it |
| description | One sentence summary of project|
| readme | detailed description of package |

## Packaging

With the pyproject.toml file, the build process is as simple as `python3 -m build`.
The command should generate two files in the `dist/` directory, one wheel and one tar.
The tar is a source distribution while the wheel is a built distribution.

### Uploading

Then use Twine for uploads.
Something similar to `python3 -m twine upload --repository testpypi dist/*` should upload things.
For Nexus upload instructions, see the [Nexus documentation](https://help.sonatype.com/repomanager3/nexus-repository-administration/formats/pypi-repositories).

### Downloading/Installing

After it is uploaded, you can download and install it from the repo.

`python3 -m pip install --index-url https://test.pypi.org/simple/ --no-deps example-package-YOUR-USERNAME-HERE`

## Extra Docs

[PIP 517](https://peps.python.org/pep-0517/) and [PIP 518](https://peps.python.org/pep-0518/) both refer to packaging and project builds.

## [pypirc](https://packaging.python.org/en/latest/specifications/pypirc/) file

The `pypirc` file defined the configuration that the package managers use for package indexes (repositories).
It is generally in `$HOME/.pypirc` but can be referenced anywhere using `--config-file <file>`.
The distutils format is:

```toml
[distutils]
index-servers =
    first-repository
    second-repository

[first-repository]
repository = <first-repository URL>
username = <first-repository username>
password = <first-repository password>

[second-repository]
repository = <second-repository URL>
username = <second-repository username>
password = <second-repository password>
```

It may not be a good idea to save username/password in this as it is plain text.
Tokens can be set with:

```toml
[pypi]
username = __token__
password = <PyPI token>
```

PyPA recommends using [keyring](https://pypi.org/project/keyring/) (which comes with Twine) to manage tokens:

```bash
keyring set https://upload.pypi.org/legacy/ __token__
keyring set https://test.pypi.org/legacy/ __token__
keyring set <private-repository URL> <private-repository username>
```
