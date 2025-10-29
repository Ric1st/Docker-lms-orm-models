from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_POST
from django.views.generic import ListView, DetailView
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q 
from django.core.files.storage import FileSystemStorage 
from django.contrib.auth import get_user_model
from django.contrib.auth import login

# Import model-model yang diperlukan
from .models import Course, CourseMember, CourseContent, Comment, Completion
from .forms import UserEditForm, UserAddForm, RegisterForm, CourseForm

User = get_user_model()


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'registration/register.html', {'form': form})


# --- UTILITY FUNCTIONS ---

def is_staff_or_superuser(user):
    """Fungsi pengecekan staff/admin"""
    return user.is_staff or user.is_superuser

def index(request):
    return render(request, 'index.html')

@login_required(login_url='login')
def home(request):
    context = {
        'username': request.user.username,
    }
    return render(request, 'home.html', context)

# --- GENERAL VIEWS ---
@login_required
def home(request):
    username = request.user.username
    course_count = request.user.coursemember_set.count() 
    total_users = User.objects.count() if request.user.is_staff or request.user.is_superuser else None

    context = {
        'username': username,
        'course_count': course_count,
        'total_users': total_users,
    }
    return render(request, 'home.html', context)

def core(request):
    return render(request, 'base.html')

# --- VIEWS USER MANAGEMENT (CRUD & SEARCH) ---

@user_passes_test(is_staff_or_superuser)
@login_required
def users(request):
    query = request.GET.get('q')
    if query:
        myusers = User.objects.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query)
        ).distinct().order_by('date_joined')
        message = f"Menampilkan hasil pencarian untuk: '{query}'"
    else:
        myusers = User.objects.all().order_by('date_joined')
        message = ""

    context = {
        'myusers': myusers,
        'query': query,
        'search_message': message,
        'total_users': User.objects.all().count()
    }
    return render(request, 'user/all_users.html', context)

@user_passes_test(is_staff_or_superuser)
@login_required
def user_create(request):
    """Membuat pengguna baru (CREATE)."""
    if request.method == 'POST':
        form = UserAddForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f"Pengguna '{user.username}' berhasil dibuat!")
            return redirect('users')
    else:
        form = UserAddForm()

    context = {
        'form': form,
    }
    return render(request, 'user/user_add_form.html', context)

@user_passes_test(is_staff_or_superuser)
@login_required
def user_update(request, pk):
    user_to_edit = get_object_or_404(User, pk=pk)
    
    if not request.user.is_superuser and user_to_edit.is_superuser:
        messages.error(request, "Anda tidak memiliki izin untuk mengedit akun superuser.")
        return redirect('users')

    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=user_to_edit)
        if form.is_valid():
            user = form.save(commit=False)
            is_staff_value = form.cleaned_data.get('is_staff', False)
            user.is_staff = is_staff_value
            user.save()
            messages.success(request, f"Pengguna '{user.username}' berhasil diperbarui!")
            return redirect('users')
    else:
        form = UserEditForm(instance=user_to_edit, initial={'is_staff': user_to_edit.is_staff})

    context = {
        'form': form,
        'target_user': user_to_edit,
    }
    return render(request, 'user/user_form.html', context)


@user_passes_test(is_staff_or_superuser)
@login_required
@require_POST # Hanya izinkan POST, sesuai penggunaan modal delete
def user_delete(request, pk):
    """Menghapus pengguna tertentu (DELETE)."""
    user_to_delete = get_object_or_404(User, pk=pk) 
    
    if user_to_delete == request.user:
        messages.error(request, "Anda tidak dapat menghapus akun Anda sendiri.")
        return redirect('users')

    if not request.user.is_superuser and user_to_delete.is_superuser:
        messages.error(request, "Anda tidak memiliki izin untuk menghapus akun superuser.")
        return redirect('users')
        
    username = user_to_delete.username
    user_to_delete.delete()
    messages.success(request, f"Pengguna '{username}' berhasil dihapus.")
    return redirect('users')

# --- VIEWS COURSE & CONTENT MANAGEMENT (DIKOREKSI) ---

class CourseListView(ListView):
    model = Course
    template_name = 'course/course_list.html'
    context_object_name = 'courses'
    ordering = ['-created_at']

    def get_queryset(self):
        query = self.request.GET.get('q')
        queryset = super().get_queryset()
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) | Q(description__icontains=query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        context['search_message'] = None
        if context['query']:
            context['search_message'] = f"Hasil pencarian untuk '{context['query']}'"
        return context

@login_required
@user_passes_test(is_staff_or_superuser)
def course_create(request):
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Kursus berhasil ditambahkan!")
            return redirect('course_list')
    else:
        form = CourseForm()
    return render(request, 'course/course_form.html', {
        'form': form,
        'title': 'Tambah Kursus Baru',
        'submit_text': 'Simpan Kursus',
    })

@login_required
@user_passes_test(is_staff_or_superuser)
def course_edit(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, "Perubahan kursus berhasil disimpan.")
            return redirect('course_list')
    else:
        form = CourseForm(instance=course)
    return render(request, 'course/course_form.html', {
        'form': form,
        'title': f'Edit Kursus: {course.name}',
        'submit_text': 'Perbarui Kursus',
    })

@login_required
@user_passes_test(is_staff_or_superuser)
def course_delete(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        course.delete()
        messages.success(request, "Kursus berhasil dihapus.")
        return redirect('course_list')
    return render(request, 'course/course_confirm_delete.html', {'course': course})

class CourseDetailView(DetailView):
    model = Course
    template_name = 'course/course_detail.html'
    context_object_name = 'course'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.get_object()

        is_joined = CourseMember.objects.filter(
            course_id=course,
            user_id=self.request.user
        ).exists()

        context['is_joined'] = is_joined
        return context

@login_required
def exit_course(request, pk):
    course = get_object_or_404(Course, pk=pk)
    
    deleted_count, _ = CourseMember.objects.filter(
        course_id=course,
        user_id=request.user
    ).delete()

    if deleted_count > 0:
        messages.success(request, f"Kamu berhasil keluar dari kursus {course.name}")
    else:
        messages.info(request, f"Kamu belum terdaftar di kursus {course.name}")

    return redirect('course_list')

@login_required
def join_course(request, pk):
    course = get_object_or_404(Course, pk=pk)
    
    created = CourseMember.objects.get_or_create(
        course_id=course,
        user_id=request.user,
        defaults={'roles': 'std'}
    )
    if created:
        messages.success(request, f"Kamu berhasil bergabung di {course.name}")
    else:
        messages.info(request, f"Kamu sudah terdaftar di {course.name}")
    return redirect('course_list') 

@login_required
def my_courses(request):
    memberships = CourseMember.objects.filter(user_id=request.user)
    return render(request, 'course/my_courses.html', {'memberships': memberships})

@login_required(login_url='login')
def course_content_list(request, course_pk):
    course = get_object_or_404(Course, pk=course_pk)
    user = request.user

    is_member = CourseMember.objects.filter(course_id=course.pk, user_id=user.pk).exists()

    if  not is_member and not user.is_staff:
        messages.error(request, f"Anda harus terdaftar di kursus '{course.name}' untuk mengakses konten ini.")
        return redirect('course_detail', pk=course.pk) # Gunakan course.pk untuk redirect

    if not is_member and not user.is_staff:
        messages.error(request, f"Anda harus terdaftar di kursus '{course.name}' untuk mengakses konten ini.")
        return redirect('course_detail', pk=course.pk)
    
    student_memberships = CourseMember.objects.filter(
        course_id=course.pk, user_id__is_staff=False,user_id__is_superuser=False).select_related('user_id') 

    student_list = [member.user_id for member in student_memberships]
    
    student_count = len(student_list)
    contents = CourseContent.objects.filter(course_id=course.pk).order_by('pk') 

    context = {
        'course': course,
        'contents': contents,
        'is_member': is_member,
        'total': student_count,
        'student_list': student_list,   
    }
    
    return render(request, 'course/course_content_list.html', context)


@login_required(login_url='login')
def course_content_detail(request, course_pk, content_pk):
    course = get_object_or_404(Course, pk=course_pk)
    content = get_object_or_404(CourseContent, pk=content_pk, course_id=course) 
    
    is_member = CourseMember.objects.filter(course_id=course, user_id=request.user).exists()
    if not is_member and not request.user.is_staff:
          messages.error(request, "Anda harus bergabung dengan kursus ini untuk melihat konten.")
          return redirect('course_detail', pk=course_pk) # Gunakan course_pk untuk redirect
    
    comments = Comment.objects.filter(content_id=content).order_by('-created_at') 

    try:
        current_member = CourseMember.objects.get(course_id=course, user_id=request.user)
    except CourseMember.DoesNotExist:
        # Ini adalah fallback, tapi is_member di atas harusnya sudah mencegah ini
        current_member = None

    if current_member :
        completed = Completion.objects.filter(member_id = current_member, content_id = content).exists()
    else:
        completed= False

    context = {
        'course': course,
        'content': content,
        'comments': comments,
        'completed' : completed,
    }
    return render(request, 'course/course_content_detail.html', context) 

@login_required(login_url='login')
@require_POST
def post_comment(request, course_pk, content_pk):
    """Memproses pengiriman komentar baru. Hanya menerima method POST."""
    
    # KOREKSI: Menggunakan course_pk dan content_pk dari URL
    course = get_object_or_404(Course, pk=course_pk)
    content = get_object_or_404(CourseContent, pk=content_pk, course_id=course)
    user = request.user
    
    # KOREKSI: Mengambil data POST dengan key 'comment' atau 'comment_text'
    # Sesuaikan dengan nama field di form HTML Anda (saya asumsikan 'comment_text')
    comment_text = request.POST.get('comment_text') 
    
    if not comment_text:
        messages.error(request, "Komentar tidak boleh kosong.")
        return redirect('course_content_detail', course_pk=course_pk, content_pk=content_pk)

    try:
        # Ambil objek CourseMember yang bersangkutan
        member = CourseMember.objects.get(course_id=course, user_id=user)

        # Buat objek Komentar
        Comment.objects.create(
            member_id=member, # Gunakan objek member
            content_id=content, # Gunakan objek content
            comment=comment_text
        )
        messages.success(request, "Komentar berhasil ditambahkan.")
        
    except CourseMember.DoesNotExist:
        messages.error(request, "Anda harus terdaftar di kursus ini untuk berkomentar.")
    
    # Redirect kembali ke halaman detail konten yang sama
    return redirect('course_content_detail', course_pk=course_pk, content_pk=content_pk)

# ----------------------------------------------------------------------
# 3. FUNGSI EDIT KOMENTAR
# ----------------------------------------------------------------------
@login_required(login_url='/login/')
def comment_edit(request, comment_pk):
    comment = get_object_or_404(Comment, pk=comment_pk)

    if request.method == 'POST':
        # Asumsi data form POST memiliki field 'comment_text'
        new_comment_text = request.POST.get('comment_text')
        if new_comment_text:
            comment.comment = new_comment_text
            comment.save()
            # Arahkan kembali ke halaman konten setelah edit
            return redirect('course_content_detail', 
                            course_pk=comment.content_id.course_id.pk, 
                            content_pk=comment.content_id.pk)
        
    # Untuk GET request (menampilkan form edit)
    context = {
        'comment': comment,
        'course': comment.content_id.course_id,
        'content': comment.content_id,
    }
    # Render template edit_comment.html
    return render(request, 'comment/edit_comment.html', context)


# ----------------------------------------------------------------------
# 4. FUNGSI HAPUS KOMENTAR
# ----------------------------------------------------------------------
login_required(login_url='/login/')
@require_POST
def comment_delete(request, comment_pk):
    comment = get_object_or_404(Comment, pk=comment_pk)
    
    comment_user = comment.member_id.user_id # Atau comment.member_id.user

    # 2. Periksa apakah User yang login adalah pemilik komentar
    if comment_user == request.user:
        
        # Simpan PK konten dan kursus sebelum komentar dihapus
        course_pk = comment.content_id.course_id.pk
        content_pk = comment.content_id.pk
        
        comment.delete()
        messages.success(request, "Komentar berhasil dihapus.")
        
        return redirect('course_content_detail', course_pk=course_pk, content_pk=content_pk)
    
    # 3. Jika bukan pemilik komentar
    messages.error(request, "Anda tidak memiliki izin untuk menghapus komentar ini.")
    # Redirect kembali ke detail konten
    return redirect('course_content_detail', course_pk=comment.content_id.course_id.pk, content_pk=comment.content_id.pk)

@login_required
def user_dashboard(request):
    user = request.user

    if user.is_staff:
        course_memberships = CourseMember.objects.filter(user_id=user)
        context = {
            'is_teacher': True,
            'courses': course_memberships,
        }
        return render(request, 'completion/dashboard.html', context)

    else:
        view_type = request.GET.get('view', 'onprogress')  
        
        if view_type == 'complete':
            completions = Completion.objects.filter(member_id__user_id=request.user)
            context = {
                'is_teacher': False,
                'active_tab': 'complete',
                'completions': completions
            }
            return render(request, 'completion/dashboard.html', context)
        
        else: 
            course_memberships = CourseMember.objects.filter(user_id=user)
            
            course_data = [] 
            
            for member in course_memberships:
                course = member.course_id
                
                total_contents = course.contents.count() 
                
                completed_contents_count = Completion.objects.filter(
                    member_id=member,  
                    content_id__course_id=course 
                ).count()
                
                is_fully_completed = (total_contents > 0 and completed_contents_count == total_contents)
                
                course_data.append({
                    'member': member,
                    'course': course,
                    'is_fully_completed': is_fully_completed
                })
            
            context = {
                'is_teacher': False,
                'active_tab': 'onprogress',
                'courses': course_data 
            }
            return render(request, 'completion/dashboard.html', context)
    
@login_required
def mark_content_complete(request, content_id):
    content = get_object_or_404(CourseContent, id=content_id)
    member = get_object_or_404(CourseMember, user_id=request.user, course_id=content.course_id)

    completion, created = Completion.objects.get_or_create(
        member_id=member, 
        content_id=content
    )

    if created:
        messages.info(request, f"Konten {content.name} ditandai selesai.")
    else:
        messages.info(request, f"Konten {content.name} sudah selesai sebelumnya.")
       
    return redirect('course_content_list', course_pk=content.course_id.id)
