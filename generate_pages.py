import pandas as pd
import os
import re
import shutil
import requests
from bs4 import BeautifulSoup
# Fresh output folder every run
if os.path.exists("output2"):
    shutil.rmtree("output2")

os.makedirs("output2")

# Read Excel
df = pd.read_excel("properties2.xlsx")

# Read template
with open("template.html", "r", encoding="utf-8") as f:
    template = f.read()


def slugify(text):
    text = str(text).lower().strip()

    text = re.sub(r'[^a-z0-9\s-]', '', text)
    text = re.sub(r'\s+', '-', text)
    text = re.sub(r'-+', '-', text)

    return text.strip("-")


used_filenames = set()
def get_field(html, field_name):

    import re

    pattern = rf"{field_name}</td>\s*<td.*?>(.*?)</td>"

    match = re.search(
        pattern,
        html,
        re.IGNORECASE | re.DOTALL
    )

    if not match:
        return ""

    value = match.group(1)

    value = re.sub("<.*?>", "", value)

    return value.strip()


def scrape_property(url):

    response = requests.get(
        url,
        headers={
            "User-Agent":
            "Mozilla/5.0"
        }
    )

    html = response.text

    rent = get_field(
        html,
        "Rent Amount"
    )

    floors = get_field(
        html,
        "No. of Floors"
    )

    parking = get_field(
        html,
        "Car Park"
    )

    furnished = get_field(
        html,
        "Furnished"
    )

    power = get_field(
        html,
        "Power Supply"
    )

    lift = get_field(
        html,
        "Lift"
    )

    servant = get_field(
        html,
        "Servant Quarters"
    )

    water = get_field(
        html,
        "Water Facility"
    )

    return {
        "rent": rent,
        "floors": floors,
        "parking": parking,
        "furnished": furnished,
        "power": power,
        "lift": lift,
        "servant": servant,
        "water": water
    }
for _, row in df.iterrows():

    property_type = str(row["Property Type"]).strip()
    locality = str(row["Locality"]).strip()
    builtup_area = str(row["Built Up Area"]).strip()
    bedrooms = str(row["Bedrooms"]).strip()
    bathrooms = str(row["Bathrooms"]).strip()
    raw_address = str(
    row["Address"]
).strip()

    address = raw_address.split("|")[0]

    address = address.strip()    
    url = str(row["URL"]).strip()

    extra = scrape_property(url)
    seo_title = (
        f"{bedrooms} BHK {property_type} "
        f"for Rent in {address} | RentIt"
    )

    meta_description = (
    f"{bedrooms} BHK {property_type} for rent in "
    f"{address}. Monthly rent "
    f"{extra['rent']}. Built-up area "
    f"{builtup_area} with "
    f"{bathrooms} bathrooms."
)

    html = template

    html = html.replace("{{PROPERTY_TYPE}}", property_type)
    html = html.replace("{{LOCALITY}}", locality)
    html = html.replace("{{BUILTUP_AREA}}", builtup_area)
    html = html.replace("{{BEDROOMS}}", bedrooms)
    html = html.replace("{{BATHROOMS}}", bathrooms)
    html = html.replace("{{ADDRESS}}", address)
    html = html.replace("{{SEO_TITLE}}", seo_title)
    html = html.replace("{{META_DESCRIPTION}}", meta_description)
    html = html.replace(
    "{{RENT}}",
    extra["rent"]
)

    html = html.replace(
    "{{FLOORS}}",
    extra["floors"]
)

    html = html.replace(
    "{{PARKING}}",
    extra["parking"]
)

    html = html.replace(
    "{{FURNISHED}}",
    extra["furnished"]
)

    html = html.replace(
    "{{POWER}}",
    extra["power"]
)

    html = html.replace(
    "{{LIFT}}",
    extra["lift"]
)

    html = html.replace(
    "{{SERVANT}}",
    extra["servant"]
)

    html = html.replace(
    "{{WATER}}",
    extra["water"]
)

    # SEO filename
    filename = (
        f"{slugify(property_type)}-rent-"
        f"{slugify(address)}.html"
    )

    # Prevent duplicate names
    original_filename = filename
    counter = 1

    while filename in used_filenames:
        filename = original_filename.replace(
            ".html",
            f"-{counter}.html"
        )
        counter += 1

    used_filenames.add(filename)

    output_path = os.path.join(
        "output2",
        filename
    )

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as f:
        f.write(html)

    print(f"Generated: {filename}")

print("\nDone!")
print(f"Generated {len(df)} SEO pages.")