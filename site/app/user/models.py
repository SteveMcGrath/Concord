from app.auth.models import User as AuthUser
from sqlalchemy.ext.hybrid import hybrid_property
from app.extensions import db
from flask import current_app
import mistune

class User(AuthUser):
    name = db.Column(db.String(120))
    shirt = db.Column(db.String(10))
    bio_md = db.Column(db.Text)

    @hybrid_property
    def bio(self):
        if not self.bio_md:
            self.bio_md = ''
        return mistune.markdown(self.bio_md, escape=True)

    @bio.setter
    def bio(self, value):
        self.bio_md = value