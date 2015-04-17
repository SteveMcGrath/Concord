from random import SystemRandom
from hashlib import sha512, md5
from StringIO import StringIO
from PIL import Image
from os import path
from flask import current_app
from flask.ext.login import UserMixin
from sqlalchemy.ext.hybrid import hybrid_property
from app.extensions import db


class SponsorTier(db.Model):
    __tablename__ = 'sponsortiers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True)
    weight = db.Column(db.Integer, default=0)


class Sponsor(db.Model):
    __tablename__ = 'sponsors'
    id = db.Column(db.Integer, primary_key=True)
    tier_id = db.Column(db.Integer, db.ForeignKey('sponsortiers.id'))
    name = db.Column(db.String(120))
    link = db.Column(db.Text)
    tier = db.relationship('SponsorTier', backref='sponsors')

    @hybrid_property
    def _image_path(self):
        return path.join(current_app.config['SPONSOR_IMAGE_FOLDER'], 
                         '%s.jpg' % self.id)

    @hybrid_property
    def image(self):
        return self._image_path


    @image.setter
    def image(self, raw):
        # First thing that we need to do 
        buff = StringIO()
        buff.write(raw_image)
        buff.seek(0)
        img = Image.open(buff).convert('RGBA')
        img.thumbnail(current_app.config['SPONSOR_IMAGE_SIZE'])
        bg = Image.new('RGBA', 
                size=img.size, 
                color=current_app.config['SPONSOR_IMAGE_BACKGROUND']
        )
        img = alpha_composite(img, bg)
        img.save(self._image_path)