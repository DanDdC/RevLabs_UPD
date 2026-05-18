import os
import time
from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from django.contrib.auth.models import User
from .models import Track, Car, PartCategory, CarPart

class Teste_01_FluxoSimulador(LiveServerTestCase):
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        # Configurações do Chrome Headless para rodar em CI/CD e localmente sem abrir janela
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--window-size=1920,1080')
        
        # Ocultar logs do WebDriver
        os.environ['WDM_LOG_LEVEL'] = '0'
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        
        cls.browser = webdriver.Chrome(options=chrome_options)
        cls.browser.implicitly_wait(10)
        cls.wait = WebDriverWait(cls.browser, 10)

    @classmethod
    def tearDownClass(cls):
        cls.browser.quit()
        super().tearDownClass()

    def setUp(self):
        """Popula o banco de dados de teste com dados mínimos necessários."""
        
        self.user = User.objects.create_user(username="tester", password="RevLabsTest123")

        # 1. Pistas
        self.track1 = Track.objects.create(
            slug_id="interlagos",
            name="Interlagos - Brazil",
            length_km=4.309,
            speed_multiplier=1.0,
            image_path="img/interlagos-icon.png",
            bg_image_path="img/bg/interlagos.jpg"
        )
        self.track2 = Track.objects.create(
            slug_id="monza",
            name="Monza - Italy",
            length_km=5.793,
            speed_multiplier=1.2,
            image_path="img/monza-icon.png",
            bg_image_path="img/bg/monza.jpg"
        )
        
        # 2. Carros
        self.car1 = Car.objects.create(
            slug_id="vw-fusca",
            name="VW Fusca",
            base_avg_speed_kmh=110.0,
            power_hp=50.0,
            weight_kg=800.0,
            image_path="img/fusca.png"
        )
        self.car2 = Car.objects.create(
            slug_id="porsche-911",
            name="Porsche 911",
            base_avg_speed_kmh=260.0,
            power_hp=450.0,
            weight_kg=1450.0,
            image_path="img/porsche.png"
        )
        
        # 3. Categorias e Peças
        self.cat_engine = PartCategory.objects.create(name="Engine", main_category="engine")
        self.cat_tyres = PartCategory.objects.create(name="Tyres", main_category="tyres")
        
        self.part_turbo = CarPart.objects.create(
            category=self.cat_engine,
            name="Twin-Scroll Turbo Kit",
            added_hp=120.0,
            added_weight_kg=15.0,
            image_path="img/turbo.png"
        )
        
        self.tyres = []

        tyre_data = [
            ("Touring Tyres", 0.0, 0.0, "img/mods/touringtyres.png"),
            ("Performance Tyres", 0.0, -1.0, "img/mods/perftyres.png"),
            ("High-Performance Tyres", 0.0, -2.0, "img/mods/highperftyres.png"),
            ("Semi-Slick Track Tyres", 0.0, -4.0, "img/mods/tracktyres.png"),
            ("Racing Slicks", 0.0, -6.0, "img/mods/racingslicks.png"),
        ]

        for name, hp, weight, image in tyre_data:
            self.tyres.append(
                CarPart.objects.create(
                    category=self.cat_tyres,
                    name=name,
                    added_hp=hp,
                    added_weight_kg=weight,
                    image_path=image
                )
            )

    def login_user(self):
        self.browser.get(self.live_server_url + '/login/')
        username = self.wait.until(EC.presence_of_element_located((By.NAME, "username")))
        password = self.browser.find_element(By.NAME, "password")
        username.clear()
        username.send_keys("tester")
        password.clear()
        password.send_keys("RevLabsTest123")
        self.browser.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        self.wait.until(lambda browser: '/circuits/' in browser.current_url)

    def test_01_deve_carregar_selecao_de_pistas(self):
        """Teste 01: Visualização da página de seleção de pistas."""
        print("Teste 01: Visualização da página de seleção de pistas.")
        self.login_user()
        
        body = self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        self.assertIn("SELECT CIRCUIT", body.text)
        self.assertIn("Choose your track", body.text)
        self.assertIn("INTERLAGOS", body.text)

    def test_02_deve_navegar_para_selecao_de_carros(self):
        """Teste 02: Navegação da seleção de pistas para seleção de carros."""
        print("Teste 02: Navegação da seleção de pistas para seleção de carros.")
        self.login_user()
        
        link_interlagos = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, 'track=interlagos')]"))
        )
        link_interlagos.click()
        
        self.assertIn("vehicles", self.browser.current_url)
        self.assertIn("track=interlagos", self.browser.current_url)
        
        body = self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        self.assertIn("SELECT VEHICLE", body.text)

    def test_03_deve_navegar_para_dashboard_e_ver_tempo(self):
        """Teste 03: Navegação para o dashboard e visualização do tempo de volta."""
        print("Teste 03: Navegação para o dashboard e visualização do tempo de volta.")
        self.login_user()
        self.browser.get(self.live_server_url + '/vehicles/?track=interlagos')
        
        link_carro = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, 'car=vw-fusca')]"))
        )
        link_carro.click()
        
        self.assertIn("dashboard", self.browser.current_url)
        
        body = self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        self.assertIn("INTERLAGOS", body.text)
        self.assertIn("VW FUSCA", body.text)
        
        tempo_display = self.wait.until(EC.presence_of_element_located((By.ID, "lap-time-display")))
        self.assertNotEqual(tempo_display.text, "--:--.---")
        self.assertTrue(":" in tempo_display.text)

    def test_04_deve_interagir_com_menu_de_mods(self):
        """Teste 04: Interação com os MODs e cálculo de tempo no dashboard."""
        print("Teste 04: Interação com os MODs e cálculo de tempo no dashboard.")
        self.login_user()
        self.browser.get(self.live_server_url + '/dashboard/?track=interlagos&car=vw-fusca')
        
        tempo_inicial = self.wait.until(EC.presence_of_element_located((By.ID, "lap-time-display"))).text
        
        add_mod_btn = self.wait.until(
            EC.element_to_be_clickable((By.ID, "add-mod-btn"))
        )
        add_mod_btn.click()
        
        aba_engine = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//li[@data-target-main='engine']"))
        )
        aba_engine.click()
        
        sub_aba_engine = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//li[@data-target='engine']"))
        )
        sub_aba_engine.click()
        
        part_turbo = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[@data-name='Twin-Scroll Turbo Kit']"))
        )
        part_turbo.click()
        
        time.sleep(1)
        
        tempo_final = self.wait.until(EC.presence_of_element_located((By.ID, "lap-time-display"))).text
        
        self.assertNotEqual(tempo_inicial, tempo_final)
        
        lista_mods = self.browser.find_element(By.ID, "installed-mods-list")
        self.assertIn("TWIN-SCROLL TURBO KIT", lista_mods.text)

    def test_05_deve_voltar_para_veiculos_e_manter_pista(self):
        """Teste 05: Voltar do dashboard para a tela de veículos e verificar se a pista permanece a mesma."""
        print("Teste 05: Voltar do dashboard para a tela de veículos e verificar se a pista permanece a mesma.")
        self.login_user()
        
        link_monza = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, 'track=monza')]"))
        )
        link_monza.click()
        
        link_carro = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, 'car=vw-fusca')]"))
        )
        link_carro.click()
        
        link_voltar = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'CHANGE VEHICLE')]"))
        )
        link_voltar.click()
        
        # CORREÇÃO: Procurar por "vehicles" em vez de "car_selection"
        self.assertIn("vehicles", self.browser.current_url)
        self.assertIn("track=monza", self.browser.current_url)