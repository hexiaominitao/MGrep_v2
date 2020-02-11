import os

from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_principal import (Permission, Principal, RoleNeed)
from flask_uploads import UploadSet, DOCUMENTS, DATA, ARCHIVES

bcrypt = Bcrypt()
login_magager = LoginManager()
principal = Principal()

file_sam = UploadSet('filesam', DOCUMENTS)
