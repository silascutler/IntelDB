#!/usr/bin/env python3
''' IntelDB
 Autor: Silas Cutler (silas@BlackLab.io)

'''
# pylint: disable=invalid-name
# pylint: disable=R0913
# pylint: disable=C0103
# pylint: disable=R0915
# pylint: disable=R0914


import json
import flask

from core import handlers

class f_server():
    '''API Server Class.'''
    def __init__(self):
        self.app = flask.Flask(__name__)    
        self.app.debug = True
        self.static_pages()
        
    def static_pages(self):
        '''Default Route'''
        @self.app.route('/')

        def generic_home():
            '''Default Function'''
            return "{}"

        ###################################
        #### API Methods
        ##################################

        #API Add
        @self.app.route('/add', methods=['POST'])
        def f_add():
            try:
                print("--")
                results = handlers.ioc_add(flask.request.form)
            except Exception as error:
                results = "Error: %s" % error
                results = json.dumps({'error': results})

            print("--")
            return results

        @self.app.route('/bulk_add', methods=['POST'])
        def fbulk_add():
            try:
                print("--")
                results = handlers.ioc_add_bulk(flask.request.form)
            except Exception as error:
                results = "Error: %s" % error
                results = json.dumps({'error': results})

            print("--")
            return results

        @self.app.route('/r_add')
        def f_raw_search():
            try:
                results = handlers.ioc_add_raw(flask.request.form)
            except Exception as error:
                results = "Error: %s" % error
                results = json.dumps({'error': results})

            return results

        # API LINK
        @self.app.route('/link', methods=['POST'])
        def f_link():
            try:
                results = handlers.ioc_link(flask.request.form)
            except Exception as error:
                results = "Error: %s" % error
                results = json.dumps({'error': results})

            return results
        @self.app.route('/alink', methods=['POST'])
        def f_alink():
            try:
                results = handlers.auto_ioc_link(flask.request.form)
            except Exception as error:
                results = "Error: %s" % error
                results = json.dumps({'error': results})
            return results

        # Search Indicators ( Type & Name passed in form)
        @self.app.route('/search', methods=['POST'])
        def f_search():
            try:
                results = handlers.ioc_search(flask.request.form)
            except Exception as error:
                print("Sending Error")
                results = "SError: %s" % error
                results = json.dumps({'error': results})
            return results


        #Link Search (MySQL)
        @self.app.route('/lsearch', methods=['POST'])
        def f_link__search():
            try:
                results = handlers.link_search(flask.request.form)
            except Exception as error:
                results = "Error: %s" % error
                results = json.dumps({'error': results})
            return results

        #######
        ### Modules
        #######
        @self.app.route('/module/resolver/pull', methods=['GET'])
        def f_resolver_pull():
            try:
                results = handlers.resolver_pull(flask.request.form)
            except Exception as error:
                results = "Error: %s" % error
                results = json.dumps({'error': results})
            return results


        @self.app.route('/module/resolver/submit', methods=['POST'])
        def f_resolver_submit():
            try:
                results = "Error: %s" % "Depricated"
                #results = handlers.resolver_post(flask.request.form)
            except Exception as error:
                results = "Error: %s" % error
                results = json.dumps({'error': results})
            return results

        @self.app.route('/module/resolver/log_res', methods=['POST'])
        def f_resolver_submit_one():
            try:
                results = handlers.resolver_post(flask.request.form)
            except Exception as error:
                results = "Error: %s" % error
                results = json.dumps({'error': results})
            return results

        @self.app.route('/module/list/active', methods=['GET'])
        def f_list_active():
            try:
                results = handlers.pull_active_ip(flask.request.form)
            except Exception as error:
                results = "Error: %s" % error
                results = json.dumps({'error': results})
            return results

        @self.app.route('/module/list/new_ip', methods=['GET'])
        def f_list_new_ip():
            try:
                results = handlers.pull_new_by_type('ipaddress')
            except Exception as error:
                results = "Error: %s" % error
                results = json.dumps({'error': results})
            return results

        @self.app.route('/module/list/new_domain', methods=['GET'])
        def f_iist_new_domain():
            try:
                results = handlers.pull_new_by_type('domain')
            except Exception as error:
                results = "Error: %s" % error
                results = json.dumps({'error': results})
            return results

        ##############################
        ### User Pages
        #############################

        @self.app.route('/user/')
        def index_page():
            try:
                return handlers.page_main(flask.request)
            except Exception as error:
                return "Broken Page: %s" % error

        @self.app.route('/user/search', methods=['GET', 'POST'])
        def search_page():
            try:
                return handlers.page_search(flask.request)
            except Exception as error:
                return "Broken Search Page: %s" % error

        @self.app.route('/user/add', methods=['GET', 'POST'])
        def add_page():
            try:
                return handlers.page_add(flask.request)
            except Exception as error:
                return "Broken Page: %s" % error

        @self.app.route('/user/bulk_add', methods=['GET', 'POST'])
        def bulkadd_page():
            try:
                return handlers.page_bulk_add(flask.request)
            except Exception as error:
                return "Broken Page: %s" % error

        @self.app.route('/user/api_doc')
        def apidoc_page():
            try:
                return handlers.page_api_doc(flask.request)
            except Exception as error:
                return "Broken Page: %s" % error

        @self.app.route('/user/ioc_details', methods=['GET', 'POST'])
        def indicator_page():
            try:
                return handlers.page_details(flask.request)
            except Exception as error:
                return "Broken Page: %s" % error

        @self.app.route('/status', methods=['GET'])
        def status_msg():
            try:
                return "online"
            except Exception as error:
                return "Broken Page: %s" % error

    def start(self):
        """Start API Server"""
        self.app.run(host='0.0.0.0', port=80, threaded=True, processes=1)
