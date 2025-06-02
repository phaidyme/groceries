import csv
from rapidfuzz import fuzz
    
nutrient_information = {}
nutrient_information = {}
with open(
    "All solids & liquids per 100g-Table 1.csv",
    newline="",
    encoding="utf-8",
) as csvfile:
    reader = csv.reader(csvfile)
    headers = next(reader)
    relevant_columns = []
    names = []
    suffixes = []
    for i, header in enumerate(headers[3:-5], 3):
        header = header.lower()
        if "%t" in header or "mg/gn" in header:
            continue
        else:
            relevant_columns.append(i)
            name, unit = header.rsplit("(", 1)
            names.append(name.strip())
            suffixes.append({
                "g": "", "mg": "e-3", "ug": "e-6",
                "kj": ""
            }[unit[:-1]])
    for row in reader:
        name = row[2].lower().split(", ")
        name = [part.strip() for part in name]
        name = " ".join(name)
        nutrients = {}
        for i, column in enumerate(relevant_columns):
            value = row[column]
            if value and value != "0.0" and value != "0":
                value = value.replace(',', '')
                nutrients[names[i]] = float(value + suffixes[i])
        nutrient_information[name] = nutrients

with open("cart.txt", 'r') as file:
    text = file.read().lower()
with open("weights.csv", 'r') as file:
    weights = {name: weight for name, weight in csv.reader(file.readlines())}

items = []
for lines in text.split('in cart'):
    if lines:
        lines = lines.split('\n')
        item = []
        for line in lines:
            line = line.strip()
            if line in ["", "kg", "in-store only", 'afternoon delivery & pick up']: continue
            if any(line.startswith(phrase) for phrase in ["was $", "save $"]): continue
            if any([all([word in line for word in l]) for l in [["low", "price"]]]): continue
            item.append(line)
        assert len(item) == 4
        items.append(item)

cart = {}
for item in items:
    assert item[1].startswith('$')
    assert all([
        item[2].startswith('$'),
        '/' in item[2],
        any([
            item[2].endswith('g'),
            item[2].endswith('l'),
            item[2].endswith('ea')
        ])
    ])
    name = item[0]
    for thing in ["no added salt"]:
        name = name.replace(thing, "")
    for thing in ["each", "per kg", "from the deli"]:
        name = name.removesuffix(" "+thing)
    for brand in ["woolworths", "essentials", "macro organic"]:
        name = name.removeprefix(brand+" ")
    price = float(item[1][1:])
    unit_price, unit_amount = item[2].split(' / ')
    
    amount = False
    if name == "twinings english breakfast tea bags 100 pack":
        amount = 284 * 100 # mL in a cup
    else:
        suffixes = {"ml": "", "l": "e+3", "kg": "e+3", "g": ""}
        for key in suffixes.keys():
            if name.endswith(key):
                try:
                    amount = float(
                        name.split()[-1].removesuffix(key) + suffixes[key]
                    )
                    name = ' '.join(name.split()[:-1])
                except ValueError:
                    pass
                break
        
    if not amount:
        if unit_amount == "1ea":
            options = {}
            for key, value in weights.items():
                if key in name.split():
                    options[key] = value
                else:
                    if key[-1] == ')':
                        key = key.split()[0]
                    if key in name.split():
                        options[key] = value
                    elif key[-1] == 's' and key[:-1] in name.split():
                        options[key] = value
            assert len(options) == 1
            amount = float(list(options.values())[0])
            if name.endswith(" quarter"):
                amount /= 4
                name = name.removesuffix(" quarter")
        else:
            amount = float({
                "1kg": 1000, "100g": 100, "100ml": 100, "700g": 700, "1l": 1000
            }[unit_amount])
    
    if item[3].endswith(" kg"):
        price = price * float(item[3].split()[0] + "e+3") / amount
        amount = float(item[3].split()[0] + "e+3")
    else:
        price *= float(item[3].split()[0])
        amount *= float(item[3].split()[0])
    
    cart[name] = [price, amount]

name_map = {key: value.lower().replace(', ', ' ') for key, value in {
    "fresh oysters pacific": "oyster pacific aquacultured raw",
    "d'orsogna chorizo": "sausage chorizo uncooked",
    "don italian style salami shaved": "salami milano",
    "lentils": "lentil dried boiled drained",
    "canola oil": "oil canola",
    "cannellini beans": "baked beans canned in tomato sauce",
    "chickpeas": "chickpea canned drained",
    "black bean": "baked beans canned in tomato sauce",
    "whole egg mayonnaise": "mayonnaise traditional (greater than 65% fat) commercial",
    "nice rice medium grain brown rice": "rice brown uncooked",
    "pure honey": "honey",
    "tomato sauce squeeze": "sauce tomato commercial",
    "corn sweet kernels": "corn kernels canned in brine drained",
    "moccona freeze dried instant coffee classic medium roast": "coffee instant dry powder or granules",
    "lee kum kee soy sauce premium": "sauce soy commercial",
    "tuna chunks in spring water": "tuna yellowfin flesh raw",
    "twinings english breakfast tea bags 100 pack": "Tea, regular, black, brewed from leaf or teabags, without milk",
    "pinto beans": "baked beans canned in tomato sauce",
    "adzuki beans": "baked beans canned in tomato sauce",
    "la gina italian tomato paste passata": "tomato paste with added salt",
    "peas": "pea green frozen boiled drained",
    "35hr sourdough loaf wholemeal": "Bread, from rye flour, sour dough",
    "vitasoy unsweetened oat long life milk uht": "Oat beverage, fluid, added calcium",
    "tasty cheese block": "Cheese, cheddar, processed, regular fat",
    "greek style yoghurt": "Yoghurt, flavoured, high fat (approx 5%)",
    "12 extra large free range eggs": "Egg, chicken, whole, raw",
    "salted butter": "Butter, plain, salted",
    "rspca approved chicken breast fillet min.": "chicken breast lean flesh raw",
    "pork mince": "pork mince untrimmed raw",
    "deli leg ham shaved": "Ham, leg, lean",
    "salmon tasmanian atlantic fillets skinned & boned": "salmon atlantic fillet raw",
    "medjool dates punnet": "date dried",
    "garlic head": "garlic peeled fresh raw", 
    "kanzi apple": "apple red skin unpeeled raw",
    "pomegranate": "pomegranate peeled raw",
    "orange navel": "orange navel peeled raw",
    "grapefruit red flesh": "grapefruit peeled raw",
    "green zucchini": "Zucchini, green skin, fresh, unpeeled, raw",
    "truss tomatoes": "Tomato, roma, raw", 
    "iceberg lettuce": "lettuce iceberg raw",
    "spinach english salad bunch": "spinach mature english fresh raw",
    "passionfruit fresh": "passionfruit raw",
    "onion white": "Onion, mature, white skinned, peeled, fresh, raw",
    "onion red": "Onion, mature, red skinned, raw",
    "onion brown": "Onion, mature, brown skinned, peeled, raw",
    "kiwi fruit green": "kiwifruit green (hayward) peeled raw",
    "white seedless grapes": "Grape, green, raw",
    "eggplant fresh": "eggplant unpeeled fresh raw",
    "pineapple naturally sweet whole": "pineapple peeled raw",
    "lebanese cucumbers": "cucumber lebanese unpeeled raw",
    "carrot fresh": "carrot mature peeled fresh raw",
    "red capsicum": "capsicum red fresh raw",
    "capsicum green": "capsicum green fresh raw",
    "green cabbage": "cabbage white raw",
    "fresh broccoli": "broccoli fresh raw",
    "cavendish bananas": "banana cavendish peeled raw",
    "fresh granny smith apples": "apple granny-smith unpeeled raw",
    "cabbage red": "cabbage red raw",
    "hass avocado": "avocado raw",
    "mushrooms cups loose": "mushroom common fresh raw",
    "laoganma crispy chilli oil": "oil canola", # close enough lol
    "campbell's real stock chicken liquid stock": "Soup, chicken & noodle, cup of soup, prepared from instant dry mix with water",
    "just caught garlic prawns": "Prawn, Western king, wild, flesh, raw",
    "just caught cooked & shelled mussel meat": "Mussel, blue, steamed",
    "kellogg's just right apricot & sultana breakfast cereal": "breakfast cereal puffed or popped rice cocoa coating added vitamins b1 b2 b3 c & folate ca fe & zn",
    "iodised table salt drum": "salt table iodised"
}.items()}

for name in cart:
    price, amount = cart[name]
    nutrients = nutrient_information[name_map[name]]
    for key in nutrients:
        nutrients[key] = amount / 100 * nutrients[key]
    cart[name].append(nutrients)

daily_requirements = {
    "protein": 100,
    "total dietary fibre": 25,
    "vitamin a": 700e-6,
    "thiamin (b1)": 1.1e-3,
    "riboflavin (b2)": 1.1e-3,
    "niacin": 14e-3,
    "pyridoxine (b6)": 1.3e-3,
    "cobalamin (b12)": 2.4e-6,
    "dietary folate equivalents": 400e-6,
    "vitamin c": 45e-3,
    "calcium (ca)": 1,
    "iodine (i)": 150e-6,
    "iron (fe)": 18e-3,
    "magnesium (mg)": 310e-3,
    "potassium (k)": 2.8,
    "sodium (na)": 2, # WHO maximum, not minimum
    "zinc (zn)": 8e-3,
}
special_cases = {
    "vitamin a": [
        'retinol (preformed vitamin a)',
        'alpha-carotene',
        'beta-carotene'
    ],
    "niacin": [
        'niacin (b3)',
        'niacin derived from tryptophan',
        'niacin derived equivalents'
    ]
}
for n in daily_requirements:
    foods = []
    for name, (price, amount, nutrients) in cart.items():
        total = sum([
            nutrients.get(sub_n, 0) for sub_n in special_cases.get(n, [n])
        ])
        if total > 0:
            foods.append((total, name))
    total = sum([food[0] for food in foods])
    print(
        f"{n}: {total:.2f} / {daily_requirements[n]:.1e} = "
        f"{total / daily_requirements[n]:.2f} days".rjust(100)
    )
    print("highest contributing in cart:\n")
    foods.sort(key=lambda thing: thing[0], reverse=True)
    [print(f"{amount:.10g} {name}") for amount, name in foods[:5]]
    print('_'*50)
    print("highest in database (per 100g):\n")
    foods = []
    for name, nutrients in nutrient_information.items():
        total = sum([
            nutrients.get(sub_n, 0) for sub_n in special_cases.get(n, [n])
        ])
        if total > 0:
            foods.append((total, name))
    foods.sort(key=lambda thing: thing[0], reverse=True)
    [print(f"{amount:.10g} {name}") for amount, name in foods[:5]]
    print('_'*100)
