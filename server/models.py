from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Sample(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    sample_hash_sha256 = db.Column(db.String(64), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='registered')

    def __repr__(self):
        return '<Sample %r>' % self.sample_hash_sha256
    
class Config(db.Model):
    
    config_name = db.Column(db.String(50), primary_key=True)
    config_value = db.Column(db.String(200))
    
    def __repr__(self):
        return '<Config %r>' % self.config_name
