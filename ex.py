import json
response ='''
{
"name": "Rahul",
"age":21
}'''

data = json.loads(response)
print(data["name"])
print(data["age"])