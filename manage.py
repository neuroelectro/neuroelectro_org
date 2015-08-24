import os
import sys
from subprocess import call

def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "neuroelectro.settings")

    from django.core.management import execute_from_command_line
    
    if len(sys.argv)>=2 and sys.argv[1]=='sync':
        from django.conf import settings
        db_path = settings.DATABASES['default']['NAME']
        print("Deleting the old database...")
        if '.neuroelectro' in db_path:
            call(["rm %s" % db_path], shell=True)
        print("Synchronizing database schema...")
        call(["manage_neuroelectro syncdb --noinput"], shell=True)
        print("Downloading database data...")
        call(["curl -L -o ~/.neuroelectro/data.json https://www.googledrive.com/host/0B2pE3nzQxTzBckFVSFRqN1VDY1k"], shell=True)
        print("Adding data to the database...")
        call(["manage_neuroelectro loaddata ~/.neuroelectro/data.json"], shell=True)
        print("Run 'manage_neuroelectro shell' to interact with the data in a python interpreter'")
    else:
        execute_from_command_line(sys.argv)

if __name__ == "__main__":
    main()
