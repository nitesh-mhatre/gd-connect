from setuptools import setup, find_packages

setup(
    name="gd-connect",
    version="0.1.0",
    description="Python module & CLI to connect Google Drive for read/write operations",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Nitesh Mhatre",
    author_email="n.mhatre90@gmail.com",
    url="https://github.com/nitesh-mhatre/gd-connect",
    packages=find_packages(),
    install_requires=[
        "google-auth>=2.0.0",
        "google-auth-oauthlib>=0.4.6",
        "google-auth-httplib2>=0.1.0",
        "google-api-python-client>=2.0.0",
        "tqdm>=4.60.0",
    ],
    entry_points={
        "console_scripts": [
            "gd-connect=gd_connect.cli:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
        "Topic :: Utilities",
        "Topic :: Internet",
    ],
    python_requires=">=3.7",
)
