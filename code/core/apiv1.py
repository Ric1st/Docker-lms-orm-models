# apiv1.py
from ninja import NinjaAPI, Schema, Query, Field, FilterSchema
from ninja.pagination import paginate, PageNumberPagination
from ninja.throttling import AnonRateThrottle, AuthRateThrottle
from pydantic import field_validator
from django.db.models import Count, Q
from datetime import datetime
from typing import List, Optional
import re
from ninja.responses import Response

from .models import User, CourseMember, CourseContent, Comment, Course
from .api import apiAuth

# Inisialisasi API dengan throttling global
apiv1 = NinjaAPI(
    urls_namespace='apiv1',
    throttle=[
        AnonRateThrottle('10/m'),  
        AuthRateThrottle('10/m'),
    ],
)

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
def postCalc(request, skim: Kalkulator):
    skim.hasil = skim.calcHasil()
    return skim

# ============= USER & REGISTER SCHEMAS ============= 
# PENTING: Definisikan UserOut SEBELUM digunakan!
class UserOut(Schema):
    id: int
    username: str
    first_name: str
    last_name: str
    email: str

class Register(Schema):
    username: str
    password: str
    email: str
    first_name: str
    last_name: str

    @field_validator("username")
    def validate_username(cls, value):
        if len(value) < 5:
            raise ValueError("Username harus lebih dari 5 karakter")
        return value

    @field_validator('password')
    def validate_password(cls, value):
        if len(value) < 8:
            raise ValueError("Password harus lebih dari 8 karakter")
       
        pattern = r'^(?=.*[A-Za-z])(?=.*\d).+$'
        if not re.match(pattern, value):
            raise ValueError("Password harus mengandung huruf dan angka")
        return value

@apiv1.post('register/', response=UserOut)
def register(request, data: Register):
    if User.objects.filter(username=data.username).exists():
        return Response({"status": "Username sudah digunakan."}, status=400)
    
    newUser = User.objects.create_user(
        username=data.username,
        password=data.password,
        email=data.email,
        first_name=data.first_name,
        last_name=data.last_name
    )
    return newUser

# ============= USER ENDPOINTS =============
class UserSchema(Schema):
    id: int
    username: str
    first_name: str
    last_name: str
    email: str

# GET users 
@apiv1.get("/users", response=List[UserSchema])
@paginate(PageNumberPagination, page_size=10)
def list_users(request, search: Optional[str] = Query(None)):
    users = User.objects.all()
    
    if search:
        users = users.filter(
            Q(username__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(email__icontains=search)
        ).distinct()
    
    return users.order_by('date_joined')

# ... (sisanya sama seperti sebelumnya)

# ============= COURSE FILTER & SCHEMAS =============
class CourseFilter(FilterSchema):
    price_gte: Optional[int] = 0
    price_lte: Optional[int] = 0
    created_gte: Optional[datetime] = None
    created_lte: Optional[datetime] = None
    search: Optional[str] = Field(None, q=['name__icontains', 'description__icontains'])

    def filter_price_gte(self, value: int):
        return Q(price__gte=value) if value else Q()

    def filter_price_lte(self, value: int):
        return Q(price__lte=value) if value else Q()

    def filter_created_gte(self, value: datetime):
        return Q(created_at__gte=value) if value else Q()

    def filter_created_lte(self, value: datetime):
        return Q(created_at__lte=value) if value else Q()

class CourseSchema(Schema):
    id: int
    name: str
    description: str
    price: int
    teacher: int

class DetailCourseOut(Schema):
    id: int
    name: str
    description: str
    price: int
    teacher: int
    num_members: int
    num_contents: int

# GET courses without auth for public access (untuk HTML dashboard)
@apiv1.get('courses-public/', response=List[CourseSchema])
def listPublicCourses(request):
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

# GET courses with auth, filter, and pagination
@apiv1.get('courses/', response=List[DetailCourseOut], auth=apiAuth)
@paginate(PageNumberPagination, page_size=5)
def listAllCourse(request, filters: CourseFilter = Query(...)):
    courses = Course.objects.all()
    courses = filters.filter(courses)
    
    # Annotate each course with the number of members and contents
    courses = courses.annotate(
        num_members=Count('coursemember'),
        num_contents=Count('coursecontent')
    )
    
    return courses

# ============= COURSE MEMBER ENDPOINTS =============
class CourseMemberSchema(Schema):
    id: int
    user_id: int
    course_id: int
    roles: str

class CourseMemberOut(Schema):
    id: int
    user_id: int
    course_id: int
    course_name: str
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

@apiv1.get('mycourses/', auth=apiAuth, response=List[CourseMemberOut])
def getMyCourses(request):
    user = User.objects.first()
    mycourses = CourseMember.objects.filter(user_id=user)\
        .select_related('course_id', 'user_id')
   
    return [
        {
            "id": c.id,
            "user_id": c.user_id.id,
            "course_id": c.course_id.id,
            "course_name": c.course_id.name,
            "roles": c.roles
        }
        for c in mycourses
    ]

@apiv1.post('course/{id}/enroll/', auth=apiAuth, response=CourseMemberSchema)
def courseEnrollment(request, id: int):
    user = User.objects.first()

    try:
        course = Course.objects.get(pk=id)
    except Course.DoesNotExist:
        return {"status": "Course tidak ditemukan"}, 404
      
    if CourseMember.objects.filter(user_id=user, course_id=course).exists():
        return {"status": "Anda sudah terdaftar di kursus ini."}, 400

    enrollment = CourseMember.objects.create(
        user_id=user, 
        course_id=course, 
        roles='std'
    )
  
    return {
        "id": enrollment.id,
        "user_id": enrollment.user_id.id,
        "course_id": enrollment.course_id.id,
        "roles": enrollment.roles
    }

# ============= COURSE CONTENT ENDPOINTS =============
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

# ============= COMMENT ENDPOINTS =============
class CommentSchema(Schema):
    id: int
    content_id: int
    member_id: int
    comment: str

class CommentIn(Schema):
    content_id: int
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

@apiv1.post('comments/', auth=apiAuth)
def postComment(request, data: CommentIn):
    user = User.objects.first()
  
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