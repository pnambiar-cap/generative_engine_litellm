# setup.py
from setuptools import setup, find_packages

setup(
    name='generative_engine_litellm',
    version='0.1.0',
    description='A custom LLM implementation for LiteLLM',
    author='Pradeep Nambiar',
    author_email='pradeep.a.nambiar@capgemini.com',
    url='https://github.com/pnambiar-cap/generative_engine_litellm/',  # Optional
    packages=find_packages(),
    install_requires=[
        'litellm',
        'pyyaml',
        # Add other dependencies here
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
