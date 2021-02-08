#!/usr/bin/env python3
''' IntelDB
 Autor: Silas Cutler (silas@BlackLab.io)


'''

import core.api

def main():
    '''Main function.'''
    server = core.api.f_server()
    server.start()

if __name__ == "__main__":
    main()
