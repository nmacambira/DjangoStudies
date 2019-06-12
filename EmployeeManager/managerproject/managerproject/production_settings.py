import os

SECRET_KEY = 'j7& +og-mig_#rlg+-e%wm)%hci8^h+trz8ng$4=k+=1^4w=zeqv44'

DEBUG = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'myappmanagerproduction',
        'USER': 'myappmanager',
        'PASSWORD': 'MyApp123456',
        'HOST': '127.0.0.1',
        'PORT': '',
    }
}

# MEDIA_ROOT = '/storage/'
# MEDIA_URL = 'http://127.0.0.1:8000/'

MEDIA_ROOT = '/home/companyname/web/myapp_static/media'
MEDIA_URL = 'http://myapp.companyname.com.br/static/media/'

# STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_ROOT = '/home/companyname/web/myapp_static/'
STATIC_URL = 'http://myapp.companyname.com.br/static/'