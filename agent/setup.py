from setuptools import setup, find_packages

setup(
    name="sentinel-agent",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "psutil>=5.9.8",
        "httpx>=0.27.0",
        "pyyaml>=6.0.1",
        "pydantic>=2.6.4",
        "watchdog>=4.0.0",
    ],
    entry_points={
        "console_scripts": [
            "sentinel-agent=sentinel_agent.main:main",
        ],
    },
)
