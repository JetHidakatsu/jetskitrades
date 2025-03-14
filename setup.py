from setuptools import setup, find_packages

setup(
    name="solana-bot",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "solders",
        "solana",
        "websockets",
        "pytest",
        "pytest-asyncio",
        "aiohttp",
        "python-dotenv",
    ],
)
