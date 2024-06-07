import os

class Config:
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:passwordpostgres@localhost:5432/grbbookstore'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
