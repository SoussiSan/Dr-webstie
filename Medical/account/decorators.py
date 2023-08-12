from django.shortcuts import render, redirect


def role_required(allowed_role):
    def decorator(view_func):
        def wrap(request, *args, **kwargs):
            if request.user.role == allowed_role:
                return view_func(request, *args, **kwargs)
            else:
                return redirect('error')
        return wrap
    return decorator

def patient_role(view_func):
        def wrap(request, *args, **kwargs):
            if request.role == "PATIENT":
                return view_func(request, *args, **kwargs)
            else:
                return redirect('error')
        return wrap
