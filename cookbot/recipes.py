# -*- coding: utf-8 -*-

import re


RECIPES = {"burger": {"the original": "mlbctE",
		      "the double": "mmlbctE",
		      "blt": "bltE",
		      "blt and c": "bltcE",
		      "the heartstopper": "mmbbcE",
		      "the lite delight": "mlE",
		      "the ryan davis": "mbcctE",
		      "the tumbleweed": "bcE",
		      "the lonely patty": "mE",
		      "the triple": "mmmcE",
		      "the triple w/bacon": "mmmbcE",
		      "the red": "mtE",
		      "the veggie": "ltpE",
		      "the pickler": "mcpE",
		      "the trio": "mtpE",
		      "the p-d": "mmbpE",
		      "the stacked": "mlbctpE",
		      "the greens": "mlpE",
		      "the super sour": "mtpoE",
		      "the aroma": "moE",
		      "the extra veggies": "ltpoE",
		      "the power": "mmbcoE",
		      "the blot": "blotE",
		      "the c-blot": "cblotE",
		      "the cheesy bread": "bcsE",
		      "the melt": "mcsE",
		      "the swiss": "mltsE",
		      "the holy burger": "mlosE",
		      "chubigans special": "mlbcsE",
		      "the double melt": "mmcsE",
                      
                      "the chick-a": "kpE",
                      "the chick-a deluxe": "kltpE",
                      "the chick-a surpreme": "klbctpE",
                      "the chick-a melt": "kbcpsE",
                      "the three cs": "kcsE",
                      "the double cs": "kklpE",
                      "the meat lovers": "kmbE",
                      "the mix burger": "kmlctE",
                      "the american": "kmbcosE",
                      "the everything": "mklpbocstE",
                      
                      
		     },
	   "salad": {"house salad": "rcbE",
		     "cheesy leaves": "rcE",
		     "pepper ranch": "rcoE",
		     "the dry greens": "gE",
		     "the dry deluxe": "mgE",
		     "kids delight": "rcE",
		     "the manhattan": "rcbomgE",
		     "the mix salad": "rcboE",
		     "tomato ranch": "rcmE",
		     "the big salad": "cgE",
		     "cheesy peppers": "coE",
		     "salad verde": "rgE",
		     "the thousand salad": "tcgE",
		     "the thousand peppers": "tcoE",
		     "thousand house": "tcbE",
		     "thousand tomatoes": "tcmE",
		     "three thousand": "tcbogE",
		     "a thousand flavors": "tcbomgE",
		     "the oily pepper": "vcoE",
		     "the oil bleu": "vcbomgE",
		     "vinaigrette house": "vcbE",
		     "the oily greens": "vmgE",
		     "cheesy vinaigrette": "vcE",
		     "vinaigrette classic": "vcobmE",
		    },

           
           "corn_dog": {"the classic corn dog": "kmE",
                        "the red dog": "kE",
                        "the yellow dog": "mE",
                        "the gerstmann": "kE",
                        },

           "sushi": {"standard sampler": "eerrttuuE",
                     "roe special": "eeerrrrtE",
                     "tuna platter": "ertuuuuuE",
                     "ebi special": "eeeeertuE",
                     "ocean plate": "eeerrtuuE",
                     "sea spirit": "errtttuuE",
                     "mixed delicious": "eerrrttuE",
                     "toro special": "ertttttuE",
                     "salmon special": "erusssssE",
                     "fives delight": "erttusssE",
                     "delight platter": "eerrtussE",
                     "plate of great": "errtuussE",
                     "ets tray": "eeettsssE",
                     "shogun plate": "rrrttussE",
                     "east sampler": "eettuussE",
                     "mackerel special": "uusmmmmmE",
                     "gourmet platter": "eerrtummE",
                     "special sampler": "eertusmmE",
                     "the mix sushi": "etuusmmmE",
                     "rice sampler": "eettssmmE",
                     "chomper plate": "errruusmE",

                     "yellowtail special": "tsmyyyyyE",
                     "gourmet sampler": "ertussmyE",
                     "bail tray": "tummyyyyE",
                     "yum tray": "rruusyyyE",
                     "sea of oceans": "eeetuuyyE",
                     "blue oil delight": "rrttssmyE",

                     "unagi special": "rmygggggE",
                     "emperor special": "ertusmygE",
                     "golden tray": "usmyggggE",
                     "fortune": "smmyygggE",
                     "slam platter": "eerummygE",
                     "tray platter plate": "rrruumygE",
                     "the mysteries": "eeetsgggE",
                     "royal debut": "tttsyyygE",
                     "crunchy plate": "uuummmygE",
                     
                     
                     },

           "baked_potato": {"classic baked potato": "csyE",
                            "classic potato w/bacon": "csybE",
                            "deluxe potato": "csyhboE",
                            "plain potato": "yE",
                            "sour potato": "soE",
                            "lite potato": "shoE",
                            "the dry potato": "E",
                            "sour potato w/bacon": "sboE",
                            "lite n cheesy potato": "csE",
                            "chives & bacon potato": "yhbE",

                            "spicy olive potato": "csyvpE",
                            "spicy classic potato": "csypE",
                            "spicy bacon potato": "csybopE",
                            "spicy deluxe potato": "cyhbovpE",
                            "broccoli & cheesy potato": "rqE",
                            "broccoli & cheesy surpreme potato": "borqE",
                            "green potato": "cshovprE",
                            "cheesy deluxe potato": "cybpqE",

                            "meat classic potato": "csbmE",
                            "meaty deluxe potato": "hbpqmE",
                            "simply meat potato": "ymE",
                            "meaty broccoli potato": "prqmE",
                            "fully loaded potato": "csyhbovprmE",
                            "fully loaded potato w/queso": "syhbovprqmE",
                            },

           "lasagna": {"classic italian lasagna": "pscrpscrpscrE",
                       "meaty rome lasagna": "psmcrpsmcrpscrE",
                       "vegetable lasagna": "psvcrpsvcrpscrE",
                       "stuffed piza lasagna": "psmcrpsvcrpscrE",
                       },

           "nachos": {"classic nachos": "qgE",
                      "surpreme nachos": "qcjtgE",
                      "royal nachos": "qcuvjtogE",
                      "veggie nachos": "qvjtoE",
                      "sour veggie nachos": "qcvjtoE",
                      "guac a nachos": "quE",
                      "fiesty nachos": "qcujoE",
                      "guac and chips": "ujtE",
                      "jalanacho": "qjE",
                      "bowl of chips": "E",
                      "italian style nachos": "qvogE",
                      "scoops of plenty": "qcuoE",
                      "the chubigans special": "qbrgE",
                      "mexican siesta": 'qubrgE',
                      "mexican fiesta": 'qcvjtobrE',
                      "rice and beans": 'qbrE',
                      "beef and beans": 'qbgE',
                      "spicy rice special": 'qcjtorE',

                      "shrimp nachos": "qcujtsE",
                      "deluxe shrimp nachos": "qcuvjtobgsE",
                      "new orleans nachos": "quvtbrsE",
                      "classic shrimp nachos": "qcusE",

                      "beefy surpreme": "qubfgE",
                      "beef fajita nachos": "qcutobfE",
                      "chicken fajita nachos": "qcutobkE",
                      "combo fajita nachos": "qcutobkfE",
                      "extreme fajitas": "qcjtobkfsE",
                      "chubigans deluxe special": "qbrkfE",
                      "classic american": "qcuvjtkfgE",
                      "fiery fiesta nachos": "qvjorksE",
                      "all meat special": "qcubkfsgE",

#                      "fully loaded nachos": "
                      },

           "pancakes": {"double header": "eshE",
                        "junior blueberry": "plbE",
                        "lite maple classic": "ppmE",
                        "the lonely pancake": "pE",
                        "triple berry blue": "ppplbE",
                        "triple pecan stack": "pppebE",                        
                        'blue double stack': 'pplbE',
                        'double desert': 'ppbE',
                        'double strawberry': 'ppsbE',
                        'dry single': 'pbE',
                        'dual maple stack': 'ppmbE',
                        'junior classic': 'pmbE',
                        'junior redberry': 'psbE',
                        'triple dry': 'pppbE',
                        'triple maple': 'pppmbE',
                        'triple red stack': 'pppsbE',
                        'junior pecan': 'pebE',
                        'double pecan stack': 'ppebE',
                        'lite double pecan': 'ppeE',
                        },

           "pizza": {'meat pizza': 'tcsE',
                     'bacon and mushroom pizza': 'tcbuE',
                     'meaty anchovy pizza': 'tcpsbaE',
                     'cheese pizza': 'tcE',
                     'veggie pizza': 'tcuvnE',
                     'p&m pizza': 'tcpsE',
                     'pepperoni pizza': 'tcpE',
                     'the pcgb pizza': 'tcpbnE',
                     'italian pizza': 'tcsuvnE',
                     'cheesy bread': 'cE',
                     'anchovy pizza': 'tcaE',
                     'dairy-lite pizza': 'tauE',
                     'olives and onions pizza': 'tcvnE',
                     'deluxe pizza': 'tcpsbuvnE',
                     'deluxe anchovy pizza': 'tcaunvE',
                     'meatlovers pizza': 'tcpsbE',

                     'pineapple and ham pizza': 'tchiE',
                     'the hawaiian pizza': 'tcpbhniE',
                     'sweet veggie p.': 'tcuviE',
                     'extra meat lovers pizza': 'tcpsbhE',
                     'super surpreme pizza': 'tcpsbahuvniE',
                     'the h. a. m. pizza': 'tcahuE',

                     'tomato lovers pizza': 'tcpoE',
                     'tomato & anchovy pizza': 'tcaoE',
                     'tomato & pineapple pizza': 'tcioE',
                     'the all-meat-tomato pizza': 'tcpsbahoE',
                     
                     'pesto pepperoni pizza': 'gcpE',
                     'all veggie pesto pizza': 'gcuvnioE',
                     'super deluxe pesto pizza': 'gcaphsbuvnioE',
                     'anchovy pesto pizza': 'gcauE',
                     'meat lovers pesto pizza': 'gcpsbhE',
                     'pineapple and ham pesto pizza': 'gchiE',
                     'sweet veggie pesto p.': 'gcuviE',
                     'cheesy pesto pizza': 'gcE',
                     'piggy pesto pizza': 'gcbhunE',
                     'italian pesto pizza': 'gcpuvnoE',
                     
                     },

           
           "pretzel": {"the buttery curves": "bE",
                       "the dry twister": "E",
                       "the classic pretzel": "sbE",
                       "the sweet twist": "bcE",
                       "the salty knot": "sE",
                       "cinnamon pretzel": "cE",
                       },

           "pasta": {'cheesy veggie pasta': 'cpusoE',
                     'creamy meat pasta': 'wmkbuE',
                     'cheesy meaty pasta': 'cmkbE',
                     'classic spaghetti': 'rmE',
                     'cheesy chicken pasta': 'ckbE',
                     'spaghetti deluxe': 'rmbusE',
                     'cheesy onion pasta': 'coE',
                     'red veggie pasta': 'rpusoE',
                     'cheese pasta': 'cE',
                     'spicy bacon pasta': 'rbiE',
                     'spicy spaghetti': 'rmiE',
                     'the meaty pasta': 'rmkbE',
                     'the carbonara': 'wkbpuiE',
                     'creamy veggie pasta': 'wpusoE',
                     'cheesy deluxe pasta': 'cmkbpusoE',
                     'red deluxe pasta': 'rmkbpusoE',
                     'creamy alfredo': 'wksE',
                     'hot bacon pasta': 'rbpE',
                     'the dry tomato': 'mtE',
                     'red pasta rally': 'rpitE',
                     'dry veggie pasta': 'psitE',
                     'cheesy tomato': 'citE',
                     'spaghetti pesto': 'gmE',
                     'manhattan pesto': 'gmkbpusoitE',

                     'chicken pesto': 'gkuiE',
                     'verde pesto': 'gsiE',

                     },

           "icecream": {"plain vanilla": "vvvE",
                        "plain chocolate": "cccE",
                        "vanilla and chocolate": "vcE",
                        "the yin and yang": "vchpE",
                        "cherry vanilla": "vvhE",
                        "chocolate sprinkles": "ccpE",
                        "trio of delicious": "vcmE",
                        "minty deluxe": "mmhwnE",
                        "mint cherry": "mmhE",
                        "nutty mint": "mmnE",
                        "nutty vanilla": "vvnE",
                        "nutty chocolate": "ccnE",

                        "vanilla dream": "vvvhpwnosE",
                        "chocolate heaven": "cmmhpwnosE",
                        "deluxe butter pecan": "bbhpwnosE",
                        "buttery nuts": "bbhwnE",
                        "birthday surprise": "vcbhpowE",
                        "the fiesta bowl": "cmbhpwsE",
                        },

           "soup": {"creamy potato": "spbc.E",
                    "baristobo soup": "kwsp.aDDD.lDDD.E",
                    "soup du jour": "wus.tDDD.aDDD.yDDD.E",
                    "vegetable soup": "tDDD.aDDD.yDDD.lDDD.d.E",
                    "chicken noodle soup": "kwu.yDDD.E",
                    "louisiana delight": "kmiusb.yDDD.E",
                    "hearty meat soup": "kmihpc.yDDD.g.E",
                    "one bean soup": "isp.yDDD.eE",

                    "broccoli soup": "sbc.aDDD.r.E",
                    "italian soup": "mibc.tDDD.zDDD.o.E",
                    "suino stew": "hwc.lDDD.zDDD.go.E",
                    },

           
           'soda': {'jumbo cola': 'UUUDiE',
                    'jumbo cola (no ice)': 'UUUDE',
                    'jumbo cola (no ice) w/flavor blast': 'UUUDfE',
                    'jumbo cola w/flavor blast': 'UUUDifE',
                    'jumbo diet': 'RRRRUUUDiE',
                    'jumbo diet w/flavor blast': 'RRRRUUUDifE',
                    'jumbo grape': 'RRUUUDiE',
                    'jumbo grape w/flavor blast': 'RRUUUDifE',
                    'jumbo tea': 'RUUUDiE',
                    'jumbo tea w/flavor blast': 'RUUUDifE',
                    'jumbo water': 'RRRUUUDiE',
                    'jumbo water w/flavor blast': 'RRRUUUDifE',
                    'large cola': 'UUDiE',
                    'large cola (no ice)': 'UUDE',
                    'large cola w/flavor blast': 'UUDifE',
                    'large diet': 'RRRRUUDiE',
                    'large diet w/flavor blast': 'RRRRUUDifE',
                    'large grape': 'RRUUDiE',
                    'large grape w/flavor blast': 'RRUUDifE',
                    'large tea': 'RUUDiE',
                    'large water': 'RRRUUDiE',
                    'medium cola': 'UDiE',
                    'medium cola (no ice)': 'UDE',
                    'medium cola w/flavor blast': 'UDifE',
                    'medium diet': 'RRRRUDiE',
                    'medium diet w/flavor blast': 'RRRRUDifE',
                    'medium grape': 'RRUDiE',
                    'medium grape w/flavor blast': 'RRUDifE',
                    'medium tea': 'RUDiE',
                    'medium water': 'RRRUDiE',
                    'small cola': 'DiE',
                    'small cola (no ice)': 'DE',
                    'small cola (no ice) w/flavor blast': 'DfE',
                    'small cola w/flavor blast': 'DifE',
                    'small diet': 'RRRRDiE',
                    'small diet w/flavor blast': 'RRRRDifE',
                    'small grape': 'RRDiE',
                    'small grape w/flavor blast': 'RRDifE',
                    'small tea': 'RDiE',
                    'small tea w/flavor blast': 'RDifE',
                    'small water': 'RRRDiE',
                    'small water w/flavor blast': 'RRRDifE',
                    },

           
           "sopapillas": {"delicious lite sopapillas": "D[2.5].pE",
                          "delicious sopapillas": "D[2.5].psE",
                          },

           "fries": {"thick cut lite fries": "D[3.1].pE",
                     "thick cut fries": "D[3.1].paE",
                     "thick cut sea fries": "D[3.1].peE",
                     "fast fries": "D[3.1].paE",
                     "sweetest potato fries": "D[3.1].psE",
                     "sweet potato fries": "D[3.1].paE",
                     "sweet potato mix fries": "D[3.1].pasE",
                     "sweet potato sea fries": "D[3.1].peE",
                     "lite fast fries": "D[3.1].pE",
                     },

           "steak": {"classic steak": "sssjE",
                     "citrus steak": "sjjcE",
                     "spicy steak": "sppppjjE",
                     "the dry spicy steak": "sppE",
                     "baconesque": "sjjbbE",
                     "spicy baconesque": "sjppbbE",
                     "spicy smokey steak": "ssdpppjjE",
                     "smokey orange steak": "sdjccE",
                     "hickory steak": "sshhjjjjE",
                     "west texas steak": "ssjjppbbddhhE",
                     },

           "dishes": {"work ticket (dishes)": '(LRU)*3 .[0.5]',                      
                      },

           "trash": {"work ticket (trash)": "(U.R)*3 .s .[0.5]",
                     },

           "rodents": {"work ticket (rodents)": "R.D.c.s.[0.5]",
                       },

           "toilet": {"work ticket (clean)": "D.s.[0.5]",
                      },

           
           "beer": {"the rich brewsky": "D[1.4].E",
                    "the brewsky": "D[1.4].E",
                    },

           "fish": {"grey tail fish": "LDRsE",
                    "long body brown raccuda": "LDRsE",
                    "long body brown raccuda w/lemon": "LDRslE",
                    "rainbow gruza": 'LDRsE',
                    "rainbow gruza w/lemon": 'LDRslE',
                    },

           "chicken_breast": {"plump chicken breast": "t*6.sE",
                              "rich chicken breast": "t*6.sE",
                              "classic chicken breast": "t*6.sE",
                              "rich chicken breast": "t*6.sE",
                              },
           
           
           "fried_chicken": {"golden fried chicken": "D[3.5].pE",
                             "greasy fried chicken": "D[3.5].pE",
                             },

           "wine": {"le cheap valu-wine": "U[0.03,0.02]*30 E",
                    "casu marzu": "w U[0.03,0.02]*30 E",
                    "serpent beard": "ww U[0.03,0.02]*30 E",
                    "elk": "www U[0.03,0.02]*30 E",
                    "deckard vineyards": "wwww U[0.03,0.02]*30 E",
                    },

           "shish_kabob": {"classic kabob": "tmgrtkgrE",
                           "meaty kabob": "mktmkgmkE",
                           "pepper kabob": "grtgrmgrE",
                           "red kabob": "trmtrgtrE",
                           "kabobber": "tmkgtmkrE",
                           "chicken kabob": "ktkgkrktE",

                           "onion kabob": "otokogorE",
                           "tower kabob": "mogrkogrE",
                           "tangy kabob": "ogrogrotE",
                           "juicy kabob": "mokomgkoE",

                           "hawaiian kabob": "koptkopmE",
                           "pineapple kabob": "ptpmpkpoE",
                           "kabomber": "kgrompmpE",
                           "kabob sampler": "ptkmgropE",

                           "squash kabob": "sposprsgE",
                           "yellow kabob": "spmspkspE",
                           "crazy kabob": "sogtsogkE",
                           "kabob platter": "ktgropskE",

                           "veggie kabob": "uzoguzotE",
                           "american kabob": "usoruskmE",
                           "green kabob": "kgzukgzuE",
                           "odessa kabob": "mzsmzumzE",
                           "kabob special": "tgputgpuE",
                           "tomato kabob": "tmutkutzE",
                           
                           },

           "fried_rice": {"sour fried rice": "feoE",
                          "classic fried rice": "fpceoE",
                          "lite fried rice": "fpcE",
                          "sweet fried rice": "fpceE",
                          "crunchy white rice": "feonE",
                          "classic white rice": "wpceoE",
                          "yellow white rice": "wenE",
                          },
           
           "breakfast_sandwich": {'double am': 'esbE',
                                  'egg biscuit': 'eE',
                                  'morning fuel': 'sbE',
                                  'sunrise sandwich': 'sE',
                                  'the classic': 'ebE',
                                  'the deluxe': 'esE',
                                  'the megabiscuit': 'esbchE',

                                  "ham & egg": "heE",
                                  "my hammy": "hE",
                                  "tower biscuit": "bcE",

                                  "cheesy deluxe": "escE",
                                  "the early bird": "esbcE",
                                  "cheesy am": "scE",
                                  "sherrisoda special": "ebchE",
                                  },

           "lobster": {"classic lobster": "bE",
                       "buttery lobster": "bbE",
                       "classic lite lobster": "E",

                       "buttery cocktail": "bcE",
                       "double cocktail": "ccE",
                       "lobster cocktail": "cE",

                       "garlic cocktail": "acE",
                       "buttery garlic": "baE",
                       "garlic lobster": "aE",

                       "tangy garlic": "agE",
                       "ginger cocktail": "cgE",
                       "ginger lobster": "gE",
                      
                       },

           "enchiladas": {"junior stack": "DUtcE",
                          "double stack": "(DUt)*2 cE",
                          "triple w/egg": "(DUt)*3 ceE",
                          "triple stack": "(DUt)*3 cE",
                          "triple w/onion": "(DUt)*3 coE",
                          "triple works": "(DUt)*3 ceoE",
                          "junior w/onion": "DUtcoE",
                          "double onion": "(DUt)*2 coE",
                          "double works": "(DUt)*2 ceoE",
                          },

           "banana_foster": {"bananas foster": "bs .[2.7] aE",
                             "bananas foster flambe": "bs .[2.7] arfE",
                             },

           "hash_browns": {"lite hash patties": "D[2.1].pE",
                           "hash patties": "D[2.1].psE",
                           "lite golden hash browns": "D[2.1] pE",
                           "golden hash browns": "D[2.1] psE",

                           },
           
           "coffee": {"black coffee": 'DE',
                      "coffee with cream": 'DcE',
                      "coffee with sugar": 'Ds*{0}E|([1-5]).*?sugar',
                      "fully loaded": 'Dcs*{0}E|([1-5]).*?sugar',
                      },

           "metagame": {"battle kitchen upgrade": ".[1]",
                        "check out my picture": "t",
                        "textin my sweetie": "",
                        }
           
           }


#import pprint
#pprint.pprint(RECIPES['grill'])

# build identifying dict
FOODS = {}

for food, recipes in RECIPES.iteritems():
    for r in recipes:
        FOODS[r] = food


# build grill data
RECIPES['pancakes_grill'] = {k: list(v).count('p') * 'p' + 'E' for (k, v) in RECIPES['pancakes'].items()}
RECIPES['nachos_grill'] =  {k: ''.join(x for x in v if x in 'gksfE') for (k, v) in RECIPES['nachos'].items()}
RECIPES['burger_grill'] = {k: ''.join(x for x in v if x in 'mkE') for (k, v) in RECIPES['burger'].items()}
RECIPES['pasta_grill'] = {k: 'rE' for k in RECIPES['pasta']}
RECIPES['lobster_grill'] = {k: 'lE' for k in RECIPES['lobster']}



# whether the food is finished after cooking or preparation
FINISH_AT = {"burger": "p",
             "burger_grill": "p",
             "salad": "p",
             "corn_dog": "p",
             "sushi": "p",
             "baked_potato": "p",
             "lasagna": "r",
             "nachos": "p",
             "nachos_grill": "p",
             "pancakes": "p",
             "pancakes_grill": "p",
             "pizza": "r",
             "pretzel": "p",
             "pasta": "p",
             "pasta_grill": "p",
             "icecream": "p",
             "soup": "r",
             "soda": "p",
             "sopapillas": "p",
             "fries": "p",
             "steak": "r",
             "beer": "p",
             "fish": "r",
             "chicken_breast": "r",
             "fried_chicken": "p",
             "wine": "p",
             "shish_kabob": "r",
             "fried_rice": "r",
             "breakfast_sandwich": "r",
             "lobster": "p",
             "lobster_grill": "p",
             "enchiladas": "p",
             "banana_foster": "p",
             "hash_browns": "p",
             "coffee": "p",
             }
             

COOKING_TIME = {'burger_grill': 9,
                'steak': 20,
                'fish': 10,
                'chicken_breast': 17,
                'fried_rice': 8,
                'nachos_grill': 9,
                'lasagna': 12,
                'pasta_grill': 12,
                'pizza': 10,
                'soup': 14,
                'breakfast_sandwich': 8,
                'pancakes_grill': 8,
                'lobster_grill': 13,
                'shish_kabob': 10,
                }


class RecipesBase(object):
    def __init__(self):
        pass

    def get_recipe(self, food, window):
        recipe = RECIPES[food][window.title]

        if '|' in recipe:

            recipe, expr = recipe.split('|')
            
            g = re.search(expr, window.text)

            if g is None:
                return
            
            recipe = recipe.format(*g.groups())

        return recipe


if __name__ == '__main__':

    d = []

    from tabulate import tabulate
    
    for food, recipes in RECIPES.iteritems():
        finish = 'prep' if FINISH_AT.get(food, 'p') == 'p' else 'cook'
        time = COOKING_TIME.get(food, 0)
        
        for name, recipe in recipes.iteritems():
            d.append((food, name, finish, time, recipe, ''))

    d.sort()

            
    print tabulate(d, ('food', 'name', 'ready', 'dT', 'recipe', 'expr'), tablefmt="simple")
