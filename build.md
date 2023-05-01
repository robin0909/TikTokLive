### 删除老包
```shell
rm -rf build dist
```


### 打包
```shell
python setup.py install
```


### 上传
```shell
twine upload dist/*

# 安装 twine
pip install twine
```


