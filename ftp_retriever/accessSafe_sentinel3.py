__author__ = 'sjdd53'

"""
Set of methods to enable access to SAFE manifest files used to access parameters to aid ingestion of ESA SAFE format data

"""
NAME_SPACES = {'xfdu':'urn:ccsds:schema:xfdu:1',
            'sentinel-safe':'http://www.esa.int/safe/sentinel-1.1',
            'sentinel3':'http://www.esa.int/safe/sentinel-3/1.0',
            's1':'http://www.esa.int/safe/sentinel-1.0/sentinel-1',
            'gml':'http://www.opengis.net/gml',
            's1sar':'http://www.esa.int/safe/sentinel-1.0/sentinel-1/sar',
            's1sarl1':'http://www.esa.int/safe/sentinel-1.0/sentinel-1/sar/level-1',
            's1sarl2':'http://www.esa.int/safe/sentinel-1.0/sentinel-1/sar/level-2',
            'gx':'http://www.google.com/kml/ext/2.2',
            'm':'http://schemas.microsoft.com/ado/2007/08/dataservices/metadata',
            'd':'http://schemas.microsoft.com/ado/2007/08/dataservices',
            'atom':'http://www.w3.org/2005/Atom',
            'opensearch':'http://a9.com/-/spec/opensearch/1.1/'
            }

def appendNameSpace(path):
    '''
    Class Method to convert the given xpath to a namespace abbreviated version so elementtree can handle it (grrr.).
    Will return an equivalent namespace qualified xpath - if errors a 'null' will be placed.

    :param path:
    :return:
    '''
    
    nameSpaceAppendedPath = ''

    appendedPath = None

    path_elements = path.split('/')

    count = 0
    for element in path_elements:

        try:
            if ':' in element:
                splitElement = element.split(':')
                nsPrefix,nsElement = splitElement[0],splitElement[1]

                if count == 0:
                    appendedPath = '{' + NAME_SPACES[nsPrefix] +'}' + nsElement

                else:
                    appendedPath = appendedPath + '/{' + NAME_SPACES[nsPrefix] +'}' + nsElement

            else:
                #No namespace specified so leave it as it is
                #use default namespace

                if count == 0:
                    appendedPath = element
                else:
                    appendedPath = appendedPath + '/' + element
            count += 1

        except Exception as ex:
           print "Could not access xpath: %s" %path

    #clear up any blank namespace prefixes
    nameSpaceAppendedPath = appendedPath.replace('{}','')

    return nameSpaceAppendedPath


class safe_access(object):    

    ATTRIBUTE = 'attribute'

    ELEMENT = 'element'


    def __init__(self, path):
        '''
        Initialise all namespaces likely to be used in a SAFE manifest file
        :return:
        '''

        self.path = self.xpath_type(appendNameSpace(path))


    def xpath_type(self,instrument_xpath):
        '''
            Method to detect what type of xpath to apply
        :param xpath:
        :return: dictionary of form {xpath:{type (element|attribute):None|attr name}}
        '''

        xpath_to_extract = {}
        if instrument_xpath.split('/')[-1][0] == '@':
            attribute_val = instrument_xpath.split('/')[-1][1:]
            xpath_to_extract[instrument_xpath] = [self.ATTRIBUTE,attribute_val]

        else:
            xpath_to_extract[instrument_xpath] = [self.ELEMENT,None]

        return xpath_to_extract


    def get_safe_value(self,et_root, instrument_xpath):
        '''
        Method to extract value from SAFE file depending on what type of xpath is supplied

        :param xpath: dictionary of form {xpath:type (element|attribute}
        :return: value extracted from SAFE file

        '''

        value = None

        try:
            xpath = instrument_xpath.keys()[0]
            element_type = instrument_xpath[xpath]

        except Exception as ex:
            print "SAFE xpath object is not in correct format ('xpath':'type'"

        try:

            #detect whether pulling an attribute value or a element value
            if element_type[0] == self.ATTRIBUTE:

                #I'm sure there's a better way than doing it like this

                #trim the xpath
                xpath = xpath.replace('/@%s'%element_type[1],'')
                value = et_root.find(xpath).attrib[element_type[1]]

            elif element_type[0] == self.ELEMENT:
                value = et_root.find(xpath).text

            else:
                raise Exception ("Incorrect element type specified!")

            return value

        except Exception as ex:
            print "Could not extract value for %s (%s)" %(xpath,ex)



