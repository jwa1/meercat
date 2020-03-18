import sqlalchemy as db
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey

import os


database_url = os.getenv('DATABASE_URL')
db_engine = db.create_engine(database_url)
Session = sessionmaker(bind=db_engine)
Base = declarative_base(name='Model')

class Mapping(Base):
    __tablename__ = 'mapping'

    id = Column(Integer, primary_key=True)
    catalyst = Column(String, ForeignKey('switch.id'))
    meraki = Column(String, ForeignKey('switch.id'))

class Switch(Base):
    __tablename__ = 'switch'

    id = Column(String, primary_key=True)
    platform = Column(String)
    model = Column(String)
    modular = Column(Boolean)

    stackable = Column(Boolean)
    network_module = Column(String)
    tier = Column(String)

    dl_ge = Column(Integer)
    dl_ge_poe = Column(Integer)
    dl_ge_poep = Column(Integer)
    dl_ge_upoep = Column(Integer)
    dl_ge_sfp = Column(Integer)
    dl_2ge_upoe = Column(Integer)
    dl_mgig_poep = Column(Integer)
    dl_mgig_upoe = Column(Integer)
    dl_10ge = Column(Integer)
    dl_10ge_sfpp = Column(Integer)
    dl_25ge_sfp28 = Column(Integer)
    dl_40ge_qsfpp = Column(Integer)
    dl_100ge_qsfp28 = Column(Integer)
    ul_ge_sfp = Column(Integer)
    ul_mgig = Column(Integer)
    ul_10ge_sfpp = Column(Integer)
    ul_25ge_sfp28 = Column(Integer)
    ul_40ge_qsfpp = Column(Integer)
    ul_100ge_qsfp28 = Column(Integer)
    
    poe_power = Column(Integer)
    switching_capacity = Column(Integer)
    mac_entry = Column(Integer)
    vlan = Column(Integer)

    def __repr__(self):
        text = "Here are the details of the equivalent switch:\n\n"
        for attr, value in vars(self).items():
            # Don't append null values or internal attributes
            if value and value != 'null' and attr[0] != '_':
                text += f"{attr}: {value}\n"

        return text
