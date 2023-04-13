from setuptools import setup, find_packages


def readme():
    with open('README.md', 'r') as f:
        return f.read()


setup(
    name='occe_api',
    version='1.0.0',
    author='surugh',
    author_email='surugh@gmail.com',
    description='Python wrapper for occe.io stock',
    long_description=readme(),
    long_description_content_type='text/markdown',
    url='http://occe.io/',
    packages=find_packages(),
    install_requires=['requests>=2.28.2'],
    classifiers=[
        'Programming Language :: Python :: 3.11',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent'
    ],
    keywords='occe python',
    project_urls={
        'Documentation': 'http://occe.io/info#api'
    },
    python_requires='>=3.10'
)
