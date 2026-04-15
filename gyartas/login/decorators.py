from django.shortcuts import redirect

def role_required(roles):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):

            # 1) Nincs bejelentkezve → login
            if not request.session.get('is_authenticated'):
                return redirect('/login/')

            # 2) Nincs szerepkör → login
            if 'szerepkor' not in request.session:
                return redirect('/login/')

            # 3) Rossz szerepkör → tiltás
            if request.session.get('szerepkor') not in roles:
                return redirect('/nincs-jogosultsag/')

            # 4) Cache tiltása → böngésző vissza NEM működik
            response = view_func(request, *args, **kwargs)
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
            return response

        return wrapper
    return decorator
