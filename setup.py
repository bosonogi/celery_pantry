import os

import setuptools

import celery_pantry


classifiers = """
    Development Status :: 3 - Alpha
    License :: OSI Approved :: MIT License
    Topic :: System :: Archiving
    Topic :: System :: Monitoring
    Topic :: System :: Distributed Computing
    Topic :: Software Development :: Object Brokering
    Intended Audience :: Developers
    Intended Audience :: System Administrators
    Programming Language :: Python :: 3.6
    Programming Language :: Python :: Implementation :: CPython
    Operating System :: OS Independent
"""

with open('README.rst') as f:
    README = f.read()


def find_package_data(package_path, *data_paths):
    """Recursively list files in a directory for use in package_data."""
    start_dir = os.path.abspath('.')
    os.chdir(package_path)
    data = []
    try:
        for data_path in data_paths:
            for root, dirs, files in os.walk(data_path):
                for file_name in files:
                    data.append(os.path.join(root, file_name))
    finally:
        os.chdir(start_dir)
    return data


setuptools.setup(
    name='celery_pantry',
    packages=setuptools.find_packages(exclude=('example_project',)),
    version=celery_pantry.__version__,
    description='Monitor and archive Celery task information',
    long_description=README,
    keywords='celery monitoring archiving',
    author='Toni Ruža',
    author_email='toni.ruza@gmail.com',
    url='https://github.com/bosonogi/celery_pantry',
    license='MIT',
    platforms=['any'],
    install_requires=[
        "celery>=4.0",
        "Django>=2.0",
        "coreapi>=2.3",
        "djangorestframework>=3.8",
        "psycopg2-binary~=2.7",
    ],
    package_data={
        'celery_pantry': find_package_data('celery_pantry', 'templates')
    },
    python_requires=">=3.6",
    classifiers=[s.strip() for s in classifiers.splitlines() if s],
    zip_safe=True,
)
