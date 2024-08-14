#!/usr/bin/env python
import subprocess
import sys
import re


def get_installed_python_versions():
    # Get the list of installed Python versions using pyenv
    result = subprocess.run(
        ["pyenv", "versions", "--bare"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    if result.returncode != 0:
        return []

    versions = result.stdout.strip().splitlines()
    return versions


def get_latest_installed_python_version(installed_versions):
    pattern = re.compile(r"^3\.\d+\.\d+$")
    valid_installed_versions = [v for v in installed_versions if pattern.match(v)]
    if valid_installed_versions:
        latest_installed_version = valid_installed_versions[-1]
        major_minor_version = ".".join(latest_installed_version.split(".")[:2])
        return major_minor_version
    else:
        return None


def update_pyproject_toml(python_version):
    with open("pyproject.toml", "r") as f:
        content = f.read()

    updated_content = re.sub(
        r'requires-python = ".*"', f'requires-python = "{python_version}"', content
    )

    with open("pyproject.toml", "w") as f:
        f.write(updated_content)


def main():
    # Check if Python version needs to be determined
    min_python = "{{cookiecutter.min_python}}"
    if not min_python.strip():
        installed_versions = get_installed_python_versions()
        latest_version = get_latest_installed_python_version(installed_versions)
        if latest_version:
            min_python = f">={latest_version}"
            print(f"Using latest installed Python version: {min_python}")
            update_pyproject_toml(min_python)
        else:
            print("Warning: Could not determine latest Python version. Using default.")
            min_python = ">=3.8"
            update_pyproject_toml(min_python)

    # run pdm use $(pyenv prefix {{cookiecutter.min_python}}/bin/python)
    subprocess.run(
        f"pdm use $(pyenv prefix {min_python})/bin/python", shell=True, check=True
    )
    print(f"Using Python version specified in pyproject.toml: {min_python}")

    print("Project setup complete!")


if __name__ == "__main__":
    main()
