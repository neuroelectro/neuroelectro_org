import sys
import json
json_file = sys.argv[1]

# Open the data file.  
with open(json_file) as f:
    data = json.load(f)

# Remove passwords and email addresses.  
for entry in data:
    items = ('password','email')
    for item in items:
        if item in entry['fields']:
            entry['fields'][item] = ''

# Save the data file.  
with open(json_file,'w') as f:
    json.dump(data,f)

