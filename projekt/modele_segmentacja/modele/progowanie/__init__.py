"""
Klasyczna metoda odniesienia (bez uczenia): znamie = obszar ciemniejszy od skory.

Jasnosc L (Lab) w zaznaczonym obszarze -> rozmycie -> prog Otsu -> otwarcie/
zamkniecie morfologiczne -> wypelnienie dziur -> najwieksza skladowa.
Sluzy jako punkt odniesienia w porownaniu z modelami glebokimi.
"""
import cv2
import numpy as np

from ...interfejs import ModelSegmentacji


class Model(ModelSegmentacji):
    klucz = "progowanie"
    nazwa = "Progowanie Otsu"
    opis = "Metoda klasyczna, bez uczenia: obszar ciemniejszy od skory (prog Otsu jasnosci L), najwieksza skladowa."

    def _prawdopodobienstwo(self, wycinek_bgr):
        L = cv2.cvtColor(wycinek_bgr, cv2.COLOR_BGR2LAB)[..., 0]
        s = max(1, min(L.shape) // 100)
        L = cv2.GaussianBlur(L, (0, 0), s)
        _, m = cv2.threshold(L, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (4 * s + 1, 4 * s + 1))
        m = cv2.morphologyEx(cv2.morphologyEx(m, cv2.MORPH_OPEN, k), cv2.MORPH_CLOSE, k)
        # wypelnienie dziur: wszystko, czego nie da sie zalac od brzegu
        tlo = cv2.copyMakeBorder(m, 1, 1, 1, 1, cv2.BORDER_CONSTANT, value=0)
        maska_zal = np.zeros((tlo.shape[0] + 2, tlo.shape[1] + 2), np.uint8)
        cv2.floodFill(tlo, maska_zal, (0, 0), 255)
        m = m | cv2.bitwise_not(tlo[1:-1, 1:-1])
        return (m > 0).astype(np.float32)
