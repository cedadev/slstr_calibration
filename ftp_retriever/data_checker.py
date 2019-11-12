import os, sys
from data_retriever import check_safe_dir_struct
'''
Quick script to run the checker on a list of input files. 

'''


MANIFEST_FILENAME = 'xfdumanifest.xml'

ISP_DATA_FILENAME = 'ISPData.dat'
XFDUMANIFEST_DATA_XPATH_MD5= "dataObjectSection/dataObject[@ID='ISPData']/byteStream/checksum"

ISP_ANNOTATION_DATA_FILENAME = 'ISPAnnotation.dat'
XFDUMANIFEST_ANNOTATION_DATA_XPATH_MD5= "dataObjectSection/dataObject[@ID='ISPAnnotationData']/byteStream/checksum"


list_of_products_file = sys.argv[1]

listobj = open(list_of_products_file, 'r')
list_of_products = listobj.readlines()
listobj.close()

files_retrieved = {}

for product in list_of_products:
    
    #zipfile or eumetsat safe dir
    if os.path.isdir(product.rstrip()):
        product_dir = product.rstrip()
        
        manifest_file = os.path.join(product_dir,MANIFEST_FILENAME)
        isp_datafile = os.path.join(product_dir, ISP_DATA_FILENAME)
        isp_annotation_datafile = os.path.join(product_dir, ISP_ANNOTATION_DATA_FILENAME)
        
        #create the structure equivalent to that used in the data_retriever code
        files_retrieved[product_dir] = [manifest_file, isp_datafile, isp_annotation_datafile]
        
        try:
            if check_safe_dir_struct([manifest_file, isp_datafile, isp_annotation_datafile], verbose = True, remove = False):
                print "%s: OK" %product_dir
            
            else:
                print "%s: BAD" %product_dir
                
        except Exception as ex:
            print "Problem: %s" %ex