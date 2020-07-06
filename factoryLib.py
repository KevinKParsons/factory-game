from PyQt5 import QtCore, QtWidgets, QtGui


class machineLib:
    def __init__(self):
        self.lib = {
            'Starter': {
                'unlock': 0,                # Unlocked by default
                'buildCost': 1000,
                'opCost': 5,
                'opTime': 3,
                'description': 'Launches new basic resources. Each basic resource must be purchased. \
                               Maximum of 10 Starters can be placed per assembly line without additional research.',
                'imageTop': QtGui.QPixmap('images/Starter.gif'),
                'imageBottom': QtGui.QPixmap('images/MachineBottom.gif'),
                'imageComposite': QtGui.QPixmap('images/Starter Composite.gif').scaled(40, 40),
                'blueprintType': 'Basic',
                },
            'Seller': {
                'unlock': 0,                # Unlocked by default
                'buildCost': 5000,
                'opCost': 0,
                'opTime': 0,
                'description': 'Sells resources.',
                'imageTop': QtGui.QPixmap('images/Seller.gif'),
                'imageBottom': QtGui.QPixmap('images/MachineBottom.gif'),
                'imageComposite': QtGui.QPixmap('images/Seller Composite.gif').scaled(40, 40),
            },
            'Crafter': {
                'unlock': 80000,
                'buildCost': 20000,
                'opCost': 5,
                'opTime': 3,
                'description': 'Creates new resources using blueprints.',
                'imageTop': QtGui.QPixmap('images/Crafter.gif'),
                'imageBottom': QtGui.QPixmap('images/MachineBottom.gif'),
                'imageComposite': QtGui.QPixmap('images/Crafter Composite.gif').scaled(40, 40),
                'blueprintType': 'Tier2',
                },
            'Roller': {
                'unlock': 5000,
                'buildCost': 300,
                'opCost': 0,
                'opTime': 0,
                'description': 'Moves resources around the factory.',
                'imageTop': QtGui.QPixmap('images/Blank.gif'),
                'imageBottom': QtGui.QPixmap('images/Roller.gif'),
                'imageComposite': QtGui.QPixmap('images/Roller Composite.gif').scaled(40, 40),
                },
            'Drawer': {
                'unlock': 40000,
                'buildCost': 10000,
                'opCost': 5,
                'opTime': 3,
                'description': 'Creates wire by consuming basic resources.',
                'imageTop': QtGui.QPixmap('images/Drawer.gif'),
                'imageBottom': QtGui.QPixmap('images/MachineBottom.gif'),
                'imageComposite': QtGui.QPixmap('images/Drawer Composite.gif').scaled(40, 40),
                'blueprintType': 'Wire',
                },
            'Cutter': {
                'unlock': 30000,
                'buildCost': 10000,
                'opCost': 5,
                'opTime': 3,
                'description': 'Creates gears by consuming basic resources.',
                'imageTop': QtGui.QPixmap('images/Cutter.gif'),
                'imageBottom': QtGui.QPixmap('images/MachineBottom.gif'),
                'imageComposite': QtGui.QPixmap('images/Cutter Composite.gif').scaled(40, 40),
                'blueprintType': 'Gear',
                },
            'Furnace': {
                'unlock': 20000,
                'buildCost': 10000,
                'opCost': 5,
                'opTime': 3,
                'description': 'Creates liquid by consuming basic resources.',
                'imageTop': QtGui.QPixmap('images/Furnace.gif'),
                'imageBottom': QtGui.QPixmap('images/MachineBottom.gif'),
                'imageComposite': QtGui.QPixmap('images/Furnace Composite.gif').scaled(40, 40),
                'blueprintType': 'Liquid',
                },
            'Press': {
                'unlock': 300000,
                'buildCost': 10000,
                'opCost': 5,
                'opTime': 3,
                'description': 'Creates plate by consuming basic resources.',
                'imageTop': QtGui.QPixmap('images/Press.gif'),
                'imageBottom': QtGui.QPixmap('images/MachineBottom.gif'),
                'imageComposite': QtGui.QPixmap('images/Press Composite.gif').scaled(40, 40),
                'blueprintType': 'Plate',
                },
            'Splitter Left': {                                    
                'unlock': 600000,
                'buildCost': 10000,
                'opCost': 5,
                'opTime': 1,
                'description': 'Splits incoming material in different directions',
                'imageTop': QtGui.QPixmap('images/Splitter Left.gif'),
                'imageBottom': QtGui.QPixmap('images/MachineBottom.gif'),
                'imageComposite': QtGui.QPixmap('images/Splitter Left Composite.gif').scaled(40, 40),
                },
            'Splitter Right': {                                    
                'unlock': 600000,
                'buildCost': 10000,
                'opCost': 5,
                'opTime': 1,
                'description': 'Splits incoming material in different directions',
                'imageTop': QtGui.QPixmap('images/Splitter Right.gif'),
                'imageBottom': QtGui.QPixmap('images/MachineBottom.gif'),
                'imageComposite': QtGui.QPixmap('images/Splitter Right Composite.gif').scaled(40, 40),
                },
            'Splitter Tee': {                                    
                'unlock': 600000,
                'buildCost': 10000,
                'opCost': 5,
                'opTime': 1,
                'description': 'Splits incoming material in different directions',
                'imageTop': QtGui.QPixmap('images/Splitter Tee.gif'),
                'imageBottom': QtGui.QPixmap('images/MachineBottom.gif'),
                'imageComposite': QtGui.QPixmap('images/Splitter Tee Composite.gif').scaled(40, 40),
                },
            'Splitter 3-Way': {                                    
                'unlock': 1000000,
                'buildCost': 10000,
                'opCost': 5,
                'opTime': 1,
                'description': 'Splits incoming material in different directions',
                'imageTop': QtGui.QPixmap('images/Splitter 3-Way.gif'),
                'imageBottom': QtGui.QPixmap('images/MachineBottom.gif'),
                'imageComposite': QtGui.QPixmap('images/Splitter 3-Way Composite.gif').scaled(40, 40),
                },
            'Filter Left': {
                'unlock': 300000,
                'buildCost': 10000,
                'opCost': 2,
                'opTime': 1,
                'description': 'Splits material based on filter selection.',
                'imageTop': QtGui.QPixmap('images/Filter Left.gif'),
                'imageBottom': QtGui.QPixmap('images/MachineBottom.gif'),
                'imageComposite': QtGui.QPixmap('images/Filter Left Composite.gif').scaled(40, 40),
                },
            'Filter Right': {
                'unlock': 500000,
                'buildCost': 10000,
                'opCost': 2,
                'opTime': 1,
                'description': 'Splits material based on filter selection.',
                'imageTop': QtGui.QPixmap('images/Filter Right.gif'),
                'imageBottom': QtGui.QPixmap('images/MachineBottom.gif'),
                'imageComposite': QtGui.QPixmap('images/Filter Right Composite.gif').scaled(40, 40),
                },
            'Filter Tee': {
                'unlock': 500000,
                'buildCost': 10000,
                'opCost': 2,
                'opTime': 1,
                'description': 'Splits material based on filter selection.',
                'imageTop': QtGui.QPixmap('images/Filter Tee.gif'),
                'imageBottom': QtGui.QPixmap('images/MachineBottom.gif'),
                'imageComposite': QtGui.QPixmap('images/Filter Tee Composite.gif').scaled(40, 40),
                },
            'Robotic Arm': {
                'unlock': 400000,
                'buildCost': 10000,
                'opCost': 2,
                'opTime': 1,
                'description': 'Picks up material and moves it drop off zone.',
                'imageTop': QtGui.QPixmap('images/Blank.gif'),
                'imageBottom': QtGui.QPixmap('images/Robotic Arm Base.gif'),
                'imageComposite': QtGui.QPixmap('images/Robotic Arm Composite.gif').scaled(40, 40),
                'imageLink1': QtGui.QPixmap('images/Robotic Arm Link 1.gif'),
                'imageLink2': QtGui.QPixmap('images/Robotic Arm Link 2.gif'),
                },
            'Filtered Arm': {
                'unlock': 500000,
                'buildCost': 10000,
                'opCost': 2,
                'opTime': 1,
                'description': 'Picks up selected material type and moves it drop off zone.',
                'imageTop': QtGui.QPixmap('images/Blank.gif'),
                'imageBottom': QtGui.QPixmap('images/Filtered Arm Base.gif'),
                'imageComposite': QtGui.QPixmap('images/Filtered Arm Composite.gif').scaled(40, 40),
                'imageLink1': QtGui.QPixmap('images/Robotic Arm Link 1.gif'),
                'imageLink2': QtGui.QPixmap('images/Robotic Arm Link 2.gif'),
                },
            'Teleporter Input': {
                'unlock': 250000000,
                'buildCost': 1000000,
                'opCost': 100,
                'opTime': 1,
                'description': 'Teleports materials to the Teleporter Output with matching ID.',
                'imageTop': QtGui.QPixmap('images/Teleporter Input.gif'),
                'imageBottom': QtGui.QPixmap('images/MachineBottom.gif'),
                'imageComposite': QtGui.QPixmap('images/Teleporter Input.gif').scaled(40, 40),
                },
            'Teleporter Output': {
                'unlock': 250000000,
                'buildCost': 1000000,
                'opCost': 100,
                'opTime': 1,
                'description': 'Receives teleported materials from the Teleporter Input with matching ID.',
                'imageTop': QtGui.QPixmap('images/Teleporter Output.gif'),
                'imageBottom': QtGui.QPixmap('images/MachineBottom.gif'),
                'imageComposite': QtGui.QPixmap('images/Teleporter Output.gif').scaled(40, 40),
                },
            }


class materialLib:
    def __init__(self):
        self.lib = {
            # Basic
            'Copper': {
                'value': 80,
                'cost': 5,
                'class': 'Basic',
                'image': QtGui.QPixmap('images/Copper.gif'),
                'image_qty_2': QtGui.QPixmap('images/Copper_2.gif'),
                'image_qty_3': QtGui.QPixmap('images/Copper_3.gif'),
                'maker': 'Starter',
                'unlock': 0,
                'components': {},
                },
            'Gold': {
                'value': 80,
                'cost': 5,
                'class': 'Basic',
                'image': QtGui.QPixmap('images/Gold.gif'),
                'image_qty_2': QtGui.QPixmap('images/Gold_2.gif'),
                'image_qty_3': QtGui.QPixmap('images/Gold_3.gif'),
                'maker': 'Starter',
                'unlock': 0,
                'components': {},
                },
            'Iron': {
                'value': 80,
                'cost': 5,
                'class': 'Basic',
                'color': 'seashell4',
                'image': QtGui.QPixmap('images/Iron.gif'),
                'image_qty_2': QtGui.QPixmap('images/Iron_2.gif'),
                'image_qty_3': QtGui.QPixmap('images/Iron_3.gif'),
                'maker': 'Starter',
                'unlock': 0,
                'components': {},
                },
            'Aluminum': {
                'value': 80,
                'cost': 5,
                'class': 'Basic',
                'image': QtGui.QPixmap('images/Aluminum.gif'),
                'image_qty_2': QtGui.QPixmap('images/Aluminum_2.gif'),
                'image_qty_3': QtGui.QPixmap('images/Aluminum_3.gif'),
                'maker': 'Starter',
                'unlock': 0,
                'components': {},
                },
            'Crystal': {
                'value': 80,
                'cost': 5,
                'class': 'Basic',
                'image': QtGui.QPixmap('images/Crystal.gif'),
                'image_qty_2': QtGui.QPixmap('images/Crystal_2.gif'),
                'image_qty_3': QtGui.QPixmap('images/Crystal_3.gif'),
                'maker': 'Starter',
                'unlock': 0,
                'components': {},
                },
            # Wire
            'Copper Wire': {
                'value': 100,
                'cost': 0,
                'image': QtGui.QPixmap('images/Copper Wire.gif'),
                'class': 'Wire',
                'maker': 'Drawer',
                'unlock': 0,
                'components': {
                    'Copper': 1
                    },
                },
            'Gold Wire': {
                'value': 100,
                'cost': 0,
                'image': QtGui.QPixmap('images/Gold Wire.gif'),
                'class': 'Wire',
                'maker': 'Drawer',
                'unlock': 0,
                'components': {
                    'Gold': 1
                    },
                },
            'Iron Wire': {
                'value': 100,
                'cost': 0,
                'image': QtGui.QPixmap('images/Iron Wire.gif'),
                'class': 'Wire',
                'maker': 'Drawer',
                'unlock': 0,
                'components': {
                    'Iron': 1
                    },
                },
            'Aluminum Wire': {
                'value': 100,
                'cost': 0,
                'image': QtGui.QPixmap('images/Aluminum Wire.gif'),
                'class': 'Wire',
                'maker': 'Drawer',
                'unlock': 0,
                'components': {
                    'Aluminum': 1
                    },
                },
            'Crystal Wire': {
                'value': 100,
                'cost': 0,
                'image': QtGui.QPixmap('images/Crystal Wire.gif'),
                'class': 'Wire',
                'maker': 'Drawer',
                'unlock': 0,
                'components': {
                    'Crystal': 1
                    },
                },
            # Gear
            'Copper Gear': {
                'value': 100,
                'cost': 0,
                'image': QtGui.QPixmap('images/Copper Gear.gif'),
                'class': 'Gear',
                'maker': 'Cutter',
                'unlock': 0,
                'components': {
                    'Copper': 1
                    },
                },
            'Gold Gear': {
                'value': 100,
                'cost': 0,
                'image': QtGui.QPixmap('images/Gold Gear.gif'),
                'class': 'Gear',
                'maker': 'Cutter',
                'unlock': 0,
                'components': {
                    'Gold': 1
                    },
                },
            'Iron Gear': {
                'value': 100,
                'cost': 0,
                'image': QtGui.QPixmap('images/Iron Gear.gif'),
                'class': 'Gear',
                'maker': 'Cutter',
                'unlock': 0,
                'components': {
                    'Iron': 1
                    },
                },
            'Aluminum Gear': {
                'value': 100,
                'cost': 0,
                'image': QtGui.QPixmap('images/Aluminum Gear.gif'),
                'class': 'Gear',
                'maker': 'Cutter',
                'unlock': 0,
                'components': {
                    'Aluminum': 1
                    },
                },
            'Crystal Gear': {
                'value': 100,
                'cost': 0,
                'image': QtGui.QPixmap('images/Crystal Gear.gif'),
                'class': 'Gear',
                'maker': 'Cutter',
                'unlock': 0,
                'components': {
                    'Crystal': 1
                    },
                },
            # Liquid
            'Molten Copper': {
                'value': 100,
                'cost': 0,
                'image': QtGui.QPixmap('images/Molten Copper.gif'),
                'class': 'Liquid',
                'maker': 'Furnace',
                'unlock': 0,
                'components': {
                    'Copper': 1
                    },
                },
            'Molten Gold': {
                'value': 100,
                'cost': 0,
                'image': QtGui.QPixmap('images/Molten Gold.gif'),
                'class': 'Liquid',
                'maker': 'Furnace',
                'unlock': 0,
                'components': {
                    'Gold': 1
                    },
                },
            'Molten Iron': {
                'value': 100,
                'cost': 0,
                'image': QtGui.QPixmap('images/Molten Iron.gif'),
                'class': 'Liquid',
                'maker': 'Furnace',
                'unlock': 0,
                'components': {
                    'Iron': 1
                    },
                },
            'Molten Aluminum': {
                'value': 100,
                'cost': 0,
                'image': QtGui.QPixmap('images/Molten Aluminum.gif'),
                'class': 'Liquid',
                'maker': 'Furnace',
                'unlock': 0,
                'components': {
                    'Aluminum': 1
                    },
                },
            'Molten Crystal': {
                'value': 100,
                'cost': 0,
                'image': QtGui.QPixmap('images/Molten Crystal.gif'),
                'class': 'Liquid',
                'maker': 'Furnace',
                'unlock': 0,
                'components': {
                    'Crystal': 1
                    },
                },
            # Plate
            'Copper Plate': {
                'value': 100,
                'cost': 0,
                'image': QtGui.QPixmap('images/Copper Plate.gif'),
                'class': 'Plate',
                'maker': 'Press',
                'unlock': 0,
                'components': {
                    'Copper': 1
                    },
                },
            'Gold Plate': {
                'value': 100,
                'cost': 0,
                'image': QtGui.QPixmap('images/Gold Plate.gif'),
                'class': 'Plate',
                'maker': 'Press',
                'unlock': 0,
                'components': {
                    'Gold': 1
                    },
                },
            'Iron Plate': {
                'value': 100,
                'cost': 0,
                'image': QtGui.QPixmap('images/Iron Plate.gif'),
                'class': 'Plate',
                'maker': 'Press',
                'unlock': 0,
                'components': {
                    'Iron': 1
                    },
                },
            'Aluminum Plate': {
                'value': 100,
                'cost': 0,
                'image': QtGui.QPixmap('images/Aluminum Plate.gif'),
                'class': 'Plate',
                'maker': 'Press',
                'unlock': 0,
                'components': {
                    'Aluminum': 1
                    },
                },
            'Crystal Plate': {
                'value': 100,
                'cost': 0,
                'image': QtGui.QPixmap('images/Crystal Plate.gif'),
                'class': 'Plate',
                'maker': 'Press',
                'unlock': 0,
                'components': {
                    'Crystal': 1
                    },
                },
            # Tier2
            'Circuit ': {                                # Unlocked by default for free
                'value': 350,
                'cost': 0,
                'image': QtGui.QPixmap('images/Circuit.gif'),
                'class': 'Tier2',
                'maker': 'Crafter',
                'unlock': 0,
                'components': {
                    'Copper Wire': 2,
                    'Gold': 1
                    },
                },
            'Engine': {
                'value': 400,
                'cost': 0,
                'image': QtGui.QPixmap('images/Engine.gif'),
                'class': 'Tier2',
                'maker': 'Crafter',
                'unlock': 360000,
                'components': {
                    'Iron Gear': 2,
                    'Gold Gear': 1
                    },
                },
            'Heating Coil': {
                'value': 350,
                'cost': 0,
                'image': QtGui.QPixmap('images/Heating Coil.gif'),
                'class': 'Tier2',
                'maker': 'Crafter',
                'unlock': 360000,
                'components': {
                    'Circuit ': 1,
                    'Aluminum': 2
                    },
                },
            'Cooling Coil': {
                'value': 350,
                'cost': 0,
                'image': QtGui.QPixmap('images/Cooling Coil.gif'),
                'class': 'Tier2',
                'maker': 'Crafter',
                'unlock': 360000,
                'components': {
                    'Crystal': 1,
                    'Gold': 1,
                    'Gold Wire': 1
                    },
                },
            'Light Bulb': {
                'value': 350,
                'cost': 5,
                'image': QtGui.QPixmap('images/Light Bulb.gif'),
                'class': 'Tier2',
                'maker': 'Crafter',
                'unlock': 360000,
                'components': {
                    'Cooling Coil': 1,
                    'Gold': 1,
                    'Aluminum': 1
                    },
                },
            'Clock': {
                'value': 500,
                'cost': 0,
                'image': QtGui.QPixmap('images/Clock.gif'),
                'class': 'Tier2',
                'maker': 'Crafter',
                'unlock': 540000,
                'components': {
                    'Iron': 2,
                    'Gold': 2,
                    'Copper Gear': 1,
                    },
                },
            'Antenna': {
                'value': 500,
                'cost': 0,
                'image': QtGui.QPixmap('images/Antenna.gif'),
                'class': 'Tier2',
                'maker': 'Crafter',
                'unlock': 540000,
                'components': {
                    'Crystal Wire': 4,
                    'Iron': 1
                    },
                },
            'Grill': {
                'value': 600,
                'cost': 0,
                'image': QtGui.QPixmap('images/Grill.gif'),
                'class': 'Tier2',
                'maker': 'Crafter',
                'unlock': 600000,
                'components': {
                    'Heating Coil': 1,
                    'Iron': 4
                    },
                },
            'Toaster': {
                'value': 900,
                'cost': 0,
                'image': QtGui.QPixmap('images/Toaster.gif'),
                'class': 'Tier2',
                'maker': 'Crafter',
                'unlock': 900000,
                'components': {
                    'Heating Coil': 1,
                    'Aluminum': 1,
                    'Copper': 1
                    },
                },
            'Air Conditioner': {
                'value': 900,
                'cost': 0,
                'image': QtGui.QPixmap('images/Air Conditioner.gif'),
                'class': 'Tier2',
                'maker': 'Crafter',
                'unlock': 900000,
                'components': {
                    'Circuit ': 1,
                    'Aluminum': 2
                    },
                },
            'Battery': {
                'value': 1000,
                'cost': 0,
                'image': QtGui.QPixmap('images/Battery.gif'),
                'class': 'Tier2',
                'maker': 'Crafter',
                'unlock': 1050000,
                'components': {
                    'Circuit ': 1,
                    'Aluminum': 1,
                    'Molten Aluminum': 1
                    },
                },
            'Washing Machine': {
                'value': 1100,
                'cost': 0,
                'image': QtGui.QPixmap('images/Washing Machine.gif'),
                'class': 'Tier2',
                'maker': 'Crafter',
                'unlock': 1100000,
                'components': {
                    'Engine': 1,
                    'Aluminum': 2,
                    'Copper': 2
                    },
                },
            'Solar Panel': {
                'value': 1200,
                'cost': 0,
                'image': QtGui.QPixmap('images/Solar Panel.gif'),
                'class': 'Tier2',
                'maker': 'Crafter',
                'unlock': 1170000,
                'components': {
                    'Circuit ': 1,
                    'Gold': 2,
                    'Crystal': 1
                    },
                },
            'Headphones': {
                'value': 1300,
                'cost': 0,
                'image': QtGui.QPixmap('images/Headphones.gif'),
                'class': 'Tier2',
                'maker': 'Crafter',
                'unlock': 1300000,
                'components': {
                    'Circuit ': 1,
                    'Gold Wire': 1,
                    'Crystal Wire': 1
                    },
                },
            'Processor': {
                'value': 1300,
                'cost': 0,
                'image': QtGui.QPixmap('images/Processor.gif'),
                'class': 'Tier2',
                'maker': 'Crafter',
                'unlock': 1320000,
                'components': {
                    'Circuit ': 2,
                    'Aluminum': 2
                    },
                },
            'Drill': {
                'value': 1500,
                'cost': 0,
                'image': QtGui.QPixmap('images/Drill.gif'),
                'class': 'Tier2',
                'maker': 'Crafter',
                'unlock': 1500000,
                'components': {
                    'Crystal': 2,
                    'Copper Gear': 2,
                    'Engine': 1
                    },
                },
            'Power Supply': {
                'value': 2000,
                'cost': 5,
                'image': QtGui.QPixmap('images/Power Supply.gif'),
                'class': 'Tier2',
                'maker': 'Crafter',
                'unlock': 1920000,
                'components': {
                    'Circuit ': 1,
                    'Copper Wire': 3,
                    'Iron Wire': 3
                    },
                },
            'Speaker': {
                'value': 3300,
                'cost': 0,
                'image': QtGui.QPixmap('images/Speaker.gif'),
                'class': 'Tier2',
                'maker': 'Crafter',
                'unlock': 3300000,
                'components': {
                    'Circuit ': 2,
                    'Gold Wire': 4,
                    'Crystal Wire': 4
                    },
                },
            'Radio': {
                'value': 5600,
                'cost': 0,
                'image': QtGui.QPixmap('images/Radio.gif'),
                'class': 'Tier2',
                'maker': 'Crafter',
                'unlock': 5670000,
                'components': {
                    'Circuit ': 1,
                    'Antenna': 1,
                    'Battery': 1
                    },
                },
            'Jack Hammer': {
                'value': 7000,
                'cost': 0,
                'image': QtGui.QPixmap('images/Jack Hammer.gif'),
                'class': 'Tier2',
                'maker': 'Crafter',
                'unlock': 6920000,
                'components': {
                    'Circuit ': 4,
                    'Crystal': 4,
                    'Iron Plate': 4
                    },
                },
            'TV': {
                'value': 4000,
                'cost': 5,
                'image': QtGui.QPixmap('images/TV.gif'),
                'class': 'Tier2',
                'maker': 'Crafter',
                'unlock': 7100000,
                'components': {
                    'Power Supply': 1,
                    'Circuit ': 1,
                    'Aluminum': 4
                    },
                },
            'Smartphone': {
                'value': 7300,
                'cost': 0,
                'image': QtGui.QPixmap('images/Smartphone.gif'),
                'class': 'Tier2',
                'maker': 'Crafter',
                'unlock': 7300000,
                'components': {
                    'Processor': 1,
                    'Battery': 1,
                    'Aluminum': 2
                    },
                },
            'Refrigerator': {
                'value': 7400,
                'cost': 0,
                'image': QtGui.QPixmap('images/Refrigerator.gif'),
                'class': 'Tier2',
                'maker': 'Crafter',
                'unlock': 7400000,
                'components': {
                    'Cooling Coil': 1,
                    'Aluminum': 6,
                    'Power Supply': 1
                    },
                },
            'Tablet': {
                'value': 7600,
                'cost': 0,
                'image': QtGui.QPixmap('images/Tablet.gif'),
                'class': 'Tier2',
                'maker': 'Crafter',
                'unlock': 7600000,
                'components': {
                    'Processor': 1,
                    'Battery': 2,
                    'Aluminum': 2
                    },
                },
            'Microwave': {
                'value': 8000,
                'cost': 0,
                'image': QtGui.QPixmap('images/Microwave.gif'),
                'class': 'Tier2',
                'maker': 'Crafter',
                'unlock': 8070000,
                'components': {
                    'Heating Coil': 5,
                    'Crystal Plate': 5,
                    'Aluminum Plate': 5
                    },
                },
            'Railroad Tracks': {
                'value': 8400,
                'cost': 0,
                'image': QtGui.QPixmap('images/Railroad Tracks.gif'),
                'class': 'Tier2',
                'maker': 'Crafter',
                'unlock': 8400000,
                'components': {
                    'Iron': 10,
                    'Iron Plate': 10
                    },
                },
            'Smart Watch': {
                'value': 10200,
                'cost': 0,
                'image': QtGui.QPixmap('images/Smart Watch.gif'),
                'class': 'Tier2',
                'maker': 'Crafter',
                'unlock': 10000000,
                'components': {
                    'Processor': 2,
                    'Iron Plate': 1,
                    'Aluminum Plate': 2,
                },
            },
            'Server Rack': {
                'value': 10600,
                'cost': 0,
                'image': QtGui.QPixmap('images/Server Rack.gif'),
                'class': 'Tier2',
                'maker': 'Crafter',
                'unlock': 11000000,
                'components': {
                    'Aluminum Plate': 20,
                    'Aluminum': 10
                },
            },
            'Computer': {
                'value': 11000,
                'cost': 0,
                'image': QtGui.QPixmap('images/Computer.gif'),
                'class': 'Tier2',
                'maker': 'Crafter',
                'unlock': 11000000,
                'components': {
                    'Processor': 1,
                    'Aluminum': 6,
                    'Power Supply': 1
                },
            },
            'Generator': {
                'value': 12000,
                'cost': 0,
                'image': QtGui.QPixmap('images/Generator.gif'),
                'class': 'Tier2',
                'maker': 'Crafter',
                'unlock': 12000000,
                'components': {
                    'Engine': 4,
                    'Copper Plate': 5,
                    'Gold Plate': 5
                    },
                },
            'Water Heater': {
                'value': 13000,
                'cost': 0,
                'image': QtGui.QPixmap('images/Water Heater.gif'),
                'class': 'Tier2',
                'maker': 'Crafter',
                'unlock': 13000000,
                'components': {
                    'Heating Coil': 5,
                    'Crystal Plate': 5,
                    'Aluminum Plate': 5
                    },
                },
            'Drone': {
                'value': 17200,
                'cost': 0,
                'image': QtGui.QPixmap('images/Drone.gif'),
                'class': 'Tier2',
                'maker': 'Crafter',
                'unlock': 17000000,
                'components': {
                    'Battery': 2,
                    'Processor': 2,
                    'Aluminum Plate': 4
                    },
                },
            'Circuit Board Assembly': {
                'value': 27000,
                'cost': 0,
                'image': QtGui.QPixmap('images/Circuit Board Assembly.gif'),
                'class': 'Tier2',
                'maker': 'Crafter',
                'unlock': 27000000,
                'components': {
                    'Circuit ': 20,
                    'Copper Plate': 6,
                    'Iron Plate': 6
                    },
                },
            'Oven': {
                'value': 27300,
                'cost': 0,
                'image': QtGui.QPixmap('images/Oven.gif'),
                'class': 'Tier2',
                'maker': 'Crafter',
                'unlock': 27000000,
                'components': {
                    'Heating Coil': 10,
                    'Iron Plate': 10,
                    'Iron': 10
                    },
                },
            'Laser': {
                'value': 32000,
                'cost': 0,
                'image': QtGui.QPixmap('images/Laser.gif'),
                'class': 'Tier2',
                'maker': 'Crafter',
                'unlock': 32000000,
                'components': {
                    'Battery': 6,
                    'Crystal Plate': 10,
                    'Circuit ': 6
                    },
                },
            'Advanced Engine': {
                'value': 70000,
                'cost': 0,
                'image': QtGui.QPixmap('images/Advanced Engine.gif'),
                'class': 'Tier2',
                'maker': 'Crafter',
                'unlock': 70000000,
                'components': {
                    'Engine': 50,
                    'Circuit ': 50
                    },
                },
            'Electric Generator': {
                'value': 470000,
                'cost': 0,
                'image': QtGui.QPixmap('images/Electric Generator.gif'),
                'class': 'Tier2',
                'maker': 'Crafter',
                'unlock': 470000000,
                'components': {
                    'Generator': 15,
                    'Circuit ': 50,
                    'Battery': 40
                    },
                },
            'Super Computer': {
                'value': 550000,
                'cost': 0,
                'image': QtGui.QPixmap('images/Super Computer.gif'),
                'class': 'Tier2',
                'maker': 'Crafter',
                'unlock': 550000000,
                'components': {
                    'Computer': 30,
                    'Server Rack': 10
                    },
                },
            'Electric Engine': {
                'value': 900000,
                'cost': 0,
                'image': QtGui.QPixmap('images/Electric Engine.gif'),
                'class': 'Tier2',
                'maker': 'Crafter',
                'unlock': 900000000,
                'components': {
                    'Advanced Engine': 10,
                    'Battery': 40
                    },
                },
            'AI Processor': {
                'value': 2500000,
                'cost': 0,
                'image': QtGui.QPixmap('images/AI Processor.gif'),
                'class': 'Tier2',
                'maker': 'Crafter',
                'unlock': 2500000000,
                'components': {
                    'Super Computer': 4,
                    'Circuit ': 40
                    },
                },
            'AI Robot Body': {
                'value': 2800000,
                'cost': 0,
                'image': QtGui.QPixmap('images/AI Robot Body.gif'),
                'class': 'Tier2',
                'maker': 'Crafter',
                'unlock': 2800000000,
                'components': {
                    'Electric Engine': 1,
                    'Electric Generator': 1,
                    'Aluminum': 400
                    },
                },
            'AI Robot Head': {
                'value': 5000000,
                'cost': 0,
                'image': QtGui.QPixmap('images/AI Robot Head.gif'),
                'class': 'Tier2',
                'maker': 'Crafter',
                'unlock': 5000000000,
                'components': {
                    'AI Processor': 1,
                    'Aluminum': 200
                    },
                },
            'AI Robot': {
                'value': 15000000,
                'cost': 0,
                'image': QtGui.QPixmap('images/AI Robot.gif'),
                'class': 'Tier2',
                'maker': 'Crafter',
                'unlock': 15000000000,
                'components': {
                    'AI Robot Body': 1,
                    'AI Robot Head': 1
                    },
                },
            }


class achievementLib:
    def __init__(self):
        self.lib = {
            'Sell All Items': {
                'description': 'Sell one of every item',
            },
            'Max Assembly Lines': {
                'description': 'Unlock all assembly lines',
            },
            'Unlock All Research': {
                'description': 'Unlock all research upgrades',
            },
            'Profit I': {
                'description': 'Make $1M per second',
            },
            'Profit II': {
                'description': 'Make $10M per second',
            },
            'Profit III': {
                'description': 'Make $100M per second',
            },
            'Scale I': {
                'description': 'Craft 1 items per second',
            },
            'Scale II': {
                'description': 'Craft 5 items per second',
            },
            'Scale III': {
                'description': 'Craft 10 items per second',
            },
        }

class researchLib:
    def __init__(self):
        self.lib = {
            'floorPlansFeatureUnlock': {
                'cost': 5000000,
                'description': 'Unlock use of floor plans to save and place machine layouts.',
                'type': 'floorPlanFeature',
                'amount': 1,
            },
            'OpCostReduc_1': {
                'cost': 150000,
                'description': 'Reduce the cost of electricity for each machine operation by 2.',
                'type': 'opCostModifier',
                'amount': 5,
            },
            'OpCostReduc_2': {
                'cost': 300000,
                'description': 'Reduce the cost of electricity for each machine operation by 2.',
                'type': 'opCostModifier',
                'amount': 5,
            },
            # Offsets tool standard op_time of 3s by subtracting, not a multiplier.
            'StarterCrafterOpTime_1': {
                'cost': 2000000,
                'description': 'Decrease Starter and Crafter operation time by 1 second.',
                'type': 'opTimeStarterCrafter',
                'amount': 1,
            },
            # Offsets tool standard op_time of 3s by subtracting, not a multiplier.
            'StarterCrafterOpTime_2': {
                'cost': 20000000,
                'description': 'Decrease Starter and Crafter operation time by 1 second.',
                'type': 'opTimeStarterCrafter',
                'amount': 1,
            },
            # Offsets tool standard op_time of 3s by subtracting, not a multiplier.
            'opTimeTier2Machines_1': {
                'cost': 1000000,
                'description': 'Decrease Drawer, Cutter, Furnace, Press and Crafter operation time by 1 second.',
                'type': 'opTimeTier2Machines',
                'amount': 1,
            },
            # Offsets tool standard op_time of 3s by subtracting, not a multiplier.
            'opTimeTier2Machines_2': {
                'cost': 10000000,
                'description': 'Decrease Drawer, Cutter, Furnace, Press and Crafter operation time by 1 second.',
                'type': 'opTimeTier2Machines',
                'amount': 1,
            },
            'MaxStarters_1': {
                'cost': 100000,
                'description': 'Increase max amount of Starters by 5.',
                'type': 'maxStarters',
                'amount': 5,
            },
            'MaxStarters_2': {
                'cost': 2500000,
                'description': 'Increase max amount of Starters by 5.',
                'type': 'maxStarters',
                'amount': 5,
            },
            'MaxStarters_3': {
                'cost': 5000000,
                'description': 'Increase max amount of Starters by 5.',
                'type': 'maxStarters',
                'amount': 5,
            },
            'MaxStarters_4': {
                'cost': 10000000,
                'description': 'Increase max amount of Starters by 10.',
                'type': 'maxStarters',
                'amount': 10,
            },
            'MaxStarters_5': {
                'cost': 100000000,
                'description': 'Increase max amount of Starters by 10.',
                'type': 'maxStarters',
                'amount': 10,
            },
            'MaxStarters_6': {
                'cost': 1000000000,
                'description': 'Increase max amount of Starters by 10.',
                'type': 'maxStarters',
                'amount': 10,
            },
            'MaxTransporters_1': {
                'cost': 50000000000,
                'description': 'Increase max amount of Transporters by 5.',
                'type': 'maxTransporters',
                'amount': 5,
            },
            'MaxTransporters_2': {
                'cost': 80000000000,
                'description': 'Increase max amount of Transporters by 5.',
                'type': 'maxTransporters',
                'amount': 5,
            },
            'starterMaxSpawnQuantity_1': {
                'cost': 20000000,
                'description': 'Increases Starter amount of max resources spawned at a time by 1.',
                'type': 'starterMaxSpawnQuantity',
                'amount': 1,
            },
            'starterMaxSpawnQuantity_2': {
                'cost': 200000000,
                'description': 'Increases Starter amount of max resources spawned at a time by 1.',
                'type': 'starterMaxSpawnQuantity',
                'amount': 1,
            },
        }


class imageLib:
    def __init__(self):
        self.lib = {
            'Key Lock': {
                'image': QtGui.QPixmap('images/Key Lock.gif').scaled(40, 40),
            },
            'Wall': {
                'image': QtGui.QPixmap('images/Wall.gif'),
            }
        }
