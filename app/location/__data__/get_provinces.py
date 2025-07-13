import json

def get_provinces(input_path, output_path):
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    provinces = []
    for city in data:
        provinces.append({
            "name": city["name"],
            "normalized_name": city["normalized_name"],
        })
        
    provinces = [dict(t) for t in {tuple(d.items()) for d in provinces}]
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(provinces, f, ensure_ascii=False, indent=2)

input_path = "app/location/__data__/vietnam_normalized.json"
output_path = "app/location/__data__/vietnam_provinces_normalized.json"
get_provinces(input_path, output_path)