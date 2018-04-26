from xml.dom import minidom
import xml.etree.ElementTree as ElementTree
from BitbucketAPI import Bitbucket
import subprocess
import os
import sys

bitbucket_api_link = 'http://repo.microlab.club/rest/api/1.0/'

app_path = os.path.abspath(os.path.dirname(sys.argv[0]))
userfile = os.path.abspath(app_path + '/usr/user.mlbu')


class SoftwareLayer(object):
    def __init__(self, name, **kwargs):
        super(SoftwareLayer, self).__init__()
        self.name = name
        self.level = kwargs["level"] if "level" in kwargs else 100
        self.modules = dict()
        self.hasSublayers = False
        
    def __eq__(self, value):
        if isinstance(value, int):
            return self.level is value
        elif isinstance(value, str):
            return self.name is value
    
    def __call__(self, **kwargs):
        """
        hasSublayers class attribute specifies if the software layer is devieded into the sublayers
        """
        if "hasSublayers" in kwargs:
            self.hasSublayers = kwargs["hasSublayers"]
        
        """
        modules specifies the functional groups
        """
        if "modules" in kwargs:
            if isinstance(kwargs["modules"], list):
                for group_name in kwargs["modules"]:
                    self.modules.update({group_name: {}})
            else:
                self.modules.update({kwargs["modules"]: {}})
                    
        if "sublayer" in kwargs:
            if self.hasSublayers is False:
                return
            else:
                splited = kwargs["sublayer"].split('/')
                group = splited[0]
                sublayer = splited[1]
                self.modules[group].update({sublayer: {}})
             
        if "module" in kwargs:
            splited = kwargs["module"].split('/')
            if self.hasSublayers is False:
                self.modules[splited[0]].update({splited[1]:[]})
            else:
                self.modules[splited[0]][splited[1]].update({splited[2]:[]})
            
     
    def __str__(self):
        return self.name
            
    def __repr__(self):
        return self.name
            

class MicroLabPlatform(Bitbucket):
    
    def __init__(self):
        super(MicroLabPlatform, self).__init__(userfile, bitbucket_api_link)
        self.architecture = None
        
    def Get_projects(self):
        super(MicroLabPlatform, self).Get_projects()
        self.progress_string = "Load architecture data"
        self.Get_Architecture()
        self.progress_string = "Finished" 
        
        
    def Get_Architecture(self):
        lastVersion = False
        try:
            if not os.path.exists(os.path.abspath(app_path+"/00_platform_modules")) \
            or not os.path.exists(os.path.abspath(app_path+"/00_platform_modules/Architecture.mlparch")):
                url = bitbucket_api_link+"projects/MLP/repos/00_platform_modules"
                rsp = self.parse_response(url)
                if not "errors" in rsp:
                    repo = self.Get_repository_by_response(rsp)
                    subprocess.call(["git","clone",repo.http_link])
                    
                    lastVersion = True
                    
                else:
                    print(rsp)
                    print("sho?")
            else:
                os.chdir("00_platform_modules")
                subprocess.call(["git","fetch"])
                responses = os.popen("git status").readlines()
                if "Your branch is up-to-date with 'origin/master'.\n" in responses:
                    lastVersion = True
                    os.chdir("..")
                else:
                    subprocess.call(["git","pull"])
                    lastVersion = True
                    
            if lastVersion is True:
                self.architecture = []
                
                mlp = ElementTree.parse(os.path.abspath("00_platform_modules/Architecture.mlparch" if not "00_platform_modules" in os.getcwd() \
                                                        else "Architecture.mlparch")).getroot()
                unsorted_layers = [SoftwareLayer(layer.attrib['name'], level = int(layer.attrib['level'])) for layer in mlp.findall(".//layer")]
                self.architecture.extend(sorted(unsorted_layers, key=lambda layer: layer.level))
                
                for layer_structure in self.architecture:
                    layer = mlp.find(".//*[@name=\""+str(layer_structure)+"\"]")
                    if "sublayers" in layer.attrib:
                        layer_structure(hasSublayers = eval(layer.attrib["sublayers"]))
                        
                    
                    for modules in layer:
                        layer_structure(modules= modules.attrib['group'] )
                        if layer_structure.hasSublayers:
                            for sublayer in modules:
                                layer_structure(sublayer= modules.attrib['group']+"/"+sublayer.attrib['functionality'])
                                for repo in sublayer:                                                        
                                    layer_structure(module= modules.attrib['group']+"/"+sublayer.attrib['functionality']+"/"+repo.attrib['name'])
                        else:
                            for repo in modules:
                                layer_structure(module= modules.attrib['group']+"/"+repo.attrib['name'])

                    
                    print(layer_structure.modules)
                    
                #print(self.architecture)
                    
        except Exception as e:
            print(str(e))
            print("Exception")
                    
        finally:
            if "00_platform_modules" in os.getcwd():
                os.chdir("..")
            
        