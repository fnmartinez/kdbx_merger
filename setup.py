from pathlib import Path
from setuptools import setup, find_namespace_packages


def __parse_pyproject_file(basepath: Path) -> dict:
    import tomli
    pyproject_file = basepath / 'pyproject.toml'
    with open(pyproject_file, 'rb') as fp:
        return tomli.load(fp)


def __set_value(raw_config: dict, pyproject_key: str, setuptools_name: str):
    raw_config[setuptools_name] = raw_config[pyproject_key]


def __normalize_contact_info(raw_config: dict, pyproject_key: str, contact_type: str):
    name_key = contact_type
    email_key = f'{contact_type}_email'
    base_names = raw_config.get(name_key, '') if name_key in raw_config else ''
    base_emails = raw_config.get(email_key, '')
    for contact_info in raw_config[pyproject_key]:
        name = contact_info.get('name', '')
        email = contact_info.get('email', '')
        if name and email:
            base_emails = ', '.join([base_emails, f'{name} <{email}>'])
        elif name:
            base_names = ', '.join([base_names, name])
        elif email:
            base_emails = ', '.join([base_emails, email])
    raw_config[name_key] = base_names
    raw_config[email_key] = base_emails


def __normalize_config(raw_config: dict) -> dict:
    normalizations = (
        ('readme', 'long_description', __set_value),
        ('authors', 'author', __normalize_contact_info),
        ('maintainers', 'maintainer', __normalize_contact_info),
        ('requires-python', 'python_requires', __set_value),
        ('urls', 'project_urls', __set_value),
        ('dependencies', 'install_requires', __set_value),
        ('optional-dependencies', 'extras_require', __set_value)
    )

    for pyproject_name, setuptools_name, action in normalizations:
        if pyproject_name in raw_config:
            action(raw_config, pyproject_name, setuptools_name)
            del raw_config[pyproject_name]


def __get_config_from_pyproject(basepath: Path) -> dict:
    pyproject_data = __parse_pyproject_file(basepath)
    project_metadata = pyproject_data['project']
    setuptools_config = dict()

    if 'tool' in pyproject_data and 'setuptools' in pyproject_data['tool']:
        setuptools_config = pyproject_data['tool']['setuptools']

    setuptools_config.update(project_metadata)
    __normalize_config(setuptools_config)
    return setuptools_config


here = Path(__file__).parent.resolve()

base_config = {
    'package_dir': {"": "src"},
    'packages': find_namespace_packages(where="src"),
    'entry_points': {
        'console_scripts': [
            'kdbx_merger = kdbx_merger.cli.entrypoints:cli'
        ]
    }
}

pyproject_config = __get_config_from_pyproject(here)

config = {**base_config, **pyproject_config}

setup(**config)
