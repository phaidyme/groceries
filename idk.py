import csv


def format_value(value, unit_suffix=""):
    """
    Convert string value to float, format removing trailing .0,
    then append the unit suffix string (like 'e-3' for mg).
    """
    # Clean up input
    value = value.replace(",", "").strip()
    val_float = float(value)
    if val_float.is_integer():
        formatted = str(int(val_float))
    else:
        formatted = str(val_float)
    return float(formatted + unit_suffix)


# Use string suffixes for multipliers (scientific notation)
unit_multipliers = {
    "mg": "e-3",
    "ug": "e-6",
    # Add other prefixes if needed
}

with open(
    "All solids & liquids per 100g-Table 1.csv",
    newline="",
    encoding="utf-8",
) as csvfile:
    reader = csv.reader(csvfile)
    headers = next(reader)

    valid_indices = []
    cleaned_headers = []
    unit_suffixes = []

    for i, header in enumerate(headers):
        header_lower = header.lower()
        if "%t" in header_lower or "mg/gn" in header_lower:
            continue
        if i < 3:
            continue  # Skip first three columns

        if "(" in header and ")" in header:
            base, unit = header.rsplit("(", 1)
            unit = unit.rstrip(")").strip().lower()
        else:
            base = header
            unit = ""

        cleaned_name = base.strip().lower()

        # Find unit suffix string for scientific notation
        unit_suffix = ""
        for prefix, suffix in unit_multipliers.items():
            if unit.startswith(prefix):
                unit_suffix = suffix
                break

        cleaned_headers.append((i, cleaned_name))
        unit_suffixes.append(unit_suffix)
        valid_indices.append(i)

    result = {}
    for row in reader:
        name_parts = row[2].lower().split(", ")
        name_parts = [part.strip() for part in name_parts]
        food_name = " ".join(name_parts)
        print(food_name)
        nutrients = {}
        for (i, cleaned_name), suffix in zip(cleaned_headers, unit_suffixes):
            raw_value = row[i].strip()
            if raw_value:
                nutrients[cleaned_name] = format_value(raw_value, suffix)
                print(cleaned_name, nutrients[cleaned_name])
        print()
        result[food_name] = nutrients


class Nutrients:
    def __init__(self, data={}):
        self.data = data

    def __getitem__(self, key):
        return self.data.get(key, "0")

    def __setitem__(self, key, value):
        self.data[key] = value

    def __add__(self, other):
        s = set(self.data.keys())
        o = set(other.data.keys())
        a = s.union(o)
        b = s.difference(o)
        c = o.difference(s)
        retval = Nutrients()
        for key in a:
            retval[key] = self[key] + other[key]
        for key in b:
            retval[key] = self[key]
        for key in c:
            retval[key] = other[key]
        return retval

    def __rmul__(self, other):
        return Nutrients({key: other * self[key] for key in self.data.keys()})

    def __repr__(self):
        return repr(self.data)


nutrients = Nutrients({"protein": 1, "fat": 0})
nutrients["fiber"] = 3.2
print(nutrients + nutrients)
print(2 * nutrients)
