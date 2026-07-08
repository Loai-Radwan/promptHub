
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('',views.index, name="index"),
    path('dashboard',views.dashboard, name="dashboard"),
    path('create_prompt',views.create_prompt, name="create_prompt"),
    path('browse',views.browse, name="browse"),
    path('prompt/<int:id>',views.prompt, name="prompt"),
    path('edit_prompt/<int:id>',views.edit_prompt, name="edit_prompt"),
    path('categories',views.categories, name="categories"),
    path('category/<str:name>',views.category, name="category"),
    path('upload_profile_picture',views.upload_profile_picture, name="upload_profile_picture"),
    path('user/<str:username>',views.user, name="user"),
    path('edit_profile',views.edit_profile, name="edit_profile"),
    path('login',views.login_view, name="login"),
    path('logout',views.logout_view, name="logout"),
    path('register',views.register, name="register"),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
