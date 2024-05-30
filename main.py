from fastapi import FastAPI, HTTPException, Path,Depends
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from models.model import HastaBilgileri, HastaBilgileriPydantic,TestSonuclarıPydantic,TestSonuclari
from typing import List



SQLALCHEMY_DATABASE_URL = "postgresql://postgres:123456@localhost/postgres"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


app = FastAPI()
# Dependency to get DB Session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/hasta/{hasta_id}", response_model=HastaBilgileriPydantic)
def get_hasta(hasta_id: int = Path(..., title="The ID of the Hasta"), db: Session = Depends(get_db)):
    db_hasta = db.query(HastaBilgileri).filter(HastaBilgileri.hasta_id == hasta_id).first()
    if db_hasta is None:
        raise HTTPException(status_code=404, detail="Hasta not found")
    return db_hasta

@app.get("/hasta/{hasta_id}/test-sonuclari", response_model=List[TestSonuclarıPydantic])
def get_test_sonuclari_for_hasta(hasta_id: int = Path(..., title="The ID of the Hasta"), db: Session = Depends(get_db)):
    db_hasta = db.query(HastaBilgileri).filter(HastaBilgileri.hasta_id == hasta_id).first()
    if db_hasta is None:
        raise HTTPException(status_code=404, detail="Hasta not found")
    return db_hasta.test_sonuclari
@app.post("/hasta_ekle/", response_model=HastaBilgileriPydantic)
def hasta_ekle(hasta: HastaBilgileriPydantic, db: Session = Depends(get_db)):
    # Hasta bilgilerini veritabanına ekle
    db_hasta = HastaBilgileri(**hasta.dict())
    db.add(db_hasta)
    db.commit()
    db.refresh(db_hasta)
    return db_hasta


@app.post("/test_ekle/{hasta_id}", response_model=TestSonuclarıPydantic)
def test_ekle(hasta_id: int, test: TestSonuclarıPydantic, db: Session = Depends(get_db)):
    # Hasta ID'sine göre hasta bul
    db_hasta = db.query(HastaBilgileri).filter(HastaBilgileri.hasta_id == hasta_id).first()
    if db_hasta is None:
        raise HTTPException(status_code=404, detail="Hasta bulunamadı")

    # Test sonuçlarını veritabanına ekle
    db_test = TestSonuclari(**test.dict())
    db.add(db_test)
    db.commit()
    db.refresh(db_test)
    return db_test


@app.delete("/hasta/{hasta_id}")
def delete_hasta(hasta_id: int, db: Session = Depends(get_db)):
    db_hasta = db.query(HastaBilgileri).filter(HastaBilgileri.hasta_id == hasta_id).first()
    if db_hasta is None:
        raise HTTPException(status_code=404, detail="Hasta bulunamadı")

    # Hasta ile ilişkili tüm test sonuçlarını bul
    db_test_sonuclari = db.query(TestSonuclari).filter(TestSonuclari.hasta_id == hasta_id).all()

    # Test sonuçlarını sil
    for test_sonucu in db_test_sonuclari:
        db.delete(test_sonucu)

    # Hasta kaydını sil
    db.delete(db_hasta)
    db.commit()

    return {"message": "Hasta ve ilişkili test sonuçları başarıyla silindi"}
@app.put("/hasta_guncelle/{hasta_id}"  , response_model=HastaBilgileriPydantic)
def hasta_guncelle(hasta_id: int, hasta: HastaBilgileriPydantic, db: Session = Depends(get_db)):
   db_hasta = db.query(HastaBilgileri).filter(HastaBilgileri.hasta_id == hasta_id).first()
   if db_hasta is None:
       raise HTTPException(status_code=404, detail="Hasta bulunamadı")


   # Hasta bilgilerini güncelle
   for attr, value in vars(hasta).items():
       setattr(db_hasta, attr, value)
   db.commit()


   # Hasta bilgileri güncellendi, şimdi test sonuçlarını güncelle
   test_sonucları = db.query(TestSonuclari).filter(TestSonuclari.hasta_id == hasta_id).all()
   if test_sonucları:
       for test_sonucu in test_sonucları:
           for attr, value in vars(hasta).items():
               setattr(test_sonucu, attr, value)
       db.commit()


   return db_hasta






@app.put("/hasta_test_sonuclari_guncelle/{hasta_id}", response_model=HastaBilgileriPydantic)
def hasta_test_sonuclari_guncelle(hasta_id: int, test_sonuclari: TestSonuclarıPydantic):
    db = SessionLocal()
    try:
        # Hasta bilgilerini bul
        hasta = db.query(HastaBilgileri).filter(HastaBilgileri.hasta_id == hasta_id).first()
        if not hasta:
            raise HTTPException(status_code=404, detail="Hasta bulunamadı")

        # Hasta bilgilerini güncelle
        hasta.kolestrol = test_sonuclari.kolestrol
        hasta.kan_basinci = test_sonuclari.kan_basinci
        hasta.kan_sekeri = test_sonuclari.kan_sekeri

        # Hasta ile ilişkili test sonuçlarını bul
        test_sonuclari_db = db.query(TestSonuclari).filter(TestSonuclari.hasta_id == hasta_id).first()
        if not test_sonuclari_db:
            raise HTTPException(status_code=404, detail="Test sonuçları bulunamadı")

        # Test sonuçlarını güncelle
        test_sonuclari_db.kolestrol = test_sonuclari.kolestrol
        test_sonuclari_db.kan_basinci = test_sonuclari.kan_basinci
        test_sonuclari_db.kan_sekeri = test_sonuclari.kan_sekeri

        # Değişiklikleri veritabanına kaydet
        db.commit()
        # Hasta bilgilerini döndür
        return HastaBilgileriPydantic.from_orm(hasta, from_attributes=True)
    finally:
        db.close()



























# Ana dosya olarak çalıştığında uygulamayı başlat
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)



