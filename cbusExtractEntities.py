from locale import format_string
from types import NoneType
import xml.etree.ElementTree as ET

cBusQoS = '0'

commentHeader = '# This file is generated from C-Bus project file, don''t modify it.\n'
commentLights = '# It is intended to be !include(d) for lights.\n'
commentSwitches = '# It is intended to be !include(d) for switches.\n'
commentSensors = '# It is intended to be included for sensors.\n'
commentEntities = '# It can be useful for copy/paste into dasboard card code.\n'

lightsYaml = open('cBusLights.yaml', 'w')
lightsYaml.write(commentHeader)
lightsYaml.write(commentLights)

switchesYaml = open('cBusSwitches.yaml', 'w')
switchesYaml.write(commentHeader)
switchesYaml.write(commentSwitches)

sensorsYaml = open('cBusSensors.yaml', 'w')
sensorsYaml.write(commentHeader)
sensorsYaml.write(commentSensors)

entitiesYaml = open('cBusEntities.yaml', 'w')
entitiesYaml.write(commentHeader)
entitiesYaml.write(commentEntities)


def writeYaml(name, address):
    cBusIcon = ''
    name = name.replace('/', '_')
    name = name.replace('.', '_')
    # determine the type based on name convention or pattern
    cBusType = 'light'  # this is default
    if name.lower() == '<unused>':
        cBusType = 'ignore'
    elif 'blind' in name.lower():
        cBusType = 'ignore'  # not doing blinds yet
    elif 'tg ' in name.lower():
        cBusType = 'ignore'  # not doing trigger groups yet
    elif 'as ' in name.lower():
        cBusType = 'ignore'  # not doing action scenes yet
    elif 'aircon' in name.lower():
        cBusType = 'switch'
        cBusIcon = 'mdi:air-conditioner'
    elif 'fan' in name.lower():
        cBusType = 'switch'
        cBusIcon = 'mdi:fan'
    elif 'light level' in name.lower():
        cBusType = 'sensor'
        cBusIcon = ''
    elif 'light sensor' in name.lower():
        cBusType = 'switch'
        cBusIcon = 'mdi:light-switch'
    elif 'switch' in name.lower():
        cBusType = 'switch'
        cBusIcon = 'mdi:light-switch'

#    hexAddr = hex(int(address))
#    inArray = (hex(int(address)) in dimmerAddrs)
    dimmable = ((hex(int(address)) in dimmerAddrs) and (cBusType == 'light'))
 #   print(name + ' is dimmable ' + str(dimmable))

    if cBusType != 'ignore':
        # write the entity
        entitiesYaml.write('  - entity: ' + cBusType +
                           '.' + name.lower().replace(' ', '_') + '\n')

        if cBusType == 'switch':
            switchesYaml.write('\n' + '    - name: ' + name + '\n')
            switchesYaml.write(
                '      state_topic: "cbus/read/254/56/' + address + '/state"' + '\n')
            switchesYaml.write(
                '      command_topic: "cbus/write/254/56/' + address + '/switch"' + '\n')
            switchesYaml.write('      payload_on: "ON"' + '\n')
            switchesYaml.write('      payload_off: "OFF"' + '\n')
            switchesYaml.write('      retain: true \n')
            if cBusIcon != '':
                switchesYaml.write('      icon: ' + cBusIcon + '\n')
            switchesYaml.write('      qos: ' + cBusQoS + '\n')
            switchesYaml.write(
                '      unique_id: cBusGroupAddr' + address + '\n')

        if cBusType == 'light':
            lightsYaml.write('\n' + '    - name: ' + name + '\n')
            lightsYaml.write(
                '      state_topic: "cbus/read/254/56/' + address + '/state"' + '\n')
            lightsYaml.write(
                '      command_topic: "cbus/write/254/56/' + address + '/switch"' + '\n')
            lightsYaml.write('      payload_on: "ON"' + '\n')
            lightsYaml.write('      payload_off: "OFF"' + '\n')
            if dimmable:
                lightsYaml.write(
                    '      brightness_state_topic: "cbus/read/254/56/' + address + '/level"' + '\n')
                lightsYaml.write(
                    '      brightness_command_topic: "cbus/write/254/56/' + address + '/ramp"' + '\n')
                lightsYaml.write('      on_command_type: "brightness"' + '\n')
                lightsYaml.write('      brightness_scale: 100\n')
            lightsYaml.write('      retain: true \n')
            if cBusIcon != '':
                lightsYaml.write('      icon: ' + cBusIcon + '\n')
            lightsYaml.write('      qos: ' + cBusQoS + '\n')
            lightsYaml.write(
                '      unique_id: cBusGroupAddr' + address + '\n')

        if cBusType == 'sensor':
            sensorsYaml.write('\n' + '    - name: ' + name + '\n')
            sensorsYaml.write(
                '      state_topic: "cbus/read/254/56/' + address + '/level"' + '\n')
            sensorsYaml.write(
                '      device_class: illuminance\n')
            if cBusIcon != '':
                sensorsYaml.write('      icon: ' + cBusIcon + '\n')
            sensorsYaml.write('      qos: ' + cBusQoS + '\n')
            sensorsYaml.write(
                '      unique_id: cBusGroupAddr' + address + '\n')

        return cBusType


project = ET.parse(
    'C:\\Program Files (x86)\\Clipsal\\C-Gate2\\tag\\BURS1303.xml')

unitCounter = 0
relayCounter = 0
dimmerAddrs = ''
for unit in project.findall('./Project/Network/Unit'):
    if unit.find('UnitType') is not None:
        if unit.find('UnitType').text == 'DIMDN4':  # Dimmer relay
            for ppAttr in unit.findall('PP'):
                if ppAttr.get('Name') == 'GroupAddress':
                    dimmerAddrs = dimmerAddrs + ' ' + ppAttr.get('Value')
            relayCounter += 1
        unitCounter += 1
    else:
        print('WARNING - Found unexpected node without a UnitType')
print(str(unitCounter) + ' units processed.')
print(str(relayCounter) + ' non dimming 12 gang relays processed.')

groupCounter = 0
for application in project.findall('./Project/Network/Application/Group'):
    if application.find('TagName') is not None and application.find('Address') is not None:
        cBusType = writeYaml(application.find('TagName').text,
                             application.find('Address').text)
        groupCounter += 1
    else:
        print('WARNING - Found unexpected group without TagName and Address')
print(str(groupCounter) + ' groups read.')

print('Done.')
