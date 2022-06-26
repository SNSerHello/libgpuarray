# 制作wheel文件

```
$ mkdir build
$ cd build
$ cmake ..
$ make -j
$ cd ..
$ python3 setup.py bdist_wheel --universal
```

The web site is at: http://deeplearning.net/software/libgpuarray/
