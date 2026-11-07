from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps


def rol_requerido(roles_permitidos):
    """
    Decorador para verificar que el usuario autenticado posea alguno de los roles permitidos.
    """
    def decorador(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('usuarios:login')

            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)

            if hasattr(request.user, 'perfil') and request.user.perfil.rol in roles_permitidos:
                return view_func(request, *args, **kwargs)

            messages.error(request, "Acceso denegado: No cuenta con los privilegios requeridos para esta sección.")
            return redirect('dashboard')
        return _wrapped_view
    return decorador


def solo_veterinario(view_func):
    return rol_requerido(['VETERINARIO', 'ADMIN'])(view_func)


def solo_recepcionista(view_func):
    return rol_requerido(['RECEPCIONISTA', 'ADMIN'])(view_func)


def solo_admin(view_func):
    return rol_requerido(['ADMIN'])(view_func)
