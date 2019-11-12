'''
Created on Aug 27, 2015

Script to generate all directories based on contents of supplied config file

@author: badc
'''
import os, sys,ConfigParser

config_file = sys.argv[1]

try:
    config=ConfigParser.RawConfigParser() 
    config.read(config_file)
                            
except:
    print "ERROR: Could not extract configuration from %s" %config_file
    
#get config targets
targets = config.sections()

for target in targets:
    
    if target != "default":
    
        local_path = config.get(target,'local_path')
        
        if not os.path.exists(local_path):
            try:
                os.mkdir(local_path)
                
                if os.path.exists(local_path):
                    print "Have successfully created: %s" %local_path
                
            except Exception as ex:
                print "Unable to make directory: %s (%s)" %(local_path,ex)
                
        else:
            print "Path %s already exists!"
         