import os
from setuptools import setup
from setuptools import find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
        name="plywood",
        version="1.11.0",
        author="Colin T.A. Gray",
        author_email="colinta@gmail.com",
        url="https://github.com/colinta/plywood",
        install_requires=['chomsky >= 1.0.2'],

        entry_points={
            'console_scripts': [
                'ply = plywood.__main__:run'
            ]
        },

        description="A template language grammar inspired by the Python code aesthetic",
        long_description=read("README.rst"),

        packages=find_packages(),
        keywords="plywood template language",
        platforms="any",
        license="BSD",
        classifiers=[
            "Programming Language :: Python",
            "Development Status :: 1 - Planning",
            'Environment :: Console',
            "License :: OSI Approved :: BSD License",
            "Operating System :: OS Independent",

            'Intended Audience :: End Users/Desktop',
            'Intended Audience :: Developers',

            "Topic :: Text Processing",
            "Topic :: Text Processing :: General",
            "Topic :: Text Processing :: Markup",
            'Topic :: Internet',
        ],
    )
