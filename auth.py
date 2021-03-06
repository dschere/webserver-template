# -*- encoding: UTF-8 -*-
#
# Form based authentication for CherryPy. Requires the
# Session tool to be loaded.
#

import cherrypy
import config

SESSION_KEY = '_cp_username'

def check_credentials(username, password):
    """Verifies credentials for username and password.
    Returns None on success or a string describing the error on failure"""
    # Adapt to your needs
    if username in config.SIMPLE_AUTH_DICT:
        if config.SIMPLE_AUTH_DICT[username] == password:
            return None
    return u"Incorrect username or password."
    
    # An example implementation which uses an ORM could be:
    # u = User.get(username)
    # if u is None:
    #     return u"Username %s is unknown to me." % username
    # if u.password != md5.new(password).hexdigest():
    #     return u"Incorrect password"

def check_auth(*args, **kwargs):
    """A tool that looks in config for 'auth.require'. If found and it
    is not None, a login is required and the entry is evaluated as a list of
    conditions that the user must fulfill"""
    conditions = cherrypy.request.config.get('auth.require', None)
    if conditions is not None:
        username = cherrypy.session.get(SESSION_KEY)
        if username:
            cherrypy.request.login = username
            for condition in conditions:
                # A condition is just a callable that returns true or false
                if not condition():
                    raise cherrypy.HTTPRedirect("/auth/login")
        else:
            raise cherrypy.HTTPRedirect("/auth/login")
    
cherrypy.tools.auth = cherrypy.Tool('before_handler', check_auth)

def require(*conditions):
    """A decorator that appends conditions to the auth.require config
    variable."""
    def decorate(f):
        if not hasattr(f, '_cp_config'):
            f._cp_config = dict()
        if 'auth.require' not in f._cp_config:
            f._cp_config['auth.require'] = []
        f._cp_config['auth.require'].extend(conditions)
        return f
    return decorate


# Conditions are callables that return True
# if the user fulfills the conditions they define, False otherwise
#
# They can access the current username as cherrypy.request.login
#
# Define those at will however suits the application.

def member_of(groupname):
    def check():
        r = False
        u = cherrypy.request.login
        if u in config.SIMPLE_GROUP_DICT:
            if groupname in config.SIMPLE_GROUP_DICT[u]:
                r = True
        return r
  
    return check

def name_is(reqd_username):
    return lambda: reqd_username == cherrypy.request.login

# These might be handy

def any_of(*conditions):
    """Returns True if any of the conditions match"""
    def check():
        for c in conditions:
            if c():
                return True
        return False
    return check

# By default all conditions are required, but this might still be
# needed if you want to use it inside of an any_of(...) condition
def all_of(*conditions):
    """Returns True if all of the conditions match"""
    def check():
        for c in conditions:
            if not c():
                return False
        return True
    return check


# Controller to provide login and logout actions

class AuthController(object):
    
    def on_login(self, username):
        """Called on successful login"""
    
    def on_logout(self, username):
        """Called on logout"""
    
    def get_loginform(self, username, msg="Enter login information", from_page="/"):
        bpath="/static/bower_components/bootstrap/dist/css/bootstrap.min.css"
        return """
         <html>
          <head>
            <link rel="stylesheet" href="%(bpath)s"/>
          </head>
          <body>
            <form method="POST" action="/auth/login">
             <fieldset class="form-group">
               
               <input type="hidden" name="from_page" value="%(from_page)s" />
                <table>
                 <tr><!-- logo could go here --></tr>

                 <tr><td colspan="2">
                   %(msg)s
                 </td></tr>

                 <tr>
                  <td> 
                    <label for="usernameInput">Username:</label>
                  </td>
                  <td>  
                   <input id="usernameInput" 
                    class="form-control" type="text" name="username" 
                     value="%(username)s" />
                  </td>
                 </tr>  
                      
                 <tr> 
                  <td>
                   <label for="passwordInput">Password:</label>
                  </td>
                  <td>   
                   <input class="form-control" id="passwordInput" 
                          type="password" name="password" />
                  </td>
                 </tr>

                 <tr><td colspan="2"> 
                  <input type="submit" value="Login" />
                 </td></tr>
                </table>
             </fieldset>
            </form>
          </body>
         </html>""" % locals()

    @cherrypy.expose
    def login(self, **args):
        username=args.get('username')
        password=args.get('password')
        from_page=args.get('from_page',"/")

        print "login ", args

        if username is None or password is None:
            return self.get_loginform("", from_page=from_page)
        
        error_msg = check_credentials(username, password)
        if error_msg:
            return self.get_loginform(username, error_msg, from_page)
        else:
            if not hasattr(cherrypy,'session'):
                cherrypy.session = {} 
            cherrypy.session[SESSION_KEY] = cherrypy.request.login = username
            self.on_login(username)
            if 'admin' in config.SIMPLE_GROUP_DICT.get(username,[]):
                raise cherrypy.HTTPRedirect("/restricted")
            else:
                raise cherrypy.HTTPRedirect(from_page or "/")
    
    @cherrypy.expose
    def logout(self, from_page="/"):
        sess = cherrypy.session
        username = sess.get(SESSION_KEY, None)
        sess[SESSION_KEY] = None
        if username:
            cherrypy.request.login = None
            self.on_logout(username)
        raise cherrypy.HTTPRedirect(from_page or "/")

