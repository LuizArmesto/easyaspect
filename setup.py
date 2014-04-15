from setuptools import setup

setup(
    name='easyaspect',
    version='0.1.0',
    description='Easy Approach to AOP in Python',
    url='http://github.com/LuizArmesto/easyaspect',
    author='Luiz Armesto',
    author_email='luiz.armesto@gmail.com',
    license='MIT',
    packages=['easyaspect'],
    package_dir={'easyaspect': 'src/easyaspect'},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
    ],
    test_suite='test'
)
