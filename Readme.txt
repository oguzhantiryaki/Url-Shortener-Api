
Kullanılan Teknolojiler:
	FastAPI: Web framework olarak kullanılmıştır. 
	Uvicorn: Uygulamayı çalıştıracak sunucu olarak kullanılmıştır.
	MySQL: Veritabanı yönetimi için kullanılmıştır.
	SQLAlchemy: Veritabanı ile etkileşimde bulunan ORM olarak kullanılmıştır.
	Pydantic: Veri doğrulama için kullanılmıştır.
	Pytest: Testleri gerçekleştirmek için kullanılmıştır.
	Redis : Caching sistemi olarak kullanılmıştır.
	Passlib: Veritabanına kaydedilecek şifrelerin hashlenmesi için kullanılmıştır.
	

Projeyi Çalıştırmak
	Proje için sanal ortam kurulmalı ve aktif edilmelidir.
	Projeyi başlatmadan önce "requirements.txt" dosyası  içindeki bağımlılıklar yüklenmelidir.
	pip install -r requirements.txt koduyla bağımlılıklar yüklenir
	config/db.py içerisindeki veritabanı bağlantısı yapılandırılmalıdır.
	routes/url.py içerisindeki redis bağlantısı yapılandırılmalıdır
	uvicorn main:app --reload komutu ile sunucu başlatılmalıdır.
	http://127.0.0.1:8000/docs adresinden apiye erişim sağlanmalıdır.
	