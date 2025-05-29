from sqlalchemy import  Column, Integer, String, Boolean, TEXT
from sqlalchemy.orm import  declarative_base
# Variable para declarar modelos de mapeo de la bd
Base = declarative_base()
# Modelo mapeado de la tabla incidencias 
class Incidencia(Base):
    __tablename__ = 'incidencias'  
    id_incidencia = Column(Integer, primary_key=True, index=True)
    nombre = Column(TEXT, nullable=False)
    email = Column(TEXT, nullable=False)
    asunto = Column(TEXT, nullable=False)
    mensaje = Column(TEXT, nullable=False)
    en_curso = Column(Boolean,default=False)
    finalizada = Column(Boolean,default=False)
    observaciones = Column(TEXT)
# Mapeo de la tabla usuarios 
class Usuario(Base):
    __tablename__ = 'usuarios'  
    id_usuario = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    es_admin = Column(Boolean, nullable=False)