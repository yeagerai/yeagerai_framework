from setuptools import setup, find_packages

setup(
    name="yeagerai-framework",
    version="0.0.1",
    description="A high-level Python framework for programming AI Teammates.",
    author="YeagerAI LLC",
    author_email="jm@yeager.ai",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "pyyaml",
        "pyyaml-include",
        "discord.py",
        "PyGithub",
    ],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Web Environment",
        "Framework :: YeagerAI",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
