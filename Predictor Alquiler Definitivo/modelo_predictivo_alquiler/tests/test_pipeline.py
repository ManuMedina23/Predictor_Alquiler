import unittest
from pipeline import *

class TestPipeline(unittest.TestCase):
    def setUp(self):
        self.features = [
            "3 habitaciones", 
            "2 baños", 
            "construido en 1998", 
            "Con ascensor", 
            "Trastero incluido", 
            "Orientacion sur", 
            "Planta 2", 
            "85 m²", 
            "Segunda mano", 
            "Armarios empotrados", 
            "Terraza", 
            "Balcon", 
            "Jardin comunitario", 
            "Garaje incluido", 
            "Calefacción individual", 
            "Aire acondicionado", 
            "Piscina", 
            "Zonas verdes"
        ]

    def test_get_habitaciones(self):
        self.assertEqual(get_habitaciones(self.features), 3)

    def test_get_baños(self):
        self.assertEqual(get_baños(self.features), 2)

    def test_get_ascensor(self):
        self.assertEqual(get_ascensor(self.features), 1)

    def test_get_trastero(self):
        self.assertEqual(get_trastero(self.features), 1)

    def test_get_orientacion(self):
        self.assertEqual(get_orientacion(self.features), "sur")

    def test_get_piso(self):
        self.assertEqual(get_piso(self.features), "Planta 2")

    def test_get_metros_reales(self):
        self.assertEqual(get_metros_reales(self.features), 85)

    def test_get_condicion(self):
        self.assertEqual(get_condicion(self.features), "Segunda mano")

    def test_get_armario_empotrado(self):
        self.assertEqual(get_armario_empotrado(self.features), 1)

    def test_get_terraza(self):
        self.assertEqual(get_terraza(self.features), 1)

    def test_get_balcon(self):
        self.assertEqual(get_balcon(self.features), 1)

    def test_get_jardin(self):
        self.assertEqual(get_jardin(self.features), 1)

    def test_get_garaje(self):
        self.assertEqual(get_garaje(self.features), 1)

    def test_get_calefaccion(self):
        self.assertEqual(get_calefaccion(self.features), 1)

    def test_get_aire_acon(self):
        self.assertEqual(get_aire_acon(self.features), 1)

    def test_get_piscina(self):
        self.assertEqual(get_piscina(self.features), 1)

    def test_get_zonas_verdes(self):
        self.assertEqual(get_zonas_verdes(self.features), 1)

    def test_process_piso(self):
        self.assertEqual(process_piso("Planta 2"), "Primeros_pisos")
        self.assertEqual(process_piso("Planta 5"), "Ultimos_pisos")
        self.assertEqual(process_piso("Bajo"), "Bajo")
        self.assertEqual(process_piso("Exterior"), "Bajo")

if __name__ == '__main__':
    unittest.main()