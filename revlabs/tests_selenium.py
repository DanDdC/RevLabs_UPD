from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from revlabs.models import Car, Track
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import os

# -------------------------------------------------------------------------
# Configuração base extraída do guia
# -------------------------------------------------------------------------
class BaseTestCase(StaticLiveServerTestCase):
    """
    Classe-base que inicializa e encerra o Chrome em modo headless
    (sem interface gráfica) antes e depois de cada teste.
    """

    def setUp(self):
        # 1. Create a fake track for the test database
        Track.objects.create(
            slug_id='interlagos', 
            name='Interlagos - Brazil', 
            length_km=4.309, 
            speed_multiplier=1.00, 
            image_path='img/interlagos-icon.png'
        )

        Track.objects.create(
            slug_id='monza', 
            name='Monza - Italy', 
            length_km=5.793, 
            speed_multiplier=1.20, 
            image_path='img/monza.png'
        )   
        
        # 2. Create a fake car for the test database
        Car.objects.create(
            slug_id='mercedes', 
            name="Mercedes-AMG GT Black Series '20", 
            base_avg_speed_kmh=160.0, 
            power_hp=730, 
            weight_kg=1540, 
            image_path='img/mercedes-amg.png'
        )

        Car.objects.create(
            slug_id='fusca', 
            name="VW Fusca", 
            base_avg_speed_kmh=95.0, 
            power_hp=65, 
            weight_kg=840, 
            image_path='img/vw-fusca.png'
        )

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        opts = Options()

        if os.environ.get('GITHUB_ACTIONS'):
            opts.add_argument("--headless")

        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument("--disable-gpu")
        opts.add_argument("--window-size=1280,800")

        service = Service(ChromeDriverManager().install())
        cls.driver = webdriver.Chrome(service=service, options=opts)
        cls.wait = WebDriverWait(cls.driver, 10)

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, "driver"):
            cls.driver.quit()
        super().tearDownClass()

    def abrir_pagina(self, caminho="/"):
        """Navega para uma URL relativa ao servidor de teste."""
        self.driver.get(self.live_server_url + caminho)

    def pause_if_local(self, seconds=8):
        """Pauses the test so you can watch it locally, but skips the wait during GitHub deployments."""
        if not os.environ.get('GITHUB_ACTIONS'):
            time.sleep(seconds)


# -------------------------------------------------------------------------
# Testes End-to-End do RevLabs
# -------------------------------------------------------------------------
class Teste_01_FluxoSimulador(BaseTestCase):
    """Testa o fluxo principal do simulador RevLabs: Pistas -> Carros -> Dashboard."""

    def test_01_deve_carregar_selecao_de_pistas(self):
        print("Teste 01: Visualização da página de seleção de pistas.")
        
        # Abre a página inicial de pistas
        self.abrir_pagina("/")
        
        body = self.wait.until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # Verifica se o título e uma das pistas estão na página
        self.assertIn("Select your Circuit", body.text)
        self.assertIn("Interlagos - Brazil", body.text)
        
        self.pause_if_local(8)

    def test_02_deve_navegar_para_selecao_de_carros(self):
        print("Teste 02: Navegação da seleção de pistas para seleção de carros.")
        self.abrir_pagina("/")
        
        # Clica no card da pista de Interlagos
        link_interlagos = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//h3[text()='Interlagos - Brazil']/ancestor::a"))
        )
        link_interlagos.click()
        
        body = self.wait.until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # Verifica se navegou para a página de veículos
        self.assertIn("Top Choices", body.text)
        self.assertIn("Mercedes-AMG GT Black Series", body.text)
        
        self.pause_if_local(8)

    def test_03_deve_navegar_para_dashboard_e_ver_tempo(self):
        print("Teste 03: Navegação para o dashboard e visualização do tempo de volta.")
        
        # Navega para a seleção de carros com a pista setada na URL
        self.abrir_pagina("/vehicles/?track=interlagos")
        
        # Clica no card do VW Fusca
        link_carro = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'car-name') and text()='VW Fusca']/ancestor::a"))
        )
        link_carro.click()
        
        body = self.wait.until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # Verifica se as informações de dashboard renderizaram corretamente
        self.assertIn("Lap time on this track", body.text)
        self.assertIn("VW Fusca", body.text)
        self.assertIn("Interlagos - Brazil", body.text)
        
        self.pause_if_local(8)

    def test_04_deve_interagir_com_menu_de_mods(self):
        print("Teste 04: Interação com os MODs e cálculo de tempo no dashboard.")
        
        self.abrir_pagina("/dashboard/?track=interlagos&car=fusca")
        
        # 1. Pega o tempo inicial antes de aplicar os mods
        time_display_initial = self.wait.until(
            EC.presence_of_element_located((By.ID, "lap-time-display"))
        ).text

        # 2. Abre o menu do Mod 1
        mod_slot = self.wait.until(
            EC.element_to_be_clickable((By.ID, "mod-1"))
        )
        mod_slot.click()

        self.pause_if_local(8)
        
        menu = self.wait.until(
            EC.visibility_of_element_located((By.ID, "mod-dropdown"))
        )
        self.assertTrue(menu.is_displayed())
        
        # 3. Clica na sub-categoria "Turbochargers" para filtrar
        turbo_category = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//li[text()='Turbochargers']"))
        )
        turbo_category.click()

        self.pause_if_local(8)

        # 4. Agora procura pela peça correta do Turbo e clica
        turbo_option = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Twin-Scroll Turbo Kit')]/ancestor::div[contains(@class, 'part-item')]"))
        )

        self.pause_if_local(8)
        
        # Usa JavaScript para clicar, prevenindo falhas de sobreposição (overlap)
        self.driver.execute_script("arguments[0].click();", turbo_option)
        
        # 5. Espera explicitamente a classe "time-improved" ser adicionada pelo JavaScript ao calcular o novo tempo
        time_display = self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#lap-time-display.time-improved"))
        )

        self.pause_if_local(8)
        
        # 6. Valida que o tempo foi alterado com sucesso e não está quebrado (NaN)
        self.assertNotEqual(time_display.text, time_display_initial)
        self.assertNotIn("NaN", time_display.text)

    def test_05_deve_voltar_para_veiculos_e_manter_pista(self):
        print("Teste 05: Voltar do dashboard para a tela de veículos e verificar se a pista permanece a mesma.")
        
        # 1. Starts at the Track Selection page
        self.abrir_pagina("/")

        self.pause_if_local(8)
        
        # 2. Selects a track (e.g., Monza)
        link_monza = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//h3[text()='Monza - Italy']/ancestor::a"))
        )
        link_monza.click()

        self.pause_if_local(8)
        
        # Confirms the page navigated to Car Selection and the track is Monza
        body_vehicles = self.wait.until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        self.assertIn("Top Choices", body_vehicles.text)
        self.assertIn("Monza - Italy", body_vehicles.text)

        # 3. Select a car to advance to the Dashboard
        link_carro = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'car-name') and text()='VW Fusca']/ancestor::a"))
        )
        link_carro.click()

        self.pause_if_local(8)
        
        # Confirms the dashboard loaded correctly
        body_dash = self.wait.until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        self.assertIn("Lap time on this track", body_dash.text)
        
        self.pause_if_local(8)
        
        # 4. Clicks the 'Vehicles' link in the top navigation bar to go back
        link_vehicles_nav = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//nav//a[contains(text(), 'Vehicles')]"))
        )
        link_vehicles_nav.click()

        self.pause_if_local(8)
        
        # 5. Confirms we successfully went back to the Car Selection page AND the track remained the same
        body_vehicles_back = self.wait.until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        self.assertIn("Top Choices", body_vehicles_back.text)
        self.assertIn("Monza - Italy", body_vehicles_back.text) # Track check assertion
        self.assertNotIn("Interlagos - Brazil", body_vehicles_back.text)
        