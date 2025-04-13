from setuptools import setup, find_packages

setup(
    name="ecloud-web",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.68.1",
        "uvicorn>=0.15.0",
        "python-multipart>=0.0.5",
        "pydantic>=1.8.2",
        "requests>=2.26.0",
        "playwright>=1.30.0",
    ],
)