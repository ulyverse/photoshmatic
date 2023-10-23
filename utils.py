#dependency modules
import hashlib
import uuid

#custom modules
from configuration import Config
from enumeration import TextSettings


def __dir__():
    return " "

class Helper:
    def __dir__():
        return " "

    #PURE HELPER
    def try_parse(digit:str) -> float | None:
        try:
            num = float(digit)
            return num
        except:
            return None
        
    #PURE HELPER
    @classmethod
    def compare_insensitive(cls, str1:str, str2:str) -> bool:
        '''
            compare both strings case insensitivity

            returns True if strings are the same otherwise False
        '''
        return  str1.lower() == str2.lower()

    #GUI CMB PHOTOMATIC
    def get_textsettings():
        txtset = list()
        for text_setting in TextSettings:
            txtset.append(text_setting.value)
        return txtset

    #SETUP HELPER
    def get_uniq_identifier():
        return hashlib.md5((Helper.get_mad()+"hehexd").encode("utf-8")).hexdigest()
    
    #SETUP HELPER
    def get_mad():
        return ':'.join(("%012X" % uuid.getnode())[i:i+2] for i in range(0, 12, 2))

    #PHOTOMATIC HELPER
    @classmethod
    def extract_size_in_file(cls, document_name:str) -> str | list | None:
        '''
            param:
            file_name:str - must include .psd the function strips it, ex: "2XL - Lower 2022 V2.psd"

            note:
            before returning the value it removes '-' and '_' to reduce uncertainty significantly

            returns:
            the found value of config_sc_sizes either "XL" or ['S','SMALL']
        '''
        file_name_arr = document_name[:-4].replace("-"," ").replace("_"," ").split()
        for file in file_name_arr:
            for size in Config.get_sc_sizes():
                if type(size) == list:
                    for s in size:
                        if cls.compare_insensitive(s,file):
                            return size
                else:
                    if cls.compare_insensitive(size,file):
                        return size
        return None
    
    #PHOTOMATIC HELPER
    @classmethod
    def get_size_condition(cls, document) -> list[str]:
        '''
            param:
            document: document_name

            extracts the 'size' in the document_name and (see return)

            returns:
            an array of both the original str, upper and lower of the size_name or an empty list
        '''
        size_name = cls.extract_size_in_file(document)
        if size_name == None:
            return []

        if type(size_name) == list:
            condition = []
            for size in size_name:
                condition.append(size.lower())
                condition.append(size.upper())
                if len(size) > 3:
                    condition.append(size.capitalize())
            return condition
        
        return [size_name, size_name.lower(), size_name.upper(), size_name.capitalize()]