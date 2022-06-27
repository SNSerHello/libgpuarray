在Linux下制作wheel文件
  $ mkdir build
  $ cd build
  $ cmake ..
  $ make -j
  $ sudo make install
  $ cd ..
  $ python3 setup.py bdist_wheel --universal

libgpuarray的默认安装信息
Install the project...
-- Install configuration: ""
-- Installing: /usr/local/include/gpuarray/array.h
-- Installing: /usr/local/include/gpuarray/blas.h
-- Installing: /usr/local/include/gpuarray/collectives.h
-- Installing: /usr/local/include/gpuarray/buffer.h
-- Installing: /usr/local/include/gpuarray/buffer_blas.h
-- Installing: /usr/local/include/gpuarray/buffer_collectives.h
-- Installing: /usr/local/include/gpuarray/abi_version.h
-- Installing: /usr/local/include/gpuarray/config.h
-- Installing: /usr/local/include/gpuarray/elemwise.h
-- Installing: /usr/local/include/gpuarray/error.h
-- Installing: /usr/local/include/gpuarray/extension.h
-- Installing: /usr/local/include/gpuarray/ext_cuda.h
-- Installing: /usr/local/include/gpuarray/kernel.h
-- Installing: /usr/local/include/gpuarray/types.h
-- Installing: /usr/local/include/gpuarray/util.h
-- Installing: /usr/local/lib/libgpuarray.so.3.0
-- Installing: /usr/local/lib/libgpuarray.so.3
-- Installing: /usr/local/lib/libgpuarray.so
-- Installing: /usr/local/lib/libgpuarray-static.a

在Windows下制作wheel文件
  $ mkdir build
  $ cd build
  $ cmake -G "Visual Studio 15 2017 Win64" -DCMAKE_INSTALL_PREFIX=..\lib ..
  $ msbuild /maxcpucount:4 /p:Configuration=Release /p:PreferredToolArchitecture=x64 ALL_BUILD.vcxproj
  $ msbuild /p:Configuration=Release INSTALL.vcxproj
  $ cd ..
  $ python3 setup.py bdist_wheel --universal
