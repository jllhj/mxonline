# apps/utils/mixin_utils.py

"""
当用户点了“开始学习”之后，应该把这门课程与用户关联起来，在这之前应该需要做个判断，如果没有登录，则让用户先登录才可以。

如果是用函数方式写的话直接加个装饰器（@login_required）就可以，但是我们是用类的方式写的，必须用继承的方式
"""
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

class LoginRequiredMixin(object):
    @method_decorator(login_required(login_url='/login/'))
    def dispatch(self,request,*args,**kwargs):
        return super(LoginRequiredMixin, self).dispatch(request,*args,**kwargs)