import json

def get_districts(input_path, output_path):
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    districts = []
    for city in data:
        for district in city["districts"]:
            print(district["name"], district["normalized_name"])
            districts.append({
                "name": district["name"],
                "normalized_name": district["normalized_name"],
            })
        
    districts = [dict(t) for t in {tuple(d.items()) for d in districts}]
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(districts, f, ensure_ascii=False, indent=2)

input_path = "app/location/__data__/vietnam_normalized.json"
output_path = "app/location/__data__/vietnam_districts_normalized.json"
get_districts(input_path, output_path)