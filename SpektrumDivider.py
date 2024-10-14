from astropy.io import fits
import matplotlib.pyplot as plt
import numpy as np
import os

def plot_spectrum(wavelength, flux, title='Spektrum Görselleştirmesi'):
    plt.figure(figsize=(12, 6))
    plt.plot(wavelength, flux, color='blue', linewidth=1)
    plt.title(title, fontsize=18)
    plt.xlabel('Dalga Boyu (Å)', fontsize=14)
    plt.ylabel('Akı (Flux)', fontsize=14)
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def main():
    # Orijinal FITS dosyasının yolu
    original_fits = '/Users/korhankara/Desktop/OtoNorm/delOri/3732_5000_uves/delori_3732_5000_uves_filtered-2.fits'
    
    # Yeni FITS dosyasının adı ve yolu
    original_dir, original_filename = os.path.split(original_fits)
    new_filename = 'kesilmis_' + original_filename
    new_fits = os.path.join(original_dir, new_filename)
    
    # Orijinal FITS dosyasını açma ve veriyi alma
    try:
        with fits.open(original_fits) as hdul:
            print("FITS dosyasındaki HDU'lar:")
            hdul.info()
            
            # Veri içeren HDU'yu bulma (BinTableHDU)
            data_hdu = None
            for hdu in hdul:
                if isinstance(hdu, fits.BinTableHDU):
                    data_hdu = hdu
                    break
            if data_hdu is None:
                raise ValueError("FITS dosyasında BinTableHDU bulunamadı.")
            
            # Veriyi alma
            data = data_hdu.data
            # Orijinal PRIMARY HDU'nun başlığını kopyalama
            primary_header = hdul[0].header.copy()
            
            # Kolon isimlerini kontrol etme
            print("\nKolonlar:")
            for col in data.columns.names:
                print(col)
            
            # Dalga boyu ve flux kolonlarını alıyoruz
            try:
                wavelength = data['X_data']
                flux = data['Y_data']
            except KeyError:
                raise KeyError("Beklenen kolon isimleri 'X_data' ve 'Y_data' değil.")
            
            # Dalga boyu ve flux değerlerini numpy dizisine dönüştürme
            wavelength = np.array(wavelength)
            flux = np.array(flux)
            
    except FileNotFoundError:
        print(f"Orijinal FITS dosyası bulunamadı: {original_fits}")
        return
    except Exception as e:
        print(f"Bir hata oluştu: {e}")
        return
    
    # Orijinal veriyi görselleştirme
    print("\nOrijinal veriyi görselleştiriyorum...")
    plot_spectrum(wavelength, flux, title='Orijinal Spektrum Görselleştirmesi')
    
    # Kullanıcıdan dalga boyu aralığını alma
    try:
        wavelength_min = float(input("Kesmek istediğiniz minimum dalga boyunu girin (örneğin 5000): "))
        wavelength_max = float(input("Kesmek istediğiniz maksimum dalga boyunu girin (örneğin 6000): "))
    except ValueError:
        print("Lütfen geçerli bir sayı girin.")
        return
    
    # Dalga boyu aralığına göre veriyi kesme
    mask = (wavelength >= wavelength_min) & (wavelength <= wavelength_max)
    new_wavelength = wavelength[mask]
    new_flux = flux[mask]
    
    if new_wavelength.size == 0:
        print("Belirtilen dalga boyu aralığında veri bulunamadı.")
        return
    
    print(f"\nOrijinal veri sayısı: {len(wavelength)}")
    print(f"Kesilmiş veri sayısı: {len(new_wavelength)}")
    
    # Yeni veri setini oluşturma
    new_data = np.rec.array(
        (new_wavelength, new_flux),
        dtype=[('X_data', new_wavelength.dtype), ('Y_data', new_flux.dtype)]
    )
    
    # Yeni FITS HDU'sunu oluşturma
    # Yeni bir Primary HDU oluşturuyoruz ve orijinal başlığı ekliyoruz
    primary_hdu_new = fits.PrimaryHDU(header=primary_header)
    
    # Yeni BinTableHDU oluşturma
    new_hdu = fits.BinTableHDU(new_data, name='SPECTRUM')
    
    # Yeni HDU listesi oluşturma
    new_hdul = fits.HDUList([primary_hdu_new, new_hdu])
    
    # Yeni FITS dosyasını kaydetme
    try:
        new_hdul.writeto(new_fits, overwrite=True)
        print(f"\nYeni FITS dosyası '{new_fits}' başarıyla oluşturuldu.")
    except Exception as e:
        print(f"Yeni FITS dosyası oluşturulurken bir hata oluştu: {e}")
        return
    
    # Yeni FITS dosyasını görselleştirme
    try:
        with fits.open(new_fits) as hdul_new:
            print("\nYeni FITS dosyasındaki HDU'lar:")
            hdul_new.info()
            
            # Veri içeren HDU'yu bulma (BinTableHDU)
            data_hdu_new = None
            for hdu in hdul_new:
                if isinstance(hdu, fits.BinTableHDU):
                    data_hdu_new = hdu
                    break
            if data_hdu_new is None:
                raise ValueError("Yeni FITS dosyasında BinTableHDU bulunamadı.")
            
            # Veriyi alma
            data_new = data_hdu_new.data
            
            # Kolon isimlerini kontrol etme
            print("\nYeni FITS dosyasındaki kolonlar:")
            for col in data_new.columns.names:
                print(col)
            
            # Dalga boyu ve flux kolonlarını alıyoruz
            try:
                wavelength_new = data_new['X_data']
                flux_new = data_new['Y_data']
            except KeyError:
                raise KeyError("Yeni FITS dosyasında beklenen kolon isimleri 'X_data' ve 'Y_data' değil.")
            
            # Dalga boyu ve flux değerlerini numpy dizisine dönüştürme
            wavelength_new = np.array(wavelength_new)
            flux_new = np.array(flux_new)
    
    except Exception as e:
        print(f"Yeni FITS dosyasını okurken bir hata oluştu: {e}")
        return
    
    # Kesilmiş veriyi görselleştirme
    print("\nKesilmiş veriyi görselleştiriyorum...")
    plot_spectrum(wavelength_new, flux_new, title='Kesilmiş Spektrum Görselleştirmesi')
    print("\nİşlem tamamlandı.")

if __name__ == "__main__":
    main()
