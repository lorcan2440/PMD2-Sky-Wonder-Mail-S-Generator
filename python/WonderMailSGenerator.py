import math
import warnings
import random

# wm.js - DONE
# wmutils.js - DONE
# wmgenerate.js - implement WMSGen as a class


# Data for the Wonder Mail S generator.
WMSGenData = {
	# Mission type format:
	#
	# name: name of type
	# mainType: struct.mainType field
	# specialType: struct.missionSpecial field
	# clientIsTarget: boolean that sets the target to the client
	# useTargetItem: boolean that enables the targetItem box if set and true; will be disabled if not set or false
	# useTarget2: boolean that enables the secondary target box if set and true; will be disabled if not set or false
	# forceClient: if set and non-zero, sets the client to this number and disables the client box
	# forceTarget: if set and non-zero, sets the target to this number and disables the target box
	# specialFloor: special floor to include in code
	# specialFloorFromList: take a random entry from the named staticList
	# noReward: disable reward boxes
	#
	# Every mission type can have a "subTypes" array which overrides all settings for the parent.
	'missionTypes': [
		{'name': "Rescue client", 'mainType': 0, 'specialType': 0, 'clientIsTarget': True},
		{'name': "Rescue target", 'mainType': 1, 'specialType': 0},
		{'name': "Escort to target", 'mainType': 2, 'specialType': 0},
		
		{'name': "Explore with client", 'mainType': 3, 'clientIsTarget': True, 'subTypes': [
			{'name': "Normal", 'specialType': 0},
			{'name': "Sealed Chamber", 'specialType': 1, 'specialFloor': 165},
			{'name': "Golden Chamber", 'specialType': 2, 'specialFloor': 111},
			{'name': "New Dungeon (broken?)", 'specialType': 3, 'advancedOnly': True}
		]},
		
		{'name': "Prospect with client", 'mainType': 4, 'specialType': 0, 'useTargetItem': True, 'clientIsTarget': True},
		{'name': "Guide client", 'mainType': 5, 'specialType': 0, 'clientIsTarget': True},
		{'name': "Find target item", 'mainType': 6, 'specialType': 0, 'useTargetItem': True, 'clientIsTarget': True},
		{'name': "Deliver target item", 'mainType': 7, 'specialType': 0, 'useTargetItem': True, 'clientIsTarget': True},
		{'name': "Search for client", 'mainType': 8, 'specialType': 0},
		
		{'name': "Steal from target", 'mainType': 9, 'useTargetItem': True, 'subTypes': [
			{'name': "Normal", 'specialType': 0},
			{'name': "Target hidden", 'specialType': 1},
			{'name': "Target runs", 'specialType': 2}
		]},
		
		{'name': "Arrest client (Magnemite)", 'advancedOnly': True, 'mainType': 10, 'forceClient': 81, 'subTypes': [
			{'name': "Normal", 'specialType': 0},
			{'name': "Escort", 'specialType': 4},
			{'name': "Special Floor (broken)", 'specialType': 6, 'useTarget2': True, 'specialFloorFromList': "thievesden"},
			{'name': "Monster House", 'specialType': 7}
		]},
		
		# This is the same list as above, just with Magnezone.
		{'name': "Arrest client (Magnezone)", 'advancedOnly': True, 'mainType': 10, 'forceClient': 504, 'subTypes': [
			{'name': "Normal", 'specialType': 0},
			{'name': "Escort", 'specialType': 4},
			{'name': "Special Floor (broken)", 'specialType': 6, 'useTarget2': True, 'specialFloorFromList': "thievesden"},
			{'name': "Monster House", 'specialType': 7}
		]},
		
		{'name': "Challenge Request", 'mainType': 11, 'subTypes': [
			{'name': "Normal (broken)", 'specialType': 0, 'useTarget2': True, 'advancedOnly': True, 'specialFloorFromList': "challengerequest"},
			{'name': "Mewtwo", 'specialType': 1, 'forceClient': 150, 'forceTarget': 150, 'specialFloor': 145},
			{'name': "Entei", 'specialType': 2, 'forceClient': 271, 'forceTarget': 271, 'specialFloor': 146},
			{'name': "Raikou", 'specialType': 3, 'forceClient': 270, 'forceTarget': 270, 'specialFloor': 147},
			{'name': "Suicine", 'specialType': 4, 'forceClient': 272, 'forceTarget': 272, 'specialFloor': 148},
			{'name': "Jirachi", 'specialType': 5, 'forceClient': 417, 'forceTarget': 417, 'specialFloor': 149}
		]},
		
		# You can use any client/target but the game prefers them to be the same.
		{'name': "Treasure hunt", 'mainType': 12, 'specialType': 0, 'forceClient': 422, 'forceTarget': 422, 'specialFloorFromList': "treasurehunt", 'noReward': True},
		
		# Let's just use game-generated codes, these are all weird and pointless to generate and stuff.
		#{'name': "Unlock seven treasures dungeon (broken)", 'mainType': 13, 'specialType': 0}
	],
	
	'validDungeons': [
		0x01, 0x03, 0x04, 0x06, 0x07, 0x08, 0x0A, 0x0C, 0x0E, 0x11, 0x14, 0x15, 0x18,
		0x19, 0x22, 0x23, 0x2C, 0x2E, 0x2F, 0x32, 0x33, 0x3E, 0x40, 0x43, 0x46, 0x48,
		0x49, 0x4B, 0x4D, 0x4F, 0x51, 0x53, 0x55, 0x57, 0x58, 0x59, 0x5A, 0x5B, 0x5C,
		0x5D, 0x5E, 0x5F, 0x60, 0x61, 0x62, 0x63, 0x64, 0x65, 0x66, 0x67, 0x6B, 0x6C,
		0x6D, 0x6E
	],
	
	'validClients': [
		# Game extracted data
		1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15, 16, 18, 19, 
		20, 21, 22, 23, 24, 26, 27, 28, 29, 30, 32, 33, 34, 35, 36, 37, 
		38, 39, 41, 42, 43, 44, 45, 46, 48, 49, 52, 53, 54, 55, 56, 57, 
		58, 59, 60, 61, 62, 64, 65, 66, 68, 69, 70, 72, 73, 74, 75, 76, 
		77, 78, 79, 80, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 
		95, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 
		112, 114, 115, 116, 117, 118, 119, 120, 121, 123, 124, 125, 126, 127, 128, 129, 
		132, 133, 134, 135, 136, 138, 139, 140, 141, 142, 143, 147, 148, 149, 152, 153, 
		154, 155, 156, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 
		171, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 184, 185, 186, 187, 188, 
		189, 190, 193, 194, 195, 196, 198, 199, 200, 230, 231, 232, 233, 234, 235, 236, 
		237, 238, 240, 245, 246, 247, 248, 249, 250, 252, 253, 254, 255, 256, 257, 258, 
		259, 261, 262, 263, 265, 266, 267, 268, 269, 273, 274, 275, 283, 284, 287, 288, 
		289, 290, 292, 293, 295, 297, 298, 299, 300, 301, 302, 303, 305, 306, 307, 308, 
		309, 311, 312, 313, 315, 316, 317, 318, 319, 320, 321, 323, 327, 328, 332, 333, 
		334, 335, 337, 338, 339, 340, 341, 342, 343, 344, 345, 346, 347, 348, 350, 351, 
		352, 353, 354, 356, 357, 358, 359, 360, 361, 362, 363, 364, 365, 366, 367, 368, 
		370, 371, 372, 373, 374, 375, 377, 385, 386, 387, 388, 389, 391, 393, 394, 395, 
		396, 397, 398, 399, 400, 401, 402, 403, 404, 405, 406, 407, 408, 422, 423, 424, 
		426, 427, 428, 429, 430, 431, 432, 433, 435, 436, 437, 439, 441, 443, 444, 445, 
		446, 447, 448, 450, 451, 452, 453, 454, 455, 457, 458, 459, 460, 462, 463, 464, 
		465, 466, 467, 468, 469, 471, 472, 473, 474, 475, 476, 477, 478, 479, 480, 481, 
		482, 484, 485, 486, 487, 488, 489, 491, 492, 493, 494, 496, 497, 498, 499, 500, 
		501, 502, 503, 505, 507, 508, 509, 511, 512, 513, 514, 515, 518, 521
	],
	
	# Items that are not valid for use as target item (should be whitelist?)
	'badTargetItems': [0, 1, 2, 3, 4, 9],
	
	# http://bulbapedia.bulbagarden.net/wiki/Category:Male-only_Pok%C3%A9mon
	'maleOnly': [0x205, 0x6A, 0x6B, 0x108, 0x19D, 0x1C5, 0x22, 0x21, 0x80, 0x107, 0x155],
	# http://bulbapedia.bulbagarden.net/wiki/Category:Female-only_Pok%C3%A9mon
	'femaleOnly': [
		0x10D, 0x71, 0x212, 0x208, 0x1E2, 0x156, 0x7C, 0x73, 0x19C, 0x10C, 0x01F,
		0x01E, 0x109, 0x1C7, 0x1C2, 0x1C3, 0x1C4
	],
	
	# Very special case... only Female is included in the list now.
	'NIDORAN_FEMALE': 0x18,
	'NIDORAN_MALE': 0x20,
	
	'staticLists': {
		# Valid floors for treasure hunts.
		'treasurehunt': [
			114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129,
			130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144
		],
		
		# Valid floors for challenge requests.
		# This is from memory, it might be wrong.
		'challengerequest': [
			145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160
		],
		
		# Valid floors for Thieves Den missions.
		# This is from memory, it might be wrong.
		'thievesden': [
			161, 162, 163, 164, 165
		]
	}
	
	# TODO: list of dungeon floor count
}


# sky dungeon data
WMSkyDungeon = {
  0: "Test Dungeon",
  1: "Beach Cave",
  2: "Beach Cave",
  3: "Drenched Bluff",
  4: "Mt. Bristle",
  5: "Mt. Bristle",
  6: "Waterfall Cave",
  7: "Apple Woods",
  8: "Craggy Coast",
  9: "Side Path",
  10: "Mt. Horn",
  11: "Rock Path",
  12: "Foggy Forest",
  13: "Forest Path",
  14: "Steam Cave",
  15: "Steam Cave",
  16: "Steam Cave",
  17: "Amp Plains",
  18: "Amp Plains",
  19: "Amp Plains",
  20: "Northern Desert",
  21: "Quicksand Cave",
  22: "Quicksand Cave",
  23: "Underground Lake",
  24: "Crystal Cave",
  25: "Crystal Crossing",
  26: "Crystal Lake",
  27: "Chasm Cave",
  28: "Dark Hill",
  29: "Sealed Ruin",
  30: "Sealed Ruin",
  31: "Sealed Ruin",
  32: "Dusk Forest",
  33: "Deep Dusk Forest",
  34: "Treeshroud Forest",
  35: "Brine Cave",
  36: "Brine Cave",
  37: "Brine Cave",
  38: "Hidden Land",
  39: "Hidden Land",
  40: "Old Ruins",
  41: "Temporal Tower",
  42: "Temporal Tower",
  43: "Temporal Tower",
  44: "Mystifying Forest",
  45: "Mystifying Forest",
  46: "Blizzard Island",
  47: "Crevice Cave",
  48: "Crevice Cave",
  49: "Crevice Cave",
  50: "Surrounded Sea",
  51: "Miracle Sea",
  52: "Miracle Sea",
  53: "Miracle Sea",
  54: "Aegis Cave",
  55: "Regice Chamber",
  56: "Aegis Cave",
  57: "Regirock Chamber",
  58: "Aegis Cave",
  59: "Registeel Chamber",
  60: "Aegis Cave",
  61: "Regigigas Chamber",
  62: "Mt. Travail",
  63: "The Nightmare",
  64: "Spacial Rift",
  65: "Spacial Rift",
  66: "Spacial Rift",
  67: "Dark Crater",
  68: "Dark Crater",
  69: "Dark Crater",
  70: "Concealed Ruins",
  71: "Concealed Ruins",
  72: "Marine Resort",
  73: "Bottomless Sea",
  74: "Bottomless Sea",
  75: "Shimmer Desert",
  76: "Shimmer Desert",
  77: "Mt. Avalanche",
  78: "Mt. Avalanche",
  79: "Giant Volcano",
  80: "Giant Volcano",
  81: "World Abyss",
  82: "World Abyss",
  83: "Sky Stairway",
  84: "Sky Stairway",
  85: "Mystery Jungle",
  86: "Mystery Jungle",
  87: "Serenity River",
  88: "Landslide Cave",
  89: "Lush Prairie",
  90: "Tiny Meadow",
  91: "Labyrinth Cave",
  92: "Oran Forest",
  93: "Lake Afar",
  94: "Happy Outlook",
  95: "Mt. Mistral",
  96: "Shimmer Hill",
  97: "Lost Wilderness",
  98: "Midnight Forest",
  99: "Zero Isle North",
  100: "Zero Isle East",
  101: "Zero Isle West",
  102: "Zero Isle South",
  103: "Zero Isle Center",
  104: "Destiny Tower",
  107: "Oblivion Forest",
  108: "Treacherous Waters",
  109: "Southeastern Islands",
  110: "Inferno Cave",
  111: "Sky Peak",
  112: "Sky Peak",
  113: "Sky Peak",
  114: "Sky Peak",
  115: "Sky Peak",
  116: "Sky Peak",
  117: "Sky Peak",
  118: "Sky Peak",
  119: "Sky Peak",
  120: "Sky Peak",
  121: "Sky Peak",
  122: "Sky Peak",
  123: "Star Cave",
  124: "Star Cave",
  125: "Star Cave",
  126: "Star Cave",
  127: "Star Cave",
  128: "Murky Forest",
  129: "Eastern Cave",
  130: "Fortune Ravine",
  131: "Fortune Ravine",
  132: "Fortune Ravine",
  133: "Barren Valley",
  134: "Barren Valley",
  135: "Barren Valley",
  136: "Dark Wasteland",
  137: "Temporal Tower",
  138: "Temporal Tower",
  139: "Dusk Forest",
  140: "Black Swamp",
  141: "Spacial Cliffs",
  142: "Dark Ice Mountain",
  143: "Dark Ice Mountain",
  144: "Dark Ice Mountain",
  145: "Icicle Forest",
  146: "Vast Ice Mountain",
  147: "Vast Ice Mountain",
  148: "Vast Ice Mountain",
  149: "Southern Jungle",
  150: "Boulder Quarry",
  151: "Boulder Quarry",
  152: "Boulder Quarry",
  153: "Right Cave Path",
  154: "Left Cave Path",
  155: "Limestone Cavern",
  156: "Limestone Cavern",
  157: "Limestone Cavern",
  158: "Spring Cave",
  159: "Spring Cave",
  160: "Spring Cave",
  161: "Spring Cave",
  162: "Spring Cave",
  163: "Spring Cave",
  164: "Spring Cave",
  165: "Little Plains",
  166: "Mt. Clear Challenge",
  167: "River Trial Forest",
  168: "Guiding Sea",
  169: "Hidden Shopkeeper Village",
  173: "Star Cave",
  174: "Star Cave",
  175: "Armaldo's Shelter",
  176: "Luminous Spring",
  177: "Hot Spring Rescue",
  178: "Normal/Fly Maze",
  179: "Dark/Fire Maze",
  180: "Rock/Water Maze",
  181: "Grass Maze",
  182: "Elec/Steel Maze",
  183: "Ice/Ground Maze",
  184: "Fight/Psych Maze",
  185: "Poison/Bug Maze",
  186: "Dragon Maze",
  187: "Ghost Maze",
  188: "Explorer Maze",
  189: "Final Maze",
  212: "???",
  213: "Beach",
  234: "Armaldo's Shelter",
  235: "Barren Valley",
  239: "Sharpedo Bluff",
  240: "Sharpedo Bluff",
  241: "Sky Peak",
  245: "Treasure Town",
  246: "Treasure Town",
  254: "Waterfall Cave",
  255: "Secret Waterfall",
  256: "Quicksand Desert",
  259: "Beach Cave",
}

# sky item data
WMSkyItem = {
  0: "None",
  1: "Stick",
  2: "Iron Thorn",
  3: "Silver Spike",
  4: "Gold Fang",
  5: "Cacnea Spike",
  6: "Corsola Twig",
  7: "Gravelerock",
  8: "Geo Pebble",
  9: "Gold Thorn",
  10: "Rare Fossil",
  13: "No-Slip Cap",
  14: "Y-Ray Specs",
  15: "Gaggle Specs",
  16: "Mobile Scarf",
  17: "Heal Ribbon",
  18: "Twist Band",
  19: "Scope Lens",
  20: "Patsy Band",
  21: "No-Stick Cap",
  22: "Pierce Band",
  23: "Joy Ribbon",
  24: "X-Ray Specs",
  25: "Persim Band",
  26: "Power Band",
  27: "Pecha Scarf",
  28: "Insomniscope",
  29: "Warp Scarf",
  30: "Tight Belt",
  31: "Sneak Scarf",
  32: "Gold Ribbon",
  33: "Goggle Specs",
  34: "Diet Ribbon",
  35: "Trap Scarf",
  36: "Racket Band",
  37: "Def. Scarf",
  38: "Stamina Band",
  39: "Plain Ribbon",
  40: "Special Band",
  41: "Zinc Band",
  42: "Detect Band",
  43: "Space Globe",
  44: "Dodge Scarf",
  45: "Bounce Band",
  46: "Curve Band",
  47: "Whiff Specs",
  48: "No-Aim Scope",
  49: "Lockon Specs",
  50: "Munch Belt",
  51: "Pass Scarf",
  52: "Weather Band",
  53: "Friend Bow",
  54: "Beauty Scarf",
  55: "Sun Ribbon",
  56: "Lunar Ribbon",
  57: "Golden Mask",
  58: "Amber Tear",
  59: "Icy Flute",
  60: "Fiery Drum",
  61: "Terra Cymbal",
  62: "Aqua-Monica",
  63: "Rock Horn",
  64: "Grass Cornet",
  65: "Sky Melodica",
  66: "Miracle Chest",
  67: "Wonder Chest",
  68: "IQ Booster",
  69: "Heal Seed",
  70: "Oran Berry",
  71: "Sitrus Berry",
  72: "Eyedrop Seed",
  73: "Reviver Seed",
  74: "Blinker Seed",
  75: "Doom Seed",
  76: "X-Eye Seed",
  77: "Life Seed",
  78: "Rawst Berry",
  79: "Hunger Seed",
  80: "Quick Seed",
  81: "Pecha Berry",
  82: "Cheri Berry",
  83: "Totter Seed",
  84: "Sleep Seed",
  85: "Plain Seed",
  86: "Warp Seed",
  87: "Blast Seed",
  88: "Ginseng",
  89: "Joy Seed",
  90: "Chesto Berry",
  91: "Stun Seed",
  92: "Gabite Scale",
  93: "Golden Seed",
  94: "Vile Seed",
  95: "Pure Seed",
  96: "Violent Seed",
  97: "Vanish Seed",
  99: "Max Elixir",
  100: "Protein",
  101: "Calcium",
  102: "Iron",
  103: "Nectar",
  104: "Dropeye Seed",
  105: "Reviser Seed",
  106: "Slip Seed",
  107: "Via Seed",
  108: "Zinc",
  109: "Apple",
  110: "Big Apple",
  111: "Grimy Food",
  112: "Huge Apple",
  115: "Golden Apple",
  116: "Mix Elixir",
  117: "Oren Berry",
  118: "Dough Seed",
  119: "White Gummi",
  120: "Red Gummi",
  121: "Blue Gummi",
  122: "Grass Gummi",
  123: "Yellow Gummi",
  124: "Clear Gummi",
  125: "Orange Gummi",
  126: "Pink Gummi",
  127: "Brown Gummi",
  128: "Sky Gummi",
  129: "Gold Gummi",
  130: "Green Gummi",
  131: "Gray Gummi",
  132: "Purple Gummi",
  133: "Royal Gummi",
  134: "Black Gummi",
  135: "Silver Gummi",
  136: "Wonder Gummi",
  137: "Gravelyrock",
  139: "Upgrade",
  140: "King's Rock",
  141: "Thunderstone",
  142: "Deepseascale",
  143: "Deepseatooth",
  144: "Sun Stone",
  145: "Moon Stone",
  146: "Fire Stone",
  147: "Water Stone",
  148: "Metal Coat",
  149: "Leaf Stone",
  150: "Dragon Scale",
  151: "Link Cable",
  152: "Dubious Disc",
  153: "Protector",
  154: "Reaper Cloth",
  155: "Razor Fang",
  156: "Razor Claw",
  157: "Electirizer",
  158: "Magmarizer",
  159: "Oval Stone",
  160: "Dawn Stone",
  161: "Shiny Stone",
  162: "Dusk Stone",
  163: "Coronet Rock",
  164: "Mossy Rock",
  165: "Frozen Rock",
  167: "Gone Pebble",
  168: "Wander Gummi",
  169: "Prize Ticket",
  170: "Silver Ticket",
  171: "Gold Ticket",
  172: "Prism Ticket",
  173: "Mystery Part",
  174: "Secret Slab",
  178: "Wonder Egg",
  179: "Gracidea",
  180: "Sky Gift",
  182: "Key",
  183: "None",
  186: "Lost Loot",
  187: "Used TM",
  188: "Focus Punch",
  189: "Dragon Claw",
  190: "Water Pulse",
  191: "Calm Mind",
  192: "Roar",
  193: "Toxic",
  195: "Bulk Up",
  196: "Bullet Seed",
  197: "Hidden Power",
  199: "Taunt",
  200: "Ice Beam",
  201: "Blizzard",
  202: "Hyper Beam",
  203: "Light Screen",
  204: "Protect",
  206: "Giga Drain",
  207: "Safeguard",
  208: "Frustration",
  209: "SolarBeam",
  210: "Iron Tail",
  211: "Thunderbolt",
  212: "Thunder",
  213: "Earthquake",
  214: "Return",
  215: "Dig",
  216: "Psychic",
  217: "Shadow Ball",
  218: "Brick Break",
  220: "Reflect",
  221: "Shock Wave",
  222: "Flamethrower",
  223: "Sludge Bomb",
  225: "Fire Blast",
  227: "Aerial Ace",
  228: "Torment",
  229: "Facade",
  230: "Secret Power",
  231: "Rest",
  232: "Attract",
  233: "Thief",
  234: "Steel Wing",
  235: "Skill Swap",
  237: "Overheat",
  238: "Roost",
  239: "Focus Blast",
  240: "Energy Ball",
  241: "False Swipe",
  242: "Brine",
  243: "Fling",
  244: "Charge Beam",
  245: "Endure",
  246: "Dragon Pulse",
  247: "Drain Punch",
  248: "Will-O-Wisp",
  249: "Silver Wind",
  250: "Embargo",
  251: "Explosion",
  252: "Shadow Claw",
  253: "Payback",
  254: "Recycle",
  255: "Giga Impact",
  256: "Rock Polish",
  257: "Wide Slash",
  260: "Vacuum-Cut",
  261: "Dive",
  262: "Flash",
  263: "Stone Edge",
  264: "Avalanche",
  265: "Thunder Wave",
  266: "Gyro Ball",
  267: "Swords Dance",
  268: "Stealth Rock",
  269: "Psych Up",
  270: "Captivate",
  271: "Dark Pulse",
  272: "Rock Slide",
  273: "X-Scissor",
  274: "Sleep Talk",
  275: "Natural Gift",
  276: "Poison Jab",
  277: "Dream Eater",
  278: "Grass Knot",
  279: "Swagger",
  280: "Pluck",
  281: "U-turn",
  282: "Substitute",
  283: "Flash Cannon",
  284: "Trick Room",
  285: "Cut",
  286: "Fly",
  287: "Surf",
  288: "Strength",
  289: "Defog",
  290: "Rock Smash",
  291: "Waterfall",
  292: "Rock Climb",
  301: "Hail Orb",
  302: "Sunny Orb",
  303: "Rainy Orb",
  304: "Evasion Orb",
  305: "Sandy Orb",
  306: "Rocky Orb",
  307: "Snatch Orb",
  308: "See-Trap Orb",
  309: "Mug Orb",
  310: "Rebound Orb",
  311: "Lob Orb",
  312: "Switcher Orb",
  313: "Blowback Orb",
  314: "Warp Orb",
  315: "Transfer Orb",
  316: "Slow Orb",
  317: "Quick Orb",
  318: "Luminous Orb",
  319: "Petrify Orb",
  320: "Stayaway Orb",
  321: "Pounce Orb",
  322: "Trawl Orb",
  323: "Cleanse Orb",
  325: "Decoy Orb",
  326: "Slumber Orb",
  327: "Totter Orb",
  328: "Two-Edge Orb",
  329: "Silence Orb",
  330: "Escape Orb",
  331: "Scanner Orb",
  332: "Radar Orb",
  333: "Drought Orb",
  334: "Trapbust Orb",
  335: "Rollcall Orb",
  336: "Invisify Orb",
  337: "One-Shot Orb",
  338: "Identify Orb",
  340: "Shocker Orb",
  341: "Sizebust Orb",
  342: "One-Room Orb",
  343: "Fill-In Orb",
  344: "Trapper Orb",
  346: "Itemizer Orb",
  347: "Hurl Orb",
  348: "Mobile Orb",
  350: "Stairs Orb",
  351: "Longtoss Orb",
  352: "Pierce Orb",
  354: "Spurn Orb",
  355: "Foe-Hold Orb",
  356: "All-Mach Orb",
  357: "Foe-Fear Orb",
  358: "All-Hit Orb",
  359: "Foe-Seal Orb",
  362: "Link Box",
  364: "Gorgeous Box",
  365: "Gorgeous Box",
  366: "Gorgeous Box",
  367: "Heavy Box",
  368: "Heavy Box",
  369: "Heavy Box",
  370: "Shiny Box",
  371: "Shiny Box",
  372: "Shiny Box",
  373: "Nifty Box",
  374: "Nifty Box",
  375: "Nifty Box",
  376: "Dainty Box",
  377: "Dainty Box",
  378: "Dainty Box",
  379: "Glittery Box",
  380: "Glittery Box",
  381: "Glittery Box",
  382: "Pretty Box",
  383: "Pretty Box",
  384: "Pretty Box",
  385: "Deluxe Box",
  386: "Deluxe Box",
  387: "Deluxe Box",
  388: "Light Box",
  389: "Light Box",
  390: "Light Box",
  391: "Cute Box",
  392: "Cute Box",
  393: "Cute Box",
  394: "Hard Box",
  395: "Hard Box",
  396: "Hard Box",
  397: "Sinister Box",
  398: "Sinister Box",
  399: "Sinister Box",
  400: "A-Stone",
  401: "B-Stone",
  402: "C-Stone",
  403: "D-Stone",
  404: "E-Stone",
  405: "F-Stone",
  406: "G-Stone",
  407: "H-Stone",
  408: "I-Stone",
  409: "J-Stone",
  410: "K-Stone",
  411: "L-Stone",
  412: "M-Stone",
  413: "N-Stone",
  414: "O-Stone",
  415: "P-Stone",
  416: "Q-Stone",
  417: "R-Stone",
  418: "S-Stone",
  419: "T-Stone",
  420: "U-Stone",
  421: "V-Stone",
  422: "W-Stone",
  423: "X-Stone",
  424: "Y-Stone",
  425: "Z-Stone",
  426: "!-Stone",
  427: "?-Stone",
  428: "Silver Bow",
  429: "Brown Bow",
  430: "Red Bow",
  431: "Pink Bow",
  432: "Orange Bow",
  433: "Yellow Bow",
  434: "Lime Bow",
  435: "Green Bow",
  436: "Viridian Bow",
  437: "Minty Bow",
  438: "Sky Blue Bow",
  439: "Blue Bow",
  440: "Cobalt Bow",
  441: "Purple Bow",
  442: "Violet Bow",
  443: "Fuchsia Bow",
  444: "Prism Ruff",
  445: "Aqua Collar",
  446: "Volt Collar",
  447: "Fire Collar",
  448: "Light Collar",
  449: "Dusk Collar",
  450: "Virid Collar",
  451: "Icy Collar",
  452: "Pep Sash",
  453: "Counter Ruff",
  454: "Victory Belt",
  455: "Power Bangle",
  456: "Thundershard",
  457: "Fallen Star",
  458: "Fluff Dust",
  459: "Egg Shard",
  460: "Heroic Medal",
  461: "Chic Shard",
  462: "Yellow Jewel",
  463: "Red Jewel",
  464: "Blue Jewel",
  465: "Laugh Dust",
  466: "Guard Sand",
  467: "Purple Jewel",
  468: "White Jewel",
  469: "Brave Dust",
  470: "Heal Dew",
  471: "Marine Cache",
  472: "Freeze Veil",
  473: "Thunder Veil",
  474: "Fire Veil",
  475: "Havoc Robe",
  476: "Life Ring",
  477: "Bolt Fang",
  478: "Flare Fang",
  479: "Aqua Mantle",
  480: "Silver Veil",
  481: "Rainbow Veil",
  482: "Chrono Veil",
  483: "Rock Sash",
  484: "Ice Sash",
  485: "Steel Sash",
  486: "Heart Brooch",
  487: "Eon Veil",
  488: "Seabed Veil",
  489: "Terra Ring",
  490: "SkyHigh Veil",
  491: "Wish Mantle",
  492: "Revive Robe",
  493: "Shadow Veil",
  494: "Plasma Veil",
  495: "Edify Robe",
  496: "Charity Robe",
  497: "Hope Robe",
  498: "Time Shield",
  499: "Air Blade",
  500: "Searing Ring",
  501: "Ancient Ring",
  502: "Nether Veil",
  503: "Lunar Veil",
  504: "Tidal Cape",
  505: "Eclipse Robe",
  506: "White Silk",
  507: "Normal Dust",
  508: "White Gem",
  509: "Joy Globe",
  510: "Red Silk",
  511: "Fire Dust",
  512: "Fiery Gem",
  513: "Fiery Globe",
  514: "Blue Silk",
  515: "Water Dust",
  516: "Aqua Gem",
  517: "Aqua Globe",
  518: "Grass Slik",
  519: "Grass Dust",
  520: "Grass Gem",
  521: "Soothe Globe",
  522: "Yellow Globe",
  523: "Thunder Dust",
  524: "Thunder Gem",
  525: "Volt Globe",
  526: "Clear Silk",
  527: "Icy Dust",
  528: "Icy Gem",
  529: "Icy Globe",
  530: "Orange Silk",
  531: "Courage Dust",
  532: "Fight Gem",
  533: "Power Globe",
  534: "Pink Silk",
  535: "Poison Dust",
  536: "Poison Gem",
  537: "Poison Globe",
  538: "Brown Silk",
  539: "Ground Dust",
  540: "Earth Gem",
  541: "Terra Globe",
  542: "Sky Silk",
  543: "Sky Dust",
  544: "Sky Gem",
  545: "Sky Globe",
  546: "Gold Silk",
  547: "Psyche Dust",
  548: "Psyche Gem",
  549: "Psyche Globe",
  550: "Green Silk",
  551: "Wonder Dust",
  552: "Guard Gem",
  553: "Defend Globe",
  554: "Gray Silk",
  555: "Rock Dust",
  556: "Stone Gem",
  557: "Rock Globe",
  558: "Purple Silk",
  559: "Shady Dust",
  560: "Shadow Gem",
  561: "Nether Globe",
  562: "Royal Silk",
  563: "Dragon Dust",
  564: "Dragon Gem",
  565: "Dragon Globe",
  566: "Black Silk",
  567: "Dark Dust",
  568: "Dark Gem",
  569: "Dusk Globe",
  570: "Iron Silk",
  571: "Steel Dust",
  572: "Metal Gem",
  573: "Steel Globe",
  574: "Bulba-Claw",
  575: "Bulba-Fang",
  576: "Grass-Guard",
  577: "Leafy Tie",
  578: "Ivy-Claw",
  579: "Ivy-Fang",
  580: "Ivy-Crest",
  581: "Plant Torc",
  582: "Venus-Claw",
  583: "Venus-Fang",
  584: "Venus-Seal",
  585: "Solar Sash",
  586: "Char-Claw",
  587: "Char-Fang",
  588: "Fiery Heart",
  589: "Heat Armlet",
  590: "Charme-Claw",
  591: "Charme-Fang",
  592: "Charme-Crest",
  593: "Kindle Scarf",
  594: "Chariz-Claw",
  595: "Chariz-Fang",
  596: "Chariz-Seal",
  597: "Flame Bangle",
  598: "Squirt-Foam",
  599: "Squirt-Card",
  600: "Water-Guard",
  601: "Aqua Tie",
  602: "Wartor-Claw",
  603: "Wartor-Fang",
  604: "Wartor-Crest",
  605: "BubbleBangle",
  606: "Blasto-Claw",
  607: "Blasto-Card",
  608: "Blasto-Seal",
  609: "Hydro Band",
  610: "Pichu Hair",
  611: "Pichu Card",
  612: "Express Tag",
  613: "Shocker Cape",
  614: "Pikachu Hair",
  615: "Pikachu Card",
  616: "Volt Charm",
  617: "Volt Torc",
  618: "Raichu Hair",
  619: "Raichu Card",
  620: "Raichu Crest",
  621: "Zapper Scarf",
  622: "Meowth Claw",
  623: "Meowth Fang",
  624: "Coin Charm",
  625: "Bling Ruff",
  626: "Persian Claw",
  627: "Persain Fang",
  628: "Insight Rock",
  629: "Noble Scarf",
  630: "Chiko-Claw",
  631: "Chiko-Card",
  632: "Dawn Jewel",
  633: "Fresh Bow",
  634: "Bayleef Claw",
  635: "Bayleef Card",
  636: "Bayleef Seal",
  637: "Spice Bow",
  638: "Megani-Claw",
  639: "Megani-Card",
  640: "Shiny Charm",
  641: "Bright Veil",
  642: "Cynda-Hair",
  643: "Cynda-Claw",
  644: "Blazing Rock",
  645: "Storm Sash",
  646: "Quila-Hair",
  647: "Quila-Card",
  648: "Quila-Crest",
  649: "Volcano Torc",
  650: "Typhlo-Gasp",
  651: "Typhlo-Fang",
  652: "Typhlo-Seal",
  653: "Blast Bangle",
  654: "Totodi-Dew",
  655: "Totodi-Fang",
  656: "Water Heart",
  657: "Wash Bow",
  658: "Croco-Fang",
  659: "Croco-Card",
  660: "Swirl Rock",
  661: "Anger Scarf",
  662: "Feral-Claw",
  663: "Feral-Fang",
  664: "Feral-Crest",
  665: "Hydro Jaw",
  666: "Treeck-Thorn",
  667: "Treeck-Card",
  668: "Forest Ore",
  669: "Guard Ring",
  670: "Grovy-Shoot",
  671: "Grovy-Card",
  672: "Jungle-Tag",
  673: "Grass Blade",
  674: "Scept-Claw",
  675: "Scept-Card",
  676: "Scept-Seal",
  677: "Drain Bangle",
  678: "Torchic Hair",
  679: "Torchic Card",
  680: "Hot Pebble",
  681: "Fire Cape",
  682: "Combus-Sweat",
  683: "Combus-Claw",
  684: "Charge Tag",
  685: "Gutsy Band",
  686: "Blazi-Claw",
  687: "Blazi-Card",
  688: "Blazi-Seal",
  689: "Blaze Torc",
  690: "Mudkip Mud",
  691: "Mudkip Card",
  692: "Mud Jewel",
  693: "Speed Scarf",
  694: "Marsh-Mud",
  695: "Marsh-Card",
  696: "Marsh-Crest",
  697: "Marsh Torc",
  698: "Swamp-Mud",
  699: "Swamp-Card",
  700: "Swamp-Seal",
  701: "Swamp Bangle",
  702: "Skitty Fang",
  703: "Skitty Card",
  704: "Smile Pebble",
  705: "Heal Pendant",
  706: "Delcat-Hair",
  707: "Delcat-Fang",
  708: "Prim Pebble",
  709: "Guard Collar",
  710: "Lucky Leaf",
  711: "Turtwig Card",
  712: "Sprout Rock",
  713: "Leafy Hat",
  714: "Grotle Twig",
  715: "Grotle Claw",
  716: "Grotle Crest",
  717: "Woody Scarf",
  718: "Tort-Claw",
  719: "Tort-Horn",
  720: "Tort-Seal",
  721: "Forest Torc",
  722: "Chim-Hair",
  723: "Chim-Fang",
  724: "Nimble Charm",
  725: "Ember Cap",
  726: "Monfer-Hair",
  727: "Monfer-Fang",
  728: "Monfer-Crest",
  729: "Burst Sash",
  730: "Infern-Hair",
  731: "Infern-Fang",
  732: "Infern-Seal",
  733: "Blazing Ruff",
  734: "Piplup Foam",
  735: "Piplup Card",
  736: "Sea Ore",
  737: "Water Cape",
  738: "Prin-Foam",
  739: "Prin-Card",
  740: "Prin-Crest",
  741: "Aqua Blade",
  742: "Empol-Claw",
  743: "Empol-Horn",
  744: "Empol-Seal",
  745: "Marine Crown",
  746: "Munch Drool",
  747: "Munch-Claw",
  748: "Tummy Charm",
  749: "Glutton Cape",
  750: "Snorlax Gasp",
  751: "Snorlax Fang",
  752: "Valor Charm",
  753: "Glee Scarf",
  754: "Scyther Fang",
  755: "Scyther Card",
  756: "Ambush Rock",
  757: "Strike Ruff",
  758: "Scizor Wing",
  759: "Scizor Card",
  760: "Steel Charm",
  761: "Red Armlet",
  762: "Lapras Song",
  763: "Lapras Card",
  764: "Wavy Charm",
  765: "Mystic Scarf",
  766: "Eevee Tail",
  767: "Eevee Card",
  768: "Evolve Charm",
  770: "Cleffa Dew",
  771: "Cleffa Card",
  772: "Starry Ore",
  773: "Comet Ring",
  774: "Clef-Claw",
  775: "Clef-Fang",
  776: "Moon Jewel",
  777: "Moon Scarf",
  778: "Clefa-Claw",
  779: "Clefa-Card",
  780: "Moon Rock",
  781: "Fairy Bow",
  782: "Iggly-Dew",
  783: "Iggly-Card",
  784: "Bouncy Charm",
  785: "Pretty Bow",
  786: "Jiggly-Song",
  787: "Jiggly-Card",
  788: "Slumber Rock",
  789: "Snooze Ring",
  790: "Wiggly-Hair",
  791: "Wiggly-Card",
  792: "Buddy Rock",
  793: "Friend Torc",
  794: "Togepi Dew",
  795: "Togepi Card",
  796: "Pure Heart",
  797: "Angel Scarf",
  798: "Togetic Wing",
  799: "Togetic Card",
  800: "Happy Rock",
  801: "Luck Brooch",
  802: "Togek-Wing",
  803: "Togek-Card",
  804: "Ovation Rock",
  805: "Glitter Robe",
  806: "Sneasel Claw",
  807: "Sneasel Card",
  808: "Dusk Jewel",
  809: "Cruel Ring",
  810: "Weavile Claw",
  811: "Weavile Fang",
  812: "Vile Tag",
  813: "Ruin Armlet",
  814: "Teddi-Claw",
  815: "Teddi-Card",
  816: "Honey Rock",
  817: "Heal Scarf",
  818: "Ursa-Claw",
  819: "Ursa-Fang",
  820: "Calming Rock",
  821: "Hiber Scarf",
  822: "Tyro-Sweat",
  823: "Tyro-Card",
  824: "Muscle Charm",
  826: "Smooch-Song",
  827: "Smooch-Card",
  828: "Kiss Charm",
  829: "Heart Tiara",
  830: "Jynx Song",
  831: "Jynx Card",
  832: "Frozen Ore",
  833: "Ruin Scarf",
  834: "Elekid Claw",
  835: "Elekid Claw",
  836: "Jolt Charm",
  837: "Current Ring",
  838: "Electa-Claw",
  839: "Electa-Fang",
  840: "Charge Seal",
  841: "Volt Bangle",
  842: "Electi-Claw",
  843: "Electi-Card",
  844: "Voltaic Rock",
  845: "Voltaic Band",
  846: "Magby Claw",
  847: "Magby Card",
  848: "Ember Jewel",
  849: "Coal Ring",
  850: "Magmar Claw",
  851: "Magmar Card",
  852: "Erupt Ore",
  853: "Magma Scarf",
  854: "Magmor-Claw",
  855: "Magmor-Card",
  856: "Vulcan Rock",
  857: "Burning Torc",
  858: "Azuri-Dew",
  859: "Azuri-Card",
  860: "Fount Charm",
  861: "Water Float",
  862: "Marill Dew",
  863: "Marill Card",
  864: "Surfer Rock",
  865: "Brine Scarf",
  866: "Azuma-Dew",
  867: "Azuma-Card",
  868: "Stream Charm",
  869: "Dotted Scarf",
  870: "Plusle Tail",
  871: "Plusle Card",
  872: "Cheer Rock",
  873: "Pulse Bow",
  874: "Minun Tail",
  875: "Minun Card",
  876: "Volt Heart",
  877: "Spark Tie",
  878: "Cast-Dew",
  879: "Cast-Card",
  880: "Cloud Rock",
  881: "Weather Cape",
  882: "Wynaut Tail",
  883: "Wynaut Card",
  884: "Grin Charm",
  885: "Cheery Scarf",
  886: "Wobbu-Sweat",
  887: "Wobbu-Card",
  888: "Endure Rock",
  889: "Suffer Scarf",
  890: "Bidoof Scarf",
  891: "Bidoof Card",
  892: "Fall Charm",
  893: "Stolid Scarf",
  894: "Biba-Tooth",
  895: "Biba-Card",
  896: "River Charm",
  897: "Dam Scarf",
  898: "Shinx Claw",
  899: "Shinx Fang",
  900: "Flash Tag",
  901: "Energy Scarf",
  902: "Luxio Claw",
  903: "Luxio Fang",
  904: "Spark Tag",
  905: "Spark Scarf",
  906: "Luxray Claw",
  907: "Luxray Fang",
  908: "Glare Tag",
  909: "Glare Sash",
  910: "Pachi-Tooth",
  911: "Pachi-Card",
  912: "Rouse Charm",
  913: "Miracle Bow",
  914: "Buizel Fang",
  915: "Buizel Card",
  916: "Swimmer Rock",
  917: "Screw Torc",
  918: "Float-Fang",
  919: "Float-Card",
  920: "Rescue Rock",
  921: "Float Aid",
  922: "Drifloo-Gasp",
  923: "Drifloo-Card",
  924: "Wind Heart",
  925: "Draft Ring",
  926: "Drifbli-Gasp",
  927: "Drifbli-Card",
  928: "Easy Charm",
  929: "Breeze Scarf",
  930: "Cherubi Seed",
  931: "Cherubi Card",
  932: "Cute Ore",
  933: "Charm Bow",
  934: "Cherrim Dew",
  935: "Cherrim Card",
  936: "Sweet Aroma",
  937: "Petal Dress",
  938: "Bonsly Dew",
  939: "Bonsly Card",
  940: "Arid Tag",
  941: "Teary Cape",
  942: "Sudo-Sweat",
  943: "Sudo-Card",
  944: "Drain Rock",
  945: "Fake Torc",
  946: "Junior Beam",
  947: "Junior Card",
  948: "Mimic Pebble",
  949: "Copy Mask",
  950: "Mime Key",
  951: "Mime Card",
  952: "Bulwark Rock",
  953: "Barrier Bow",
  954: "Happiny Dew",
  955: "Happiny Card",
  956: "Play Tag",
  957: "Nurture Cape",
  958: "Chansey Song",
  959: "Chansey Card",
  960: "Lucky Charm",
  961: "Lucky Scarf",
  962: "Blissey Song",
  963: "Blissey Card",
  964: "Amity Rock",
  965: "Faith Ring",
  966: "Gible Fang",
  967: "Gible Card",
  968: "Dragon Jewel",
  969: "Dragon Tie",
  970: "Gabite Claw",
  971: "Gabite Fang",
  972: "Star Rock",
  973: "Meteor Torc",
  974: "Gar-Claw",
  975: "Gar-Fang",
  976: "Speed Tag",
  977: "Mach Scarf",
  978: "Riolu Tail",
  979: "Riolu Card",
  980: "Valiant Rock",
  981: "Emit Ring",
  982: "Lucario Fang",
  983: "Lucario Card",
  984: "Pledge Rock",
  985: "Ravage Ring",
  986: "Mantyke Beam",
  987: "Mantyke Card",
  988: "Waft Rock",
  989: "Ocean Bow",
  990: "Mantine Foam",
  991: "Mantine Card",
  992: "Sunset Rock",
  993: "Horizon Bow",
  994: "Phione Song",
  995: "Phione Card",
  996: "Wave Jewel",
  997: "Ripple Cape",
  998: "Vulpix Tail",
  999: "Vulpix Card",
  1000: "Vulpix Tag",
  1001: "Glowing Bow",
  1002: "Nine-Hair",
  1003: "Nine-Card",
  1004: "Nine-Seal",
  1005: "Afire Collar",
  1006: "Phanpy Claw",
  1007: "Phanpy Card",
  1008: "Phanpy Tag",
  1009: "Value Ruff",
  1010: "Donphan Fang",
  1011: "Donphan Card",
  1012: "Don-Crest",
  1013: "Armor Scarf",
  1014: "Cater-Belt",
  1015: "Defense Bow",
  1016: "Glittery Bow",
  1017: "Weedle Bow",
  1018: "Kakuna Scarf",
  1019: "Charge Scarf",
  1020: "Pidgey Bow",
  1021: "Pidgeo-Scarf",
  1022: "Pidgeot Torc",
  1023: "Ratta-Scarf",
  1024: "Overcome Bow",
  1025: "Quirky Bow",
  1026: "Wing Scarf",
  1027: "Leash Bow",
  1028: "Shock Ruff",
  1029: "Sand-Scarf",
  1030: "Sandy Torc",
  1031: "Pointy Scarf",
  1032: "Return Scarf",
  1033: "Impact Torc",
  1034: "Halve Scarf",
  1035: "Thorny Scarf",
  1036: "King Sash",
  1037: "Dodge Bow",
  1038: "Absorb Scarf",
  1039: "Odd Bow",
  1040: "Guard Hat",
  1041: "Aroma Scarf",
  1042: "Moving Scarf",
  1043: "Firm Hat",
  1044: "Gaze Goggles",
  1045: "Venomoth Bow",
  1046: "Diglett Hat",
  1047: "Dugtrio Bow",
  1048: "Psyduck Hat",
  1049: "Paddle Scarf",
  1050: "Mankey Torc",
  1051: "Nullify Belt",
  1052: "Growl-Scarf",
  1053: "Legend Bow",
  1054: "Damp Bow",
  1055: "Poli-Bow",
  1056: "Bold Belt",
  1057: "Predict Torc",
  1058: "Psychic Torc",
  1059: "Sparkle Ruff",
  1060: "Impish Band",
  1061: "Strong Belt",
  1062: "Machamp Belt",
  1063: "Bell-Bow",
  1064: "Digest Scarf",
  1065: "Victree-Torc",
  1066: "Tangle Bow",
  1067: "Tenta-Cape",
  1068: "Geodude Torc",
  1069: "Rocky Torc",
  1070: "Rugged Sash",
  1071: "Heated Bow",
  1072: "Sunlight Bow",
  1073: "Slowpoke Hat",
  1074: "Slow-Scarf",
  1075: "Magne-Torc",
  1076: "Magneton Bow",
  1077: "Bullseye Bow",
  1078: "Buddy Torc",
  1079: "Fight Torc",
  1080: "Gentle Bow",
  1081: "North Torc",
  1082: "Grimy Scarf",
  1083: "Slimy Bow",
  1084: "Shell-Torc",
  1085: "Cover Armor",
  1086: "Gastly Veil",
  1087: "Slip Scarf",
  1088: "Sunglasses",
  1089: "Trust Brooch",
  1090: "Drowzee Tie",
  1091: "Dream Coin",
  1092: "Krabby Bow",
  1093: "Super Sash",
  1094: "Ball Scarf",
  1095: "Electro-Bow",
  1096: "Repel Scarf",
  1097: "Exeggu-Sash",
  1098: "Cubone Scarf",
  1099: "Marowak Torc",
  1100: "Licky Scarf",
  1101: "Koffing Bow",
  1102: "Weez-Scarf",
  1103: "Solid Shield",
  1104: "Pierce Drill",
  1105: "Sticky Bow",
  1106: "Kang-Apron",
  1107: "Horsea Bow",
  1108: "Swirl Scarf",
  1109: "Goldeen Bow",
  1110: "Seaking Bow",
  1111: "Recover Torc",
  1112: "Starmie Belt",
  1113: "Pinsir Sash",
  1114: "Rushing Bow",
  1115: "Magikarp Bow",
  1116: "Tempest Sash",
  1117: "Ditto Torc",
  1118: "AI Brooch",
  1119: "Spike Brooch",
  1120: "Aged Scarf",
  1121: "Kabuto Hat",
  1122: "Kabu-Torc",
  1123: "Old Brooch",
  1124: "Dragon Sash",
  1125: "Aloft Mantle",
  1126: "Mirage Cape",
  1127: "Sentret Ruff",
  1128: "Body Collar",
  1129: "Expose Specs",
  1130: "Noctowl Torc",
  1131: "Morning Bow",
  1132: "Ledian Bow",
  1133: "Spina-Scarf",
  1134: "Ariados Bow",
  1135: "Slash Bow",
  1136: "Shine Torc",
  1137: "Lanturn Bow",
  1138: "Lively Scarf",
  1139: "Xatu Bow",
  1140: "Wool Bow",
  1141: "Fluffy Scarf",
  1142: "Sacred Scarf",
  1143: "Bright Tiara",
  1144: "Rain Crown",
  1145: "Zephyr Bow",
  1146: "Skip-Scarf",
  1147: "Cotton Torc",
  1148: "Revenge Ruff",
  1149: "Hasty Bow",
  1150: "Sun Scarf",
  1151: "Chitin Bow",
  1152: "Wooper Bow",
  1153: "Quag-Torc",
  1154: "Murkrow Hat",
  1155: "King Cap",
  1156: "Misdrea-Cape",
  1157: "Cryptic Sash",
  1158: "Reverse Bow",
  1159: "Robust Bow",
  1160: "Dense Poncho",
  1161: "Escape Scarf",
  1162: "Takeoff Ruff",
  1163: "Quartz Torc",
  1164: "Snub-Cape",
  1165: "Stern Sash",
  1166: "Qwilfish Bow",
  1167: "Shuckle Bow",
  1168: "Horn Torc",
  1169: "Lava Bow",
  1170: "Torrid Scarf",
  1171: "Frigid Bow",
  1172: "Frost Torc",
  1173: "Eager Brooch",
  1174: "Reach Bow",
  1175: "Psy Bow",
  1176: "Snow Brooch",
  1177: "Skar-Cape",
  1178: "Dark Choker",
  1179: "Pit Fang",
  1180: "Tornado Bow",
  1181: "Virtual Bow",
  1182: "Delusion Bow",
  1183: "Paint Scarf",
  1184: "Milky Scarf",
  1185: "Larvitar Bow",
  1186: "Pupita-Scarf",
  1187: "Crash Claw",
  1188: "Pooch-Collar",
  1189: "Dark Fang",
  1190: "Merry Scarf",
  1191: "Linoone Ruff",
  1192: "Wurmple Bow",
  1193: "Tough Scarf",
  1194: "Vivid Silk",
  1195: "Guard Bow",
  1196: "Dustox Bow",
  1197: "Kelp Hat",
  1198: "Jolly Scarf",
  1199: "Ludicolo Hat",
  1200: "Seedot Hat",
  1201: "Nuzleaf Bow",
  1202: "Shiftry Belt",
  1203: "Taillow Bow",
  1204: "Midair Scarf",
  1205: "Wingull Bow",
  1206: "Stock Scarf",
  1207: "Sensing Hat",
  1208: "Magical Bow",
  1209: "Caring Scarf",
  1210: "Bliss Scarf",
  1211: "Blocking Bow",
  1212: "Mobile Bow",
  1213: "Thwart Bow",
  1214: "Slak-Scarf",
  1215: "Vigor Sash",
  1216: "Lazy Ruff",
  1217: "Novice Scarf",
  1218: "Ninja Ruff",
  1219: "Awe Mantle",
  1220: "Good Earring",
  1221: "Nice Bangle",
  1222: "Great Torc",
  1223: "Makuhit-Belt",
  1224: "Thrust Belt",
  1225: "Nose-Torc",
  1226: "Sable-Scope",
  1227: "Deceit Mask",
  1228: "Iron Torc",
  1229: "Metal Bangle",
  1230: "Iron Helmet",
  1231: "Intuit Bow",
  1232: "Ponder Sash",
  1233: "Punish Torc",
  1234: "Protect Mask",
  1235: "Neon Scarf",
  1236: "Evening Bow",
  1237: "Thorned Torc",
  1238: "Gulpin Bow",
  1239: "Swalot Belt",
  1240: "Carva-Sash",
  1241: "Vicious Bow",
  1242: "Spout Scarf",
  1243: "Huge Bow",
  1244: "Numel Bow",
  1245: "Erupt Scarf",
  1246: "Sooty Sash",
  1247: "Spring Bow",
  1248: "Scheme Scarf",
  1249: "Hula Bow",
  1250: "Desert Bow",
  1251: "Vibra Scarf",
  1252: "Red Glasses",
  1253: "Desert Sash",
  1254: "Cacturne Hat",
  1255: "Tuft Bow",
  1256: "Cloud Ruff",
  1257: "Strong Sash",
  1258: "Seviper Bow",
  1259: "Lunaton-Torc",
  1260: "Solrock Bow",
  1261: "Soak Scarf",
  1262: "Whiscash Bow",
  1263: "Bossy Scarf",
  1264: "Cower Sash",
  1265: "Bal-Brooch",
  1266: "Claydol Torc",
  1267: "Bind Scarf",
  1268: "Cradily Bow",
  1269: "Guard Claw",
  1270: "Rigid Cape",
  1271: "Admire Scarf",
  1272: "Grace Scarf",
  1273: "Kecleon Torc",
  1274: "Shuppet Cape",
  1275: "Ominous Torc",
  1276: "Duskull Ruff",
  1277: "Illusion Bow",
  1278: "Tropius Bow",
  1279: "Chime-Scarf",
  1280: "Perish Torc",
  1281: "Chilly Hat",
  1282: "Hail Scarf",
  1283: "Sleet Bow",
  1284: "Safe Scarf",
  1285: "Walrein Torc",
  1286: "Clam-Brooch",
  1287: "Deep Torc",
  1288: "Gore-Scarf",
  1289: "Reli-Torc",
  1290: "Luvdisc Torc",
  1291: "Crag Helmet",
  1292: "Outlast Bow",
  1293: "Sala-Cape",
  1294: "Beldum Torc",
  1295: "Metang Scarf",
  1296: "Meta-Torc",
  1297: "Starly Bow",
  1298: "Regret Torc",
  1299: "Guts Sash",
  1300: "Still Bow",
  1301: "Kricke-Torc",
  1302: "Budew Scarf",
  1303: "Bouquet Cape",
  1304: "Hard Helmet",
  1305: "Skull Helmet",
  1306: "Rebound Bow",
  1307: "Block Brooch",
  1308: "Straw Cape",
  1309: "Worma-Bow",
  1310: "Mothim Bow",
  1311: "Nectar Bow",
  1312: "Vespi-Torc",
  1313: "Awake Bow",
  1314: "Gastro-Torc",
  1315: "Ambipom Bow",
  1316: "Defrost Ruff",
  1317: "Allure Coat",
  1318: "Magic Hat",
  1319: "Honch-Cape",
  1320: "Glameow Bow",
  1321: "Scary Belt",
  1322: "Ching-Torc",
  1323: "Stinky Scarf",
  1324: "Stench Sash",
  1325: "Image Brooch",
  1326: "Mirror Torc",
  1327: "Chatot Scarf",
  1328: "Thick Scarf",
  1329: "Grit Veil",
  1330: "Skorupi Bow",
  1331: "Dust Scarf",
  1332: "Croa-Torc",
  1333: "Toxi-Belt",
  1334: "Carni-Bow",
  1335: "Swim Bow",
  1336: "Lumi-Torc",
  1337: "Snowy Torc",
  1338: "Frozen Cape",
  1339: "Builder Sash",
  1340: "Flabby Belt",
  1341: "Rhyperi-Torc",
  1342: "Clinging Bow",
  1343: "Yanmega Bow",
  1344: "Gliscor Cape",
  1345: "Glacier Cape",
  1346: "Best Scarf",
  1347: "Gallant Torc",
  1348: "Probo-Hat",
  1349: "Unlucky Sash",
  1350: "Froslass Bow",
  1351: "Purify Veil",
}

WMRewardType = {
    0: "Cash",
    1: "Cash + ??? (Reward item)",
    2: "Item",
    3: "Item + ??? (Random)",
    4: "??? (Reward item)",
    5: "??? (Egg)",
    6: "??? (Client joins)"
}

# sky poke data
WMSkyPoke = {
  1: "Bulbasaur",
  2: "Ivysaur",
  3: "Venusaur",
  4: "Charmander",
  5: "Charmeleon",
  6: "Charizard",
  7: "Squirtle",
  8: "Wartortle",
  9: "Blastoise",
  10: "Caterpie",
  11: "Metapod",
  12: "Butterfree",
  13: "Weedle",
  14: "Kakuna",
  15: "Beedrill",
  16: "Pidgey",
  17: "Pidgeotto",
  18: "Pidgeot",
  19: "Rattata",
  20: "Raticate",
  21: "Spearow",
  22: "Fearow",
  23: "Ekans",
  24: "Arbok",
  25: "Pikachu",
  26: "Raichu",
  27: "Sandshrew",
  28: "Sandslash",
  29: "Nidoran",
  30: "Nidorina",
  31: "Nidoqueen",
  33: "Nidorino",
  34: "Nidoking",
  35: "Clefairy",
  36: "Celefable",
  37: "Vulpix",
  38: "Ninetails",
  39: "Jigglypuff",
  40: "Wigglytuff",
  41: "Zubat",
  42: "Golbat",
  43: "Oddish",
  44: "Gloom",
  45: "Vileplume",
  46: "Paras",
  47: "Parasect",
  48: "Venonat",
  49: "Venomoth",
  50: "Diglett",
  51: "Dugtrio",
  52: "Meowth",
  53: "Persian",
  54: "Psyduck",
  55: "Golduck",
  56: "Mankey",
  57: "Primeape",
  58: "Growlithe",
  59: "Arcanine",
  60: "Poliwag",
  61: "Poliwhirl",
  62: "Poliwrath",
  63: "Abra",
  64: "Kadabra",
  65: "Alakazam",
  66: "Machop",
  67: "Machoke",
  68: "Machamp",
  69: "Bellsprout",
  70: "Weepinbell",
  71: "Victreebel",
  72: "Tentacool",
  73: "Tentacruel",
  74: "Geodude",
  75: "Graveler",
  76: "Golem",
  77: "Ponyta",
  78: "Rapidash",
  79: "Slowpoke",
  80: "Slowbro",
  81: "Magnemite",
  82: "Magneton",
  83: "Farfetch'd",
  84: "Doduo",
  85: "Dodrio",
  86: "Seel",
  87: "Dewgong",
  88: "Grimer",
  89: "Muk",
  90: "Shellder",
  91: "Cloyster",
  92: "Gastly",
  93: "Haunter",
  94: "Gengar",
  95: "Onix",
  96: "Drowzee",
  97: "Hypno",
  98: "Krabby",
  99: "Kingler",
  100: "Voltorb",
  101: "Electrode",
  102: "Exeggcute",
  103: "Exeggutor",
  104: "Cubone",
  105: "Marowak",
  106: "Hitmonlee",
  107: "Hitmonchan",
  108: "Lickitung",
  109: "Koffing",
  110: "Weezing",
  111: "Rhyhorn",
  112: "Rhydon",
  113: "Chansey",
  114: "Tangela",
  115: "Kangaskhan",
  116: "Horsea",
  117: "Seadra",
  118: "Goldeen",
  119: "Seaking",
  120: "Staryu",
  121: "Starmie",
  122: "Mr. Mime",
  123: "Scyther",
  124: "Jynx",
  125: "Electabuzz",
  126: "Magmar",
  127: "Pinsir",
  128: "Tauros",
  129: "Magikarp",
  130: "Gyarados",
  131: "Lapras",
  132: "Ditto",
  133: "Eevee",
  134: "Vaporeon",
  135: "Jolteon",
  136: "Flareon",
  137: "Porygon",
  138: "Omanyte",
  139: "Omastar",
  140: "Kabuto",
  141: "Kabutops",
  142: "Aerodactyl",
  143: "Snorlax",
  144: "Articuno",
  145: "Zapdos",
  146: "Moltres",
  147: "Dratini",
  148: "Dragonair",
  149: "Dragonite",
  150: "Mewtwo",
  151: "Mew",
  152: "Chikorita",
  153: "Bayleef",
  154: "Meganium",
  155: "Cyndaquil",
  156: "Quilava",
  157: "Typhlosion",
  158: "Totodile",
  159: "Croconaw",
  160: "Feraligatr",
  161: "Sentret",
  162: "Furret",
  163: "Hoothoot",
  164: "Noctowl",
  165: "Ledyba",
  166: "Ledian",
  167: "Spinarak",
  168: "Ariados",
  169: "Crobat",
  170: "Chinchou",
  171: "Lanturn",
  172: "Pichu",
  173: "Cleffa",
  174: "Igglybuff",
  175: "Togepi",
  176: "Togetic",
  177: "Natu",
  178: "Xatu",
  179: "Mareep",
  180: "Flaaffy",
  181: "Ampharos",
  182: "Bellossom",
  183: "Marill",
  184: "Azumarill",
  185: "Sudowoodo",
  186: "Politoed",
  187: "Hoppip",
  188: "Skiploom",
  189: "Jumpluff",
  190: "Aipom",
  191: "Sunkern",
  192: "Sunflora",
  193: "Yanma",
  194: "Wooper",
  195: "Quagsire",
  196: "Espeon",
  197: "Umbreon",
  198: "Murkrow",
  199: "Slowking",
  200: "Misdreavus",
  201: "Unown A",
  202: "Unown B",
  203: "Unown C",
  204: "Unown D",
  205: "Unown E",
  206: "Unown F",
  207: "Unown G",
  208: "Unown H",
  209: "Unown I",
  210: "Unown J",
  211: "Unown K",
  212: "Unown L",
  213: "Unown M",
  214: "Unown N",
  215: "Unown O",
  216: "Unown P",
  217: "Unown Q",
  218: "Unown R",
  219: "Unown S",
  220: "Unown T",
  221: "Unown U",
  222: "Unown V",
  223: "Unown W",
  224: "Unown X",
  225: "Unown Y",
  226: "Unown Z",
  227: "Unown !",
  228: "Unown ?",
  229: "Wobbuffet",
  230: "Girafarig",
  231: "Pineco",
  232: "Forretress",
  233: "Dunsparce",
  234: "Gligar",
  235: "Steelix",
  236: "Snubbull",
  237: "Granbull",
  238: "Qwilfish",
  223: "Scizor",
  240: "Shuckle",
  241: "Heracross",
  242: "Sneasel",
  243: "Teddiursa",
  244: "Ursaring",
  245: "Slugma",
  246: "Magcargo",
  247: "Swinub",
  248: "Piloswine",
  249: "Corsola",
  250: "Remoraid",
  251: "Octillery",
  252: "Delibird",
  253: "Mantine",
  254: "Skarmory",
  255: "Houndour",
  256: "Houndoom",
  257: "Kingdra",
  258: "Phanpy",
  259: "Donphan",
  260: "Porygon2",
  261: "Stantler",
  262: "Smeargle",
  263: "Tyrogue",
  264: "Hitmontop",
  265: "Smoochum",
  266: "Elekid",
  267: "Magby",
  268: "Miltank",
  269: "Blissey",
  270: "Raikou",
  271: "Entei",
  272: "Suicune",
  273: "Larvitar",
  274: "Pupitar",
  275: "Tyranitar",
  276: "Lugia",
  277: "Ho-oh",
  278: "Celebi (Green)",
  279: "Celebi (Pink)",
  280: "Treecko",
  281: "Grovyle",
  282: "Sceptile",
  283: "Torchic",
  284: "Combusken",
  285: "Blaziken",
  286: "Mudkip",
  287: "Marshtomp",
  288: "Swampert",
  289: "Poochyena",
  290: "Mightyena",
  291: "Zigzagoon",
  292: "Linoone",
  293: "Wurmple",
  294: "Silcoon",
  295: "Beautifly",
  296: "Cascoon",
  297: "Dustox",
  298: "Lotad",
  299: "Lombre",
  300: "Ludicolo",
  301: "Seedot",
  302: "Nuzleaf",
  303: "Shiftry",
  304: "Taillow",
  305: "Swellow",
  306: "Wingull",
  307: "Pelipper",
  308: "Ralts",
  309: "Kirlia",
  310: "Gardevoir",
  311: "Surskit",
  312: "Masquerain",
  313: "Shroomish",
  314: "Breloom",
  315: "Slakoth",
  316: "Vigoroth",
  317: "Slaking",
  318: "Nincada",
  319: "Ninjask",
  320: "Shedinja",
  321: "Whismur",
  322: "Loudred",
  323: "Exploud",
  324: "Makuhita",
  325: "Hariyama",
  326: "Azurill",
  327: "Nosepass",
  328: "Skitty",
  329: "Delcatty",
  330: "Sableye",
  331: "Mawile",
  332: "Aron",
  333: "Lairon",
  334: "Aggron",
  335: "Meditite",
  336: "Medicham",
  337: "Electrike",
  338: "Manectric",
  339: "Plusle",
  340: "Minun",
  341: "Volbeat",
  342: "Illumise",
  343: "Roselia",
  344: "Gulpin",
  345: "Swalot",
  346: "Carvanha",
  347: "Sharpedo",
  348: "Wailmer",
  349: "Wailord",
  350: "Numel",
  351: "Camerupt",
  352: "Torkoal",
  353: "Spoink",
  354: "Grumpig",
  355: "Spinda",
  356: "Trapinch",
  357: "Vibrava",
  358: "Flygon",
  359: "Cacnea",
  360: "Cacturne",
  361: "Swablu",
  362: "Altaria",
  363: "Zangoose",
  364: "Seviper",
  365: "Lunatone",
  366: "Solrock",
  367: "Barboach",
  368: "Whiscash",
  369: "Corphish",
  370: "Crawdaunt",
  371: "Baltoy",
  372: "Claydol",
  373: "Lileep",
  374: "Cradily",
  375: "Anorith",
  376: "Armaldo",
  377: "Feebas",
  378: "Milotic",
  379: "Castform (a)",
  380: "Castform (b)",
  381: "Castform (c)",
  382: "Castform (d)",
  383: "Kecleon (Green)",
  384: "Kecleon (Purple)",
  385: "Shuppet",
  386: "Banette",
  387: "Duskull",
  388: "Dusclops",
  389: "Tropius",
  390: "Chimecho",
  391: "Absol",
  392: "Wynaut",
  393: "Snorunt",
  394: "Glalie",
  395: "Spheal",
  396: "Sealeo",
  397: "Walrein",
  398: "Clamperl",
  399: "Huntail",
  400: "Gorebyss",
  401: "Relicanth",
  402: "Luvdisc",
  403: "Bagon",
  404: "Shelgon",
  405: "Salamence",
  406: "Beldum",
  407: "Metang",
  408: "Metagross",
  409: "Regirock",
  410: "Regice",
  411: "Registeel",
  412: "Latias",
  413: "Latios",
  414: "Kyogre",
  415: "Groudon",
  416: "Rayquaza",
  417: "Jirachi",
  418: "Deoxys (a)",
  419: "Deoxys (b)",
  420: "Deoxys (c)",
  421: "Deoxys (d)",
  422: "Turtwig",
  423: "Grotle",
  424: "Torterra",
  425: "Chimchar",
  426: "Monferno",
  427: "Infernape",
  428: "Piplup",
  429: "Prinplup",
  430: "Empoleon",
  431: "Starly",
  432: "Staravia",
  433: "Staraptor",
  434: "Bidoof",
  435: "Bibarel",
  436: "Kricketot",
  437: "Kricketune",
  438: "Shinx",
  439: "Luxio",
  440: "Luxray",
  441: "Budew",
  442: "Roserade",
  443: "Cranidos",
  444: "Rampardos",
  445: "Shieldon",
  446: "Bastiodon",
  447: "Burmy (Pink)",
  448: "Burmy (Green)",
  449: "Burmy (Yellow)",
  450: "Wormadam (Blue)",
  451: "Wormadam (Green)",
  452: "Wormadam (Pink)",
  453: "Mothim",
  454: "Combee",
  455: "Vespiquen",
  456: "Pachirisu",
  457: "Buizel",
  458: "Floatzel",
  459: "Cherubi",
  460: "Cherrim (a)",
  461: "Cherrim (b)",
  462: "Shellos(a)",
  463: "Shellos(b)",
  464: "Gastrodon (a)",
  465: "Gastrodon (b)",
  466: "Ambipom",
  467: "Drifloon",
  468: "Drifblim",
  469: "Buneary",
  470: "Lopunny",
  471: "Mismagius",
  472: "Honchkrow",
  473: "Glameow",
  474: "Purugly",
  475: "Chingling",
  476: "Stunky",
  477: "Skuntank",
  478: "Bronzor",
  479: "Bronzong",
  480: "Bonsly",
  481: "MimeJr.",
  482: "Happiny",
  483: "Chatot",
  484: "Spiritomb",
  485: "Gible",
  486: "Gabite",
  487: "Garchomp",
  488: "Munchlax",
  489: "Riolu",
  490: "Lucario",
  491: "Hippopotas",
  492: "Hippowdon",
  493: "Skorupi",
  494: "Drapion",
  495: "Croagunk",
  496: "Toxicroak",
  497: "Carnivine",
  498: "Finneon",
  499: "Lumineon",
  500: "Mantyke",
  501: "Snover",
  502: "Abomasnow",
  503: "Weavile",
  504: "Magnezone",
  505: "Lickilicky",
  506: "Rhyperior",
  507: "Tangrowth",
  508: "Electivire",
  509: "Magmortar",
  510: "Togekiss",
  511: "Yanmega",
  512: "Leafeon",
  513: "Glaceon",
  514: "Gliscor",
  515: "Mamoswine",
  516: "Porygon-Z",
  517: "Gallade",
  518: "Probopass",
  519: "Dusknoir",
  520: "Froslass",
  521: "Rotom",
  522: "Uxie",
  523: "Mesprit",
  524: "Azelf",
  525: "Dialga",
  526: "Palkia",
  527: "Heatran",
  528: "Regigigas",
  529: "Giratina",
  530: "Cresselia",
  531: "Phione",
  532: "Manaphy",
  533: "Darkrai",
  534: "Shaymin",
}



# Wonder Mail S Structure data
WMSStruct = [
	{"name": "nullBits", "note": "Null bits", "size": 8},
	{"name": "specialFloor", "note": "Special floor marker", "size": 8},
	{"name": "floor", "note": "Floor", "size": 8},
	{"name": "dungeon", "note": "Dungeon", "size": 8},
	{"name": "flavorText", "note": "Modifies the flavor text", "size": 24},
	{"name": "restriction", "note": "Restriction data", "size": 11},
	{"name": "restrictionType", "note": "Restriction type; mon = 1, type = 0", "size": 1},
	{"name": "reward", "note": "Reward", "size": 11},
	{"name": "rewardType", "note": "Reward type", "size": 4},
	{"name": "targetItem", "note": "Target item", "size": 10},
	{"name": "target2", "note": "Additional target Poke for certain mission types", "size": 11},
	{"name": "target", "note": "Target Poke", "size": 11},
	{"name": "client", "note": "Client Poke", "size": 11},
	{"name": "missionSpecial", "note": "Mission special texts", "size": 4},
	{"name": "missionType", "note": "Mission type", "size": 4},
	{"name": "mailType", "note": "Mail type marker (must be 0100 = 4)", "size": 4},
	{"name": "checksum", "note": "checksum", "size": 32, "noinclude": True}
]


def numToBits(num: int, outputSize: int):
    '''
    Converts a given decimal to outputSize-bit unsigned binary string.
    '''

    formatStr = '\"{0:0' + str(outputSize) + 'b}\"'
    return eval(r"f'{formatStr}'.format(num)").strip('\"')

def bitsToNum(bits: str):
    '''
    Convert a string of bits to a number.
    '''
    return int(bits, 2)

def getItemName(itemId):
    '''
    Returns the item name for a given item ID.
    '''
    return WMSkyItem.get(itemId, 'Unknown Item')

def getDungeonName(dungeonID):
    '''
    Returns the dungeon name for a given dungeon ID.
    '''
    return WMSkyDungeon.get(dungeonID, 'Unknown')

def getMonName(monId):
    '''
    Returns the monster name for a given monster ID.
    '''
    female = (monId > 600)
    if female:
        monId -= 600
    return WMSkyPoke.get(monId, 'Unknown')

def getTrueMonId(id, femaleChecked: bool):
    id = id % 600
    if id == WMSGenData['NIDORAN_MALE'] or id == WMSGenData['NIDORAN_FEMALE']:
        if femaleChecked:
            return WMSGenData['NIDORAN_FEMALE']
        else:
            return WMSGenData['NIDORAN_MALE']
    maleOnly = id in WMSGenData['maleOnly']
    femaleOnly = id in WMSGenData['femaleOnly']
    if (maleOnly or femaleOnly) and femaleChecked:
        print(f'Prevented {id} from being marked as female')
        return id
    elif femaleChecked:
        return id + 600
    else:
        return id


class WMSParser:

    def __init__(self, printLog: bool = True):

        # Byte-swap patterns
	    # 07 1B 0D 1F 15 1A 06 01 17 1C 09 1E 0A 20 10 21 0F 08 1D 11 14 00 13 16 05 12 0E 04 03 18 02 0B 0C 19
	    # http://www.gamefaqs.com/boards/detail.php?board=955859&topic=51920426&message=571612360
        self.byteSwap = [
		    0x07, 0x1B, 0x0D, 0x1F, 0x15, 0x1A, 0x06, 0x01,
		    0x17, 0x1C, 0x09, 0x1E, 0x0A, 0x20, 0x10, 0x21,
		    0x0F, 0x08, 0x1D, 0x11, 0x14, 0x00, 0x13, 0x16,
		    0x05, 0x12, 0x0E, 0x04, 0x03, 0x18, 0x02, 0x0B,
		    0x0C, 0x19
	    ]

        self.byteSwapEU = [
		    0x0E, 0x04, 0x03, 0x18, 0x09, 0x1E, 0x0A, 0x20,
		    0x10, 0x21, 0x14, 0x00, 0x13, 0x16, 0x05, 0x12,
		    0x06, 0x01, 0x17, 0x1C, 0x07, 0x1B, 0x0D, 0x1F,
		    0x15, 0x1A, 0x02, 0x0B, 0x0C, 0x19, 0x0F, 0x08,
		    0x1D, 0x11
	    ]

        # Each WM byte maps to these bit values
	    # http://www.gamefaqs.com/boards/genmessage.php?board=938931&topic=42726909&page=9
        # http://www.gamefaqs.com/boards/genmessage.php?board=938931&topic=42949038
        self.bitValues = "&67NPR89F0+#STXY45MCHJ-K12=%3Q@W"

        # Encryption data from:
	    # http://docs.google.com/Doc?id=ddpvsk95_17fr7qpmgc
		# Listed vertical: first part of the 2-character hex code range
		# Listed horizontal: second part of the 2-character hex code
		#   0     1     2     3     4     5     6     7     8     9     A     B     C     D     E     F
        self.encryptionData = [
            0x2E, 0x75, 0x3F, 0x99, 0x09, 0x6C, 0xBC, 0x61, 0x7C, 0x2A, 0x96, 0x4A, 0xF4, 0x6D, 0x29, 0xFA, # 00-0F
		    0x90, 0x14, 0x9D, 0x33, 0x6F, 0xCB, 0x49, 0x3C, 0x48, 0x80, 0x7B, 0x46, 0x67, 0x01, 0x17, 0x59, # 10-1F
		    0xB8, 0xFA, 0x70, 0xC0, 0x44, 0x78, 0x48, 0xFB, 0x26, 0x80, 0x81, 0xFC, 0xFD, 0x61, 0x70, 0xC7, # 20-2F
		    0xFE, 0xA8, 0x70, 0x28, 0x6C, 0x9C, 0x07, 0xA4, 0xCB, 0x3F, 0x70, 0xA3, 0x8C, 0xD6, 0xFF, 0xB0, # 30-3F
		    0x7A, 0x3A, 0x35, 0x54, 0xE9, 0x9A, 0x3B, 0x61, 0x16, 0x41, 0xE9, 0xA3, 0x90, 0xA3, 0xE9, 0xEE, # 40-4F
		    0x0E, 0xFA, 0xDC, 0x9B, 0xD6, 0xFB, 0x24, 0xB5, 0x41, 0x9A, 0x20, 0xBA, 0xB3, 0x51, 0x7A, 0x36, # 50-5F
		    0x3E, 0x60, 0x0E, 0x3D, 0x02, 0xB0, 0x34, 0x57, 0x69, 0x81, 0xEB, 0x67, 0xF3, 0xEB, 0x8C, 0x47, # 60-6F
		    0x93, 0xCE, 0x2A, 0xAF, 0x35, 0xF4, 0x74, 0x87, 0x50, 0x2C, 0x39, 0x68, 0xBB, 0x47, 0x1A, 0x02, # 70-7F
		    0xA3, 0x93, 0x64, 0x2E, 0x8C, 0xAD, 0xB1, 0xC4, 0x61, 0x04, 0x5F, 0xBD, 0x59, 0x21, 0x1C, 0xE7, # 80-8F
		    0x0E, 0x29, 0x26, 0x97, 0x70, 0xA9, 0xCD, 0x18, 0xA3, 0x7B, 0x74, 0x70, 0x96, 0xDE, 0xA6, 0x72, # 90-9F
		    0xDD, 0x13, 0x93, 0xAA, 0x90, 0x6C, 0xA7, 0xB5, 0x76, 0x2F, 0xA8, 0x7A, 0xC8, 0x81, 0x06, 0xBB, # A0-AF
		    0x85, 0x75, 0x11, 0x0C, 0xD2, 0xD1, 0xC9, 0xF8, 0x81, 0x70, 0xEE, 0xC8, 0x71, 0x53, 0x3D, 0xAF, # B0-BF
		    0x76, 0xCB, 0x0D, 0xC1, 0x56, 0x28, 0xE8, 0x3C, 0x61, 0x64, 0x4B, 0xB8, 0xEF, 0x3B, 0x41, 0x09, # C0-CF
		    0x72, 0x07, 0x50, 0xAD, 0xF3, 0x2E, 0x5C, 0x43, 0xFF, 0xC3, 0xB3, 0x32, 0x7A, 0x3E, 0x9C, 0xA3, # D0-DF
		    0xC2, 0xAB, 0x10, 0x60, 0x99, 0xFB, 0x08, 0x8A, 0x90, 0x57, 0x8A, 0x7F, 0x61, 0x90, 0x21, 0x88, # E0-EF
		    0x55, 0xE8, 0xFC, 0x4B, 0x0D, 0x4A, 0x7A, 0x48, 0xC9, 0xB0, 0xC7, 0xA6, 0xD0, 0x04, 0x7E, 0x05  # F0-FF]
	    ]

        # Data used when calculating a checksum in Sky
        self.skyChecksumData = [None] * 256
        for i in range(256):
            entry = i
            for j in range(8):
                if bool((entry & 0x01) ^ 0x01):
                    entry = entry >> 1
                else:
                    entry = 0xEDB88320 ^ (entry >> 1)
                self.skyChecksumData[i] = entry

        self.printLog = printLog

    def sanitize(self, wmString):
        '''
        Sanitizes a WonderMail S string by removing all unknown characters.
        '''
        wmString = wmString.upper()
        outString = ''.join([char for char in wmString if char in self.bitValues])

        # check if the length is ok
        if len(outString) != 34:
            raise ValueError(f'Sanitized WMS code is {len(outString)} chars long, should be 34')
        return outString

    def prettyMailString(self, mailString, rows, middleColumnSize):
        '''
        Prettifies a mail string, given the amount of rows and the length of the middle column. Outer column
        width is automagically calculated.
        '''
        mailString = self.sanitize(mailString)
        outerColumnSize = int((len(mailString) - (rows * middleColumnSize)) / (rows * 2))
        prettyString = ''
        stringPtr = 0
        for _ in range(rows):
            if prettyString != '':
                prettyString += "\n"
            prettyString += mailString[stringPtr : stringPtr + outerColumnSize] + " "
            stringPtr += outerColumnSize
            prettyString += mailString[stringPtr : stringPtr + middleColumnSize] + " "
            stringPtr += middleColumnSize
            prettyString += mailString[stringPtr : stringPtr + outerColumnSize]
            stringPtr += outerColumnSize
        return prettyString

    def unscrambleString(self, wmString, swapArray):
        '''
        Unscrambles a scrambled WMS string.
        '''
        swapArray = [a | b for a, b in zip(swapArray, self.byteSwap)]
        outString = ''.join([wmString[source] for source in swapArray])
        return outString

    def scrambleString(self, wmString, swapArray):
        '''
        Scrambles a unscrambled WMS string.
        '''
        swapArray = [a | b for a, b in zip(swapArray, self.byteSwap)]
        outArray = [''] * len(swapArray)
        for i, target in enumerate(swapArray):
            outArray[target] += wmString[i]
        return ''.join(outArray)

    def getEncryptionEntries(self, checksum):
        '''
        Returns the encryption entries for a given checksum.
        '''
        amount = 17
        entries = []
        encPointer = checksum
        backwards = bool((checksum & 0x01) ^ 0x01)

        for _ in range(amount):
            entries.append(self.encryptionData[encPointer])
            if backwards:
                encPointer -= 1
                if encPointer < 0:
                    encPointer = len(self.encryptionData) - 1
            else:
                encPointer += 1
                if encPointer >= len(self.encryptionData):
                    encPointer = 0

        return entries

    def bytesToBits(self, wmIntString):
        '''
        Converts the unscrambled representation of a mail string to an encrypted bitstream.
        '''
        outString = ''
        for i in range(len(wmIntString) - 1, -1, -1):
            curChar = wmIntString[i]
            if curChar in self.bitValues:
                index = self.bitValues.index(curChar)
                outString += numToBits(index, 5)
            else:
                raise ValueError(f'Unknown character {curChar} at position {i}')
        return outString

    def bitsToBytes(self, bitStream):
        '''
        Converts an encrypted bitStream to an unscrambled mail.
        '''
        blocks = int(len(bitStream) / 5)
        outStr = ''
        for i in range(blocks):
            curChars = bitStream[(blocks - i - 1) * 5 : (blocks - i - 1) * 5 + 5]
            num = bitsToNum(curChars)
            if 0 <= num < 32:
                outStr += self.bitValues[num]
            else:
                raise ValueError(f'Could not find {curChars} in the reverse lookup table')
        return outStr

    def getResetByte(self, checksum):
        '''
        Returns the resetByte for a given checksum.
        '''
        checksumByte = checksum % 256
        resetByte = math.floor((checksumByte / 16) + 8 + (checksumByte % 16))
        return resetByte if resetByte < 17 else -1

    def decryptBitStream(self, curBitStream, encrypt=False):
        '''
        Decrypts or encrypts a bitstream according to the encryption data.
        '''
		# This will contain the 8-bit blocks as numbers (0-255), each representing one byte.
		# The checksum byte is NOT included in these blocks.
		# The first block in the array is the last block in the bitstream (we work backwards).
        bitPtr = 0
        blocks = []
        origBlocks = []
        # Checksum data
        checksumByte = 0
        checksumBits = ''
        skyChecksumBits = ''
        # Go 8 bits back from the end. We'll read the next 8 bits as our checksum.
        bitPtr = len(curBitStream) - 8
        checksumBits = curBitStream[bitPtr : bitPtr + 8]
        checksumByte = bitsToNum(checksumBits)
        # The Sky Checksum is 24 bits.
        bitPtr -= 24
        skyChecksumBits = curBitStream[bitPtr : bitPtr + 24]
        fullChecksum = bitsToNum(str(skyChecksumBits) + str(checksumBits))
		# http://www.gamefaqs.com/boards/genmessage.php?board=938931&topic=42949038&page=6
		# "At the moment, I figured out what the game is doing with the other half of the encryption. 
		# Apparently, if you have an even checksum, you go backwards through the encryption bytes.
		# With an odd checksum, you go forwards through the encryption bytes."
        backwards = bool((checksumByte & 0x01) ^ 0x01)
        if self.printLog:
            print(f'Checksum: {checksumByte}, encPtr goes backwards: {backwards}')

		# Parse everything into blocks.
		# Sky: 1 2-bit block + 16 8-bit blocks + 24-bit skyChecksum + 8-bit checksum.
        while bitPtr > 7:
            bitPtr -= 8
            data = bitsToNum(curBitStream[bitPtr : bitPtr + 8])
            blocks.append(data)
            origBlocks.append(data)

        # Handle the 2-bit block at the beginning (should always be 00?)
        twoBitsStart = curBitStream[:2]
        bitPtr -= 2
        # Get our encryption entries.
        entries = self.getEncryptionEntries(checksumByte)
        # Figure out the resetByte.
        resetByte = 255
        resetByte = self.getResetByte(fullChecksum)
        if self.printLog:
            print(f'resetByte used for this code: {resetByte}')

        # Do the decryption.
        tblPtr = 0
        encPtr = 0
        for i in range(len(blocks)):
            if encPtr == resetByte:
                remaining = len(blocks) - i
                if self.printLog:
                    print(f'Resetting at {encPtr}. {remaining} blocks remain for decryption.')
                encPtr = 0
            inputByte = blocks[tblPtr]
            # Add or subtract the number in the encryption entry from it.
            if encrypt:
                result = (inputByte + entries[encPtr]) & 0xFF
            else:
                result = (inputByte - entries[encPtr]) & 0xFF
            if self.printLog:
                print(f'pos {tblPtr}, value {inputByte} ({hex(inputByte)}), encbyte {entries[encPtr]}, result is {result}')
            # Update the data in the block.
            blocks[i] = result
            # Update blockPtr.
            tblPtr += 1
            encPtr += 1

        # String everything together. If we use twoBitsStart, that will be our base point.
        outString = twoBitsStart
		# We start at the end and work backwards; the last encryption block is
        # the first 8 bits in the bitstream. That's just how it works.
        for blockPtr in range(len(blocks) - 1, -1, -1):
            outString += numToBits(blocks[blockPtr], 8)
        # Re-add the checksums to the data.
        outString += skyChecksumBits + checksumBits
        return outString

    def encryptBitStream(self, curBitStream):
        '''
        Encrypts a bitstream according to the encryption data.
        '''
        return self.decryptBitStream(curBitStream, encrypt=True)

    def bitsToStructure(self, bitString):
        '''
        Converts a bit string to our internal structure.
        '''
        bitPtr = 0
        outputStruct = {}
        outputStructBit = {}
        for structPtr in range(len(WMSStruct)):
            structInfo = WMSStruct[structPtr]
            bitData = bitString[bitPtr : bitPtr + structInfo['size']]
            bitPtr += structInfo['size']
            numData = bitsToNum(bitData, 8)
            outputStruct[structInfo['name']] = numData
            outputStructBit[structInfo['name']] = bitData

        # We should be at the end now
        if bitPtr != len(bitString):
            warnings.warn('Not all available data was parsed into struct. '
            f'Final bitPtr is {bitPtr}, length is {len(bitString)}', RuntimeWarning)

        if self.printLog:
            print(f'outStruct: {outputStruct}, bitStruct: {outputStructBit}')
        return outputStruct

    def calculateChecksum(self, bitStream):
        '''
        Calculates the checksum for a given bitStream.
        '''
        if self.printLog:
            print(f'Sky Checksum calculation - bitStream of length {len(bitStream)}')
        if len(bitStream) == 170:
            if self.printLog:
                print('Truncating the 170-long bitStream for you. By golly, I\'m so nice.')
            bitStream = bitStream[2 : 138]
        if len(bitStream) != 136:
            warnings.warn(f'bitStream should be 136 bits long - currently {len(bitStream)}')

        checksum = 0xFFFFFFFF
        data = ''
        for i in range(16, -1, -1):
            bits = bitStream[i * 8 : i * 8 + 8]   
            num = bitsToNum(bits)
            data += chr(num).encode('utf-16', 'surrogatepass').decode('utf-16')
            entry = self.skyChecksumData[(checksum ^ num) & 0xFF]
            checksum = (checksum >> 8) ^ entry

        checksum = checksum ^ 0xFFFFFFFF
        if checksum < 0:
            checksum += 4294967296
        if self.printLog:
            print(f'Generated a Sky checksum of {checksum} ({hex(checksum)})')
        return checksum
        
    def structureToBits(self, inputStruct):
        '''
        Converts an object to an unencrypted bitstream.
        '''
        bitStream = ''
        totalSize = 0
        for i in range(len(WMSStruct)):
            key = WMSStruct[i]
            if key.get('noinclude', False):
                continue
            if key['name'] not in inputStruct:
                raise ValueError(f"The key {key['name']} was not defined in inputStruct {inputStruct}")

            data = inputStruct[key['name']]
            binData = numToBits(data, key['size'])
            bitStream += binData
            totalSize += key['size']

		# For Sky, our "null" byte is 8 bits in length. However, 2 of those bits aren't encrypted.
        # To make it easier on ourselves, we chop those two off here and re-add them later.
        # These will always be zero so it's ok.
        bitStream = bitStream[2:]
        if self.printLog:
            print(f'Generated a {len(bitStream)}-length bitStream: {bitStream}')
        checksum = self.calculateChecksum(bitStream)
        bitStream = "00" + bitStream + numToBits(checksum, 32)
        return bitStream


class WMSGen:
    def __init__(self, missionType='Rescue Client', missionSubType=None, dungeon='Beach Cave',
            floor=1, client='Bulbasaur', clientGender='Male', target='Bulbasaur',
            targetGender='Male', targetItem=None, rewardType='Item + ??? (Random)',
            rewardItem=None, isEuropean=False, advanced=False, flavorText=None, specialFloor=None, printLog=True):

        # set all user inputs and defaults
        self.missionType = missionType
        self.missionSubType = missionSubType
        self.dungeon = dungeon
        self.floor = floor
        self.client = client
        self.clientGender = clientGender
        self.target = target
        self.targetGender = targetGender
        self.targetItem = targetItem
        self.rewardType = rewardType
        self.rewardItem = rewardItem
        self.isEuropean = isEuropean
        self.advanced = advanced
        self.flavorText = flavorText
        self.specialFloor = specialFloor

        # convert user inputs to integer/boolean data
        clientFemale = (self.clientGender == ' Female')
        targetFemale = (self.targetGender == 'Female')
        typeData, typeNum, subTypeData, subTypeNum = self.getTypeData()
        rewardTypeNum = self.getRewardType(self.rewardType)
        client = typeData.get('forceClient', getTrueMonId(self.getMon(self.client), clientFemale))
        if typeData.get('clientIsTarget', False):
            target = typeData.get('forceTarget', client)
        else:
            target = getTrueMonId(self.getMon(self.target), targetFemale)
        target2 = target if typeData.get('target2', False) else 0

        if typeData.get('noReward', False):
            rewardTypeNum = 1
            rewardNum = 109  # apple
        elif 1 <= rewardTypeNum <= 4:
            rewardNum = self.getItem(self.rewardItem)
        elif 5 <= rewardTypeNum <= 6:
            rewardNum = client
        else:
            rewardNum = 109

        if typeData.get('useTargetItem', False):
            targetItemNum = self.getItem(self.targetItem)
        else:
            targetItemNum = 109

        dungeonNum = self.getDungeon(self.dungeon)
        dungeonNum |= 1
        floor = self.floor if 1 <= self.floor <= 99 else 1

        if self.specialFloor is not None:
            specialFloor = self.specialFloor
        elif typeData.get('specialFloor', False):
            specialFloor = typeData['specialFloor']
        elif typeData.get('specialFloorFromList', False):
            listName = typeData['specialFloorFromList']
            if listName not in WMSGenData['staticLists']:
                raise ValueError(f'Static list {listName} not found.')
            specialFloor = random.choice(typeData['specialFloorFromList'][listName])
        else:
            specialFloor = 0

        struct = {
            'missionType': typeNum,
            'missionSpecial': subTypeNum,
            'nullBits': 0,
            'mailType': 4,
            'restriction': 0,
            'restrictionType': 0,
            'rewardType': rewardTypeNum,
            'reward': rewardNum,
            'targetItem': targetItemNum,
            'client': client,
            'target': target,
            'target2': target2,
            'dungeon': dungeonNum,
            'floor': floor,
            'specialFloor': specialFloor,
        }

        parser = WMSParser(printLog=printLog)

        if self.flavorText is not None:
            struct['flavorText'] = flavorText
            decBitStream = parser.structureToBits(struct)
        else:
            struct['flavorText'] = 300000 if self.advanced else random.randint(300000, 399999)
            decBitStream = parser.structureToBits(struct)
            checksum = bitsToNum(decBitStream[:138])
            resetByte = parser.getResetByte(checksum)
            if printLog:
                print(f'flavorText {flavorText}, checksum {checksum}, reset {resetByte}')

        encBitStream = parser.encryptBitStream(decBitStream)
        bitpacked = parser.bitsToBytes(encBitStream)
        byteSwap = parser.byteSwapEU if self.isEuropean else parser.byteSwap
        scrambled = parser.scrambleString(bitpacked, byteSwap)
        prettified = parser.prettyMailString(scrambled, 2, 7)
        if printLog:
            print(f'enc: {encBitStream}, packed: {bitpacked}, scrambled: {scrambled}, prettified: {prettified}')
        self.wonderMailCode = prettified
        

    def getTypeData(self) -> tuple[dict, int, dict, int]:
        '''
        Converts the mission type string to data
        '''
        for mission in WMSGenData['missionTypes']:
            if mission['name'] == self.missionType:
                typeData = mission
                typeNum = mission['mainType']
                break
        else:
            return False, False

        if 'subTypes' in typeData:
            for subType in typeData['subTypes']:
                if subType['name'] == self.missionSubType:
                    subTypeNum = subType['specialType']
                    subTypeData = subType
                    break
            else:
                return typeData, typeNum, False, False
        else:
            return typeData, typeNum, False, False
        
        return typeData, typeNum, subTypeData, subTypeNum

    # dict reverse lookups

    def getRewardType(self, rewardType):
        for key, value in WMRewardType.items():
            if value == rewardType:
                return key
        else:
            return False

    def getMon(self, pokemonName):
        for key, value in WMSkyPoke.items():
            if value == pokemonName:
                return key
        else:
            return False

    def getItem(self, itemName):
        for key, value in WMSkyItem.items():
            if value == itemName:
                return key
        else:
            return False

    def getDungeon(self, dungeonName):
        for key, value in WMSkyDungeon.items():
            if value == dungeonName:
                return key
        else:
            return False


wm = WMSGen(
    missionType='Rescue client',
    dungeon='Waterfall Cave',
    floor=4,
    client='Squirtle',
    clientGender='Male',
    rewardType='Item + ??? (Random)',
    rewardItem='Lockon Specs',
    printLog=False)

print(wm.wonderMailCode)
