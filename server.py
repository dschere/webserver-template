import cherrypy
import config
from auth import AuthController, require, member_of, name_is
import os
import upload

class RestrictedArea:
    _cp_config = {
        'auth.require': [member_of('admin')]
    }

    upload = upload.fileUpload() 
    
    
    @cherrypy.expose
    def index(self):
        return """This is the admin only area."""



class WebserviceRoot(object):
    _cp_config = {
        'tools.sessions.on': True,
        'tools.auth.on': True,
    }

    if config.AUTH_IMPLEMENTATION == "simple":
        checkpassword = \
           cherrypy.lib.auth_basic.checkpassword_dict(config.SIMPLE_AUTH_DICT)
        basic_auth = {'tools.auth_basic.on': True,
              'tools.auth_basic.realm': 'earth',
              'tools.auth_basic.checkpassword': checkpassword,  
        }
        _cp_config['/'] = basic_auth

    def __init__(self):
        self.cache = {}
        if config.AUTH_IMPLEMENTATION == "basic-multi":
            self.auth = AuthController() 
            self.restricted = RestrictedArea()



    @cherrypy.expose
    @require()
    def index(self, **params):
        if not cherrypy.request.login:
            raise cherrypy.InternalRedirect("/auth/login")
        elif cherrypy.request.login == "admin":
            raise cherrypy.InternalRedirect("/restricted")
        return "logged in as non admin user"


cherrypy.config.update({'server.socket_host': '0.0.0.0',
                        'server.socket_port': 8000,
                       })


static_config = {
    '/static':{
    'tools.staticdir.debug': True,
    'tools.staticdir.on': True,
    'tools.staticdir.root': config.STATIC_WEBCONTENT,
    'tools.staticdir.dir': '' 
    }
}
cherrypy.quickstart(WebserviceRoot(), '/', config = static_config)

