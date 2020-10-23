import os

os.system('aerich migrate --name drop_column')
os.system('aerich upgrade')