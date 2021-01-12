from pathlib import Path, PurePath
import os

# Path 支持链式调用

# /Users/tdesmtfa09/myweb
BASE_DIR1 = Path(__file__).resolve(strict=True).parent.parent  # 结果相同
BASE_DIR2 = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

BASE_DIR1 / 'static'  # 直接拼接路径 --> /Users/tdesmtfa09/myweb/static
BASE_DIR1.joinpath('static')

Path.cwd()  #  当前工作目录
Path.cwd().is_dir()  #  判断是否为目录

# 获取给定路径文件名及文件扩展名
fp = Path('/home/www/index.html')
name = fp.name # index.html  文件名(name)
step = fp.stem # index  文件名主体部分(stem)
suffix = fp.suffix # .html  文件后缀(suffix)

# 创建文件目录
# 对于创建文件目录，os.path提供了 mkdir 和 mkdirs 两个方法，一个只能用于创建一级目录，另一个支持逐级创建目录。
# pathlib简化为了 mkdir 一个方法，只需要在使用该方法时设置 parents , mode, exist_ok 参数即可。
# 如果希望逐级创建目录，需指定 parents=True.
# 如果希望指定在目标目录不存在时才创建文件夹，需设置 exist_ok=True
Path('/base/child').mkdir(parents=True, exist_ok=True)

# 查找指定文件夹文件
# 打印出指定目录所有的python文件名
p=Path(r'C:\Users\Desktop\django')
PY=[x for x in p.glob('*.py')]
print(PY)


# os模块和pathlib模块方法对应一览表
os.path.abspath     	Path.resolve    # 设置路径为绝对路径，解析路径上的所有符号链接并对其进行规范化（例如，在Windows下将斜杠转换为反斜杠）
os.chmod	            Path.chmod      # 更改路径的权限
os.mkdir	            Path.mkdir      # 在此给定路径下创建一个新目录
os.rename	            Path.rename     # 将此路径重命名为给定路径
os.replace	            Path.replace    # 将此路径重命名为给定路径，破坏现有目标（如果存在）
os.rmdir	            Path.rmdir      # 删除该目录, 该目录必须为空
os.remove, os.unlink	Path.unlink     # 删除此文件或链接。 如果路径是目录，请改用rmdir（）
os.getcwd	            Path.cwd        # 返回指向当前工作目录的路径（由os.getcwd（）返回）
os.path.exists	        Path.exists     # 路径是否存在
os.path.expanduser	    Path.home       # 返回指向用户主目录的路径（由os.path.expanduser（'〜'）返回）
os.path.isdir	        Path.is_dir     # 此路径是否为目录
os.path.isfile	        Path.is_file    # 此路径是否为文件
os.path.islink	        Path.is_symlink # 此路径是否为符号链接
os.stat	                Path.stat       # 像os.stat（）一样，在此路径上返回stat（）系统调用的结果
                        Path.owner      # 返回文件所有者的登录名
                        Path.group      # 返回文件名的组名
os.path.samefile	    Path.samefile   # 返回other_path是否与此文件相同（由os.path.samefile（）返回）
os.path.isabs	        PurePath.is_absolute    # 如果路径是绝对路径（既有根又有驱动器），则为true
os.path.join	        PurePath.joinpath       # 将此路径与一个或多个参数组合，然后返回代表子路径（如果所有参数均为相对路径）或完全不同的路径（如果其中一个参数已锚定）的新路径
os.path.basename	    PurePath.name           # 文件名(name)
os.path.dirname	        PurePath.parent         # 路径的逻辑父级
os.path.splitext	    PurePath.suffix         # 文件后缀(suffix)
                        PurePath.stem           # 文件名主体部分(stem)