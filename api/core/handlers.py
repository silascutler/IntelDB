#!/usr/bin/env python3
''' IntelDB
 Autor: Silas Cutler (silas@BlackLab.io)


'''
# pylint: disable=invalid-name
# pylint: disable=R0902
# pylint: disable=R0913
# pylint: disable=C0301
# pylint: disable=R1702


import datetime
import time
import json
import flask
import bson
from bson.json_util import dumps

from core import functions
from core import objects



def string_clean(rtext):
    """Function to remove non-ascii printable chars fast"""
    return ''.join(i for i in rtext if ord(i) < 128 and ord(i) > 32)


def ioc_add_bulk(rrequest):
    """Add multiple indicators of the same type"""

    if 'type' in rrequest:
        if 'indicator' in rrequest:
            if 'note' in rrequest:
                results = []
                if "," in rrequest['indicator']:
                    indicators = rrequest['indicator'].replace(" ", '').split(',')
                    for i in indicators:
                        trequest = {}
                        trequest["type"] = rrequest['type']
                        trequest["note"] = rrequest['note']
                        trequest["indicator"] = i
                        results.append(json.loads(ioc_add(trequest)))
                else:
                    results.append(json.loads(ioc_add(rrequest)))
                return json.dumps({"results": results})


    return json.dumps({})


def ioc_add(rrequest):
    """ Add IOC to datastore"""
    result = {}
    pdata = {}
    desc = ""
    valid = False
    if 'type' in rrequest:
        if 'indicator' in rrequest:
            if 'note' in rrequest:
                valid = True
                pdata['type'] = rrequest['type']
                print("[+] Add IOC: %s (Type: %s)\n    Notes:%s" % (rrequest['indicator'], rrequest['type'], rrequest['note']))

                # If the inbound indicaotr contains possibly non-ascii chars
                if string_clean(rrequest['indicator']) is not rrequest['indicator']:
                    print("[X] Dirty request indicator: %s (Pre: %s | Post: %s" % (string_clean(rrequest['indicator']), len(rrequest['indicator']), len(string_clean(rrequest['indicator']))))

                pdata['indicator'] = string_clean(rrequest['indicator'])
                pdata['note'] = rrequest['note']

                if len(pdata['indicator']) < 1:
                    valid = False

                if 'details' in rrequest:
                    pdata['details'] = json.loads(string_clean(string_clean(rrequest['details'].replace("'", '"'))))
                else:
                    pdata['details'] = {}
                if 'timestamp' in rrequest:
                    pdata['timestamp'] = rrequest['timestamp']
                else:
                    pdata['timestamp'] = int(time.time())



    if valid:
        print("[DEBUG] VALID")
        t_indicator = objects.indicator(pdata['type'], pdata['indicator'], pdata['note'], pdata['details'], pdata['timestamp'])
        result['errors'] = t_indicator.store()
        result['ecode'] = 0
        result['result'] = [t_indicator.rdict()]
        del t_indicator
    else:
        result['code'] = -1
        result['message'] = "Error: Missing field. Requred 'note', 'indicator' and 'note'"
        result['result'] = []

    return json.dumps(result)

def ioc_add_raw(request):
    """Maybe remove"""
    return "Not implimented"

def ioc_link(rrequest):
    """Link two indicators - must have objct IDs"""

    result = {}
    valid = False
    if 'source' in rrequest:
        if 'stype' in rrequest:
            if 'dest' in rrequest:
                if 'dtype' in rrequest:
                    if 'note' in rrequest:
                        rdata = rrequest
                        nlink = objects.link(rdata['source'], rdata['stype'], rdata['note'], rdata['dest'], rdata['dtype'])
                        ecode, message = nlink.log()
                        if ecode:
                            valid = True
                            result['code'] = True
                            result['message'] = message
                        else:
                            result['code'] = ecode
                            result['message'] = message

                        del nlink
        return json.dumps(result)
    return json.dumps({"error" :"problem linking"})


def auto_ioc_link(rrequest):
    """Link two indicators"""

    result = {}
    valid = False
    if 'source' in rrequest:
        if 'stype' in rrequest:
            if 'dest' in rrequest:
                if 'dtype' in rrequest:
                    if 'note' in rrequest:
                        rdata = rrequest

                        nlink = objects.link(rdata['source'], rdata['stype'], rdata['note'], rdata['dest'], rdata['dtype'], True)
                        ecode, message = nlink.log()
                        if ecode:
                            valid = True
                            result['code'] = True
                            result['message'] = message
                        else:
                            result['code'] = ecode
                            result['message'] = message
                        del nlink
            return json.dumps(result)
    return json.dumps({"error" :"problem linking"})





def ioc_search(rrequest):
    """Search for indicator"""

    result = {}
    valid = False
    if 'query' in rrequest:
        if 'type' in rrequest:
            valid = True
            if 'regex' in rrequest:
                print(rrequest['query'])
                rcode, rmessage, rsearch = functions.r_search(rrequest['type'], rrequest['query'], True)
            else:
                print(rrequest['query'])
                rcode, rmessage, rsearch = functions.r_search(rrequest['type'], rrequest['query'])

            if rcode == -1:
                result['message'] = "Error: %s" % rmessage
            result['results'] = list(rsearch)

    if 'json' in rrequest:
        return json.dumps(result)

    message = ""
    for post in result['results']:
        message += "%s\n" % post['name']
        for rnote in post['note']:
            message += " - %s\n" % rnote
    return message

def link_search(rrequest):
    """Search for indicators based on link"""
    result = {}
    valid = False
    if 'id' in rrequest:
        status, results = functions.link_search(rrequest['id'])
        if status:
            result['results'] = results
            result['code'] = True
            result['message'] = ""
    return json.dumps(result)

"""Module specific Functions"""


def resolver_pull(rrequest):
    """Fetch IP addresses for resolution"""
    return json.dumps(functions.get_domains_for_resolution())

def resolver_post(rrequest):
    """Receive and process IP addresses for resolution"""

    if 'results' in rrequest:
        results = rrequest['results']
        status, message, results = functions.submit_domains_from_resolution(results)
        return str(status)
    return False

def resolver_post_one(rrequest):
    """Receive and process single IP addresses for resolution"""

    if 'results' in rrequest:
        results = rrequest['results']
        status, message, results = functions.submit_domains_from_resolution_one(results)
        return str(status)
    return False

def pull_active_ip(rrequest):
    """Fetch active IP addresses"""

    try:
        return json.dumps(functions.get_active_ip_list())
    except Exception as e:
        print(e)
        return json.dumps([])

def pull_new_by_type(rtype):
    """Fetch new hosts by type"""

    rlist = functions.get_new_hosts(rtype)
    hosts = []
    for x in rlist:
        hosts.append(x['name'])
    return json.dumps(hosts)




def readme():
    """return generic readme"""
    return """
/<br />/add<br />/r_add<br /><br />/link<br /><br />/search<br />/lsearch<br /><br />#### Modules ####<br /><br />/module/resolver/pull<br /><br />/module/resolver/submit
/module/list/new_ip<br />/module/list/domain<br />/module/list/active<br />"""


def page_main(rrequest):
    """Fetch main page"""

    try:
        recent = functions.get_recent_additions("|")
        return flask.render_template('index.html', recent=recent)
    except Exception as e:
        print(e)
        return "Failure with pulling recent:%s" % e

def page_search(rrequest):
    """Main Seach Page"""

    search_results = []
    bresults = False

    if rrequest.method == "POST":
        if "query" in rrequest.form:
            bresults = True

            results = functions.wide_search(rrequest.form['query'])
            for rsu_type, res_results in results:
                for rsu in res_results:
                    if ('note' in rsu and 'details' in rsu and 'name' in rsu and 'added' in rsu):
                        search_results.append([
                            rsu['name'],
                            datetime.datetime.fromtimestamp(int(rsu['added'])).strftime('%Y-%m-%d %H:%M:%S'),
                            "\n".join(rsu['note']),
                            json.dumps(rsu['details']),
                            rsu_type,
                            bson.ObjectId(oid=str(rsu['_id']))
                            ])


    return flask.render_template('search.html', bresults=bresults, recent=search_results)

def page_add(rrequest):
    """Place holder"""
    return "Add"

def page_bulk_add(rrequest):
    """Place holder"""    
    return "Bulk Add"

def page_api_doc(rrequest):
    """Place holder"""    
    return readme()

def page_details(rrequest):
    """Place holder"""    
    return "Details"
