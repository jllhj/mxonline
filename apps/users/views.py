
from django.urls import reverse
# Create your views here.



from django.shortcuts import render,redirect,HttpResponse,HttpResponseRedirect
from apps.utils.mixin_utils import LoginRequiredMixin
from pure_pagination import Paginator,PageNotAnInteger
import json
from django.contrib.auth import authenticate, login,logout

from django.contrib.auth.backends import ModelBackend
from users.models import UserProfile
from django.db.models import Q
from .forms import LoginForm,RegisterForm,ForgetPwdForm,ModifyPwdForm,UserInfoForm
from django.contrib.auth.hashers import make_password
from utils.email_send import send_register_eamil
from django.views.generic.base import View
from operation.models import UserCourse,UserFavorite,UserMessage
from organization.models import CourseOrg,Teacher
from course.models import Course


#邮箱和用户名都可以登录
# 基础ModelBackend类，因为它有authenticate方法
class CustomBackend(ModelBackend):
    """
    用于mx_login下的authenticate，
    setting中需配置全局路径AUTHENTICATION_BACKENDS，当用户登录验证时，用到mx_login下的authenticate进行验证，会
    跳到此处进行验证
    """
    def authenticate(self, request, username=None, password=None, **kwargs):# 重写authenticate方法
        try:
            # 不希望用户存在两个，get的结果只能有一个，否则报错
            user = UserProfile.objects.get(Q(username=username)|Q(email=username))

            # django的后台中密码是加密处理的，拿到客户登录的密码需要加密后才能对比判断，所以不能直接password==password
            # UserProfile继承的AbstractUser中有check_password（）方法，会直接将传入的密码加密后于后台的作比较:
            if user.check_password(password):# 如果为False，则密码不一致，否则密码正确
                return user
        except Exception as e:
            return None


# def index(request):
#     """首页"""
#     return render(request,"index.html")
from users.models import Banner


class IndexView(View):
    '''首页'''
    def get(self,request):
        #轮播图
        all_banners = Banner.objects.all().order_by('index')
        #课程
        courses = Course.objects.filter(is_banner=False)[:6]
        #轮播课程
        banner_courses = Course.objects.filter(is_banner=True)[:3]
        #课程机构
        course_orgs = Course.objects.all()[:15]
        return render(request,'index.html',{
            'all_banners':all_banners,
            'courses':courses,
            'banner_courses':banner_courses,
            'course_orgs':course_orgs,
        })

# def user_login(request):
#     if request.method == "POST":
#         login_form = LoginForm(request.POST)
#         if login_form.is_valid():  # form验证通过
#             # 获取用户提交的用户名和密码
#             user_name = request.POST.get('username', None)
#             pass_word = request.POST.get('password', None)
#             # 成功返回user对象,失败None
#             user = authenticate(username=user_name, password=pass_word)
#             # 如果不是null说明验证成功
#             if user:
#                 # if user.is_active:
#                 #     # 只有注册激活才能登录
#                 #     login(request, user)
#                 #     return HttpResponseRedirect(reverse('index'))
#                 # request.session["is_login"] = True
#                 # request.session["username"] = user_name
#                 # request.session.set_expiry(5)
#                 login(request, user)
#                 return redirect(reverse('index'))
#                 # else:
#                 #     return render(request, 'login.html', {'msg': '用户名或密码错误', 'login_form': login_form})
#             # 账号或密码错误
#             else:
#                 return render(request, 'login.html', {'msg': '用户名或密码错误'})
#         else:
#             return render(request, 'login.html', {'login_form': login_form})
#
#     return render(request, 'login.html')

# 激活用户
from users.models import EmailVerifyRecord
class ActiveUserView(View):
    def get(self, request, active_code):
        # 查询邮箱验证记录是否存在
        all_record = EmailVerifyRecord.objects.filter(code = active_code)

        if all_record:
            for record in all_record:
                # 获取到对应的邮箱
                email = record.email
                # 查找到邮箱对应的user
                user = UserProfile.objects.get(email=email)
                user.is_active = True
                user.save()
         # 验证码不对的时候跳转到激活失败页面
        else:
            return render(request,'active_fail.html')
        # 激活成功跳转到登录页面
        return render(request, "login.html", )


# class LoginUnsafeView(View):
#     def get(self, request):
#         return render(request, "login.html", {})
#     def post(self, request):
#         user_name = request.POST.get("username", "")
#         pass_word = request.POST.get("password", "")
#
#         import MySQLdb
#         conn = MySQLdb.connect(host='127.0.0.1', user='root', passwd='468867748', db='mxonline', charset='utf8')
#         cursor = conn.cursor()
#         sql_select = "select * from users_userprofile where email='{0}' and password='{1}'".format(user_name, pass_word)
#
#         result = cursor.execute(sql_select)
#         for row in cursor.fetchall():
#             # 查询到用户
#             print(row)
#         print('test')


class LoginView(View):
    '''用户登录'''

    def get(self,request):
        return render(request, 'login.html')

    def post(self,request):
        # 实例化
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            # 获取用户提交的用户名和密码
            user_name = request.POST.get('username', None)
            pass_word = request.POST.get('password', None)
            # 成功返回user对象,失败None
            user = authenticate(username=user_name, password=pass_word)
            # 如果不是null说明验证成功
            if user is not None:
                if user.is_active:
                    # 只有注册激活才能登录
                    login(request, user)
                    return render(request, 'index.html')
                else:
                    return render(request, 'login.html', {'msg': '该用户没有被激活', 'login_form': login_form})
            # 只有当用户名或密码不存在时，才返回错误信息到前端
            else:
                return render(request, 'login.html', {'msg': '用户名或密码错误','login_form':login_form})

        # form.is_valid（）已经判断不合法了，所以这里不需要再返回错误信息到前端了
        else:
            return render(request,'login.html',{'login_form':login_form})



class RegisterView(View):
    '''用户注册'''
    def get(self,request):
        register_form = RegisterForm()
        return render(request,'register.html',{'register_form':register_form})

    def post(self,request):
        register_form = RegisterForm(request.POST)
        if register_form.is_valid():
            user_name = request.POST.get('email')
            # 如果用户已存在，则提示错误信息
            if UserProfile.objects.filter(email = user_name):
                return render(request, 'register.html', {'register_form':register_form,'msg': '用户已存在'})

            pass_word = request.POST.get('password')
            # 实例化一个user_profile对象
            user_profile = UserProfile()
            user_profile.username = user_name
            user_profile.email = user_name
            # 默认添加的用户是激活状态（is_active = 1表示True），在这里我们修改默认的状态（改为is_active = False），只有用户去邮箱激活之后才改为True

            user_profile.is_active = False
            # 对保存到数据库的密码加密
            user_profile.password = make_password(pass_word)
            user_profile.save()
            send_register_eamil(user_name,'register')
            # id: 主键, password
            # 密码, last_login
            # Django自动记录用户最后登录时间,。
            # is_superuser
            # 表明用户是否是超级用户(后台管理会用到)。
            # username
            # 用户名字段不要随便改动, email
            # 邮箱,
            # is_staff
            # 表示是否是员工(后台管理会用到)。
            # is_active
            # 用户是否是激活状态, date_joined
            # 注册时间。
            return render(request,'login.html')
        else:
            return render(request,'register.html',{'register_form':register_form})



class ForgetPwdView(View):
    '''找回密码'''
    def get(self,request):
        forget_form = ForgetPwdForm()
        return render(request,'forgetpwd.html',{'forget_form':forget_form})

    def post(self,request):
        forget_form = ForgetPwdForm(request.POST)
        if forget_form.is_valid():
            email = request.POST.get('email',None)
            # 到email_send文件 执行函数 发送邮箱和forget
            send_register_eamil(email,'forget')
            return render(request, 'send_success.html')
        else:
            return render(request,'forgetpwd.html',{'forget_form':forget_form})


class ResetView(View):
    """重置密码"""
    def get(self, request, active_code):
        all_records = EmailVerifyRecord.objects.filter(code=active_code)
        if all_records:
            for record in all_records:
                email = record.email
                return render(request, "password_reset.html", {"email":email})
        else:
            return render(request, "active_fail.html")
        return render(request, "login.html")



class ModifyPwdView(View):
    """修改密码"""
    def post(self, request):
        modify_form = ModifyPwdForm(request.POST)
        if modify_form.is_valid():
            pwd1 = request.POST.get("password1", "")
            pwd2 = request.POST.get("password2", "")
            email = request.POST.get("email", "")
            if pwd1 != pwd2:
                return render(request, "password_reset.html", {"email":email, "msg":"密码不一致！"})
            user = UserProfile.objects.get(email=email)
            user.password = make_password(pwd2)
            user.save()

            return render(request, "login.html")
        else:
            email = request.POST.get("email", "")
            return render(request, "password_reset.html", {"email":email, "modify_form":modify_form })


class UserinfoView(LoginRequiredMixin,View):
    '''用户个人信息'''
    def get(self,request):
        print(request.user)
        print(request.user.nick_name)
        return render(request,'usercenter-info.html',{})


from apps.users.forms import UploadImageForm
class UploadImageView(LoginRequiredMixin,View):
    '''用户图像修改'''
    def post(self,request):
        #上传的文件都在request.FILES里面获取，所以这里要多传一个这个参数
        image_form = UploadImageForm(request.POST,request.FILES)
        if image_form.is_valid():
            image = image_form.cleaned_data['image']
            request.user.image = image
            request.user.save()
            return HttpResponse('{"status":"success"}', content_type='application/json')
        else:
            return HttpResponse('{"status":"fail"}', content_type='application/json')


class UpdatePwdView(View):
    """
    个人中心修改用户密码
    """
    def post(self, request):
        modify_form = ModifyPwdForm(request.POST)
        if modify_form.is_valid():
            pwd1 = request.POST.get("password1", "")
            pwd2 = request.POST.get("password2", "")
            if pwd1 != pwd2:
                return HttpResponse('{"status":"fail","msg":"密码不一致"}',  content_type='application/json')
            user = request.user
            user.password = make_password(pwd2)
            user.save()

            return HttpResponse('{"status":"success"}', content_type='application/json')
        else:
            return HttpResponse(json.dumps(modify_form.errors), content_type='application/json')


class SendEmailCodeView(LoginRequiredMixin, View):
    '''发送邮箱修改验证码'''
    def get(self,request):
        email = request.GET.get('email','')

        if UserProfile.objects.filter(email=email):
            return HttpResponse('{"email":"邮箱已存在"}', content_type='application/json')

        send_register_eamil(email,'update_email')
        return HttpResponse('{"status":"success"}', content_type='application/json')


class UpdateEmailView(LoginRequiredMixin, View):
    '''修改邮箱'''
    def post(self, request):
        email = request.POST.get("email", "")
        code = request.POST.get("code", "")

        existed_records = EmailVerifyRecord.objects.filter(email=email, code=code, send_type='update_email')
        if existed_records:
            user = request.user
            user.email = email
            user.save()
            return HttpResponse('{"status":"success"}', content_type='application/json')
        else:
            return HttpResponse('{"email":"验证码无效"}', content_type='application/json')


class UserinfoView(LoginRequiredMixin,View):
    '''用户个人信息'''
    def get(self,request):
        return render(request,'usercenter-info.html')

    def post(self, request):
        user_info_form = UserInfoForm(request.POST, instance=request.user)

        if user_info_form.is_valid():
            user_info_form.save()
            return HttpResponse('{"status":"success"}', content_type='application/json')
        else:
            print(user_info_form.errors)
            return HttpResponse(json.dumps(user_info_form.errors), content_type='application/json')


class MyCourseView(LoginRequiredMixin, View):
    '''我的课程'''
    def get(self, request):
        user_courses = UserCourse.objects.filter(user=request.user)
        return render(request, "usercenter-mycourse.html", {
            "user_courses":user_courses,
        })


class MyFavOrgView(LoginRequiredMixin,View):
    '''我收藏的课程机构'''

    def get(self, request):
        org_list = []
        fav_orgs = UserFavorite.objects.filter(user=request.user, fav_type=2)
        # 上面的fav_orgs只是存放了id。我们还需要通过id找到机构对象
        for fav_org in fav_orgs:
            # 取出fav_id也就是机构的id。
            org_id = fav_org.fav_id
            # 获取这个机构对象
            org = CourseOrg.objects.get(id=org_id)
            org_list.append(org)
        return render(request, "usercenter-fav-org.html", {
            "org_list": org_list,
        })


class MyFavTeacherView(LoginRequiredMixin, View):
    '''我收藏的授课讲师'''

    def get(self, request):
        teacher_list = []
        fav_teachers = UserFavorite.objects.filter(user=request.user, fav_type=3)
        for fav_teacher in fav_teachers:
            teacher_id = fav_teacher.fav_id
            teacher = Teacher.objects.get(id=teacher_id)
            teacher_list.append(teacher)
        return render(request, "usercenter-fav-teacher.html", {
            "teacher_list": teacher_list,
        })


class MyFavCourseView(LoginRequiredMixin,View):
    """
    我收藏的课程
    """
    def get(self, request):
        course_list = []
        fav_courses = UserFavorite.objects.filter(user=request.user, fav_type=1)
        for fav_course in fav_courses:
            course_id = fav_course.fav_id
            course = Course.objects.get(id=course_id)
            course_list.append(course)

        return render(request, 'usercenter-fav-course.html', {
            "course_list":course_list,
        })


class MyMessageView(LoginRequiredMixin, View):
    '''我的消息'''

    def get(self, request):
        all_message = UserMessage.objects.filter(user= request.user.id)

        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        p = Paginator(all_message, 4,request=request)
        messages = p.page(page)
        return  render(request, "usercenter-message.html", {
        "messages":messages,
        })


class LogoutView(View):
    '''用户登出'''
    def get(self,request):
        logout(request)
        from django.urls import reverse
        return HttpResponseRedirect(reverse('index'))


from django.shortcuts import render_to_response
def pag_not_found(request):
    # 全局404处理函数
    response = render_to_response('404.html', {})
    response.status_code = 404
    return response

def page_error(request):
    # 全局500处理函数
    from django.shortcuts import render_to_response
    response = render_to_response('500.html', {})
    response.status_code = 500
    return response