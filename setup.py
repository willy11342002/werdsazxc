from setuptools import find_packages
from setuptools import setup

setup(
    url='https://github.com/willy11342002/werdsazxc',
    name='werdsazxc',
    version='1.9.1',
    description='Tools For Improve Effeciveness Of Project Develop',
    author='Werdsazxc',
    author_email='willy11342002@gmail.com',
    # 自動抓取此專案擁有的套件包
    packages=find_packages(),
    # 靜態文件
    data_files=[
        # (目錄, 檔案名)
        # ('', ['*.yaml']),
    ],
    # 依賴的套件
    install_requires=[
        'pycryptodome>=3.9.8',
        'PyYAML>=5.1.2'
    ]
)
