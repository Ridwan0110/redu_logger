from setuptools import setup, find_packages

setup(
    name="redu_logger",
    version="1.0.5",
    author="Ridwan Hossain Abid",
    description="A Python module to log data in files locally or remotely for any application or script.",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    include_package_data=True,
    install_requires=['requests>=2.32.3,<3.0.0'],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
