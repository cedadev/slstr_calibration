'''
Created on Jul 14, 2015

@author: sdonegan

Module to identify items on the SLSTR test site ready for download
'''
import os,sys
import ConfigParser
from optparse import OptionParser, OptionGroup

from SLSTR_Utilities import identify_files as identify_files
from SLSTR_Utilities import generate_list as generate_list
from SLSTR_Utilities import create_file_list as create_file_list
from SLSTR_Utilities import activate_logging, output_director

#Method to define available options
def set_options(parser):
    
    ingest_opt = OptionGroup(parser, "FTP List Options", "Use these options to find data on ESA FTP site for SLSTR rehearsal data " )
    
    ingest_opt.add_option("-s", "--stream", dest = "stream", type = "str", action = "store", help = "Stream name target in config file to be ingested" )
    ingest_opt.add_option("-c", "--config", dest = "config", type = "str", action = "store", help = "Name of configuration file")            
    ingest_opt.add_option("-o", "--output-list", dest = "outputlist", type = "str", action = "store", help = "Location to write output lists to (of ingested/existing/failed files)" )
    ingest_opt.add_option("-v", "--verbose", dest = "verbose", action = "store_true", default = False, help = "Print out full information on ingest to STDOUT" )    
    ingest_opt.add_option("-l", "--logging", dest = "logging", action = "store_true", default = False, help = "Print output to logfile specified in config file" )
    ingest_opt.add_option("-d", "--no-check-days", dest = "no_check_days", action = "store_true", default = False, help = "Ignore the check_days config file directive. Will look for ALL data irrespective of time on server" )

    parser.add_option_group(ingest_opt)
    
    (options,args) = parser.parse_args()
    
    return (options,args)


#Method to check options
def check_options(options):
           
    if options.stream is None:
        print "\nError: Please specify a retrieval stream within the configuration file (i.e. LI_017_RoI_Greenland)"
        parser.print_help()
        sys.exit()
        
    if options.config is None:
        print "\nError: Please specify an valid configuration file!"
        parser.print_help()
        sys.exit()
        
    if options.outputlist is None:
        print "\nError: Please specify an output file to list found data to!"
        parser.print_help()
        sys.exit()
        
    if not options.verbose and not options.logging:
        print "\nError: Please specify either verbose or logging option!!"
        parser.print_help()
        sys.exit()
        

class List_Data_Items(object):
    
    def list_data_items(self):
        '''
            Method to wrap SLSTR utilites listing objects
        '''
                
        try:
            #files_to_retrieve = identify_files(self.config,options)
            files_to_retrieve = identify_files(self.config, self.product, self.path, existing_products = None, ignore_time_check = self.ignore_time_check)
            #todo - reinstate existing_products
            
            #if len(files_to_retrieve.keys()) == 0:
                #raise Exception ("No files available")            
        except Exception as ex:
            raise Exception ("Unable to identify files on remote server (%s)" %ex)
        
        return files_to_retrieve
    
    
    def create_list_of_items(self, files_to_retrieve, output_list_file):
            
        try:
           
            if create_file_list(output_list_file,files_to_retrieve.values()):
                print "\nFinished: Found %s files in within last %s days" %(len(files_to_retrieve.values()), self.days)
    
            else:
                print "Problem: Could not write file list %s (NO products found)" %(output_list_file)
                              
        except Exception as ex:
            print "ERROR: Could not write file list %s (Error:%s)" %(output_list_file,ex)
            
    
    def __init__(self,**kwargs):
                
        self.verbose = None
        self.logging= None
        self.configFile = None
        self.stream = None
        self.options = None
        
        #attribute to the object all kwargs
        for name, value in kwargs.items():
            setattr(self, name, value)
           
        #sort out logging
        '''
        self.output_director = activate_logging(outputfile_stream_name_dt)
        self.output_director("\nFiles not ingested! Report file: %s" %list_not_ingested_files_file)
        '''
        if os.path.isfile(self.configFile):
            
            try:
                self.config=ConfigParser.RawConfigParser() 
                self.config.read(self.configFile)
                
                self.path = str(self.config.get(self.stream,'ftp_server_path'))
                self.days = self.config.get('default','check_days_num')
                self.product = self.config.get(self.stream,'product_base')
                
            except:
                print "ERROR: Could not extract configuration from %s" %self.configFile

            #over-ride path supplied in config file if -p option supplied
            if self.options.server_path is not None:
                self.path = self.options.server_path

        else:            
            
            print "ERROR: Cannot open configuration file: %s" %self.configFile
            
        
if __name__ == '__main__':
    
    
    parser = OptionParser()

    options,args = set_options(parser)
    
    check_options(options)
    
    #Use decent arguements parser
    try:
        list_data= List_Data_Items(verbose = options.verbose, \
                                   logging = options.logging, configFile = options.config, \
                                   stream = options.stream, ignore_time_check=options.ignore_check_days)
        
    except Exception as ex:
        print "ERROR: unable to initiate data finder class (%s)" %ex
        sys.exit()
    
    #activate the main script
    try:
        files_to_retrieve = list_data.list_data_items()
        
    except Exception as ex:
        print "ERROR: unable to generate list of files to retrieve (%s)" %ex
        
    #create the list
    try:
        list_data.create_list_of_items(files_to_retrieve, options.outputlist)
        
    except Exception as ex:
        print "ERROR: unable to write list of files to retrieve (%s)" %ex
        
        
        
    
    
    