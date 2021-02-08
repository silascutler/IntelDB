#!/usr/bin/env python3
"""Stores Objects used by API"""
# -*- coding: utf-8 -*-
''' IntelDB
 Autor: Silas Cutler (silas@BlackLab.io)


'''
# pylint: disable=invalid-name
# pylint: disable=R0902
# pylint: disable=R0913



import sys
import time
import base64
import json
import pymongo
import MySQLdb

from core import functions

class link_store():
    """Class for handline links between obects"""
    def __init__(self):
        print("Creating Link DB Handle")
        self.link_db = MySQLdb.connect(
            host="127.0.0.1", 
            user="root", 
            passwd="", 
            db="intel_link_db")

        self.link_db.autocommit(True)

    def shutdown(self):
        """Close database connection"""
        try:
            self.link_db.close()
            return True
        except Exception as e:
            pass
            return False

    def finish(self):
        """Close database connection"""
        return self.shutdown()

    def __del__(self):
        try:
            self.shutdown()
        except Exception as e:
                pass

    def add_link(self, values):
        """Add object link to database"""
        sql_insert = """INSERT INTO links 
            (stype, sid, note, dtype, did, added, last_valid) 
            VALUES ( %s, %s, %s, %s, %s, unix_timestamp(now()), unix_timestamp(now()) )"""

        try:
            db_cursor = self.link_db.cursor()
            db_cursor.execute(sql_insert, (values))
            return True, ""
        except Exception as e:
            return False, e

    def check_new(self, values):
        """Check if objects are already linked"""
        sql_insert = """select count(stype) from links 
            WHERE ( stype=%s and sid=%s and dtype=%s and did=%s )"""
        try:
            db_cursor = self.link_db.cursor()
            db_cursor.execute(
                sql_insert, 
                (values[0], values[1], values[3], values[4])
                )
            res = db_cursor.fetchone() 
            if res:
                if res[0] == 0:
                    return True, ""
                    
        except Exception as e:
                return False, e
        return False, ""

    def get_active_new(self, values={}):
        """Fetch links marked active"""

        sql_insert = """select stype, sid, dtype, did from links 
            WHERE ( last_valid > unix_timestamp(now()) - 604800 )"""
        try:
            db_cursor = self.link_db.cursor()
            db_cursor.execute(sql_insert, (values))
            res = db_cursor.fetchall()
            return res
        except Exception as e:
            print("Link Store - Get Active New error: %s" % e)
            return False, e



    def update_link(self, values):
        """Update link to mark valid"""

        sql_insert = """UPDATE links SET last_valid = unix_timestamp(now()) 
            WHERE ( stype=%s and sid=%s and note=%s and dtype=%s and did=%s )"""
        try:
            db_cursor = self.link_db.cursor()
            db_cursor.execute(sql_insert, (values))
            return True, ""
        except Exception as e:
            return False, e

    def find_links(self, rid):
        """Find links to object"""

        sql_insert = """SELECT stype, sid, note, dtype, did FROM links 
            WHERE ( did = %s or sid = %s)"""
        try:
            db_cursor = self.link_db.cursor()
            db_cursor.execute(sql_insert, ([rid, rid]))
            res = db_cursor.fetchall()
            if res:
                if res[0] != 0:
                    return True, res
            return False, []
        except Exception as e:
            print("Link Store ; Find Links Error: %s " % e)
            return False, e        


class mongo_store():
    """Class for primary datastore"""

    def __init__(self, rtype=""):
        print("Creating Indicator DB Handle")
        self.dbclient = pymongo.MongoClient("127.0.0.1")
        self.db = self.dbclient['inteldb']
        self.collection = self.db[rtype]

    def shutdown(self):
        """Close DB connection"""
        self.dbclient.close()

    def change_type(self, ntype):
        """Change type of object"""
        self.rtype = ntype

    def store_ioc(self, data):
        """Save indicator"""
        return self.collection.insert(data)

    def merge_ioc(self, index, data):
        """marge two indicators"""
        return self.collection.update(index, data, upsert=True)

    def search(self, query):
        """Search"""
        return self.collection.find(query) 

    def lookup_id(self, query):
        """Return ObjectID of object by name"""
        search = self.collection.find({'name': query})

        if search.count() == 0:
            return -1
        return search[0]['_id']

    def lookup_name(self, query):
        """Lookup object name by ObjectID"""
        search = self.collection.find({'_id': query})
        if search.count() == 0:
            return -1
        return search[0]['name']

    def __del__(self):
        try:
            self.shutdown()
        except Exception as e:
            pass


class indicator():
    """Object for indicators"""
    def __init__(
            self, 
            rtype, 
            rioc, 
            rnote="", 
            rdetails={}, 
            timestamp=int(time.time()), 
            db_handle=None):
        self.rtype = rtype
        self.name = rioc.lower()
        self.note = [rnote]
        self.details = rdetails
        self.added = timestamp

        if db_handle:
            self.localdb = False
            self.db = db_handle
        else:
            self.localdb = True
            self.db = mongo_store(self.rtype)

    def print_short(self):
        """Print Type + Name of indicator"""
        print("[%s] %s" % (self.rtype, self.name))

    def rdict(self):
        """retrun dict struct of values"""
        return { 
            'id' : str(self.rid), 
            'type' : self.rtype, 
            'name': self.name, 
            'note': self.note, 
            'added': self.added, 
            'details': self.details}

    def store(self):
        """Save indicator"""
        message = []
        search = self.db.search({'name': self.name})

        if search.count() == 0:
            self.rid = self.db.store_ioc({
                'name': self.name, 
                'note': self.note, 
                'added': self.added, 
                'details': self.details})
            return True
    
        message.append("Merging")
        self.rid = search[0]["_id"]

        if (self.details.items() == [] and 'details' in search[0]):
            self.details = dict(search[0]['details'].items())

        elif ('details' not in search[0] and self.details.items() != []):
            self.details = dict(self.details.items())

        elif ('details' in search[0] and self.details.items() != []):
# https://stackoverflow.com/questions/38987/how-to-merge-two-dictionaries-in-a-single-expression
            ndetails = search[0]['details'].copy()
            self.details.update(ndetails)
#### Caused Original details to overwrite new details

#                self.details = search[0]['details'].copy()
#                self.details.update(search[0]['details'])

#### Unknown failure 
#                        for key, value in search[0]['details'].iteritems():
#                                if key in self.details.keys():
##                        print("%s - %s" % ( type(value), type([]) ))
#
#                                        if type(value) == type([]):
#                            t_add_det = []
#                            for tmp in value:
#                                if tmp in self.details[key]:
#                                    pass
#                                else:
#                                    t_add_det.append( tmp )
#                                                self.details[key] += t_add_det
#
#                                        if type(value) == type('string'):
#                            if value != details[key]:
#                                                    self.details[key] = [ details[key], value ]
#                                else:
#                                        self.details[key] = value

        print(self.details)
        self.note = list(set(list(self.note + search[0]['note'])))
        self.db.merge_ioc({"_id": self.rid}, {"$set": {"details":self.details}})
        self.db.merge_ioc({"_id": self.rid}, {"$set": {"note":self.note}})

        if self.localdb:
            self.db.shutdown()

        return message

    def __del__(self):
        if self.localdb:
            try:
                self.db.shutdown()
            except Exception as e:
                pass



class link():
    """Object for Links"""
    def __init__(
            self, 
            rsource, 
            rstype, 
            rnote, 
            rdest, 
            rdtype, 
            auto=False, 
            db_handle=None):
        self.stype = rstype
        self.dtype = rdtype

        if auto:
            self.sm_db = mongo_store(self.stype)
            t_sid = self.sm_db.lookup_id(rsource)
            self.source = functions.new_handler(t_sid, self.stype, rsource)

            self.dm_db = mongo_store(self.dtype)
            t_did = self.dm_db.lookup_id(rdest)
            self.dest = functions.new_handler(t_did, self.dtype, rdest)
        else:
            self.source = rsource
            self.dest = rdest

        self.note = rnote
        if db_handle:
            self.localdb = False
            self.db = db_handle
        else:
            self.localdb = True
            self.db = link_store()        
            
    def finish(self):
        """Call db.shutdown"""
        if self.localdb:
            self.db.shutdown()

    def log(self, noupdate=False):
        """Store link"""
        values = [
            str(self.stype), 
            str(self.source), 
            str(self.note), 
            str(self.dtype), 
            str(self.dest)
            ]
        ncode, nmessage = self.db.check_new(values)
        if ncode:
            ecode, message = self.db.add_link(values)
            if ecode:
                return True, ""
            return False, "Failed to Add to DB.  Error: %s" % message

        if noupdate:
            return True, ""

        necode, message = self.db.update_link(values)
        if necode:
            return True, ""  
        return False, "Failed to Update DB.  Error: %s" % message
        

    def __del__(self):
        if self.localdb:
            try:
                self.db.shutdown()
            except Exception as e:
                pass
            try:
                self.dm_db.shutdown()
            except Exception as e:
                pass
            try:
                self.sm_db.shutdown()
            except Exception as e:
                pass
