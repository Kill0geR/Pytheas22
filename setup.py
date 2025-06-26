from setuptools import setup, find_packages

classifiers = [
    'Development Status :: 6 - Mature',
    'Intended Audience :: Education',
    'Operating System :: Microsoft :: Windows :: Windows 10',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3'
]

setup(
    name='Pytheas22',
    version='0.1.0',
    description='Pytheas22 is a Port Scanner which scans IP-Cameras, internal networks and individual hosts. If the port 22 is open it will try to login to that host via bruteforce',
    long_description_content_type="text/markdown",
    long_description=open('README.md').read() + '\n\n' + open('CHANGELOG.txt').read(),
    url='',
    author='Fawaz Bashiru',
    author_email='fawazbashiru@gmail.com',
    license='MIT',
    classifiers=classifiers,
    keywords='portscanner',
    packages=find_packages(),
    install_requires=["BetterPrinting", "colorama", "paramiko"]
)