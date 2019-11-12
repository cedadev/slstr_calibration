'''
Created on Aug 27, 2015

Script to control the identification and retrieval of SLSTR commissioning phase data.

@author: sdonegan
'''

import os,sys
import ConfigParser
from optparse import OptionParser, OptionGroup
import zipfile
from datetime import datetime
import logging

from List_Data_Items import List_Data_Items
from Identify_Retrievals import Identify_Retrievals
from SLSTR_Utilities import Retrieve_By_FTP, generate_directories, extract_s3_filename_date
from SLSTR_Utilities import access_xml_file
from SLSTR_Utilities import get_xpath_value
from SLSTR_Utilities import check_data_checksum

from SLSTR_Utilities import PlockError, PlockPresent, Retrieve_Lock

MANIFEST_FILENAME = 'xfdumanifest.xml'

ISP_DATA_FILENAME = 'ISPData.dat'
XFDUMANIFEST_DATA_XPATH_MD5= "dataObjectSection/dataObject[@ID='ISPData']/byteStream/checksum"

ISP_ANNOTATION_DATA_FILENAME = 'ISPAnnotation.dat'
XFDUMANIFEST_ANNOTATION_DATA_XPATH_MD5= "dataObjectSection/dataObject[@ID='ISPAnnotationData']/byteStream/checksum"

REGET_RETRIES = 5

def check_datafile_md5(manifest_file, data_file, xpath):
        '''
            Method to find stated md5 value and compare against value for downloaded data file
        '''
        
        #get the md5 value from the manifest
        try:
            root = access_xml_file(manifest_file)
            
            md5_value=get_xpath_value(root,xpath)
            
            if not md5_value:
                raise Exception ("Problem accessing md5 value")
            
            #dummy for debugging purposes
            #md5_value = '%s_scoobydoo'%md5_value
                
        except Exception as ex:
            raise Exception ("Unable to check md5 value: %s" %ex)
            
        #compare the values
        try:
            return check_data_checksum(data_file, md5_value)
            
        except Exception as ex:
            raise Exception ("Problem checking md5 value: %s" %ex)


def check_safe_dir_struct(safe_product, verbose = False, remove = False):
    '''
        Class Method to check safe dir struct data md5 values against values published in manifest file 
        
    :param safe_product_list: list of downloaded files constituing a single SAFE product dir in uncompressed format
    '''
    
    valid_data= True
    local_manifest_file = None
    local_data_file = None
    local_annotation_data_file = None
    
    for filename in safe_product:
                                    
        if os.path.basename(filename) == ISP_DATA_FILENAME:
            local_data_file= filename
            
        if os.path.basename(filename) == ISP_ANNOTATION_DATA_FILENAME:
            local_annotation_data_file= filename            
            
        if os.path.basename(filename) == MANIFEST_FILENAME:
            local_manifest_file = filename
            
    #check values
    try:
        if local_manifest_file and local_data_file and local_annotation_data_file:
            
            #first data file
            md5_data_check = check_datafile_md5(local_manifest_file, local_data_file, XFDUMANIFEST_DATA_XPATH_MD5)
            
            #annotation_data file
            md5_annotation_data_check = check_datafile_md5(local_manifest_file, local_annotation_data_file, XFDUMANIFEST_ANNOTATION_DATA_XPATH_MD5)
            
            if not md5_data_check or not md5_annotation_data_check:
                valid_data = False
                
        else:
            valid_data = False
            
    except Exception as ex:
        
        valid_data = False
        
        if options.verbose:
            print "Problem assessing safe dir struct for: %s" %ex
            
    #clear bad data so picked up next time
    if not valid_data and remove:
        
        for filename in safe_product:
            if verbose:
                print "REMOVING: %s " %(filename)             
            
            os.remove(filename)
            logging.info("REMOVED: %s" %filename)
            
                    
    return valid_data


class Retrieve_Data():
    
    def check_zip(self,filename):        
        '''
            Method lifted from S1A code base to check a zip file for consistency
        '''
        
        ext = os.path.splitext(filename)[-1]
           
        #data
        if ext == '.zip':
           
            try:
                filename_zip = zipfile.ZipFile(filename,'r')
               
                if filename_zip.testzip() is not None:
                    raise Exception ("Bad zipfile: %s" %filename)
               
                else:
                    return True
                               
            except Exception as ex:
                return False
            
        else:
            raise Exception("Not a zipfile")
        
    
    def check_zip_file(self, retrieved_file, remove = False):
        '''
        
            Method to check integrity of zipped files
        '''    
        #check zip file integrity.  Any that do not pass zip test we must remove
        valid_data = True
            
        try:
            if not self.check_zip(retrieved_file):
                if options.verbose:
                    print "Problem with file %s" %retrieved_file
                                
                valid_data = False
                              
        except Exception as ex:
            if options.verbose:
                print "Could not check file: %s (%s)" %(retrieved_file,ex)
                            
            valid_data = False
            
        #clear bad data so picked up next time
        if not valid_data and remove:
            
            if options.verbose:
                print "REMOVING: %s " %(retrieved_file)             
            
            os.remove(retrieved_file)
            logging.info("REMOVED: %s" %retrieved_file)
            
        return valid_data
    
        
    def check_retrieved_files(self,files_retrieved):
        '''
            Method to check retrieved files
        
        '''        
        check_retrieved = {}
        
        good_files_retrieved = []
        bad_files_retrieved = []
    
        for product_name in files_retrieved.keys():
            
            #SAFE dir struct
            if type(files_retrieved[product_name])is list:     
                
                if check_safe_dir_struct(files_retrieved[product_name], verbose = options.verbose,remove = options.remove):
                    
                    logging.info("SUCCESS: %s passed md5 checks!" %product_name)
                    
                    for filename in files_retrieved[product_name]:
                        good_files_retrieved.append(filename)
                        
                else:
                    
                    logging.info("FAIL: %s failed checks!" %product_name)
                    
                    for filename in files_retrieved[product_name]:
                        bad_files_retrieved.append(filename)                        
                
            else:
                
                #zipped data                
                data_file = files_retrieved[product_name]
                if os.path.splitext(data_file)[1] == '.zip':                                        
                
                    if self.check_zip_file(data_file, remove = options.remove):
                        
                        logging.info("SUCCESS: %s passed zip checks!" %data_file)                        
                        good_files_retrieved.append(data_file)
                    
                    else:
                        logging.info("FAIL: %s failed zip checks!" %data_file)
                        bad_files_retrieved.append(data_file)
                
                else:
                    #must be eumetsat safe dir structure
                    #raise Exception ("Non ZIP product encountered! (%s)") %data_file
                    logging.info("FAIL: %s failed checks!" %data_file)
                    bad_files_retrieved.append(data_file)
                    
        return good_files_retrieved, bad_files_retrieved
                                    
        
    def retrieve_files_by_ftp(self, file_list, force = False, flat_structure = False):
        '''
            Method lifted from older Retrieve_Data to retrieve a data file in the given list
        '''
        cnt = 0
        
        files_retrieved = {}
        #bad_files_retrieved = []
        files_already_retrieved = []
        #good_files_retrieved = []
        
        if not os.path.exists(self.local_path):
            raise Exception ("Local destination directory %s does NOT exist!" %self.local_path)
                
        #bulk_transfer_start=datetime.now()
        
        for product_file in file_list.keys():
        
            if options.verbose:
                print "Attempting to retrieve %s" %(product_file)
                                                 
            
            if not flat_structure:
                
                #need to make sure data is in YYYY/MM/DD structure NOTE consistent naming convention!
                if type(file_list[product_file])is list:      
                    
                    #product dir type structure - need to include product name          
                    dates = extract_s3_filename_date(product_file)
                    dates.append(product_file)
                
                else:
                    dates = extract_s3_filename_date(product_file)
                    
                try:
                    local_full_path = generate_directories(self.local_path, dates, verbose = options.verbose)
                    
                    if not local_full_path:
                        raise Exception("Problem generating local directory structure!")
                                            
                except Exception as ex:                
                    raise Exception ("Cannot generate local path: %s" %ex)
                
            else:
                #just download to the directory specified in the config
                local_full_path = self.local_path
                        
            #get connection
            #retrieved = None            
            try:
                
                #again need to work out what type of product
                if type(file_list[product_file])is list:
                    
                    file_set = []
                    
                    for file_to_retrieve in file_list[product_file]:
                        
                        retrieved_status, speed = self.connection.get_file(local_full_path, file_to_retrieve, options, force=force)
                        
                        if retrieved_status:
                            logging.info("SUCCESS: %s to %s (at ~%s Kb/s)" %(product_file,retrieved_status.keys()[0], speed))      
                            file_set.append(retrieved_status.keys()[0])
                            
                        else:
                            
                            #record files previously retrieved.
                            files_already_retrieved.append(os.path.join(local_full_path,file_list[product_file]))
                        
                            
                        cnt += 1
                        
                    files_retrieved[product_file] = file_set
                    
                else:                
                    retrieved_status, speed = self.connection.get_file(local_full_path, file_list[product_file], options, force=force)
                                    
                    if retrieved_status[os.path.join(local_full_path,product_file)]:
                        logging.info("SUCCESS: %s to %s (at ~%s Kb/s)" %(product_file,retrieved_status.keys()[0], speed))      
                        files_retrieved[product_file] = retrieved_status.keys()[0]
                        
                    else:
                        #record files previously retrieved.
                        files_already_retrieved.append(os.path.join(local_full_path,file_list[product_file]))
                        
                    cnt += 1
                        
            except Exception as ex:
                #could be that file in question is a link - seems to be issues with these
                logging.info("PROBLEM: %s (%s)" %(product_file, ex))                                
                
        #close connection before doing any processing
        self.connection.close_ftp_connection()
                             
        return files_retrieved, files_already_retrieved
            
            
    def __init__(self, config, stream):
        
        #default configuration
        try:
            self.ftp_user = config.get('default','ftp_user')
            self.ftp_pass = config.get('default','ftp_pw')
            self.ftp_site = config.get('default','ftp_host')
            self.local_path = config.get(stream,'local_path')
            
            self.product_type = config.get(stream,'product_base')
            
        except Exception as ex:
            raise Exception ("ERROR: Unable to access default section of configuration(%s)" %ex)
        
        #setup connection
        try:
            self.connection = Retrieve_By_FTP(self.ftp_user, self.ftp_pass,self.ftp_site)
            
        except Exception as ex:            
            self.connection.close_ftp_connection()
            raise Exception ("ERROR: Could not connect to %s (%s)" %(self.ftp_site,ex))
        
               
        
def set_options(parser):
        
    ingest_opt = OptionGroup(parser, "FTP List Options", "Use these options to find data on ESA FTP site for SLSTR rehearsal data.  \
    By default script will use retrieve data. Logging is by default" )
    
    ingest_opt.add_option("-c", "--config", dest = "config", type = "str", action = "store", help = "Name of configuration file")
    
    ingest_opt.add_option("-s", "--stream", dest = "stream", type = "str", action = "store", \
                          help = "Optional: Stream name target in config file to be ingested.  \
                          If supplied will only retrieve data for this stream otherwise all streams will be retrieved" )
    
    ingest_opt.add_option("-L", "--LIST-DATA-ITEMS", dest = "list_data_items", action = "store_true", default = False,\
                           help = "Optional: ONLY list data items on remote server" )
    
    ingest_opt.add_option("-I", "--IDENTIFY_RETRIEVALS", dest = "identify_retrievals", action = "store_true", default = False,\
                           help = "Optional: ONLY Identify files not on local system but present on remote server.  Note must be used with -L option" )
    
    ingest_opt.add_option("-C", "--CHECK_DATA", dest = "check_data", action = "store_true", default = False,\
                           help = "Optional: Check downloaded data (either by performing SAFE manifest md5 check or via ZIP integrity check" )
    
    ingest_opt.add_option("-m", "--missing", dest = "missing", action = "store_true", default = False, \
                          help = "Optional: Will print out data on remote server but missing from local. ")
    
    ingest_opt.add_option("-d", "--ignore_day_check", dest = "ignore_check_days", action = "store_true", default = False, \
                          help = "Ignore the check_days config file directive. Will look for ALL data irrespective of time on server" )
        
    ingest_opt.add_option("-v", "--verbose", dest = "verbose", action = "store_true", default = False, help = "Print out full information on ingest to STDOUT" )
    
    ingest_opt.add_option("-e", "--email", dest = "email", action = "store_true", default = False, help = "Email summary logs to addresses specified in the config file" )
    
    ingest_opt.add_option("-f", "--force", dest = "force", action = "store_true", default = False, help = "Force download of remote file even if local file already present" )
    
    ingest_opt.add_option("-r", "--remove", dest = "remove", action = "store_true", default = False, help = "Remove files that fail data checks (md5 or zip)" )
    
    ingest_opt.add_option("-F", "--flat_dir_structure", dest = "flat_structure", action = "store_true", default = False, \
                          help = "Download to a flat directory: Do NOT place files according to a structure based on extracts from the file name." )

    ingest_opt.add_option("-p", "--server-path", dest="server_path", type="str", action="store", \
                          help="Directory path on remote ftp server.  NOTE: will override ftp_server_path in config file")


    ingest_opt.add_option("-x", "--extensions", dest="extensions", type="str", action="store", \
                          help="Will download only files with this extension.  NOTE: supply without the '.' and separate multiple extensions with a ','")
    
    
    parser.add_option_group(ingest_opt)
    
    (options,args) = parser.parse_args()
    
    return (options,args)


#Method to check options
def check_options(options):
      
    '''     
    if options.stream is None:
        print "\nError: Please specify a retrieval stream within the configuration file (i.e. LI_017_RoI_Greenland)"
        parser.print_help()
        sys.exit()
    ''' 
    if options.config is None:
        print "\nError: Please specify an valid configuration file!"
        parser.print_help()
        sys.exit()
        
    '''
    if not options.verbose and not options.logging:
        print "\nError: Please specify either verbose or logging option!"
        parser.print_help()
        sys.exit()
    '''
         
    if options.remove and not options.check_data:
        print "\nError: can only remove files if -C option is used!"
        parser.print_help()
        sys.exit()
        
    if options.missing and not options.identify_retrievals:
        print "\nError: can only show missing files if -I option is used!"
        parser.print_help()
        sys.exit()
        
        
def list_products(config, stream, verbose = None, logging = None):
    '''
        Method to wrap calling List_Data_Items
    '''
    files_to_get= []
    
    list_data = List_Data_Items()
    
    #activate the main script
    try:
        list_data.list_data_items()
        
    except Exception as ex:
        print "ERROR: unable to generate list of files to retrieve (%s)" %ex
        
    #activate the main script
    try:
        files_to_get = list_data.list_data_items()
        
    except Exception as ex:
        print "ERROR: unable to generate list of files to retrieve (%s)" %ex
        
        
    return files_to_get


def summarise_data_struct(files_retrieved):
    '''
        Method to summarise returned data structure
    
    '''
    
    #summarise what we have retrieved:
    list_files_retrieved = []
    
    products = len(files_retrieved.keys())
    
    try:
    
        for sub_struct in files_retrieved.values():
            if type(sub_struct) is list:
                for product in sub_struct:
                    list_files_retrieved.append(product)
                    
            else:
                list_files_retrieved.append(sub_struct)
                    
        return list_files_retrieved, products
    
    except Exception as ex:
        print "Problem summarising structure! (%s)" %ex
        return None, None


def retrieve_data(config,options,stream):
    '''
        Method to retrieve data for specific config stream
    
    '''
    
    #what type of product
    data_retrieved = False
    
    roi_email_summary = ''
    
    try:
        list_data= List_Data_Items(verbose = options.verbose, \
                                    configFile = options.config, options = options, \
                                   stream = stream, ignore_time_check = options.ignore_check_days)
        
        files_on_server = list_data.list_data_items()
        
    except Exception as ex:
        msg = "ERROR: unable to find data on server (%s)" %ex
        print msg
        return data_retrieved, msg
    
    list_files_retrieved, number_of_products = summarise_data_struct(files_on_server)
    
    if len(list_files_retrieved) != 0:
        msg= "\nFound %s files on remote server" %len(list_files_retrieved)
    
        if options.verbose:
            print msg
        
        logging.info(msg)
        
    else:
        return data_retrieved, '\nNo files found on server!'
    
    if options.list_data_items:
        #Stop here if this is all we wanted to do - but list the files we found
        
        for filename in list_files_retrieved:            
            print filename
            
        #print "\nFound %s products and %s files to retrieve" %(number_of_products,len(list_files_retrieved)) 
            
        return data_retrieved, roi_email_summary
    
    #activate the main script
    try:
        products = Identify_Retrievals(verbose = options.verbose, input_list = files_on_server, \
                                    configFile = options.config, \
                                   stream = stream, missing = options.missing)
        
        filtered_files = products.identify_retrievals(inc_existing=options.force)
        
    except Exception as ex:
        msg =  "ERROR: unable to generate list of files to retrieve (%s)" %ex
        return data_retrieved, msg
       
    
    list_files_identified, products_to_retrieve = summarise_data_struct(filtered_files)
    msg = "\nFound %s products and %s files to retrieve" %(number_of_products,len(list_files_retrieved))
    #msg= "\nFound %s products in %s files on remote server not present (or to be overwritten) on local path" %(products_to_retrieve,len(list_files_identified))
    
    #if options.verbose:
    print msg
    
    logging.info(msg)
    
    if options.identify_retrievals:
        #Stop here if this is all we wanted to do - but list the files we found
        if options.verbose:
            for filename in list_files_identified:
                print filename
                
        return data_retrieved, msg
    
    #retrieve data
    try:
        get_data = Retrieve_Data(config, stream)
        
        bulk_transfer_start = datetime.now()
        
        files_retrieved, files_already_retrieved = get_data.retrieve_files_by_ftp(filtered_files, force=options.force, flat_structure = options.flat_structure)
        
        bulk_transfer_end =datetime.now()
        
        bulk_transfer_duration = bulk_transfer_end - bulk_transfer_start
        
        list_files_retrieved, products_retrieved = summarise_data_struct(files_retrieved)
        
    except Exception as ex:
        msg = "Unable to retrieve data: %s" %ex
        
        if options.verbose:
            print msg
        
        logging.info("Problem retrieving data: %s" %msg)
        
        return data_retrieved, msg
    
    
    
    msg= "\n\nRetrieved %s files (%s products) for %s in %ss. %s files already retrieved. \n" %(len(list_files_retrieved), products_retrieved,\
                                                                                                 stream, bulk_transfer_duration.seconds, \
                                                                                                 len(files_already_retrieved))
    
    if options.verbose:
        print msg
    
    logging.info(msg)
    
    #only check data if option is given
    if not options.check_data:
        return True, msg
        
    else:
        roi_email_summary += msg
        
        try:
            
            bulk_check_start = datetime.now()
            
            good_files_retrieved,bad_files_retrieved = get_data.check_retrieved_files(files_retrieved)
            
            bulk_check_end = datetime.now()
            
            bulk_check_duration = bulk_check_end - bulk_check_start
            
            msg = "\nChecked %s for %s in %ss (%s bad files)\n" %(len(good_files_retrieved), stream, bulk_check_duration.seconds, len(bad_files_retrieved))
            logging.info(msg)        
            roi_email_summary += msg
            
        except Exception as ex:
            msg = "Unable to check data: %s" %ex
            roi_email_summary += msg
            if options.verbose:
                print msg
            
            logging.info("Problem checking data: %s" %msg)
        
        return True, roi_email_summary
    
    
def email_summary(message):
    '''
        Method to send email summarising retrieval
    '''
    #extract email recipients as list
    try:
        recipients = config.get('default','email_alerts').split(';')
        
    except Exception as ex:
        logging.info("Could not extract email addresses to send summary information to!")
        sys.exit()
        
    import smtplib
    
    try:
        
        mail = smtplib.SMTP('localhost')
        mail.sendmail('SLSTR_data_retrieval', recipients, message)
        
        print "Successfully sent email!"
    
    except Exception as ex:
        logging.info("Could not extract email addresses to send summary information to!")          
    
        

if __name__ == '__main__':
    '''
    Script to wrap the retrieval of all data via ftp of files found for all sections in the given config file
    
    '''
    
    parser = OptionParser()
    
    options,args = set_options(parser)
    
    check_options(options)
    
    #Use rawconfigparser to prevent dirtemplate %() expansions
    if os.path.isfile(options.config):
        
        try:
            config=ConfigParser.RawConfigParser() 
            config.read(options.config)
            
            targets = config.sections()
          
        except:
            print "ERROR: Could not extract configuration from %s" %options.config
            
    else:
        print "ERROR: Cannot open configuration file: %s" %options.config
        sys.exit()
        
    #sort logging
    log_dir = config.get('default','log_dir')
    
    #sort out logging
    try:
        log_file_name = os.path.join(log_dir,'%s_retrieve.log' \
                                      %(datetime.now().strftime('%Y-%m-%d_%H%M%S')))
                
        logging.basicConfig(filename=log_file_name,  level=logging.INFO,\
                            format='%(asctime)s:\t%(message)s', datefmt="%Y-%m-%dT%H:%M:%S")
        
        print "Logging output: %s" %log_file_name
                
    except Exception as ex:
        print "Cannot initiate logging!"
        sys.exit()
        
    
    #check for existing processes - mandatory to prevent multiple sessions.    
    try:
        lockfile = config.get('default','lockfile')
                   
        plock= Retrieve_Lock(lockfile)
       
    except PlockPresent, err:
        raise Exception ("Previous process still in operation. Could not create lockfile (%s)" %lockfile)               
        sys.exit()
        
    except Exception as ex:
        print "Problem with plock file! %s"%ex
        sys.exit()
        
    
    #loop through all available sections in specified config - or just the specified section
    if options.stream:
        targets = [options.stream]
    
    cnt = 0
    message = ''
    
    for target in targets:
    
        if target != "default":
            msg = "\nSTARTING ROI: %s\n" %target
            
            if options.verbose:
                print msg 
            logging.info(msg)
            
            if options.email:
                message += msg
            
            try:
                successful_retrieve, message_summary = retrieve_data(config, options, target)
                
                if options.email:
                    message += message_summary
                            
            except Exception as ex:
                msg = "Problem obtaining data: %s" %ex
                print msg
                successful_retrieve = False
                
                if options.email:
                    message += msg
                    
            #if just doing listing of whats on the server finish here
            if options.list_data_items:
                sys.exit(0)
                
            if successful_retrieve:
                msg = "\nFINISHED ROI <SUCCESS>: %s\n" %target
                
                if options.email:
                    message += msg
                
            else:
                msg = "\nFINISHED ROI <FAILURE>: %s\n" %target
                
                if options.email:
                    message += msg
                        
            if options.verbose:
                print msg 
            logging.info(msg)
            
            cnt += 1
    
    msg = "\nFINISHED retrieve job (%s ROI's) at %s" %(cnt,datetime.now())
    
    if options.email:
        message += msg
        
        message += "\nSummary log file: %s" %log_file_name
            
    if options.verbose:
        print msg
        
    logging.info(msg)
    
    #send email if required
    if options.email:
        email_summary(message)
        
    plock.release()
    
    print "Finished"

    
    
    