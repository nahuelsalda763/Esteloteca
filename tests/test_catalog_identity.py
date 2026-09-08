import unittest

from database_orm import (crear_clave_catalogo, limpiar_valor_catalogo)


class CatalogIdentityTest(unittest.TestCase):
    def test_mayusculas_y_minusculas_no_crean_otra_identidad(self):
        clave_a = crear_clave_catalogo(
            "Dior",
            "Sauvage",
            "Eau de Toilette",
        )
        clave_b = crear_clave_catalogo(
            "DIOR",
            "SauvAGE",
            "EAU DE TOILETTE",
        )
        self.assertEqual(clave_a, clave_b)

    def test_espacios_extra_no_crean_otra_identidad(self):
        clave_a = crear_clave_catalogo(
            "Dior",
            "Sauvage",
            "Eau de Toilette",
        )
        clave_b = crear_clave_catalogo(
            "  Dior  ",
            "Sauvage    ",
            "Eau   de    Toilette",
        )
        self.assertEqual(clave_a,clave_b)

    def test_concentraciones_distintas_son_identidades_distintas(self):
        edt = crear_clave_catalogo(
            "Dior",
            "Sauvage",
            "Eau de Toilette",
        )
        edp = crear_clave_catalogo(
            "Dior",
            "Sauvage",
            "Eau de Parfum",
        )
        self.assertNotEqual(edt, edp)


    def test_marca_o_nombre_distintos_no_se_fusionan(self):
        sauvage = crear_clave_catalogo(
            "Dior",
            "Sauvage",
            "Eau de Toilette",
        )
        homme = crear_clave_catalogo(
            "Dior",
            "Dior Homme",
            "Eau de Toilette",
        )
        self.assertNotEqual(sauvage, homme)


    def test_limpieza_conserva_capitalizacion_visible(self):
        self.assertEqual(
            limpiar_valor_catalogo("Dior   Sauvage  "),
            "Dior Sauvage",
        )


if __name__ == "__main__":
    unittest.main()