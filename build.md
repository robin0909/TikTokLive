### 删除老包
```shell
rm -rf build dist
```


### 打包
```shell
python3 setup.py sdist bdist_wheel
python setup.py install

# 安装 bdist_wheel
# python3 setup.py sdist bdist_wheel
```


### 上传
```shell
twine upload dist/*

# 安装 twine
# pip install twine
```


