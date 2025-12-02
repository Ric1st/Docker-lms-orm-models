# apuv1.py
from ninja import NinjaAPI, Schema
from pydantic import field_validator
import re
from .models import User, CourseMember, CourseContent,Comment,Course
from typing import List
from typing import Optional
# from .api import apiAuth

apiv1 = NinjaAPI()

@apiv1.get('/hello')
def helloApi(request):
    return "Menyala abangkuh ..."

@apiv1.get('calc/{nil1}/{opr}/{nil2}')
def calculator(request, nil1:int, opr:str, nil2:int):
    hasil = nil1 + nil2
    if opr == '-':
        hasil = nil1 - nil2
    elif opr == 'x':
        hasil = nil1 * nil2
   
    return {'nilai1': nil1, 'nilai2': nil2, 'operator': opr, 'hasil': hasil}

@apiv1.post('hello/')
def helloPost(request):
    if 'nama' in request.POST:
        return f"Selamat menikmati ya {request.POST['nama']}"
    return "Selamat tinggal dan pergi lagi"

@apiv1.put('users/{id}')
def userUpdate(request, id:int):
    return f"User dengan id {id} Nama aslinya adalah Herdiono kemudian diganti menjadi {request.body}"

@apiv1.delete('users/{id}')
def userDelete(request, id:int):
    return f"Hapus user dengan id: {id}"

class Kalkulator(Schema):
    nil1: int
    nil2: int
    opr: str
    hasil: int = 0

    def calcHasil(self):
        hasil = self.nil1 + self.nil2
        if self.opr == '-':
            hasil = self.nil1 - self.nil2
        elif self.opr == 'x':
            hasil = self.nil1 * self.nil2
       
        return {'nilai1': self.nil1, 'nilai2': self.nil2,
                'operator': self.opr, 'hasil': self.hasil}

@apiv1.post('calc')
def postCalc(request, skim : Kalkulator):
    skim.hasil = skim.calcHasil()
    return skim

class Register(Schema):
    username: str
    password: str
    email: str
    first_name: str
    last_name: str

class UserOut(Schema):
    id: int
    username: str
    first_name: str
    last_name: str
    email: str

@apiv1.post('register/', response=UserOut)
def register(request, data:Register):
    newUser = User.objects.create_user(username=data.username,
                                password=data.password,
                                email=data.email,
                                first_name=data.first_name,
                                last_name=data.last_name)
    return newUser

    @field_validator("username")
    def validate_username(cls, value):
        if len(value) < 5:
            raise ValueError("Username harus lebih dari 3 karakter")
        return value

    @field_validator('password')
    def validate_password(cls, value):
        if len(value) < 8:
            raise ValueError("Password harus lebih dari 8 karakter")
       
        pattern = r'^(?=.*[A-Za-z])(?=.*\d).+$'
        if not re.match(pattern, value):
            raise ValueError("Password harus mengandung huruf dan angka")

class UserSchema(Schema):
    id: int
    username: str
    first_name: str
    last_name: str
    email: str

@apiv1.get("/users", response=List[UserSchema])
def list_users(request):
    users = User.objects.all()
    return users

class CourseSchema(Schema):
    id: int
    name: str
    description: str
    price: int
    teacher: int

@apiv1.get("/courses", response=List[CourseSchema])
def list_courses(request):
    courses = Course.objects.all()
    return [
        {
            "id": c.id,
            "name": c.name,  
            "description": c.description,
            "price": c.price,
            "teacher": c.teacher.id if c.teacher else None
        }
        for c in courses
    ]

class CourseMemberSchema(Schema):
    id: int
    user_id: int
    course_id: int
    roles: str
   
@apiv1.get("/members", response=List[CourseMemberSchema])
def list_members(request):
    members = CourseMember.objects.all()
    return [
        {
            "id": m.id,
            "user_id": m.user_id.id,  
            "course_id": m.course_id.id,  
            "roles": m.roles,
        }
        for m in members
    ]

# kurang auth=apiAuth
@apiv1.get('mycourses/', response=List[CourseMemberSchema])
def getMyCourses(request):
    user_id = User.objects.get(pk=request.user.id)
    mycourses = CourseMember.objects.filter(user_id=user_id)\
    .select_related('course_id', 'user_id')
   
    return [
        {
            "id": c.id, 
            "user_id": c.user_id.id, 
            "course_id": c.course_id.id, 
            "roles": c.roles
        } 
        for c in mycourses
    ]

# kurang auth=apiAuth
@apiv1.post('course/{id}/enroll/', response=CourseMemberSchema)
def courseEnrollment(request, id:int):
    user_id = User.objects.get(pk=request.user.id)

    try:
        course = Course.objects.get(pk=id)
    except Course.DoesNotExist:
        return {"status": "Course tidak ditemukan"}, 404
      
    if CourseMember.objects.filter(user_id=user_id, course_id=course).exists():
         return {"status": "Anda sudah terdaftar di kursus ini."}, 400

    enrollment = CourseMember.objects.create(user_id=user_id, course_id=course, roles='std') 
  
    return {
        "id": enrollment.id,
        "user_id": enrollment.user_id.id,
        "course_id": enrollment.course_id.id,
        "roles": enrollment.roles
    }

class CourseContentSchema(Schema):
    id: int
    course_id: int
    name: str
    description: str
    video_url: str
    file_attachment: Optional[str] = None
   
@apiv1.get("/contents", response=List[CourseContentSchema])
def list_contents(request):
    contents = CourseContent.objects.all()
    return [
        {
            "id": c.id,
            "course_id": c.course_id.id,  
            "name": c.name,
            "description": c.description,
            "video_url": c.video_url,
            "file_attachment": c.file_attachment 
        }
        for c in contents
    ]

class CommentSchema(Schema):
    id: int
    content_id: int
    member_id: int
    comment: str
   
@apiv1.get("/comments", response=List[CommentSchema])
def list_comments(request):
    comments = Comment.objects.all()
    return [
        {
            "id": c.id,
            "content_id": c.content_id.id,  
            "member_id": c.member_id.id,
            "comment": c.comment,
           
        }
        for c in comments
    ]

# kurang auth=apiAuth 
@apiv1.post('komen/')
def postComment(request, data:CommentSchema):
    user = User.objects.get(pk=request.user.id)
  
    content = CourseContent.objects.filter(id=data.content_id).first()
    if not content:
        return {"status": "Content tidak ditemukan"}, 404
      
    coursemember = CourseMember.objects.filter(
        user_id=user, 
        course_id=content.course_id
    ).first()
  
    if coursemember:
        Comment.objects.create(
            comment=data.comment, 
            member_id=coursemember,  
            content_id=content       
        )
        return {"status": "berhasil"}
    else:
        return {"status": "tidak boleh komentar di sini"}, 403
    
    # c_id = 4 | con_id = 4