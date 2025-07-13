import json
import re
import unicodedata

def slugify_vietnamese(text):
    text = text.strip().lower()

    # Replace Vietnamese abbreviations
    text = re.sub(r'\b(tp\.?|thành phố)\b', 'thanh pho', text)
    text = re.sub(r'\b(q\.?|quận)\b', 'quan', text)
    text = re.sub(r'\b(h\.?|huyện)\b', 'huyen', text)
    text = re.sub(r'\b(t\.?|tỉnh)\b', 'tinh', text)
    text = re.sub(r'\b(p\.?|phường)\b', 'phuong', text)
    text = re.sub(r'\b(x\.?|xã)\b', 'xa', text)

    # Remove accents
    text = ''.join(
        c for c in unicodedata.normalize('NFD', text)
        if unicodedata.category(c) != 'Mn'
    )

    # Replace non-alphanum with _
    text = re.sub(r'[^a-z0-9]+', '_', text)

    return text.strip('_')


def normalize_vietnam_province_file(input_path, output_path):
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    for city in data:
        city["normalized_name"] = slugify_vietnamese(city["name"])
        for district in city.get("districts", []):
            district["normalized_name"] = slugify_vietnamese(district["name"])
            for ward in district.get("wards", []):
                ward["normalized_name"] = slugify_vietnamese(ward["name"])

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        
        
input_path = "app/location/__data__/vietnam.json"
output_path = "app/location/__data__/vietnam_normalized.json"
normalize_vietnam_province_file(input_path, output_path)