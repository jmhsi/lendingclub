import os
#import sys

'''
Setup all relevant paths
'''

fpath = os.path.realpath(__file__)
src_dir = os.path.dirname(fpath)
prj_dir = os.path.dirname(src_dir)
data_dir = os.path.join(prj_dir, 'data') 
csv_dir = os.path.join(data_dir, 'csvs')
raw_dl_dir = os.path.join(csv_dir, 'raw_zipped_csvs')
arch_dir = os.path.join(csv_dir, 'archived_csvs')
wrk_csv_dir = os.path.join(csv_dir, '02_working_csvs')
modeling_dir = os.path.join(prj_dir, 'modeling')
model_dir = os.path.join(modeling_dir, 'models')

# print(srcdir)
# print(prjdir)
# print(datadir)
