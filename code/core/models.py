# code/core/models.py
from django.db import models
from django.contrib.auth.models import User 
from django.db.models.signals import post_save

# TABLE COURSE ()
class Course(models.Model):
    teacher = models.ForeignKey(User, on_delete=models.RESTRICT, verbose_name="pengajar") 
    
    name = models.CharField("nama matkul", max_length=100)
    description = models.TextField("deskripsi", default='-')
    price = models.IntegerField("harga", default=10000)
    image = models.ImageField("gambar", upload_to='course_images/', null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Mata Kuliah"
        verbose_name_plural = "Mata Kuliah"

    def student_count(self):
        return CourseMember.objects.filter(course_id=self, roles='std').count()
    def content_count(self):
        return self.contents.count()
    def comment_count(self):
        return Comment.objects.filter(content_id__course_id=self).count()

    def __str__(self) -> str:
        return f"{self.name} : Rp{self.price:,}"

ROLE_OPTIONS = [('std',"Siswa"), ('ast',"Asisten")]

# TABLE COURSE MEMBER
class CourseMember(models.Model):
    course_id = models.ForeignKey(Course, on_delete=models.RESTRICT, verbose_name="matkul")
    user_id = models.ForeignKey(User, on_delete=models.RESTRICT, verbose_name="siswa")
    roles = models.CharField("peran", max_length=3, choices=ROLE_OPTIONS, default='std')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Subscriber Kuliah"
        verbose_name_plural = "Subscriber Kuliah"

    def __str__(self) -> str:
        return f"{self.user_id.username} → {self.course_id.name} ({self.roles})"


# TABLE COURSE CONTENT
class CourseContent(models.Model):    
    name = models.CharField("Judul", max_length=200)
    description = models.TextField("deskripsi", default='-')
    video_url = models.CharField("URL Video", max_length=200, null=True, blank=True)
    file_attachment = models.FileField("File", null=True, blank=True)
    
    course_id = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name='contents', related_name='contents')
    parent_id = models.ForeignKey('self', on_delete=models.RESTRICT, null=True, blank=True, verbose_name="induk")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Konten Matkul"
        verbose_name_plural = "Konten Matkul"

    def __str__(self) -> str:
        return f"{self.name} ({self.course_id.name})"

# TABLE COMMENT
class Comment(models.Model):
    content_id = models.ForeignKey(CourseContent, on_delete=models.CASCADE, verbose_name="konten", null=True, blank=True, related_name='comments')
    member_id = models.ForeignKey(CourseMember, on_delete=models.CASCADE, verbose_name="pengguna", null=True, blank=True)
    
    comment = models.TextField('komentar')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Komentar"
        verbose_name_plural = "Komentar"

    def __str__(self):
       return f"Komen oleh {self.member_id.user_id.username} pada konten: {self.content_id.name}"

# TABLE COMPLETION 
class Completion(models.Model):
    member_id = models.ForeignKey(CourseMember, on_delete=models.CASCADE, verbose_name="alumni")
    content_id = models.ForeignKey(CourseContent, on_delete=models.CASCADE, verbose_name='Lulusan')
    
    last_update = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('member_id', 'content_id') 

    def __str__(self):
        return f"{self.member_id.user_id.username} completed {self.content_id.course_id.name}"