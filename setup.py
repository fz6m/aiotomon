from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='aiotomon',
    version='1.3',
    url='https://github.com/fz6m/aiotomon',
    license='MIT License',
    author='fz6m',
    author_email='fz6meng@gmail.com',
    description='A tomon bot asynchronous python basic development sdk',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(include=('aiotomon', 'aiotomon.*')),
    package_data={
        '': ['*.pyi'],
    },
    install_requires=[
        'aiofiles >= 0.4.0', 
        'aiohttp >= 3.6.2', 
        'websockets >= 8.1'
        ],
    extras_require={
        'all': ['ujson'],
    },
    python_requires='>=3.7',
    platforms='any',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Framework :: Robot Framework'
    ],
)
