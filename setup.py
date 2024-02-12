from setuptools import setup, find_packages

setup(
    name="file-check",
    version="1.0.0",
    description="Pre-commit hook for validating files",
    packages=find_packages(),
    install_requires=["GitPython", "packaging"],
    entry_points={
        "console_scripts": ["file-check = file_check.main:main"]
    },
)
