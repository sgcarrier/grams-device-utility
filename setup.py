from setuptools import setup, find_packages

setup(  name='grams-device-utility',
        version='0.1',
        description='Toolkit for device comm',
        long_description='',
        classifiers=[
        'Programming Language :: Python :: 3',
        ],
        author='Simon Carrier',
        author_email='simon.g.carrier@usherbrooke.ca',
        packages=find_packages(),
        install_requires=[
            'pip',
            'python-periphery',
            'setuptools',
            'smbus',
            'spidev'
        ],
        include_package_data=True,
        zip_safe=False)
