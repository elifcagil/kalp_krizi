from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from pydantic import BaseModel

engine = create_engine('postgresql://postgres:123456@localhost/postgres')
Base = declarative_base()

class HastaBilgileri(Base):
    __tablename__ = 'hasta_bilgileri'

    hasta_id = Column(Integer, primary_key=True, autoincrement=True)
    yas = Column(Integer, nullable=False)
    cinsiyet = Column(String(10), nullable=False)
    egzersiz = Column(String(5), nullable=False)
    aile_gecmisi = Column(String(5), nullable=False)
    sigara = Column(String(5), nullable=False)
    alkol = Column(String(5), nullable=False)
    kalp_krizi_riski = Column(Boolean, nullable=False)

    test_sonuclari = relationship("TestSonuclari", back_populates="hasta")

class HastaBilgileriPydantic(BaseModel):
    hasta_id: int
    yas: int
    cinsiyet: str
    egzersiz: str
    aile_gecmisi: str
    sigara: str
    alkol: str
    kalp_krizi_riski: bool

    class Config:
        orm_mode = True
        from_orm = True

class TestSonuclari(Base):
    __tablename__ = 'test_sonuclari'

    id = Column(Integer, primary_key=True, autoincrement=True)
    hasta_id = Column(Integer, ForeignKey('hasta_bilgileri.hasta_id'), nullable=False)
    kolestrol = Column(Integer, nullable=False)
    kan_basinci = Column(Integer, nullable=False)
    kan_sekeri = Column(Integer, nullable=False)

    hasta = relationship("HastaBilgileri", back_populates="test_sonuclari")

class TestSonuclarıPydantic(BaseModel):
    id: int
    hasta_id: int
    kolestrol: int
    kan_basinci: int
    kan_sekeri: int

    class Config:
        orm_mode = True
        from_attributes = True

Base.metadata.create_all(engine)
