import csv, yaml


class Nutrients:
    def __init__(self, data={}):
        self.data = data

    def __getitem__(self, key):
        return self.data.get(key, 0)

    def __rmul__(self, other):
        return Nutrients(
            {nutrient: other * amount for nutrient, amount in self.data.items()}
        )

    def __add__(self, other):
        return Nutrients(
            {
                self.get(nutrient, 0) + other.get(nutrient, 0)
                for nutrient in set(self.data.keys()).union(
                    set(other.data.keys())
                )
            }
        )

    def __repr__(self):
        return str(self.data)


def read_nutrient_info():
    with open("All solids & liquids per 100g-Table 1.csv") as file:
        reader = csv.reader(file)
        rows = [row for row in reader]

    relevant_columns = []
    for i, header in enumerate(rows.pop(0)):
        header = header.lower()
        if i < 3 or header == "" or "%t" in header or "mg/gn" in header:
            continue
        j = header.rfind("(")
        nutrient = header[: j - 2]
        unit = header[j + 1 : -1]
        relevant_columns.append(
            (
                i,
                nutrient,
                {"g": "", "mg": "e-3", "ug": "e-6", "kj": ""}[unit],
            )
        )
    nutrient_info = {}
    for row in rows:
        food = row[2].lower().replace(", ", " ")
        nutrients = {}
        for i, nutrient, suffix in relevant_columns:
            amount = row[i].replace(",", "")
            if amount not in ["", "0", "0.0"]:
                nutrients[nutrient] = float(amount + suffix)
        nutrient_info[food] = Nutrients(nutrients)
    return nutrient_info


nutrient_info = read_nutrient_info()

daily_requirements = {
    "energy, without dietary fibre, equated": 6500,
    "protein": 100,
    "total dietary fibre": 25,
    "vitamin a": 700e-6,
    "thiamin (b1)": 1.1e-3,
    "riboflavin (b2)": 1.1e-3,
    "niacin": 14e-3,
    "pyridoxine (b6)": 1.3e-3,
    "cobalamin (b12)": 2.4e-6,
    "dietary folate equivalents": 400e-6,  # it's okay if you go higher as long as sources are natural
    "vitamin c": 45e-3,
    "calcium (ca)": 1,
    "copper (cu)": 900e-6,
    "iodine (i)": 150e-6,
    "iron (fe)": 18e-3,
    "magnesium (mg)": 310e-3,
    "potassium (k)": 2.8,
    "sodium (na)": 2,  # WHO maximum, not minimum
    "zinc (zn)": 8e-3,
}
special_cases = {
    "vitamin a": [
        "retinol (preformed vitamin a)",
        "beta-carotene",
        # "alpha-carotene",
    ],
    "niacin": [
        "niacin (b3)",
        "niacin derived from tryptophan",
        "niacin derived equivalents",
    ],
}
cart = {}
for name, nutrients in nutrient_info.items():
    cart[name] = {"amount": 0, "price": 0, "count": 0}
with open("cart.yaml", "r") as file:
    cart = yaml.safe_load(file)

requirements_met = {}
for n in daily_requirements:
    foods = []
    for name in cart:
        amount = cart[name]["amount"]
        count = cart[name]["count"]
        price = cart[name]["price"]
        nutrients = (count * amount / 100) * nutrient_info[name]
        total = sum([nutrients[sub_n] for sub_n in special_cases.get(n, [n])])
        if total > 0:
            foods.append((total, name))
    total = sum([food[0] for food in foods])
    requirements_met[n] = total
    days = total / daily_requirements[n]
    print(
        f"{n}: {total:.2f} / {daily_requirements[n]:.1e} = "
        f"{days:.2f} days".rjust(100)
    )
    if False:
        print("highest contributing in cart:\n")
        foods.sort(key=lambda thing: thing[0], reverse=True)
        [print(f"{amount:.10g} {name}") for amount, name in foods[:5]]


scores = {food: 0 for food in nutrient_info}
for n in daily_requirements:
    days = requirements_met[n] / daily_requirements[n]
    if days > 30:
        continue
    weight = 30 - days
    print(n, weight)
    for name, nutrients in nutrient_info.items():
        weight_2 = weight
        if "dried" in name or "dry" in name:
            weight_2 /= 2
        if "ground" in name:
            weight_2 /= 2
        if "powder" in name:
            weight_2 /= 2
        scores[name] += weight_2 * nutrients[n]

for key, value in sorted(scores.items(), key=lambda item: item[1]):
    if value > 0:
        print(key)
for key, value in sorted(
    cart.items(), key=lambda thing: thing[1]["price"] * thing[1]["count"]
):
    print(value["price"] * value["count"], key)
    print(value)
    print()
print(sum([cart[item]["price"] * cart[item]["count"] for item in cart]) / 30)
