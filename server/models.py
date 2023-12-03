from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Sample(db.Model):
    hash_sha256 = db.Column(db.String(64), nullable=False, primary_key=True)
    status = db.Column(db.String(20), nullable=False, default='registered')
    pin_tool_success =  db.Column(db.Boolean, default=False)
    dynamorio_tool_success =  db.Column(db.Boolean, default=False)
    frida_tool_success =  db.Column(db.Boolean, default=False)
    die_infos = db.relationship('DieInfo', backref='sample', lazy=True)
    yara_infos = db.relationship('YaraInfo', backref='sample', lazy=True)
    capa_infos = db.relationship('CapaInfo', backref='sample', lazy=True)

    def __repr__(self):
        return '<Sample %r>' % self.hash_sha256


class DieInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sample_hash_sha256 = db.Column(db.String(64), db.ForeignKey('sample.hash_sha256'), nullable=False)
    filetype = db.Column(db.String(80), nullable=True)
    parentfilepart = db.Column(db.String(80), nullable=True)
    info = db.Column(db.String(80), nullable=True)
    name = db.Column(db.String(80), nullable=True)
    string = db.Column(db.String(120), nullable=True)
    type = db.Column(db.String(80), nullable=True)
    version = db.Column(db.String(80), nullable=True)

    def __repr__(self):
        return f'<DieInfo {self.name}>'
    

class YaraInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sample_hash_sha256 = db.Column(db.String(64), db.ForeignKey('sample.hash_sha256'), nullable=False)
    rule = db.Column(db.String(120), nullable=True)
    author = db.Column(db.String(120), nullable=True)
    original_author = db.Column(db.String(120), nullable=True)
    reference = db.Column(db.String(255), nullable=True)
    tags = db.Column(db.String(255), nullable=True)
    namespace = db.Column(db.String(120), nullable=True)
    description = db.Column(db.Text, nullable=True)
    date = db.Column(db.String(50), nullable=True)

    def __repr__(self):
        return f'<YaraInfo {self.rule}>'


class CapaInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sample_hash_sha256 = db.Column(db.String(64), db.ForeignKey('sample.hash_sha256'), nullable=False)
    name = db.Column(db.String(120), nullable=True)
    authors = db.Column(db.String(255), nullable=True)
    scope = db.Column(db.String(120), nullable=True)
    references = db.Column(db.Text, nullable=True) 
    description = db.Column(db.Text, nullable=True)
    namespace = db.Column(db.String(120), nullable=True)

    def __repr__(self):
        return f'<CapaInfo {self.name}>'


class Config(db.Model):
    
    config_name = db.Column(db.String(50), primary_key=True)
    config_value = db.Column(db.String(200))
    
    def __repr__(self):
        return '<Config %r>' % self.config_name
