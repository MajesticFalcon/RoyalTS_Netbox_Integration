import pynetbox
import json

nb = pynetbox.api(NETBOX_URL, token=TOKEN)

#
# Define the structure of the dynamic-folder JSON
# 
class Folder:
    def __init__(self, name, connections):
        self.name = name
        self.connections = connections

    #
    # This format assumes everything is a terminal session. You can adjust the code to add additional types
    #
    def to_dict(self):
        objects = [{"Type": "TerminalConnection",
                    "TerminalConnectionType": "SSH",
                    "Name": connection["name"],
                    "ComputerName": connection["computer_name"]}
                   for connection in self.connections]
        return {"Type": "Folder", "Name": self.name, "Objects": objects}

class Connections:
    def __init__(self):
        self.folders = []

    def add_folder(self, name, connections):
        folder = Folder(name, connections)
        self.folders.append(folder)

    def to_dict(self):
        objects = [folder.to_dict() for folder in self.folders]
        return {"Objects": objects}

    def to_json(self):
        return json.dumps(self.to_dict(), indent=4)
#################

#
# Add a site filter. The current code is acceptable as well.
#
sites = nb.dcim.sites.all()

#
# Adjust these roles to match the roles that contain the devices you want to import
#
interesting_role_names = [
    'Switch',
    'Server',
    'Router',
    'Firewall',
    'AC Power PDUs'
]

#
# We only need the role_ids to match against
#
interesting_role_ids = [nb.dcim.device_roles.get(name=role).id for role in interesting_role_names ]


connections = Connections()


#
# Add all interesting devices to the connection array
#
for site in sites:
    connection_objects = []
        devices = nb.dcim.devices.filter(site_id=site.id)
        for device in devices:
            if device.device_role.id not in interesting_role_ids:
                break
            connection_objects.append(
                {
                    "name": str(device),
                    "computer_name": str(device)
                }
            )
    connections.add_folder(str(site), connection_objects)

print(connections.to_json())
