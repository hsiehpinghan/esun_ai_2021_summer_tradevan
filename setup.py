from setuptools import find_packages, setup

setup(
    name='esun-ai-2021-summer-tradevan',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Pillow==8.2.0',
        'Flask==2.0.1',
        'Flask-Caching==1.10.1',
        'redis==3.5.3',
        'opencv-python-headless==4.5.2.52',
        'tensorflow==2.4.1',
    ],
)
