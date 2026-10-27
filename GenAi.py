from pydantic import BaseModel, Field
class Student(BaseModel):
    name : str
    age: int = Field(gt = 0, le = 100)

student = Student(
    name= "Rahul",
    age= 21
)
print(student.name)
print(student.age)
