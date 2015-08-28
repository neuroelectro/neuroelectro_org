import os

old_file = 'neuroelectro/fixtures/validated_data.json'
tmp_file = 'neuroelectro/fixtures/tmp.json'

import re
with open(old_file)  as f:
    with open(tmp_file, 'w+') as fw:
        for l in f.readlines():
            if "password" in l:
                new_line = re.sub('".+",', '"password": "",', l)
                fw.write(new_line)
            else:
                fw.write(l)
os.rename(tmp_file, old_file)
