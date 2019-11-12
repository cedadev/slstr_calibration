'''
Created on Jul 14, 2015

@author: sdonegan

Set of utilities to aid in the identification and retrieval of Sentinel3 SLSTR data
'''

import os, sys,re
import ftplib
from datetime import datetime,timedelta
import xml.etree.ElementTree as ET
import hashlib
import logging
from accessSafe_sentinel3 import safe_access

#DIR_TYPE = 'd'
#FILE_TYPE = '-'
#LINK_TYPE = 'l'
FTP_TYPES = {'-':'file','d':'directory','l':'link'}

def check_data_checksum(data_file, checksum):
    '''
    Method to check the actual checksum of the data against the value in the checksum file TBC
    :return:
    '''

    md5 = hashlib.md5()
    
    try: 
        datafile = open(data_file)
        
        for line in datafile:
            md5.update(line)
            
        datafile.close()
        
        actual_checksum = md5.hexdigest()
        
    except Exception as ex:
        raise Exception ("ERROR: could not open and calculate checksum for: %s (%s)" %(data_file,ex))
    
    if actual_checksum == checksum:
        return True
    
    else:
        return False


def get_xpath_value(root,xpath):
    '''
        Class method to access an xml path given an ET object and the namespace qualified xpath
    '''
        
    try: 
        pathob = safe_access(xpath)
    
        return pathob.get_safe_value(root,pathob.path)
        
    except Exception:
        return None
    

def access_xml_file(filename):
    '''
        Class method to simply open and return an xml tree structure
    '''
    
    #now access the xml
    try:
        manifest_tree = ET.parse(filename)
        root = manifest_tree.getroot()
        
        if root is None:
            raise Exception ("Could not access xml")
        
        else:
            return root
        
    except Exception as ex:
        raise Exception ("Could not parse product entry file (%s)" %ex)
        return None
    

def generate_list(options,path,files_to_retrieve):    
    '''
        Method to generate a list object used in list_data_items and Identify_retrievals
    
    '''
    
    product_cnt = 0
    file_cnt = 0
    
    listing = []
    
    try:
        
        for product in files_to_retrieve.keys():
            listing.append(os.path.join(path,product)) 
            
        return listing
            
    except Exception as ex:
        
        print "ERROR: could not generate list (%s)" %ex
        
        return None
        

def filter_dir_products(file_list):
    '''
        Method to calculate unique parent directories from a full listing
    '''
    try:
        dir_products = []
        for filename in file_list:
            dir_product = os.path.dirname(filename)
            if dir_product not in dir_products:
                dir_products.append(dir_product)
                
        return dir_products
    
    except Exception as ex:
        raise Exception ("Could not filter list of products into unique product directories (%s)" %ex)


def activate_logging(self, outputfile_stream_name_dt):
        '''
            Method to create a log file handler if required.
        '''        
        self.logfilename = '%s.log' %outputfile_stream_name_dt
        logging.basicConfig(filename=self.logfilename,level=logging.INFO,format='%(message)s')


def output_director(self, msg):
        '''
            Simple method to cut down on what to do with output depending on logging and verbose options
        '''
        if self.output_logging:                                            
            logging.info(msg) 
        
        if self.verbose:
            print'%s'%msg
            

def identify_files(config,product, path, existing_products = None, ignore_time_check = False):
    '''
        Wrapper class method to retrieve a listing of suitable files on the remote server 
        
        @arg existing_products: list of directory name products to retrieve
        
    '''
    
    #default configuration
    try:
        user = config.get('default','ftp_user')
        pw = config.get('default','ftp_pw')
        site = config.get('default','ftp_host')
        days = config.get('default','check_days_num')
        check_days = config.get('default','check_days')
        
    except Exception as ex:
        raise Exception ("ERROR: Unable to access default section of configuration(%s)" %ex)
              
    #get connection
    try:
        
        connection = Retrieve_By_FTP(user,pw,site)
        
        #get listing of directory (products beneath desired path
        dir_listing = connection.ftp_list(path)
        
        #Note products refers to the S3A_SL_* directory *NOT* like current S1A products..
        products_available = connection.find_products_of_interest(dir_listing, product, days = days, compare_time = check_days, ignore_time_check = ignore_time_check)
        
    except Exception as ex:
        print "ERROR: Could not connect to %s (%s)" %(site,ex)
          
        #close connection before doing any processing
        connection.close_ftp_connection()
        
    #automatically build upa picture of whats a directory or not..    
    files_to_retrieve = {}
    
    for product in products_available.keys():
            
        ftp_path = os.path.join(path,product)
                
        sub_files = []
        
        #get listing of directory (products beneath desired path
        try:
            dir_listing = connection.ftp_list(ftp_path)
            #raise Exception ("do something about this") 
            
            #files_to_retrieve[product] = connection.find_files(dir_listing)
            for sub_product in connection.find_files(dir_listing):
                sub_files.append(os.path.join(path,product,sub_product))
                
            files_to_retrieve[product] = sub_files
                            
        except Exception as ex:
            #if thrown then likely a file object on remote ftp rather than a directory with subsequent files
            #print "ERROR: could not retrieve files for %s (%s)" %(ftp_path,ex)
            files_to_retrieve[product] = os.path.join(path,product)
            
    #close connection before doing any processing
    connection.close_ftp_connection()
    
    return files_to_retrieve
 

def extract_s3_filename_date(filename):
    '''
        Method to extract the acquisition date attributes from the s3 filename structure
        
    '''
    #filename = os.path.basename(filename_full)
    
    year = filename[16:20] ; month = filename[20:22]; day = filename[22:24]
    
    return [year,month,day]


def create_file_list(outputlistfile, file_list):
    '''
        Method to create an outputfile containing lists of data
    '''
    
    #open a file list and write the output list to it.
    if os.path.exists(outputlistfile):
        print "%s as already exists ..will delete" %outputlistfile
        os.remove(outputlistfile)
    
    try:
        ingest_listing = open(outputlistfile,mode='w')
        
        for missing_data in file_list:
            ingest_listing.write('%s\n' %missing_data)
            
        ingest_listing.close()
        
        return True
    
    except Exception as ex:
        raise Exception ("ERROR: could not write file containing list of missing data: %s" %ex)
        
        
def open_file_list(input_file):
    '''
        Metho 
    '''
    
    try:
        ingest_listing = open(input_file,mode='r')
        ingest_list = ingest_listing.readlines()
        ingest_listing.close()
    
    except Exception as ex:
        raise Exception("ERROR: could not open list of data files to ingest: %s" %ex)
    
    try:
        file_list = []
        for line in ingest_list:
            file_list.append(line.rstrip())
        
        return file_list
    
    except Exception as ex:
        raise Exception("ERROR: could generate list of data files to ingest: %s" %ex)
    


    
    
def generate_directories(base_path, sub_path_list, verbose=False):
    '''
        Method to recursively generate paths based on contents of a list supplied.
        Typically this is intended to be year month day but could be anything else.
    '''
    
    #does it exist already in which case return quickly
    final_path = os.path.join(base_path, *sub_path_list)
    if os.path.exists(final_path):
        if verbose:
            print "Path %s exists!" %final_path
            
        return final_path
    
    path_to_generate = base_path
    
    for comp in sub_path_list:
        path_to_generate = os.path.join(path_to_generate, comp)
        
        try:
            if not os.path.exists(path_to_generate):
                #if verbose:
                    #print "Making path: %s" %path_to_generate
                    
                os.mkdir(path_to_generate)
                
            #else:
                #if verbose:
                    #print "Path %s exists" %path_to_generate
                
        except Exception as ex:
            raise Exception( "Cannot make path: %s (%s)" %(path_to_generate, ex))
        
    #check that we get what we're expecting..
    if final_path != path_to_generate:
        raise Exception ("Found path mismatch: %s != %s" %(path_to_generate,final_path))
        
    #check it worked
    if os.path.exists(path_to_generate):
        if verbose:
            print "Have created path: %s"%path_to_generate
        
        return path_to_generate
    
    else:
        return None
        

class Retrieve_By_FTP(object):
    
    def ftp_connection(self):
        '''
            Method to get FTP connection using specifed parameters
        '''
       
        try:
            self.connection = ftplib.FTP(self.host, self.username, self.password)
            
        except Exception as ex:
            raise Exception ("Could not generate FTP connection (%s)" %ex)
            
    
    def close_ftp_connection(self):
        
        try:
            self.connection.close()
            
        except Exception as ex:
            raise Exception ("Could not close connection!")
        
        
    def get_file(self,local_path,server_path,options, force = False):
        '''
            Method to retrieve file on remote ftp site.
        
            NOTE: new option force - will overwrite existing file if force set to True - otherwise will leave file already in place
        '''
        
        server_directory = os.path.dirname(server_path)
        server_filename = os.path.basename(server_path)
        local_filename = os.path.join(local_path,server_filename)

        if os.path.exists(local_filename):
            
            if force:
                msg = "WARNING: %s already exists on file system.  Replacing with remote file." %server_filename
                if options.verbose:
                    print msg
                logging.info(msg)
                
                try:
                    os.remove(local_filename)
                    
                except Exception as ex:
                    self.connection.close()
                    raise Exception ("Could not change to local directory (%s)!" %ex)                                
        
            else:
                msg = "WARNING: %s already exists on file system.  Will NOT replace." %server_filename
                    
                if options.verbose:
                    print msg
                    
                logging.info(msg)
                
                return {local_filename:False}, None        
            
        #change current local directory
        try:
            os.chdir(local_path)
            
        except Exception as ex:
            self.connection.close()
            raise Exception ("Could not change to local directory (%s)!" %ex)
        
        try:
            self.connection.cwd(server_directory)
            
        except Exception as ex:
            self.connection.close()
            raise Exception ("Could not change to remote directory(%s)!" %ex)
        
        #get the file!
        try:
                       
            local_file = open(local_filename,"wb")
            
            transfer_starttime = datetime.now()
            
            self.connection.retrbinary('RETR %s' %server_filename, local_file.write)
            
            transfer_endtime = datetime.now()
            
            local_file.close()
            
        except Exception as ex:
            self.connection.close()
            raise Exception ("Could not retrieve file to local directory(%s)!" %ex)
        
        if os.path.exists(local_filename):
            
            transfertime = transfer_endtime - transfer_starttime
            
            file_size = float(os.stat(local_filename).st_size)
            
            #transfer rate expressed as bits per second
            averaged_transfer_rate = (file_size/1024.0)/(float(transfertime.microseconds)/1000.0)
            
            if options.verbose:
                print"--------- Successfully transferred %s (%s bytes in %s secs = %s ~KB/s) --------" %(server_filename,file_size, transfertime.seconds,averaged_transfer_rate)
            
            return {local_filename:True}, averaged_transfer_rate   
        else:
            if options.verbose:
                print "Could not download: %s" %server_filename
                
            return None, None
        
    

    def ftp_list(self,path):
        '''
            Get a listing of the contents at a desired point on the remote site
        '''
        lines= []
        #change to required path
        try:
            
            self.connection.cwd(path)
            
        except Exception as ex:
            raise Exception ("Could not change to directory: %s (%s)" %(path, ex))
        
        try:
            #listing = ftp_func.dir()
            #return ftp_func.retrlines('LIST'
            self.connection.retrlines('LIST ',callback = lines.append)
            
            return lines
            
        except Exception as ex:
            raise Exception ("Could not list directory: %s (%s)" %(path, ex))
        
        
    def product_details(self, line):
        '''
            Method to return a datetime and name extracted from a sinle line in an ftp returned long listing - need to deal with all the issues involved!
            
        '''
        
        #typical neodc ftp log with files > 6m-1yr
        #-rw-r-----   1 badc     esacat1  201246951 May  1  2008 AT1_TOA_1PTRAL19970101_223515_000000008020_00043_28588_0000.E1.gz
        #-rw-r-----   1 badc     esacat1  201246951 Dec 14 16:23 AT1_TOA_1PTRAL19970101_223515_000000008020_00043_28588_0000.E1.gz -> mockup.gz
        
        #typical slstr comm ftp log with files <6m -1y
        #-rw-r--r--    1 1031       1008        388771799 Nov 26 14:35 S3A_SL_1_RBT____20130708T145541_20130708T145841_20151124T193352_0179_015_296_1620_LN2_O_NT_001.zip
        
        #typical slstr comm ftp log with files <6m -1y AND redirect
        #lrwxrwxrwx    1 1031       1008              186 Dec 14 16:23 S3A_SL_0_SLT____20130708T181107_20130708T181607_20151124T113924_0299_015_298______SVL_O_NR_001.zip -> /STORNEXT/MyVolume/home/Sentinel-3A/Output/IPF/Products/ESRIN/OPTICAL/LI_005_ROI_Europe/S3A_SL_0_SLT____20130708T181107_20130708T181607_20151124T113924_0299_015_298______SVL_O_NR_001.zip
        #lrwxrwxrwx    1 1031       1008              186 May 1 2008 S3A_SL_0_SLT____20130708T181107_20130708T181607_20151124T113924_0299_015_298______SVL_O_NR_001.zip -> /STORNEXT/MyVolume/home/Sentinel-3A/Output/IPF/Products/ESRIN/OPTICAL/LI_005_ROI_Europe/S3A_SL_0_SLT____20130708T181107_20130708T181607_20151124T113924_0299_015_298______SVL_O_NR_001.zip
        
        months = {'Jan':1,'Feb':2,'Mar':3, 'Apr' : 4, 'May':5, 'Jun':6,'Jul':7,'Aug':8, 'Sep':9, 'Oct':10, 'Nov':11, 'Dec':12}
        
        product = None
        dateval = None
        product_type = None
        
        if line[0][0] in FTP_TYPES.keys():
            product_type = FTP_TYPES[line[0][0]]
                    
        if '->' in line[-2]:
            #is this a link on the server?
            datestr = line[-4]
            daynum = line[-5]
            monthstr = line[-6]            
            product = line[-3]
                
        else:
            datestr = line[-2]            
            daynum = line[-3]
            monthstr = line[-4]            
            product = line[-1]  
        
        if ':' in datestr:
            
            year = datetime.now().year
            hr = int(datestr.split(':')[0])
            mn = int(datestr.split(':')[1])
                          
        else:
            year = int(datestr)
            hr = 0
            mn = 0
        
        dateval = datetime(year=int(year),month=int(months[monthstr]), day=int(daynum), \
                               hour = hr, minute = mn)
        
        #12/01/16- bug found in this calculation after roll over of year - check this by testing whether calculated date is BEFORE current date
        #- if it is, then due to the linux/ftp date rules then actual datetime must be previous year (any longer and it would have date specified in the string
        datediff = datetime.now() - dateval
        if datediff.days < 0:
            year = (datetime.now().year) - 1
            dateval = (dateval - timedelta(days = 366)) # fudge, lets ignore leap years for now...
            
        return dateval, product, product_type
        
    
    def find_products_of_interest(self,listing, product, days = None, compare_time = None, ignore_time_check = False):
        '''
            Method to scan the directory listing for products that match the desired template
        
        '''
        products_of_interest = {}
        
        cnt = 0
        for line in listing: 
            
            ignore = False # err on the safe side

            #'drwxr-xr-x   2 srv_s3mpc-rw grp_ftp-s3mpcl0        0 Jun 12 17:36 S3A_SL_0_SLT____20170612T000014_20170612T000514_20170612T012813_0299_018_344______SVL_O_NR_002.SEN3'

            try:
                product_dt, product_name, product_type = self.product_details(line.split())

                product_match = re.search(product,product_name)

                if product_match is not None:

                    if compare_time:

                            diff = (datetime.now()-product_dt).days

                            '''
                            print '%s %s    %s'%(cnt, product_dt, diff)
                            if diff == 5:
                                print 'here'
                            '''
                            if not ignore_time_check:
                                if diff > int(days) :
                                    ignore = True

                    #ensure we are looking at the expected directory structure
                    #NOTE 12/01/2015 - they have changed their structure!!
                    #if type[0] == 'd' and not ignore:
                    if not ignore:
                        products_of_interest[product_name] = product_type

                cnt += 1

            except Exception as ex:
                print "ERROR: unable to calculate ftp server file time(will retrieve) [%s]" % ex
                
        return products_of_interest
    

    def find_files(self,listing):
        '''
            Method to find files in a given directory and return names in a dictionary with the file sizes
        '''
        files = {}
        for line in listing:        
               
            vars = line.split()  
            
            if (vars[-1] != '.') and (vars[-1] != '..'):
                
                files[vars[-1]] = vars[4]
            
        return files   
    
    
    def __init__(self,user,pw,site):
        
        self.username = user
        self.password = pw
        self.host= site
            
        #Will raise exception if doesnt work    
        self.ftp_connection()
            
            
#from Retrieve_Data import Retrieve_Data
class PlockError(Exception): pass
class PlockPresent(PlockError): pass

class Retrieve_Lock():
    '''
        Class to provide checks on previous processes so to prevent multiple threads using same hub credentials
        
        (based on Plock from ICwrapper - but needed extra info in the lock file - ie. date of data being obtained)
        
    '''    
    def __init__(self,filename):
        
        self.filename = filename
        
        pid=self._haslock()
        if pid: raise PlockPresent("lock by process: %d"%pid)
        else: self.lock()

        
    def _haslock(self):
        """_haslock check for existence of file and check process id"""
        if os.path.exists(self.filename):
            fd = file(self.filename)
            pid = fd.readline()
            if os.path.exists("/proc/%s"%pid):
                return int(pid)
        return 0
    
    def lock(self):
        """lock create lock file and write current process id"""
        fd = file(self.filename, 'w')
        pid = os.getpid()
        fd.write("%d" % pid)
        fd.close()
        self.pid = pid
        
        
    def release(self):
        """release remove lock file to release lock"""
        os.unlink(self.filename)

     
            

