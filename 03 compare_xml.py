# 對比xml，並顯示不同之處
import os
import global_variable as gv
import re
import xml.etree.ElementTree as ET
import pandas as pd 

def reprocess_string(input_string):
    input_string = re.sub('<TDSUFFIX2>.*</TDSUFFIX2>', '', input_string)
    input_string = re.sub('<TDCOVTITLE>.*</TDCOVTITLE>', '', input_string)
    input_string = re.sub('<TDDEST>.*</TDDEST>', '', input_string)
    input_string = re.sub('<TIMESTAMP>.*</TIMESTAMP>', '', input_string)
    input_string = re.sub('<CORR_KEY>.*?</CORR_KEY>', '', input_string)
    input_string = re.sub('<CORR_REQ_CREATION_DATE>.*</CORR_REQ_CREATION_DATE>', '', input_string)
    return input_string

def find_differences(elem1, elem2, path='.'):
    differences = []

    if elem1.tag != elem2.tag:
        differences.append({"Path": path, "Type": "Tag Mismatch", "Description": f"{elem1.tag} != {elem2.tag}"})
        
    if elem1.attrib != elem2.attrib:
        differences.append({"Path": path, "Type": "Attribute Mismatch", "Description": f"{elem1.attrib} != {elem2.attrib}"})
        
    if elem1.text != elem2.text:
        differences.append({"Path": path, "Type": "Text Mismatch", "Description": f"{elem1.text} != {elem2.text}"})

    children1 = list(elem1)
    children2 = list(elem2)
    
    for idx, (child1, child2) in enumerate(zip(children1, children2)):
        child_path = f"{path}/{child1.tag}[{idx}]"
        differences.extend(find_differences(child1, child2, path=child_path))

    if len(children1) > len(children2):
        for idx, child in enumerate(children1[len(children2):]):
            differences.append({"Path": f"{path}/{child.tag}[{len(children2)+idx}]", "Type": "Missing in second tree", "Description": "Element is missing"})
    elif len(children1) < len(children2):
        for idx, child in enumerate(children2[len(children1):]):
            differences.append({"Path": f"{path}/{child.tag}[{len(children1)+idx}]", "Type": "Missing in first tree", "Description": "Element is missing"})

    return differences

output_df = pd.DataFrame()

for file in os.listdir(gv.before_file_directory):
    before_file = open(os.path.join(gv.before_file_directory, file), "r", encoding="utf-8")
    before_file_string = before_file.read()
    before_file.close()
    before_file_string = reprocess_string(before_file_string)

    after_file = open(os.path.join(gv.after_file_directory, file), "r", encoding="utf-8")
    after_file_string = after_file.read()
    after_file.close()
    after_file_string = reprocess_string(after_file_string)

    if before_file_string != after_file_string:
        before_tree = ET.ElementTree(ET.fromstring(before_file_string))
        before_root = before_tree.getroot()

        after_tree = ET.ElementTree(ET.fromstring(after_file_string))
        after_root = after_tree.getroot()

        differences = find_differences(before_root, after_root, path=file)
        output_df = pd.concat([output_df, pd.DataFrame(differences)].reset_index(drop=True), axis=0)

output_df.to_excel(os.path.join(gv.result_directory, file + ".xlsx"), index=False, encoding="utf-8-sig")



