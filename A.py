import json
from pydantic import BaseModel,Field
class Student(BaseModel) :
    name : str
    age : int = Field(gt=0,le=100)
llm_response = """ {
    "name" : "Rahul" ,
    "age" : 21
}
"""
data = json.loads(llm_response)
student = Student.model_validate(data)
print(student.name)
print(student.age)


def multiply(a: int, b: int) -> int:
    return a * b


result = multiply(25, 8)


print(result)