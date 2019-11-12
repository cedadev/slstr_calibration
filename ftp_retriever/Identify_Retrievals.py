'''
Created on Jul 15, 2015

Script to check contents of list obtained by List_Data_Items.py that are not currently in the local tree

@author: sdonegan
'''
import os,sys
import ConfigParser
from optparse import OptionParser, OptionGroup

from SLSTR_Utilities import identify_files as identify_files
from SLSTR_Utilities import generate_list as generate_list
from SLSTR_Utilities import open_file_list as open_file_list
from SLSTR_Utilities import create_file_list as create_file_list
from SLSTR_Utilities import filter_dir_products as filter_dir_products
from SLSTR_Utilities import extract_s3_filename_date as extract_s3_filename_date
#from rehearsal.test_slstr_data_retrieval import local_path

#Method to define available options
def set_options(parser):
    
    ingest_opt = OptionGroup(parser, "FTP List Options", "Use these options to find data on ESA FTP site for SLSTR rehearsal data " )
    
    ingest_opt.add_option("-s", "--stream", dest = "stream", type = "str", action = "store", help = "Stream name target in config file to be ingested" )
    ingest_opt.add_option("-c", "--config", dest = "config", type = "str", action = "store", help = "Name of configuration file")
    ingest_opt.add_option("-v", "--verbose", dest = "verbose", action = "store_true", default = False, help = "Print out full information on ingest to STDOUT" )    
    ingest_opt.add_option("-i", "--input-list", dest = "inputlist", type = "str", action = "store", help = "Location to write output lists to (of ingested/existing/failed files)" )
    ingest_opt.add_option("-o", "--output-list", dest = "outputlist", type = "str", action = "store", help = "Location to write output lists to (of ingested/existing/failed files)" )
    ingest_opt.add_option("-l", "--logging", dest = "logging", action = "store_true", default = False, help = "Print output to logfile specified in config file" )

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
        
    if options.inputlist is None:
        print "\nError: Please specify an input file of found data!"
        parser.print_help()
        sys.exit()
        
    if not options.verbose and not options.logging:
        print "\nError: Please specify either verbose or logging option!!"
        parser.print_help()
        sys.exit()
        


class Identify_Retrievals():
    
    def identify_retrievals(self, inc_existing = False):
        '''
            Main method to sift through list of products available on SLSTR server and compare to local contents and output those
            files that are present locally to a list
            
            Args:
                inc_existing (bool): include products already downloaded/found in the returned list
        '''
            
        
        #list of dicts of missing files to retrieve 
        missing_products = {}
        missing_tot_cnt = 0
        
        #for products in files_to_retrieve.keys():
        for products in self.input_list.keys():
            
            product_name = os.path.basename(products)
            
            #need to deal with YYYY/MM/DD structure
            dates = extract_s3_filename_date(products)            
                                    
            #are we dealing with a EUMETSAT safe dir struct or an ESRIN zipfile?  If dir add it to the dates list to generate path
            if type(self.input_list[products]) is list:
                
                missing_sub_files = []
                
                #EUMETSAT SAFE dir?
                dates.append(products)
                
                local_product_dir = os.path.join(self.local_path, *dates)
                
                for sub_file in self.input_list[products]:
                    
                    sub_file_stub = os.path.join(*sub_file.split(os.path.sep)[-2:])
                    
                    sub_product = os.path.join(local_product_dir, os.path.basename(sub_file_stub))
                    
                    if not os.path.exists(sub_product):
                        
                        missing_tot_cnt += 1
                
                        if self.verbose:
                            print "Checking local files for %s ... MISSING" %(sub_file_stub)
                    
                        #add REMOTE file to list to eventually retrieve
                        missing_sub_files.append(sub_file)
                        
                    else:
                        if inc_existing:
                            missing_sub_files.append(sub_file)
                        
                        if self.verbose and not self.missing:
                            print "Checking local files for %s ... PRESENT" %(sub_file_stub)
                                  
                missing_products[products] = missing_sub_files
                
            else:
                                
                local_product_dir = os.path.join(self.local_path, *dates)         
            
                #check for missing files if we already have the directory - some files may be missing
                zipfile = product_name
                uncompressed_zipfile = product_name.replace('zip','SEN3') 
                
                if os.path.exists(os.path.join(local_product_dir, product_name)) or os.path.exists(os.path.join(local_product_dir, uncompressed_zipfile)):
                    
                    if inc_existing:
                        missing_products[products] = self.input_list[products]                      
                    
                    if self.verbose:
                        print "Checking local files for %s ... PRESENT" %(product_name)
                else:
                    
                    missing_tot_cnt += 1
                    
                    if self.verbose and not self.missing:
                        print "Checking local files for %s ... MISSING" %(product_name)
                
                    missing_products[products] = self.input_list[products]                                              
                                                        
        if self.missing:
            print "Found %s products (and %s files) missing on local system" %(len(missing_products.keys()),missing_tot_cnt)
        
        return missing_products
                
                
    
    def create_list_of_items(self, files_to_retrieve, output_list_file):
            
        try:
           
            if create_file_list(output_list_file,files_to_retrieve):
                print "\nFinished: Identified %s files to retrieve" %(len(files_to_retrieve))
    
            else:
                print "Problem: Could not write file list %s (NO products found)" %(output_list_file)
                              
        except Exception as ex:
            print "ERROR: Could not write file list %s (Error:%s)" %(output_list_file,ex)
            
    
        
    def __init__(self, **kwargs):
                
        self.verbose = None
        self.logging= None
        self.configFile = None
        self.stream = None
        self.local_path = None
        self.input_list_file = None
        self.input_list = None
        self.missing = None
        
        #attribute to the object all kwargs
        for name, value in kwargs.items():
            setattr(self, name, value)
            
        #check whether we're pulling info from an input list or a list object
        if not self.input_list and not self.input_list_file:
            raise Exception ("Neither input list file or object has been supplied!")
        
        if self.input_list and self.input_list_file:
            raise Exception ("Please supply EITHER input list file or object!")
        
        #generate the internal list object
        if self.input_list_file:
            
            try:
                self.input_list = open_file_list(self.input_list_file)
                
            except Exception as ex:
                raise Exception ("ERROR: Could not open %s (%s)" %(self.input_list_file,ex))
        
        if not self.input_list:
            raise Exception ("ERROR: Could not read input list")    
               
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
                self.local_path = str(self.config.get(self.stream,'local_path'))
                
            except:
                print "ERROR: Could not extract configuration from %s" %self.configFile
                
        else:
            print "ERROR: Cannot open configuration file: %s" %self.configFile
            
    
    
if __name__ == '__main__':
        
    parser = OptionParser()
    
    options,args = set_options(parser)
    
    check_options(options)
    
    '''
    try:
        list_data= List_Data_Items(verbose = options.verbose, \
                                   logging = options.logging, configFile = options.config, \
                                   stream = options.stream)
        
    except Exception as ex:
        print "ERROR: unable to initiate data finder class (%s)" %ex
        sys.exit()
    
    '''
    
    #activate the main script
    try:
        products = Identify_Retrievals(verbose = options.verbose, input_list_file = options.inputlist, \
                                   logging = options.logging, configFile = options.config, \
                                   stream = options.stream)
        
    except Exception as ex:
        print "ERROR: unable to generate list of new files to retrieve (%s)" %ex
        
    try:
        products_to_retrieve = products.identify_retrievals()
   
    except Exception as ex:
        print "ERROR: unable to generate list of new files to retrieve (%s)" %ex
        
        
    #create the list
    try:
        products.create_list_of_items(products_to_retrieve, options.outputlist)
        
    except Exception as ex:
        print "ERROR: unable to write list of files to retrieve (%s)" %ex
        
        
   