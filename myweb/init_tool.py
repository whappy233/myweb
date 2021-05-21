import os
import glob
import shutil




base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def run_commands(account='891953720'):
    os.chdir(base_dir)
    os.system('python3 manage.py makemigrations')
    os.system('python3 manage.py migrate')
    os.system(f'python3 manage.py createsuperuser --username {account} --email {account}@abc.com')
    print(f'创建账户: {account} 邮箱: {account}@abc.com')

def clean():
    i = input('警告:确认执行清理操作(y/n)? 这将会删除一些文件和文件夹.\n')
    ipt = i.lower()
    if ipt in ['y', 'n']:
        if ipt == 'n':
            print('操作取消!')
            return
    else:
        print('操作取消!')
        return

    shutil.rmtree(os.path.join(base_dir, '.vscode') , True)
    shutil.rmtree(os.path.join(base_dir, 'log') , True)
    for i in glob.glob(os.path.join(base_dir, 'media/*/')):
        shutil.rmtree(i, True)
    try:
        os.remove(os.path.join(base_dir, 'db.sqlite3'))
    except:
        pass

    for i in glob.glob(base_dir+'/*/'):
        for root, dirnames, filenames in os.walk(i):
            for dirname in dirnames:
                if '__pycache__' in dirname:
                    p = os.path.join(root, dirname)
                    shutil.rmtree(p, True)
        for root, dirnames, filenames in os.walk(i):
            for filename in filenames:
                if '_initial.py' in filename:
                    os.remove(os.path.join(root, filename))

    print('============= 清理完成 =============')
    ii = input('需要执行migrate吗?(y/n)\n')
    iipt = ii.lower()
    if iipt == 'y':
        run_commands()
    print('完成!')

clean()



