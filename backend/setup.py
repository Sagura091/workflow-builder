from setuptools import setup, find_packages

setup(
    name="workflow-builder",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        "networkx",
        "pydantic",
    ],
    python_requires=">=3.8",
)
