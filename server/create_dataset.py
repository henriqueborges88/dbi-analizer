import os
import json
import string 
import re

def create_dataset():
    import pandas as pd
    dirname = os.path.dirname(__file__)
    path_processed = "C:\\Users\\henri\\Desktop\\ML_Malware_Tj\\Analisys\\processed"
    dataset_path =  os.path.join(dirname, "dataset.csv")
    strings_dataset_path = os.path.join(dirname, "strings_dataset.csv")
    list_dir = os.listdir(path_processed)

    dataset = []
    dataset_strings = []
    for index, dir in enumerate(list_dir):
        sample_dir = os.path.join(path_processed, dir)
        if os.path.isdir(sample_dir):
            info_out_path = sample_dir + "\\info_out.json"
            pe_out_path = sample_dir + "\\pe_out.json"
            die_out_path = sample_dir + "\\die_out.json"
            strings_out_path = sample_dir + "\\strings_out.json" 
            
            with open (info_out_path, "r") as info_out_file:
                info_obj = json.load(info_out_file)
            with open (pe_out_path, "r") as pe_out_file:
                pe_obj = json.load(pe_out_file)
            with open (die_out_path, "r") as die_out_file:
                die_out = json.load(die_out_file)
            with open (strings_out_path, "r") as strings_out_file:
                strings_obj = json.load(strings_out_file)
            
            malware_sample = {}
            malware_sample_strings = {}
            
            malware_sample["id"] = index
            malware_sample.update(info_obj)
            malware_sample["imphash"] = pe_obj["imphash"]
            malware_sample["name"] = pe_obj["name"]
            malware_sample["size"] = pe_obj["size"]
            malware_sample["sha256"] = pe_obj["sha-256"]
            
            malware_sample["section_text_entropy"] = -1
            malware_sample["section_data_entropy"] = -1
            malware_sample["section_rdata_entropy"] = -1
            malware_sample["section_idata_entropy"] = -1
            malware_sample["section_rsrc_entropy"] = -1
        
            for section in pe_obj["PE_Sections"]:
                section_name = section["Name"]["Value"]
                section_entropy = section.get("Entropy", -1)
                if section_name.startswith("text"):
                    malware_sample["section_text_entropy"] = section_entropy
                if section_name.startswith("data"):
                    malware_sample["section_data_entropy"] = section_entropy
                if section_name.startswith("rdata"):
                    malware_sample["section_rdata_entropy"] = section_entropy
                if section_name.startswith("idata"):
                    malware_sample["section_idata_entropy"] = section_entropy
                if section_name.startswith("rsrc"):    
                    malware_sample["section_rsrc_entropy"] = section_entropy
            
            malware_sample["imported_symbols"] = ""
            for imported_symbols in pe_obj["Imported_symbols"]:
                for imported_descriptor in imported_symbols:
                    if imported_descriptor.get("DLL", None):
                        malware_sample["imported_symbols"] += " " + imported_descriptor.get("DLL", "") + "." + imported_descriptor.get("Name", "")
            
            malware_sample["detects"] = ""
            for detect in die_out["detects"][0].get("values", []):
                malware_sample["detects"] += " " + detect.get("type", "").replace(" ", "_") + "." + detect.get("name", "").replace(" ", "_")  
            
            dataset.append(malware_sample)
            
            for string in strings_obj["strings"]["static_strings"]:
                malware_sample_strings["sample_id"] = index
                malware_sample_strings["encoding"] = string["encoding"]
                malware_sample_strings["string"] = string["string"]
                dataset_strings.append(malware_sample_strings)
            
            print('Processado ' + str(index) + ' de ' + str(len(list_dir)))
    pd.DataFrame.from_dict(dataset).to_csv(dataset_path)
    pd.DataFrame.from_dict(dataset_strings).to_csv(strings_dataset_path)
            
          
def create_datasetv2():
    import pandas as pd
    dirname = os.path.dirname(__file__)
    path_processed = "C:\\Users\\henri\\Desktop\\ML_Malware_Tj\\Analisys\\processed"
    dataset_path =  os.path.join(dirname, "dataset_v5.csv")
    strings_dataset_path = os.path.join(dirname, "strings_dataset_v3.csv")
    list_dir = os.listdir(path_processed)

    dataset = []
    dataset_strings = []
    for index, dir in enumerate(list_dir):
        sample_dir = os.path.join(path_processed, dir)
        if os.path.isdir(sample_dir):
            info_out_path = sample_dir + "\\info_out.json"
            pe_out_path = sample_dir + "\\pe_out.json"
            die_out_path = sample_dir + "\\die_out.json"
            strings_out_path = sample_dir + "\\strings_out.json" 
            
            with open (info_out_path, "r") as info_out_file:
                info_obj = json.load(info_out_file)
            with open (pe_out_path, "r") as pe_out_file:
                pe_obj = json.load(pe_out_file)
            with open (die_out_path, "r") as die_out_file:
                die_out = json.load(die_out_file)
            with open (strings_out_path, "r") as strings_out_file:
                strings_obj = json.load(strings_out_file)
            
            malware_sample = {}
            malware_sample_strings = {}
            
            malware_sample["sample_name"] = info_obj["sample_name"]
            malware_sample["imported_symbols"] = ""
            malware_sample_list =[]
            for imported_symbols in pe_obj["Imported_symbols"]:
                for imported_descriptor in imported_symbols:
                    if imported_descriptor.get("DLL", ""):
                        if imported_descriptor.get("DLL", "") not in malware_sample_list:
                            malware_sample["imported_symbols"] += " " + imported_descriptor.get("DLL", "") + "." + imported_descriptor.get("Name", "")
            
            malware_sample["detects"] = ""
            for detect in die_out["detects"][0].get("values", []):
                malware_sample["detects"] += " " + detect.get("type", "").replace(" ", "_") + "." + detect.get("name", "").replace(" ", "_")  
            
            malware_sample["strings"] = ""
            sample_string_list =[]
            for s_string in strings_obj["strings"]["static_strings"]:
                if len(s_string["string"]) > 3 and s_string["string"].lower() not in sample_string_list:
                    if len(s_string["string"]) <= 50 or (len(s_string["string"]) > 50 and " " not in s_string["string"]): # chaves de registro e diretorios que não contenham espaco
                        sample_string_list.append(s_string["string"].lower())
                    
            sans_punctuation_documents = []    
            for i in sample_string_list:
                no_punc = i.translate(str.maketrans('','',string.punctuation))
                splitted_s = no_punc.split()
                significant_words = [w for w in splitted_s if len(w) > 4]
                sans_punctuation_documents.append(" ".join(significant_words))
            
            malware_sample["strings"] = " ".join(sans_punctuation_documents)
            malware_sample["strings"] = re.sub('\s{2,}', ' ', malware_sample["strings"])
            
            dataset.append(malware_sample)
            print('Processado ' + str(index) + ' de ' + str(len(list_dir)))
    pd.DataFrame.from_dict(dataset).to_csv(dataset_path)
          

def create_datasetv3():
    import pandas as pd
    dirname = os.path.dirname(__file__)
    path_processed = "C:\\Users\\henri\\Desktop\\ML_Malware_Tj\\Analisys\\processed"
    dataset_path =  os.path.join(dirname, "dataset_v6.csv")
    strings_dataset_path = os.path.join(dirname, "strings_dataset_v3.csv")
    list_dir = os.listdir(path_processed)

    dataset = []
    dataset_strings = []
    for index, dir in enumerate(list_dir):
        sample_dir = os.path.join(path_processed, dir)
        if os.path.isdir(sample_dir):
            info_out_path = sample_dir + "\\info_out.json"
            pe_out_path = sample_dir + "\\pe_out.json"
            die_out_path = sample_dir + "\\die_out.json"
            strings_out_path = sample_dir + "\\strings_out.json" 
            
            with open (info_out_path, "r") as info_out_file:
                info_obj = json.load(info_out_file)
            with open (pe_out_path, "r") as pe_out_file:
                pe_obj = json.load(pe_out_file)
            with open (die_out_path, "r") as die_out_file:
                die_out = json.load(die_out_file)
            with open (strings_out_path, "r") as strings_out_file:
                strings_obj = json.load(strings_out_file)
            
            malware_sample = {}
            malware_sample_strings = {}
            
            malware_sample["sample_name"] = info_obj["sample_name"]
            malware_sample_imports =[]
            for imported_symbols in pe_obj["Imported_symbols"]:
                for imported_descriptor in imported_symbols:
                    if imported_descriptor.get("DLL", ""):
                        if imported_descriptor.get("DLL", "") + "." + imported_descriptor.get("Name", "") not in malware_sample_imports:
                            malware_sample_imports.append(imported_descriptor.get("DLL", "") + "." + imported_descriptor.get("Name", ""))
            
            #malware_sample["detects"] = ""
            malware_sample_detects = []
            for detect in die_out["detects"][0].get("values", []):
                malware_sample_detects.append(detect.get("type", "").replace(" ", "_") + "." + detect.get("name", "").replace(" ", "_"))
            
            malware_sample["strings"] = ""
            sample_string_list =[]
            for s_string in strings_obj["strings"]["static_strings"]:
                if len(s_string["string"]) > 3 and s_string["string"].lower() not in sample_string_list:
                    if len(s_string["string"]) <= 50 or (len(s_string["string"]) > 50 and " " not in s_string["string"]): # chaves de registro e diretorios que não contenham espaco
                        sample_string_list.append(s_string["string"].lower())
                    
            sans_punctuation_documents = []    
            for i in sample_string_list:
                no_punc = i.translate(str.maketrans('','',string.punctuation))
                splitted_s = no_punc.split()
                significant_words = [w for w in splitted_s if len(w) > 4]
                sans_punctuation_documents.append(" ".join(significant_words))
            
            malware_sample_imports.sort()
            malware_sample_detects.sort()
            sans_punctuation_documents.sort()
            malware_sample["strings"] =  " ".join(malware_sample_imports) + " " + " ".join(malware_sample_detects) + " " + " ".join(sans_punctuation_documents)
            malware_sample["strings"] = re.sub('\s{2,}', ' ', malware_sample["strings"])
            
            dataset.append(malware_sample)
            print('Processado ' + str(index) + ' de ' + str(len(list_dir)))
    pd.DataFrame.from_dict(dataset).to_csv(dataset_path)
              
     

def create_datasetv4():
    import pandas as pd
    dirname = os.path.dirname(__file__)
    path_processed = "C:\\Users\\henri\\Desktop\\ML_Malware_Tj\\Analisys\\processed"
    dataset_path =  os.path.join(dirname, "dataset_v10.csv")
    strings_dataset_path = os.path.join(dirname, "strings_dataset_v3.csv")
    list_dir = os.listdir(path_processed)

    dataset = []
    dataset_strings = []
    for index, dir in enumerate(list_dir):
        sample_dir = os.path.join(path_processed, dir)
        if os.path.isdir(sample_dir):
            info_out_path = sample_dir + "\\info_out.json"
            pe_out_path = sample_dir + "\\pe_out.json"
            die_out_path = sample_dir + "\\die_out.json"
            strings_out_path = sample_dir + "\\strings_out.json" 
            
            with open (info_out_path, "r") as info_out_file:
                info_obj = json.load(info_out_file)
            with open (pe_out_path, "r") as pe_out_file:
                pe_obj = json.load(pe_out_file)
            with open (die_out_path, "r") as die_out_file:
                die_out = json.load(die_out_file)
            with open (strings_out_path, "r") as strings_out_file:
                strings_obj = json.load(strings_out_file)
            
            malware_sample = {}
            malware_sample_strings = {}
            
            malware_sample["sample_name"] = ".".join(info_obj["sample_name"].split(".")[:3]).replace("UDS-", "").replace("VHO-", "").replace("HEUR-", "")
            #malware_sample["imphash"] = pe_obj["imphash"]
            #malware_sample["name"] = pe_obj["name"]
            #malware_sample["size"] = pe_obj["size"]
            #malware_sample["sha256"] = pe_obj["sha-256"]
            
            # malware_sample["section_text_entropy"] = -1
            # malware_sample["section_data_entropy"] = -1
            # malware_sample["section_rdata_entropy"] = -1
            # malware_sample["section_idata_entropy"] = -1
            # malware_sample["section_rsrc_entropy"] = -1
        
            text_entropy = 0.
            for section in pe_obj["PE_Sections"]:
                section_name = section["Name"]["Value"]
                section_entropy = section.get("Entropy", 1.)
                if section_name.startswith("text") or section_name.startswith(".text"):
                    text_entropy = section_entropy
            
            if text_entropy > 5.5:
                continue

            malware_sample_imports =[]
            for imported_symbols in pe_obj["Imported_symbols"]:
                for imported_descriptor in imported_symbols:
                    if imported_descriptor.get("DLL", ""):
                        if imported_descriptor.get("DLL", "") + "." + imported_descriptor.get("Name", "") not in malware_sample_imports:
                            malware_sample_imports.append("IPT_" + imported_descriptor.get("DLL", "") + "." + imported_descriptor.get("Name", ""))
            
            #malware_sample["detects"] = ""
            malware_sample_detects = []
            for detect in die_out["detects"][0].get("values", []):
                malware_sample_detects.append("DTT_" + detect.get("type", "").replace(" ", "_") + "." + detect.get("name", "").replace(" ", "_"))
            
            malware_sample["strings"] = ""
            sample_string_list =[]
            for s_string in strings_obj["strings"]["static_strings"]:
                if len(s_string["string"]) > 3 and s_string["string"].lower() not in sample_string_list:
                    if len(s_string["string"]) <= 50 or (len(s_string["string"]) > 50 and " " not in s_string["string"]): # chaves de registro e diretorios que não contenham espaco
                        sample_string_list.append(s_string["string"].lower())
                    
            sans_punctuation_documents = []    
            for i in sample_string_list:
                no_punc = i.translate(str.maketrans('','',string.punctuation))
                splitted_s = no_punc.split()
                significant_words = [w for w in splitted_s if len(w) > 4 and len(w) < 100 and ("a" in w or "e" in w or "i" in w or "o" in w or "u" in w)]
                sans_punctuation_documents.append(" ".join(significant_words))
            
            malware_sample_imports.sort()
            malware_sample_detects.sort()
            sans_punctuation_documents.sort()
            malware_sample_imports_str = " ".join(malware_sample_imports)
            malware_sample_detects_str = " ".join(malware_sample_detects)
            all_strings = " ".join(sans_punctuation_documents)
            malware_sample["strings"] = malware_sample_detects_str.strip() + " " + malware_sample_imports_str.strip() + " " + re.sub('\s{2,}', ' ', all_strings).strip()
            
            if len(malware_sample_detects_str) > 3: 
                dataset.append(malware_sample)
            print('Processando ' + str(index) + ' de ' + str(len(list_dir)))
    pd.DataFrame.from_dict(dataset).to_csv(dataset_path, index=False)
    #pd.DataFrame.from_dict(dataset_strings).to_csv(strings_dataset_path)
                       
create_datasetv4()