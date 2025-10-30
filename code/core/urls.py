from django.urls import path
from . import views
from .views import CourseListView, CourseDetailView 

urlpatterns = [
    path('register/', views.register, name='register'),

    # URLS UTAMA
    path('', views.index, name='index'), 
    
    # URL untuk dashboard (setelah login), nama: 'home'
    path('home/', views.home, name='home'),
    
    # URLS UNTUK PENGELOLAAN USER (STAFF/ADMIN) - CRUD
    path('users/', views.users, name='users'),
    path('users/add/', views.user_create, name='user_create'), # CREATE
    path('users/<int:pk>/edit/', views.user_update, name='user_update'), # UPDATE
    path('users/<int:pk>/delete/', views.user_delete, name='user_delete'), # DELETE

    # URLS COURSE
    path('courses/list/', CourseListView.as_view(), name='course_list'),
    path('course/<int:pk>/', CourseDetailView.as_view(), name='course_detail'),
    path('course/<int:pk>/join/', views.join_course, name='join_course'),
    path('course/<int:pk>/exit/', views.exit_course, name='exit_course'),

    path('my-courses/', views.my_courses, name='my_courses'),
    path('course/<int:course_pk>/contents/', views.course_content_list, name='course_content_list'),
    path('course/<int:course_pk>/content/<int:content_pk>/', views.course_content_detail, name='course_content_detail'),
    path('course/<int:course_pk>/content/<int:content_pk>/comment/', views.post_comment, name='post_comment'),
    
    #Course CRUD
    path('courses/add/', views.course_create, name='course_create'),
    path('<int:pk>/edit/', views.course_edit, name='course_edit'),
    path('<int:pk>/delete/', views.course_delete, name='course_delete'),

    #Course Content CRUD
    path('course/<int:course_pk>/contents/add/', views.content_create, name='course_content_add'),
    path('course/<int:course_pk>/content/<int:content_pk>/edit/', views.content_edit, name='course_content_edit'),
    path('course/<int:course_pk>/content/<int:content_pk>/delete/', views.content_delete, name='course_content_delete'),
    
    # URL Baru untuk Komentar (Harus di atas atau di bawah URL konten)
    path('comment/edit/<int:comment_pk>/', views.comment_edit, name='comment_edit'),
    path('comment/delete/<int:comment_pk>/', views.comment_delete, name='comment_delete'),

    #completion
    path('dashboard/', views.user_dashboard, name='dashboard'),
    path('content/<int:content_id>/complete/', views.mark_content_complete, name='mark_content_complete'),
]