#!/router/bin/python3

import sys
import re
import xml.etree.ElementTree as ET
from optparse import OptionParser

usage = "usage: %prog -f|--file <Input xml file name>"
parser = OptionParser(usage=usage)
parser.add_option("-f","--file", dest="xml_file",help="Input xml file name")
(options,args) = parser.parse_args()

if options.xml_file:
        xmlFile = options.xml_file
else:
    print('Please provide input xml file name.')
    parser.print_help()
    exit()

#Function to parse xml file
def parseDeviceXML(xmlFile):
    """"""

    context = ET.iterparse(xmlFile, None, None)
    device_dict = {}
    devices = []
    for action, elem in context:
        if not elem.text:
            text = "None"
        else:
            text = elem.text
        device_dict[elem.tag] = text
        if elem.tag == "device":
            device_dict['id'] = elem.attrib['id']
            devices.append(device_dict)
            device_dict = {}
    return devices

#Function to extract interface list from xml input
def extractInterfaceList(interfaces):
    interface_list = []
    for int_range in interfaces.split(','):
        if re.search("-",int_range):
            start_int = int_range.split("-")[0]
            end_int = int_range.split("-")[1]
            temp_lst = list(start_int)
            start_index = start_int.split("/")[-1]
            interface_prefix = "/".join(start_int.split("/")[0:-1])
            interface_prefix = interface_prefix + "/"
            end_index = end_int           
            for i in range(int(start_index),int(end_index) + 1):
                intf_name = interface_prefix + str(i)
                interface_list.append(intf_name)
        else:
            interface_list.append(int_range)
    return interface_list
#Parse xml & store data
devices = parseDeviceXML(xmlFile)


print('\n\nPLEASE VERIFY THE GENERATED CONFIGURATIONS BEFORE LOADING IT ON THE DEVICE\n')
for dev in devices:
    print('\n\n****************************************')
    print('Configuration for Device "' + dev['id'] + '"' )
    print('\n****************************************\n')
    if 'upstream_interface' in dev:
        upstream_interface = dev['upstream_interface']
    else:
        print('Upstream interface for device ' + dev['id'] + \
                ' missing. Please update the input file')
        exit()
    if 'hostname' in dev:
        prompt = dev['hostname'] + ".*#" + "|ios.*#"
    else:
        prompt = "ios.*#"
    if 'bridge_group' in dev:
        bridge_group = dev['bridge_group']
    else:
        bridge_group = "autonomic"
    if 'bridge_domain' in dev:
        bridge_domain = dev['bridge_domain']
    else:
        bridge_domain = "autonomic"
    if 'sub_int_id' in dev:
        sub_int_id = dev['sub_int_id']
    else:
        sub_int_id = 4000
    print('configure terminal')
    #Check whether interfaces are specified
    if 'interfaces' in dev:
        interface_name_list = extractInterfaceList(dev['interfaces'])
    else:     
        print('Interface list for device ' + dev['id'] + \
                ' missing.Please update the input file')
        exit()
    #For each interface configure subinterface & enable encapsulation default
    for interface in interface_name_list:
        sub_interface = interface + "." + str(sub_int_id)
        print('interface ' + sub_interface + ' l2transport')
        print(' encapsulation default\n exit')
    #Configure l2vpn & bridge group
    print('l2vpn\n bridge group ' + bridge_group + '\n  bridge-domain ' + bridge_domain)
    for interface in interface_name_list:
        sub_interface = interface + "." + str(sub_int_id)
        sub_interface = sub_interface.replace(' ','')
        print('   interface ' + sub_interface)
        upstream_interface = upstream_interface.replace(' ','')
        if re.search(upstream_interface,sub_interface,re.IGNORECASE):            
            print('    exit')
        else:
            print('    split-horizon group')
            print('    exit')
    print(' end')
