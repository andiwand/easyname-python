from setuptools import setup

setup(
    name="ezname",
    version="0.0.1",
    url="https://github.com/andiwand/ezname",
    license="GNU Lesser General Public License",
    author="Andreas Stefl",
    install_requires=["selenium"],
    author_email="stefl.andreas@gmail.com",
    description="easyname domain api",
    long_description="",
    package_dir = {"": "src"},
    packages=["ezname"],
    platforms="any",
)
