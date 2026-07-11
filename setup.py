from setuptools import setup, find_packages

setup(
    name='DynoSure-slcanv1',
    version='0.4.4',
    packages=find_packages(),
    include_package_data=True,
    package_data={'slcanv1': ['*.dll']},
    author='Muksehbhai Patel',
    author_email='dynosure.india@gmail.com',
    description='Python wrapper for slcanv1.dll',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    zip_safe=False,
)
