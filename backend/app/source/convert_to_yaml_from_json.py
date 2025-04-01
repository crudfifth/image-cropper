import json
import yaml

# JSONファイルを読み込む
with open('schema.json', 'r') as json_file:
    data = json.load(json_file)

# JSONをYAMLに変換する
yaml_data = yaml.dump(data)

# YAMLデータをファイルに書き込む
with open('schema.yml', 'w') as yaml_file:
    yaml_file.write(yaml_data)