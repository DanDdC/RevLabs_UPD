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
        if os.environ.get('GITHUB_ACTIONS'):
            chrome_options.add_argument("--headless")
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
            image_path="img/vw-fusca.png"
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

    def pause_if_local(self, seconds=8):
        if not os.environ.get('GITHUB_ACTIONS'):
            time.sleep(seconds)

    def login_user(self):
        self.browser.get(self.live_server_url + '/login/')
        self.pause_if_local(4)
        username = self.wait.until(EC.presence_of_element_located((By.NAME, "username")))
        password = self.browser.find_element(By.NAME, "password")
        username.clear()
        username.send_keys("tester")
        password.clear()
        password.send_keys("RevLabsTest123")
        self.pause_if_local(5)
        self.browser.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        self.wait.until(lambda browser: '/circuits/' in browser.current_url)

    def test_01_fluxo_completo_selecao_ate_dashboard_com_mods(self):
        """Teste Integrado (1 ao 4 + remoção): Navega de pistas, para veículos, dashboard, instala e remove um MOD."""
        print("Teste Integrado: Pistas -> Veículos -> Dashboard -> Instalação/Remoção de MOD.")
        
        # Faz o login inicial (Substitui os logins redundantes)
        self.login_user()
        
        # --- PARTE 1: Seleção de Pistas ---
        body = self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        self.pause_if_local(8)
        self.assertIn("SELECT CIRCUIT", body.text)
        self.assertIn("Choose your track", body.text)
        self.assertIn("INTERLAGOS", body.text)

        # --- PARTE 2: Navegar para Seleção de Veículos ---
        link_interlagos = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, 'track=interlagos')]"))
        )
        self.pause_if_local(4)
        link_interlagos.click()
        
        # Espera a URL mudar para veículos de forma fluida
        self.wait.until(lambda browser: 'vehicles' in browser.current_url)
        self.assertIn("vehicles", self.browser.current_url)
        self.assertIn("track=interlagos", self.browser.current_url)
        
        body = self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        self.assertIn("SELECT VEHICLE", body.text)

        # --- PARTE 3: Escolher Carro, Navegar para Dashboard e Ver Tempo ---
        link_carro = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, 'car=vw-fusca')]"))
        )
        self.pause_if_local(4)
        link_carro.click()

        # Espera a URL mudar para o dashboard
        self.wait.until(lambda browser: 'dashboard' in browser.current_url)
        self.assertIn("dashboard", self.browser.current_url)
        
        body = self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        self.assertIn("INTERLAGOS", body.text)
        self.assertIn("VW FUSCA", body.text)
        
        # Captura e valida o tempo inicial
        tempo_display = self.wait.until(EC.presence_of_element_located((By.ID, "lap-time-display")))
        tempo_inicial = tempo_display.text
        self.assertNotEqual(tempo_inicial, "--:--.---")
        self.assertTrue(":" in tempo_inicial)
        self.pause_if_local(4)

        # --- PARTE 4: Interagir com Menu de MODs ---
        add_mod_btn = self.wait.until(
            EC.element_to_be_clickable((By.ID, "add-mod-btn"))
        )
        add_mod_btn.click()

        self.pause_if_local(4)
        
        aba_engine = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//li[@data-target-main='engine']"))
        )
        aba_engine.click()

        self.pause_if_local(4)
        
        sub_aba_engine = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//li[@data-target='engine']"))
        )
        sub_aba_engine.click()

        self.pause_if_local(4)
        
        part_turbo = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[@data-name='Twin-Scroll Turbo Kit']"))
        )
        part_turbo.click()

        self.pause_if_local(4)
        time.sleep(1) # Aguarda o cálculo de tempo ser renderizado
        
        # --- VERIFICAÇÃO FINAL ---
        tempo_final = self.wait.until(EC.presence_of_element_located((By.ID, "lap-time-display"))).text
        
        # Garante que o tempo mudou após o mod
        self.assertNotEqual(tempo_inicial, tempo_final)
        
        # Garante que o MOD apareceu na lista de instalados
        lista_mods = self.browser.find_element(By.ID, "installed-mods-list")
        self.assertIn("TWIN-SCROLL TURBO KIT", lista_mods.text)

        # --- PARTE 5: Remoção do MOD (Undo) ---
        self.pause_if_local(4)
        
        # Encontra o botão de remover dentro da lista de mods instalados
        # Dica: Substitua '.remove-btn' pela classe ou tag exata que você usa no seu HTML para excluir o mod
        btn_remover = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(@onclick, 'Twin-Scroll Turbo Kit')]")) 
        )
        btn_remover.click()

        self.pause_if_local(4)
        time.sleep(1) # Aguarda o recálculo de tempo após remoção

        # Captura o tempo após remover a peça
        tempo_apos_remocao = self.wait.until(EC.presence_of_element_located((By.ID, "lap-time-display"))).text
        
        # Valida se o tempo voltou a ser exatamente igual ao inicial
        self.assertEqual(tempo_inicial, tempo_apos_remocao)
        
        # Valida se a peça sumiu da interface
        lista_mods_atualizada = self.browser.find_element(By.ID, "installed-mods-list")
        self.assertNotIn("TWIN-SCROLL TURBO KIT", lista_mods_atualizada.text)

    def test_05_deve_voltar_para_veiculos_e_manter_pista(self):
        """Teste 05: Voltar do dashboard para a tela de veículos e verificar se a pista permanece a mesma."""
        print("Teste 05: Voltar do dashboard para a tela de veículos e verificar se a pista permanece a mesma.")
        self.login_user()

        self.pause_if_local(4)
        
        link_monza = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, 'track=monza')]"))
        )
        link_monza.click()

        self.pause_if_local(4)
        
        link_carro = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, 'car=vw-fusca')]"))
        )
        link_carro.click()

        self.pause_if_local(4)
        
        link_voltar = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'CHANGE VEHICLE')]"))
        )
        link_voltar.click()

        self.pause_if_local(4)
        
        # CORREÇÃO: Procurar por "vehicles" em vez de "car_selection"
        self.assertIn("vehicles", self.browser.current_url)
        self.assertIn("track=monza", self.browser.current_url)

    def test_06_nao_deve_acessar_dashboard_sem_login(self):
        """Tenta acessar uma rota protegida e deve ser redirecionado para o login."""
        print("Teste 06: Bloqueio de rota protegida para usuário anônimo.")
        self.browser.get(self.live_server_url + '/dashboard/?track=interlagos&car=vw-fusca')

        self.pause_if_local(4)
        
        # O Selenium deve observar que a URL mudou para /login/
        self.wait.until(lambda browser: '/login/' in browser.current_url)
        self.assertIn("login", self.browser.current_url.lower())