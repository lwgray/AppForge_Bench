apk_path = 'compiler/output_v2.2.2/vv0811_round0/Chess_Clock/app/build/outputs/apk/debug/app-debug.apk'
folder  = 'gemini2.5pro'
import os, shutil
for test_id in range(1,6):
    cmd = f''' python evaluate_app.py --task Chess_Clock --test functional{test_id}screenshot --package-name 0\
        --apk-path {apk_path}  '''
    os.system(cmd)
    shutil.copytree('screenshots/',f'{folder}/screenshots{test_id}')
