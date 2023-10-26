from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '0.0.1'
DESCRIPTION = 'longevity genie Web UI'
LONG_DESCRIPTION = 'longevity genie Web UI'

# Setting up
setup(
    name="genie",
    version=VERSION,
    author="antonkulaga (Anton Kulaga)",
    author_email="<antonkulaga@gmail.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=['pyfunctional', 'pycomfort', 'more-itertools', 'click', 'python-dotenv', 'tiktoken',
                      'langchain', 'openai', 'Deprecated', 'loguru', 'fastembed',
                      'qdrant-client', 'indexpaper', 'sentence_transformers', 'datasets', 'polars', 'beartype'],
    keywords=['python', 'utils', 'files', 'papers', 'download', 'index', 'vector databases', "python-Levenshtein", "longdata", "thefuzz"],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
