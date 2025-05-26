import re
import csv

with open("cart.txt", 'r') as file:
    text = file.read().lower()
with open("weights.csv", 'r') as file:
    weights = {name: weight for name, weight in csv.reader(file.readlines())}

items = [item.split('\n')[:-1] for item in text.split('in cart')][:-1]
frequencies = {number: [] for number in range(10)}

for item in items:
    cleaned_item = []
    for line in item:
        line = line.strip()
        if line in ["", "kg", "in-store only", 'afternoon delivery & pick up']: continue
        if any(line.startswith(phrase) for phrase in ["was $", "save $"]): continue
        if any([all([word in line for word in l]) for l in [["low", "price"]]]): continue
        cleaned_item.append(line)

    frequencies[len(cleaned_item)].append(cleaned_item)

for item in frequencies[3]:
    name = item[0]
    price = item[1]
    if not price.startswith('$'):
        print(1, item)
    if not (item[2].startswith('$') or '/' in item[2] or (item[2].endswith('g') or item[2].endswith('l') or item[2].endswith('ea'))):
        print(2, item)
    amount = False
    if name.endswith(" each"):
        name = name[:-len(" each")]
    if name.endswith("pack"):
        amount = float(name.split()[-2])
    elif name.endswith('l') or name.endswith('g'):
        # practically I don't need this for most items since item[2] is enough but since I wrote it I might as well use it cause I need something like it for packs and stuff anyways I guess
        try:
            if name[-2] == 'm':
                amount = float(name.split()[-1][:-2] + 'e-3')
            elif name[-2] == 'k':
                amount = float(name.split()[-1][:-2] + 'e+3')
            else:
                amount = float(name.split()[-1][:-1])
        except ValueError:
            pass
    unit_price, unit_amount = item[2].split(' / ')
    if not amount and unit_amount == "1ea":
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

        if len(options) != 1:
            print(name)
            print(options)
            print()
        else:
            amount = float(list(options.values())[0])
        if name.endswith("quarter"):
            amount /= 4
    if unit_amount.endswith('kg'):
        unit_amount = float(unit_amount[:-2] + "e+3")
    elif unit_amount.endswith('ml'):
        unit_amount = float(unit_amount[:-2] + "e-3")
    elif unit_amount.endswith('g') or unit_amount.endswith('l'):
        unit_amount = float(unit_amount[:-1])
    elif unit_amount == "1ea":
        pass
    else:
        print(item)
        raise Exception()
    
    if not amount:
        amount = unit_amount
    else:
        if unit_amount == "1ea":
            pass
        elif amount != unit_amount:
            if abs(amount / float(price[1:]) - unit_amount / float(unit_price[1:])) > 10:
                print(item, amount, amount / float(price[1:]), unit_amount / float(unit_price[1:]))
    print('\t', item, amount, price)

for f in frequencies:
    if frequencies[f] and f != 3:
        print(f, len(frequencies[f]))
        [print(fr) for fr in frequencies[f]]
        print()