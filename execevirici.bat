@echo off
REM pip ile pygame ve pyinstaller'ı yükle
echo Gerekli kütüphaneler yükleniyor...
pip install pygame pyinstaller

REM Aynı klasördeki ilk .py dosyasını bul
for %%f in (*.py) do (
    set "target=%%f"
    goto build
)

:build
REM PyInstaller ile .exe dosyasına çevir
echo Derleniyor: %target%
pyinstaller --onefile --windowed "%target%"

REM build ve dist dışında oluşan dosyaları temizle
echo Gereksiz dosyalar siliniyor...
rmdir /s /q build
del /q "%~n0.spec"

echo .exe dosyası 'dist' klasöründe hazır!
pause
