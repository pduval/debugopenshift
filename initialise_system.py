#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
import os

app_name = os.environ["ULYSSES_APP_NAME"]
solr_base = os.environ["ULYSSES_SOLR_BASE"]

db_server = os.environ["ULYSSES_DB_HOST"]
db_password = os.environ["ULYSSES_DB_MASTER_PASSWORD"]
db_user = os.environ["ULYSSES_DB_MASTER_USER"]

ulysses_db_password = os.environ["ULYSSES_DB_PASSWORD"]


#First ensure Solr Core exists
core_exists = False
try:
    r = requests.get(
        "{0}/admin/cores".format(solr_base),
        data={
               "core": app_name,
               "action": "STATUS",
               "wt": "json"
        })
    core_exists = r.json()["status"][app_name]
except:
    core_exists = False
if not core_exists:
    requests.get("{0}/admin/cores".format(solr_base), data={
        "name": app_name,
        "configSet": "ulysses",
        "action": "CREATE",
        "instanceDir": "mycores/{0}".format(app_name)
    })

#we have solr.
#Now make sure we have a database
from psycopg2 import connect
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
has_db = False
try:
    user_con = connect(user = app_name, host = db_server, password = ulysses_db_password, database=app_name)
    user_con.close()
    has_db = True
except:
    has_db = False
if not has_db:
    con = connect(user=db_user, host = db_server, password=db_password, database="uly_template")
    con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

    cur = con.cursor()
    cur.execute("CREATE USER {0} WITH PASSWORD '{1}'".format(app_name, ulysses_db_password))
    cur.close()

    cur = con.cursor()
    cur.execute("GRANT {0} to {1}".format(app_name, db_user))
    cur.close()

    cur = con.cursor()
    cur.execute("CREATE DATABASE {0} WITH TEMPLATE uly_template OWNER {0}".format(app_name))
    cur.close()

    con.close()

#Finally make sure nginx knows about us
#Not done yet...

#And now migrate the application
from crimson.utils.script_utils import get_ulysses_backend_app
app = get_ulysses_backend_app("ulysses")
from crimson.core_modules.datamodel import Module
Module.current_instance.apply_migrations(partial=False)
