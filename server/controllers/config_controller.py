
from models import db, Config

def update_config_item(name, value):
    config_item = Config.query.filter_by(config_name=name).first()
    if config_item:
        config_item.config_value = value
    else:
        config_item = Config(config_name=name, config_value=value)
        db.session.add(config_item)
    db.session.commit()

def get_config_item(name):
    config_item = Config.query.filter_by(config_name=name).first()
    if config_item:
        return config_item.config_value
    return None