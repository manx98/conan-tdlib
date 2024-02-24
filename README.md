# 如何安装
### 编译依赖
    编译过程中需要使用 gperf 代码生成工具,否者编译会报 Could NOT find gperf
    1. Linux 可以使用包管理工具安装
    2. Windows需要将下载程序配置到PATH环境变量中
### 克隆当前仓库
  ```text
  git clone https://github.com/manx98/conan-tdlib
  ```
### 执行安装
  ```shell
  cd conan-tdlib && conan create . --build=missing 
  ```
# 如何使用
conan 依赖名称：tdlib/1.8.25
