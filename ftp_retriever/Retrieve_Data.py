'''
Created on Jul 16, 2015

Script to retrieve data by FTP identified in an input list on the ESA server

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
from SLSTR_Utilities import Retrieve_By_FTP
from SLSTR_Utilities import access_xml_file
from SLSTR_Utilities import get_xpath_value
from SLSTR_Utilities import check_data_checksum

XFDUMANIFEST_XPATH_MD5= "dataObjectSection/dataObject[@ID='ISPData']/byteStream/checksum"
MANIFEST_FILENAME = 'xfdumanifest.xml'
DATA_FILENAME = 'ISPData.dat'
REGET_RETRIES = 5

#from rehearsal.test_slstr_data_retrieval import local_path

#Method to define available options
def set_options(parser):
    
    ingest_opt = OptionGroup(parser, "FTP retrieve Options", "Use these options to RETRIEVE data on ESA FTP site for SLSTR rehearsal data " )
    
    ingest_opt.add_option("-s", "--stream", dest = "stream", type = "str", action = "store", help = "Stream name target in config file to be ingested" )
    ingest_opt.add_option("-c", "--config", dest = "config", type = "str", action = "store", help = "Name of configuration file")
    ingest_opt.add_option("-v", "--verbose", dest = "verbose", action = "store_true", default = False, help = "Print out full information on ingest to STDOUT" )    
    ingest_opt.add_option("-i", "--input-list", dest = "inputlist", type = "str", action = "store", help = "Location to write output lists to (of ingested/existing/failed files)" )
    ingest_opt.add_option("-r", "--report-file", dest = "reportFile", type = "str", action = "store", help = "Location to write output lists to (of ingested/existing/failed files)" )
    
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
        
    if options.reportFile is None:
        print "\nError: Please specify an output report file to list data retrieved to!"
        parser.print_help()
        sys.exit()
        
    if options.inputlist is None:
        print "\nError: Please specify an input file of found data!"
        parser.print_help()
        sys.exit()
        
        
def prepare_directories(local_location,local_path):
    '''
        Method to prepare local directories prior to data retrieval
    '''
    
    if not os.path.exists(local_path):        
        raise Exception ("Path as defined in config (%s) does not exist.  Create and re-run" %local_path)
        
    #if local path is not there throw an error as this must be made prior to running "safetys sake"
    if not os.path.exists(local_location):
        
        new_directory = os.path.basename(local_location)
        
        try:
            os.mkdir(os.path.join(local_path,new_directory))
            
            if not os.path.exists(local_location):
                return False
            else:
                return True
            
        except Exception as ex:
            raise Exception("ERROR: Could not make %s in path %s" %(new_directory,local_path))
        
    else:
        #path already exist
        return True
        
    
def check_datafile_md5(manifest_file, data_file):
    '''
        Method to find stated md5 value and compare against value for downloaded data file
    '''
    
    #get the md5 value from the manifest
    try:
        root = access_xml_file(manifest_file)
        
        md5_value=get_xpath_value(root,XFDUMANIFEST_XPATH_MD5)
        
        #dummy for debugging purposes
        #md5_value = '%s_scoobydoo'%md5_value
            
    except Exception as ex:
        raise Exception ("Unable to check md5 value (%s, %s): %s" %(manifest_file, data_file,ex))
        
    #compare the values
    try:
        return check_data_checksum(data_file, md5_value)
        
    except Exception as ex:
        raise Exception ("Problem checking md5 value (%s, %s): %s" %(manifest_file, data_file, ex))
    
    
def group_files_to_retrieve(file_list):
    '''
        Method to group files by target folder, so can download in distinct groups
    '''
    #need to group files together per directory to ease file checking - do this by local file (as defined in config)
    common_dirs = []
    filesets = {}
    
    for product in file_list:
        
        #local_location = product.split(':')[0]
        ftp_location = product.split(':')[1]
        
        if os.path.dirname(ftp_location) not in common_dirs:
            common_dirs.append(os.path.dirname(ftp_location))          
    
    for dir_path in common_dirs:
        filesets[dir_path] = []
        
        for product in file_list:
            ftp_location = product.split(':')[1]
             
            if os.path.dirname(ftp_location) == dir_path:
                filesets[dir_path].append(product)
                
    return filesets


def get_fileset(file_list, cnt, local_path, product, conn_details, options):
    '''
        Method to wrap the retrieval of all files associated with a single remote directory
    '''
    
    all_files_retrieved = False
    
    fileset_retrieve = {}
    files_retrieved = []
    downloaded_datafiles = []
    files_not_retrieved = []

    for product_file in file_list:
        
        local_location = product_file.split(':')[0]
        ftp_location = product_file.split(':')[1] 
        
        if options.verbose:
            print "[%s] Attempting to retrieve %s" %(cnt,ftp_location)
        
        #create local directories to place data retrieved into
        try:                        
            generated = prepare_directories(local_location, local_path)
            
        except Exception as ex:
            raise Exception ( "Problem with local directory: %s" %ex)
            
        if generated:
                            
            #get connection
            retrieved = None
            try:
                #tidy this up later                
                
                connection = Retrieve_By_FTP(conn_details['user'], conn_details['pw'],conn_details['site'])
                
                retrieved = connection.get_file(local_location, ftp_location, options)                
                #close connection before doing any processing
                connection.close_ftp_connection()                
                    
            except Exception as ex:
                connection.close_ftp_connection()
                raise Exception ("ERROR: Could not connect to %s (%s)" %(conn_details['site'],ex))
                                        
            if retrieved:
                
                filename=os.path.basename(ftp_location)
        
                #have we got the data_file
                if filename == DATA_FILENAME:
                    local_data_file= os.path.join(local_location,filename)                   
                    downloaded_datafiles.append(local_data_file)
                    
                if filename == MANIFEST_FILENAME:
                    local_md5_file = os.path.join(local_location,filename)    
                        
                files_retrieved.append(retrieved)
                
                fileset_retrieve[product_file] = True
                
            else:
                #could not retrieve a file
                files_not_retrieved.append(ftp_location)
                fileset_retrieve[product] = False
                                                     
        else:
            print "ERROR: could not make local directory!"
            sys.exit(2)
                
        cnt += 1  
       
    #check whether all products in the fileset have been successfully retrieved
    success= True # assume the worst        
    for files in file_list:
        if not fileset_retrieve[files]:
            success = False
            
    #if all there, perform the md5 check            
    if not check_datafile_md5(local_md5_file, local_data_file):
        
        #if this fails remove the data and warn
        print "--------- Problem: %s failed md5 check.  Removing data files for this download." %(local_data_file)
        
        try:
            os.remove(local_data_file)
            
            #also need to remove from retrieve list
            fileset_retrieve[product] = False
            files_retrieved.remove(retrieved)
            files_not_retrieved.append(ftp_location)
            
            
        except Exception as ex:
            raise Exception ("Could not remove problem data file (%s)" %ex)
        
    else:
        #only now can we say everything retrieved ok and data file checked
        all_files_retrieved = True
        
        
    return all_files_retrieved, files_retrieved, files_not_retrieved


def retrieve_data(config, options):
    '''
        Main method governing the retrieval of data from the FTP site
    '''
    
    local_path = config.get(options.stream,'local_path')

    try:
        file_list = open_file_list(options.inputlist)
        
    except Exception as ex:
        print "ERROR: Could not open %s (%s)" %(options.inputlist,ex)
        sys.exit(2)
        
    #get config information
    #now retrieve the data to the local path
    #default configuration
    conn_details = {}
    
    try:
        
        
        conn_details['user'] = config.get('default','ftp_user')
        conn_details['pw'] = config.get('default','ftp_pw')
        conn_details['site'] = config.get('default','ftp_host')
        days = config.get('default','check_days_num')
        check_days = config.get('default','check_days')
        
    except Exception as ex:
        raise Exception ("ERROR: Unable to access default section of configuration(%s)" %ex)
    
    #stream configuration
    #default configuration
    try:
        product = config.get(options.stream,'product_base')
        path = str(config.get(options.stream,'ftp_server_path'))  
        
    except Exception as ex:
        raise Exception ("ERROR: Unable to access STREAM section of configuration(%s)" %ex)
        
        
    cnt = 1
    
    #need to group files together per directory to ease file checking - do this by local file (as defined in config)
    filesets = group_files_to_retrieve(file_list)
    
    files_retrieved = []
    files_not_retrieved = []
    
    for fileset in filesets.keys():
        
        file_list = filesets[fileset]
        
        #try N times to get data
        success = False
        retry_cnt = 0
        while retry_cnt <= REGET_RETRIES:
            
            try:
                success, files_retrieved_lp,files_not_retrieved_lp = get_fileset(file_list, cnt, local_path, product, conn_details, options)
                files_retrieved += files_retrieved_lp
                files_not_retrieved += files_not_retrieved_lp
               
            except:
                #catch any problems and try again
                success = False
                
            #if all ok, break out
            if success:
                break
                
            retry_cnt += 1
            
        if not success:
            print "Problem downloading: "
        
    #now generate output lists
    if create_file_list(options.reportFile,files_retrieved):
            print "\nFinished: Retrieved %s files.  Report at %s" %(len(files_retrieved),options.reportFile )
        
    else:
        print "Problem generating report file: %s" %options.reportFile
            
    if len(files_not_retrieved) > 0:
        print "Problem retrieving following files on FTP host:"
        
        for probfile in files_not_retrieved:
            print probfile
        

if __name__ == '__main__':
    
    parser = OptionParser()
    
    options,args = set_options(parser)
    
    check_options(options)
    
    #Use rawconfigparser to prevent dirtemplate %() expansions
    if os.path.isfile(options.config):
        
        try:
            config=ConfigParser.RawConfigParser() 
            config.read(options.config)
                                    
        except:
            print "ERROR: Could not extract configuration from %s" %options.config
            
    else:
        print "ERROR: Cannot open configuration file: %s" %options.config
            
    #activate the main script
    try:
        retrieve_data(config, options)
        
    except Exception as ex:
        print "ERROR: Could not retrieve data: %s" %ex
        
        
   