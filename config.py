import os

CWD=os.path.dirname(os.path.realpath(__file__))

STATIC_WEBCONTENT=CWD+os.sep+"static"+os.sep
print STATIC_WEBCONTENT
assert os.access( STATIC_WEBCONTENT, os.F_OK )

#assert bower_components/bootstrap/dist/bootstrap.min.css

# Chhose authentication level
#  simple: one user gets all permissions 
#  basic-multi: basic username/password auth 
#               with multiple user levels
AUTH_IMPLEMENTATION="basic-multi"
# if you use "simple" please change this to something
# sane other than admin:admin
#                  username:password
SIMPLE_AUTH_DICT={'admin':'admin'}
#                  username:groups
SIMPLE_GROUP_DICT={'admin':['admin']}
