'''
为整个工程提供统一的绝对路径
'''

import os

def get_project_root():
    '''
    获取工程根目录
    '''
    #当前文件绝对路劲
    current_file = os.path.abspath(__file__)
    #获取工程根目录  (dirname是文件夹所在路径 )
    current_dir = os.path.dirname(current_file)

    #返回项目根目录
    project_root = os.path.dirname(current_dir)

    return project_root

def get_abs_path(relative_path : str) -> str:
    project_root = get_project_root()

    #将两个路径拼接
    return os.path.join(project_root, relative_path)

if __name__ == '__main__':
    print(get_abs_path("config/config.text"))