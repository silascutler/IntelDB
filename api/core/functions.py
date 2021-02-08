#!/usr/bin/env python3
''' IntelDB
 Autor: Silas Cutler (silas@BlackLab.io)


'''
# pylint: disable=invalid-name
# pylint: disable=R0902
# pylint: disable=R0913

import re
import json
import time
import datetime

import bson
import pymongo
from bson.json_util import dumps

from core import objects


def r_search(rtype, query, regex=False, raw=False):
    """ Search """
    print('r_search start')
    result = {}    
    try:
        db_handle = objects.mongo_store(rtype)
    except Exception as e:
        print("r_search db error: %s" % e)
        return -1, "Failed on mongodb connect", {}
    if raw is not False:
        try:
            jquery = json.loads(query.replace("'", '"'))
        except Exception as e:
            print("r_search json error: %s" % e)
            db_handle.shutdown() 
            return -1, "Failed on Query Conversion", {}
    else:
        jquery = query
        
    if regex:
        print("r_search - regex")
        nquery = jquery
        jquery = {}
        for key, value in nquery.items():
            jquery[key] = {'$regex': re.compile(value)}

    if "_id" in jquery.keys():
        jquery['_id'] = bson.ObjectId(oid=str(jquery['_id']))

    try:
        result = db_handle.search(jquery).sort([('$natural', pymongo.DESCENDING)])
    except Exception as error:
        print("r_search db_Search error: %s" % error)
        db_handle.shutdown()
        return -1, "Failed on search", {}
    db_handle.shutdown()

    if raw:
        return result

    return 0, "", json.loads(dumps(result))

def link_search(rid):
    '''Find indicator links.'''

    db_handle = objects.link_store()
    status, results = db_handle.find_links(rid)
    db_handle.finish()

    if status:
        return True, results
    if isinstance(results, str):
        return False, "Error: %s" % results

    return True, []

def setup_resolve_list(host_list):
    '''Return a validated list of domains due for resolution'''

    rlist = {}
    name = ""
    rlist.clear()
    regex = "^[A-Za-z0-9]([A-Za-z0-9-\.]+)*\.[A-Za-z0-9-]+"

    for host in host_list:
        if 'name' in host:
            qry = re.search(regex, host['name'])
            if qry:
                name = host['name']
                rlist[host['name']] = {'name': host['name'], 'id': str(host['_id'])}
    return rlist


def get_domains_for_resolution():
    '''Return a list of domains due for resolution'''
    try:
            domain_handle = objects.mongo_store('domain')
    except Exception as error:
            print("Get Pending resolutions error: %s " % error)
            return -1, "Failed on mongodb connect", {}

    rlist = setup_resolve_list(domain_handle.collection.find(
                {"$and": [
                    {"$or": [
                        {"details": {"$nin": ["NOACTION"]}},
                        {"details": {"NOACTION": 0}}]},
                    {"$or": [
                        {"last_resolved": {"$lt": int(time.time() - 86400)}},
                        {"last_resolved": {"$exists": False}}]},
                    {"DISABLED": {'$ne': True}}
                ]}).limit(20))

    for indicatorid in rlist:
        domain_handle.merge_ioc(
            {"_id": bson.ObjectId(oid=rlist[indicatorid]['id'])}, 
            {"$set": {"last_resolved": int(time.time())}}
            )
    return rlist

def get_active_ip_list():
    '''Return a list of IP addresses recently resolved'''
    host_list = []

    try:
        link_store = objects.link_store()
        ip_handle = objects.mongo_store('ipaddress')
    except Exception as error:
        print("get active IP errro" %  error)
        return -1, "Failed on db setup", {}

    try:
        active_ioc = link_store.get_active_new()
        for r_ioc in active_ioc:
            if r_ioc[0] == 'ipaddress':
                rname = ip_handle.lookup_name(bson.ObjectId(oid=str(r_ioc[1])))
                host_list.append(rname)
                if r_ioc[2] == 'ipaddress':
                        rname = ip_handle.lookup_name(bson.ObjectId(oid=str(r_ioc[3])))
                        host_list.append(rname)


    except Exception as error:
        print("get active ip error listing: %s" % error)
        link_store.finish()
        ip_handle.shutdown()
        return -1, "Failed initial pull", {}

    link_store.finish()
    ip_handle.shutdown()
    return host_list

def get_new_hosts(rtype):
    '''Return a list of new domains'''
    try:
        ip_handle = objects.mongo_store(rtype)
        rlist = ip_handle.collection.find({'added':  {"$gt": int(time.time()) - (86400 * 7)}})
        ip_handle.shutdown()
        return rlist
    except Exception as error:
        print("get new hosts error" % error)
        return -1, "Failed on mongodb connect", {}

    rlist = []
    return rlist



#def submit_domains_from_resolution(domain_list):
#    global POOL_SIZE
#    try:
#        pool = Pool(POOL_SIZE)
#    except Exception as e:
#        print(e)
#        return -1, "Failed to create Pool", {}
#
#        try:
#                domain_handle = objects.mongo_store('domain')
#        rlink = objects.link_store()
#        except Exception as e:
#                print(e)
#        rlink.finish()
#                return -1, "Failed on mongodb or mysql connect", {}
#
#    try:
#        t_host_list = domain_list.encode('ascii','ignore')
#        rlist = json.loads(domain_list)
#    except Exception as e:
#        return -1, "Failed to load update %s" % e, {}
#
#    with gevent.Timeout(36000, False):
#            for x in rlist:
#            pool.spawn(db_handle_resolution, rlist[x])
#        pool.join()
#    try:
#        pool.close()
#    except Exception as e:
#        print(dir(pool))
#        print("Exception Clearing / Flushing Pool: %s" % e)
#    rlink.finish()
#    return 0, "", {}

def submit_domains_from_resolution(domain_list):
    '''Submit a set of domains from external resolution'''
    try:
        # setup DB Handles
        link_store = objects.link_store()
        ioc_store = objects.mongo_store('ipaddress')
    except Exception as error:
        return -1, "Failed to setup db links: %s" % error, {}

    try:
            t_host_list = domain_list.encode('ascii', 'ignore')
            blist = json.loads(domain_list)
    except Exception as error:
            return -1, "Failed to load update %s" % error, {}

    try:
        for rlist in blist:
            print("Res: %s " % rlist)
            if "address" in json.dumps(rlist):
                print("Submitting")
                ioc = objects.indicator(
                    'ipaddress', rlist['address'], 
                    "Identifed by resolution", 
                    db_handle=ioc_store)
                ioc.store()
    
                print("Linking...")
                rlink = objects.link(
                    rlist['id'], 'domain', 
                    "Resolution", 
                    ioc.rid, 'ipaddress', 
                    db_handle=link_store)
                rlink.log(True)

        print("Finished submitting res")
        try:
            link_store.shutdown()
            ioc_store.shutdown()
        except Exception as error:
            print("Problem killing temp DB handles")
    
    except Exception as error:
            print("Exception Submitting: %s" % error)
    return 0, "", {}




def submit_domains_from_resolution_one(domain_list):
    '''Submit a single resoltution'''
    try:
        t_host_list = domain_list.encode('ascii', 'ignore')
        rlist = json.loads(domain_list)
    except Exception as error:
            return -1, "Failed to load update %s" % error, {}
    try:
        if "address" in rlist:
            ioc = objects.indicator('ipaddress', rlist['address'], "Identifed by resolution")
            ioc.store()

            rlink = objects.link(rlist['id'], 'domain', "Resolution", ioc.rid, 'ipaddress')
            rlink.log()
            rlink.finish()

    except Exception as error:
        print("Exception Submitting: %s" % error)

    return 0, "", {}


def new_handler(r_id, rstype, name):
    '''Add Indicator to db'''
    if r_id == -1:
        print("Adding new IOC")
        ioc = objects.indicator(rstype, name, "Audo add from linkage")
        ioc.store()
        return str(ioc.rid)
    return str(r_id)

def get_recent_additions(formatter='\n'):
    '''Return recently added domains'''
    recent = []
    try:
        domain_handle = objects.mongo_store('domain')
    except Exception as error:
        print("Get recent additions error: %s" % error)
        return -1, "Failed on mongodb connect", {}

    rlist = domain_handle.collection.find({"$and": [
                {"name": {"$exists": True}}, 
                {"added": {"$exists": True}}, 
                {"note": {"$exists": True}}, 
                {"details": {"$exists": True}}, 
                {"$or": [
                    {"DISABLED": {"$exists": False}},
                    {"DISABLED": False},
                ]}, ]}).sort([("added", -1)]).limit(10)

    for result in rlist:
        try:
            recent.append([
                result['name'], 
                datetime.datetime.fromtimestamp(int(result['added'])).strftime('%Y-%m-%d %H:%M:%S'), 
                formatter.join(result['note']), 
                json.dumps(result['details']), 
                bson.ObjectId(oid=str(result['_id'])) 
            ])

        except Exception as error:
            print("Get recent additons error 2: %s " % error)

    return recent

def wide_search(query):
    '''# Fix this to search types:'''
    results = []
    try:
        results.append(['domain', r_search('domain', {'note': query}, regex=True, raw=True)])
    except Exception as error:
        print("Wide search error: %s" %  error)

        try:
                results.append(['file', r_search('file', {'note': query}, regex=True, raw=True)])
        except Exception as error:
                print("wide search error append: %s" % error)

    return results
