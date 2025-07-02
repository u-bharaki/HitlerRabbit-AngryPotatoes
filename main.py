import pygame
import math
import random
import json
import os
from enum import Enum
import time

# Pygame'i başlat
pygame.init()
pygame.mixer.init()

# Sabitler
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60

# Renkler
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)  
LIGHT_GRAY = (192, 192, 192)
ORANGE = (255, 165, 0)
BROWN = (139, 69, 19)
DARK_GREEN = (0, 100, 0)
LIGHT_GREEN = (144, 238, 144)

class GameState(Enum):
    MENU = 1
    GAME = 2
    PAUSED = 3
    GAME_OVER = 4
    LOAD_GAME = 5

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Hitler Bıyıklı Tavşan Shooter")
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = GameState.MENU
        
        # Ses ayarları
        self.sound_enabled = True
        self.music_enabled = True
        
        # Font'lar
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)
        
        # Oyun değişkenleri
        self.reset_game()
        
        # Sesler (placeholder - gerçek ses dosyaları eklenmeli)
        self.sounds = {}
        try:
            # Ses dosyalarını yükle (yoksa sessiz çalışır)
            self.load_sounds()
        except:
            print("Ses dosyaları yüklenemedi, oyun sessiz çalışacak")
        
        # Müzik
        self.start_music()
        
        # Kayıt dosyası
        self.save_dir = "saves"
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
    
    def load_sounds(self):
        # Gerçek ses dosyaları olsaydı böyle yüklenirdi
        # self.sounds = {
        #     'shoot': pygame.mixer.Sound('shoot.wav'),
        #     'hit': pygame.mixer.Sound('hit.wav'),
        #     'kill': pygame.mixer.Sound('kill.wav'),
        #     'levelup': pygame.mixer.Sound('levelup.wav'),
        #     'upgrade': pygame.mixer.Sound('upgrade.wav'),
        #     'damage': pygame.mixer.Sound('damage.wav')
        # }
        pass
    
    def play_sound(self, sound_name):
        if self.sound_enabled and sound_name in self.sounds:
            self.sounds[sound_name].play()
    
    def start_music(self):
        if self.music_enabled:
            try:
                # pygame.mixer.music.load('background_music.mp3')
                # pygame.mixer.music.play(-1)  # Sonsuz döngü
                pass
            except:
                pass
    
    def reset_game(self):
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.carrots = []
        self.potatoes = []
        self.dead_potatoes = []
        self.game_time = 0
        self.killed_potatoes = 0
        self.level = 1
        self.total_power = 1.0
        self.potato_spawn_timer = 0
        self.potato_spawn_delay = 120  # 2 saniye (60 FPS'de)
        
        # Geliştirmeler
        self.upgrades = {
            'speed': {'level': 0, 'cost': 5, 'multiplier': 1.3},
            'power': {'level': 0, 'cost': 8, 'multiplier': 1.3},
            'count': {'level': 0, 'cost': 15, 'multiplier': 2.0},
            'size': {'level': 0, 'cost': 3, 'multiplier': 1.0}
        }
        
        self.paused = False
        self.pause_menu_buttons = []
        self.upgrade_buttons = []
        self.create_upgrade_buttons()
    
    def create_upgrade_buttons(self):
        self.upgrade_buttons = [
            Button(SCREEN_WIDTH - 250, 50, 100, 30, f"Hız: {self.upgrades['speed']['cost']}", 'speed'),
            Button(SCREEN_WIDTH - 250, 90, 100, 30, f"Güç: {self.upgrades['power']['cost']}", 'power'),
            Button(SCREEN_WIDTH - 250, 130, 100, 30, f"Sayı: {self.upgrades['count']['cost']}", 'count'),
            Button(SCREEN_WIDTH - 250, 170, 100, 30, f"Boyut: {self.upgrades['size']['cost']}", 'size')
        ]
    
    def update_upgrade_buttons(self):
        self.upgrade_buttons[0].text = f"Hız: {self.upgrades['speed']['cost']}"
        self.upgrade_buttons[1].text = f"Güç: {self.upgrades['power']['cost']}"
        self.upgrade_buttons[2].text = f"Sayı: {self.upgrades['count']['cost']}"
        self.upgrade_buttons[3].text = f"Boyut: {self.upgrades['size']['cost']}"
    
    def get_level_requirement(self, level):
        return int(4 * (1.3 ** (level - 1)))
    
    def handle_upgrade(self, upgrade_type):
        cost = self.upgrades[upgrade_type]['cost']
        if self.killed_potatoes >= cost:
            self.killed_potatoes -= cost
            self.upgrades[upgrade_type]['level'] += 1
            
            # Toplam gücü güncelle (boyut hariç)
            if upgrade_type != 'size':
                self.total_power *= self.upgrades[upgrade_type]['multiplier']
            
            # Maliyeti artır (exponansiyel)
            self.upgrades[upgrade_type]['cost'] = int(cost * 1.8)
            
            self.update_upgrade_buttons()
            self.play_sound('upgrade')
    
    def spawn_potato(self, max_health: int = 5):
        # Ekranın kenarlarından patates spawn et
        side = random.randint(0, 3)
        if side == 0:  # Üst
            x, y = random.randint(0, SCREEN_WIDTH), -30
        elif side == 1:  # Sağ
            x, y = SCREEN_WIDTH + 30, random.randint(0, SCREEN_HEIGHT)
        elif side == 2:  # Alt
            x, y = random.randint(0, SCREEN_WIDTH), SCREEN_HEIGHT + 30
        else:  # Sol
            x, y = -30, random.randint(0, SCREEN_HEIGHT)
        
        # Seviye arttıkça patates hızı artar
        speed_multiplier = 1 + (self.level - 1) * 0.2
        self.potatoes.append(Potato(x, y, speed_multiplier, max_health))
    
    def update_game(self):
        if self.paused:
            return
        
        self.game_time += 1/60  # 60 FPS varsayımı
        
        # Seviye kontrolü
        required_kills = self.get_level_requirement(self.level)
        if self.killed_potatoes >= required_kills:
            self.level += 1
            self.play_sound('levelup')
        
        # Patates spawn
        self.potato_spawn_timer += 1
        spawn_delay = max(5, self.potato_spawn_delay - self.level * 10)  # Seviye arttıkça daha hızlı spawn
        if self.potato_spawn_timer >= spawn_delay:
            self.spawn_potato(max(5, self.level / 2))
            self.potato_spawn_timer = 0
        
        # Player güncelle
        self.player.update()
        
        # Havuçları güncelle
        for carrot in self.carrots[:]:
            carrot.update()
            if carrot.x < -50 or carrot.x > SCREEN_WIDTH + 50 or carrot.y < -50 or carrot.y > SCREEN_HEIGHT + 50:
                self.carrots.remove(carrot)
        
        # Patatesleri güncelle
        for potato in self.potatoes[:]:
            potato.update(self.player.x, self.player.y)
            
            # Oyuncu ile çarpışma kontrolü
            if potato.collides_with(self.player):
                self.player.take_damage(1)
                self.potatoes.remove(potato)
                self.play_sound('damage')
                if self.player.health <= 0:
                    self.state = GameState.GAME_OVER
        
        # Havuç-patates çarpışma kontrolü
        for carrot in self.carrots[:]:
            for potato in self.potatoes[:]:
                if carrot.collides_with(potato):
                    damage = carrot.damage
                    potato.take_damage(damage)
                    
                    if damage >= potato.health + damage:  # Havuç yok olmadan devam eder
                        pass
                    else:  # Havuç yok olur
                        if carrot in self.carrots:
                            self.carrots.remove(carrot)
                    
                    self.play_sound('hit')
                    
                    if potato.health <= 0:
                        self.potatoes.remove(potato)
                        self.dead_potatoes.append(DeadPotato(potato.x, potato.y))
                        self.killed_potatoes += 1
                        self.play_sound('kill')
                    break
        
        # Ölü patatesleri güncelle
        for dead_potato in self.dead_potatoes[:]:
            dead_potato.update()
            if dead_potato.timer <= 0:
                self.dead_potatoes.remove(dead_potato)
    
    def handle_click(self, pos):
        if self.state == GameState.GAME and not self.paused:
            # Upgrade butonları
            for button in self.upgrade_buttons:
                if button.rect.collidepoint(pos):
                    self.handle_upgrade(button.action)
            # Havuç fırlat
            count = 1 + self.upgrades['count']['level']
            for i in range(count):
                angle_offset = (i - count//2) * 0.2 if count > 1 else 0
                self.shoot_carrot(pos, angle_offset)
        elif self.state == GameState.PAUSED:
            # Pause menü butonları
            for button in self.pause_menu_buttons:
                if button.rect.collidepoint(pos):
                    if button.action == 'resume':
                        self.paused = False
                        self.state = GameState.GAME
                    elif button.action == 'sound':
                        self.sound_enabled = not self.sound_enabled
                    elif button.action == 'music':
                        self.music_enabled = not self.music_enabled
                        if self.music_enabled:
                            self.start_music()
                        else:
                            pygame.mixer.music.stop()
                    elif button.action == 'exit':
                        self.state = GameState.MENU
        elif self.state == GameState.GAME:
            # Upgrade butonları
            for button in self.upgrade_buttons:
                if button.rect.collidepoint(pos):
                    self.handle_upgrade(button.action)
    
    def shoot_carrot(self, target_pos, angle_offset=0):
        # Oyuncudan hedefe açı hesapla
        dx = target_pos[0] - self.player.x
        dy = target_pos[1] - self.player.y
        angle = math.atan2(dy, dx) + angle_offset
        
        # Geliştirmelere göre havuç özellikleri
        speed = 8 * (1 + self.upgrades['speed']['level'] * 0.3)
        damage = 1 + self.upgrades['power']['level']
        size = 5 + self.upgrades['size']['level'] * 2
        
        carrot = Carrot(self.player.x, self.player.y, angle, speed, damage, size)
        self.carrots.append(carrot)
        self.play_sound('shoot')
    
    def draw_background(self):
        # Çimen arkaplanı
        self.screen.fill(LIGHT_GREEN)
        
        # Ağaç ve çalılar (basit çizim)
        for i in range(0, SCREEN_WIDTH, 100):
            for j in range(0, SCREEN_HEIGHT, 100):
                if (i < 200 or i > SCREEN_WIDTH - 200 or 
                    j < 150 or j > SCREEN_HEIGHT - 150):
                    # Ağaç
                    pygame.draw.circle(self.screen, DARK_GREEN, (i + 50, j + 50), 20)
                    pygame.draw.rect(self.screen, BROWN, (i + 45, j + 60, 10, 20))
    
    def draw_ui(self):
        # Can barı (alt)
        health_bar_width = 300
        health_bar_height = 20
        health_bar_x = (SCREEN_WIDTH - health_bar_width) // 2
        health_bar_y = SCREEN_HEIGHT - 40
        
        # Can barı arkaplanı
        pygame.draw.rect(self.screen, GRAY, 
                        (health_bar_x, health_bar_y, health_bar_width, health_bar_height))
        # Can barı
        health_ratio = self.player.health / self.player.max_health
        pygame.draw.rect(self.screen, RED, 
                        (health_bar_x, health_bar_y, health_bar_width * health_ratio, health_bar_height))
        
        # Öldürülen patates sayısı (sol üst)
        kills_text = self.font_medium.render(f"🥕 {self.killed_potatoes}", True, BLACK)
        pygame.draw.ellipse(self.screen, WHITE, (10, 10, 120, 40))
        pygame.draw.ellipse(self.screen, BLACK, (10, 10, 120, 40), 2)
        self.screen.blit(kills_text, (20, 20))
        
        # Sağ üst panel
        
        panel_x = SCREEN_WIDTH - 300
        panel_y = 10
        panel_width = 290
        panel_height = 250
        
        s = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        s.fill((255, 255, 255, 100))
        self.screen.blit(s, (panel_x, panel_y))
        # pygame.draw.rect(self.screen, WHITE, (panel_x, panel_y, panel_width, panel_height))
        pygame.draw.rect(self.screen, BLACK, (panel_x, panel_y, panel_width, panel_height), 2)
        
        # Upgrade butonları
        for button in self.upgrade_buttons:
            color = GREEN if self.killed_potatoes >= self.upgrades[button.action]['cost'] else GRAY
            pygame.draw.rect(self.screen, color, button.rect)
            pygame.draw.rect(self.screen, BLACK, button.rect, 2)
            text_surface = self.font_small.render(button.text, True, BLACK)
            text_rect = text_surface.get_rect(center=button.rect.center)
            self.screen.blit(text_surface, text_rect)
        
        # Oyun bilgileri (sağ üst)
        info_x = panel_x + 170
        time_text = self.font_small.render(f"Süre: {int(self.game_time)}s", True, BLACK)
        level_text = self.font_small.render(f"Seviye: {self.level}", True, BLACK)
        power_text = self.font_small.render(f"Güç: {self.total_power:.1f}", True, BLACK)
        
        self.screen.blit(time_text, (info_x, 50))
        self.screen.blit(level_text, (info_x, 75))
        self.screen.blit(power_text, (info_x, 100))
    
    def draw_menu(self):
        self.screen.fill(LIGHT_GREEN)
        
        # Başlık
        title = self.font_large.render("Hitler Bıyıklı Tavşan Shooter", True, BLACK)
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, 200))
        self.screen.blit(title, title_rect)
        
        # Menü butonları
        buttons = [
            Button(SCREEN_WIDTH//2 - 75, 300, 150, 50, "Start", 'start'),
            Button(SCREEN_WIDTH//2 - 75, 370, 150, 50, "Load", 'load'),
            Button(SCREEN_WIDTH//2 - 75, 440, 150, 50, "Exit", 'exit')
        ]
        
        for button in buttons:
            pygame.draw.rect(self.screen, WHITE, button.rect)
            pygame.draw.rect(self.screen, BLACK, button.rect, 2)
            text_surface = self.font_medium.render(button.text, True, BLACK)
            text_rect = text_surface.get_rect(center=button.rect.center)
            self.screen.blit(text_surface, text_rect)
            
            # Buton tıklama kontrolü
            mouse_pos = pygame.mouse.get_pos()
            if button.rect.collidepoint(mouse_pos):
                if pygame.mouse.get_pressed()[0]:
                    if button.action == 'start':
                        self.reset_game()
                        self.state = GameState.GAME
                    elif button.action == 'load':
                        self.state = GameState.LOAD_GAME
                    elif button.action == 'exit':
                        self.running = False
    
    def draw_pause_menu(self):
        # Saydam overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Pause menü paneli
        panel_width, panel_height = 300, 250
        panel_x = (SCREEN_WIDTH - panel_width) // 2
        panel_y = (SCREEN_HEIGHT - panel_height) // 2
        
        pygame.draw.rect(self.screen, WHITE, (panel_x, panel_y, panel_width, panel_height))
        pygame.draw.rect(self.screen, BLACK, (panel_x, panel_y, panel_width, panel_height), 3)
        
        # Pause başlığı
        pause_text = self.font_large.render("PAUSE", True, BLACK)
        pause_rect = pause_text.get_rect(center=(SCREEN_WIDTH//2, panel_y + 40))
        self.screen.blit(pause_text, pause_rect)
        
        # Pause menü butonları
        self.pause_menu_buttons = [
            Button(panel_x + 50, panel_y + 80, 200, 30, "Devam", 'resume'),
            Button(panel_x + 50, panel_y + 120, 200, 30, f"Ses: {'Açık' if self.sound_enabled else 'Kapalı'}", 'sound'),
            Button(panel_x + 50, panel_y + 160, 200, 30, f"Müzik: {'Açık' if self.music_enabled else 'Kapalı'}", 'music'),
            Button(panel_x + 50, panel_y + 200, 200, 30, "Çıkış", 'exit')
        ]
        
        for button in self.pause_menu_buttons:
            pygame.draw.rect(self.screen, WHITE, button.rect)
            pygame.draw.rect(self.screen, BLACK, button.rect, 2)
            text_surface = self.font_small.render(button.text, True, BLACK)
            text_rect = text_surface.get_rect(center=button.rect.center)
            self.screen.blit(text_surface, text_rect)
    
    def draw_game_over(self):
        # Saydam overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Game over paneli
        panel_width, panel_height = 400, 350
        panel_x = (SCREEN_WIDTH - panel_width) // 2
        panel_y = (SCREEN_HEIGHT - panel_height) // 2
        
        pygame.draw.rect(self.screen, WHITE, (panel_x, panel_y, panel_width, panel_height))
        pygame.draw.rect(self.screen, BLACK, (panel_x, panel_y, panel_width, panel_height), 3)
        
        # Game Over başlığı
        title = self.font_large.render("GAME OVER", True, RED)
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, panel_y + 40))
        self.screen.blit(title, title_rect)
        
        # İstatistikler
        stats = [
            f"Seviye: {self.level}",
            f"Toplam Güç: {self.total_power:.1f}",
            f"Öldürülen Patates: {self.killed_potatoes}",
            f"Süre: {int(self.game_time)}s",
            f"Hız Geliştirmesi: {self.upgrades['speed']['level']}",
            f"Güç Geliştirmesi: {self.upgrades['power']['level']}",
            f"Sayı Geliştirmesi: {self.upgrades['count']['level']}",
            f"Boyut Geliştirmesi: {self.upgrades['size']['level']}"
        ]
        
        y_offset = 80
        for stat in stats:
            stat_text = self.font_small.render(stat, True, BLACK)
            self.screen.blit(stat_text, (panel_x + 20, panel_y + y_offset))
            y_offset += 25
        
        # Butonlar
        restart_button = Button(panel_x + 50, panel_y + 280, 120, 40, "Tekrar Oyna", 'restart')
        exit_button = Button(panel_x + 230, panel_y + 280, 120, 40, "Çıkış", 'exit')
        
        for button in [restart_button, exit_button]:
            pygame.draw.rect(self.screen, WHITE, button.rect)
            pygame.draw.rect(self.screen, BLACK, button.rect, 2)
            text_surface = self.font_small.render(button.text, True, BLACK)
            text_rect = text_surface.get_rect(center=button.rect.center)
            self.screen.blit(text_surface, text_rect)
            
            # Buton tıklama kontrolü
            mouse_pos = pygame.mouse.get_pos()
            if button.rect.collidepoint(mouse_pos):
                if pygame.mouse.get_pressed()[0]:
                    if button.action == 'restart':
                        self.reset_game()
                        self.state = GameState.GAME
                    elif button.action == 'exit':
                        self.state = GameState.MENU
    
    def draw_load_menu(self):
        self.screen.fill(LIGHT_GREEN)
        
        # Başlık
        title = self.font_large.render("Kayıt Dosyaları", True, BLACK)
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, 100))
        self.screen.blit(title, title_rect)
        
        # Kayıt dosyalarını listele
        save_files = []
        if os.path.exists(self.save_dir):
            save_files = [f for f in os.listdir(self.save_dir) if f.endswith('.json')]
        
        y_offset = 200
        for i, save_file in enumerate(save_files[:5]):  # En fazla 5 kayıt göster
            button = Button(SCREEN_WIDTH//2 - 150, y_offset, 300, 40, save_file[:-5], f'load_{i}')
            pygame.draw.rect(self.screen, WHITE, button.rect)
            pygame.draw.rect(self.screen, BLACK, button.rect, 2)
            text_surface = self.font_medium.render(button.text, True, BLACK)
            text_rect = text_surface.get_rect(center=button.rect.center)
            self.screen.blit(text_surface, text_rect)
            
            # Buton tıklama kontrolü
            mouse_pos = pygame.mouse.get_pos()
            if button.rect.collidepoint(mouse_pos):
                if pygame.mouse.get_pressed()[0]:
                    self.load_game(save_file)
                    self.state = GameState.GAME
            
            y_offset += 60
        
        # Geri dön butonu
        back_button = Button(50, 50, 100, 40, "Geri", 'back')
        pygame.draw.rect(self.screen, WHITE, back_button.rect)
        pygame.draw.rect(self.screen, BLACK, back_button.rect, 2)
        text_surface = self.font_medium.render(back_button.text, True, BLACK)
        text_rect = text_surface.get_rect(center=back_button.rect.center)
        self.screen.blit(text_surface, text_rect)
        
        mouse_pos = pygame.mouse.get_pos()
        if back_button.rect.collidepoint(mouse_pos):
            if pygame.mouse.get_pressed()[0]:
                self.state = GameState.MENU
    
    def save_game(self):
        save_data = {
            'player_health': self.player.health,
            'game_time': self.game_time,
            'killed_potatoes': self.killed_potatoes,
            'level': self.level,
            'total_power': self.total_power,
            'upgrades': self.upgrades
        }
        
        timestamp = int(time.time())
        filename = f"save_{timestamp}.json"
        filepath = os.path.join(self.save_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(save_data, f)
    
    def load_game(self, filename):
        filepath = os.path.join(self.save_dir, filename)
        try:
            with open(filepath, 'r') as f:
                save_data = json.load(f)
            
            self.reset_game()
            self.player.health = save_data['player_health']
            self.game_time = save_data['game_time']
            self.killed_potatoes = save_data['killed_potatoes']
            self.level = save_data['level']
            self.total_power = save_data['total_power']
            self.upgrades = save_data['upgrades']
            self.update_upgrade_buttons()
        except Exception as e:
            print(f"Kayıt yüklenemedi: {e}")
    
    def draw_game_elements(self):
        # Arkaplanı çiz
        self.draw_background()
        
        # Ölü patatesleri çiz
        for dead_potato in self.dead_potatoes:
            dead_potato.draw(self.screen)
        
        # Oyuncuyu çiz
        self.player.draw(self.screen)
        
        # Mouse takip okunu çiz
        mouse_pos = pygame.mouse.get_pos()
        if not self.paused:
            self.player.draw_aim_arrow(self.screen, mouse_pos)
        
        # Havuçları çiz
        for carrot in self.carrots:
            carrot.draw(self.screen)
        
        # Patatesleri çiz
        for potato in self.potatoes:
            potato.draw(self.screen)
        
        # UI'ı çiz
        self.draw_ui()
    
    def run(self):
        while self.running:
            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.state == GameState.GAME:
                            self.paused = not self.paused
                            self.state = GameState.PAUSED if self.paused else GameState.GAME
                        elif self.state == GameState.PAUSED:
                            self.paused = False
                            self.state = GameState.GAME
                    elif event.key == pygame.K_s and pygame.key.get_pressed()[pygame.K_LCTRL]:
                        if self.state == GameState.GAME:
                            self.save_game()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Sol tık
                        self.handle_click(event.pos)
            
            # Update
            if self.state == GameState.GAME:
                self.update_game()
            
            # Draw
            if self.state == GameState.MENU:
                self.draw_menu()
            elif self.state == GameState.LOAD_GAME:
                self.draw_load_menu()
            elif self.state == GameState.PAUSED:
                self.draw_game_elements()
                self.draw_pause_menu()
            elif self.state == GameState.GAME_OVER:
                self.draw_game_elements()
                self.draw_game_over()
            else:  # GameState.GAME
                self.draw_game_elements()
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.max_health = 100
        self.health = self.max_health
        self.size = 25
    
    def update(self):
        pass
    
    def take_damage(self, damage):
        self.health -= damage
        if self.health < 0:
            self.health = 0
    
    def draw(self, screen):
        # Tavşan vücudu (büyük kafa)
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y - 5)), self.size)
        pygame.draw.circle(screen, BLACK, (int(self.x), int(self.y - 5)), self.size, 2)
        
        # Hitler bıyığı
        pygame.draw.rect(screen, BLACK, (self.x - 8, self.y - 3, 16, 4))
        
        # Gözler
        pygame.draw.circle(screen, BLACK, (int(self.x - 8), int(self.y - 10)), 3)
        pygame.draw.circle(screen, BLACK, (int(self.x + 8), int(self.y - 10)), 3)
        
        # Tavşan kulakları
        pygame.draw.ellipse(screen, WHITE, (self.x - 15, self.y - 35, 8, 20))
        pygame.draw.ellipse(screen, WHITE, (self.x + 7, self.y - 35, 8, 20))
        pygame.draw.ellipse(screen, BLACK, (self.x - 15, self.y - 35, 8, 20), 2)
        pygame.draw.ellipse(screen, BLACK, (self.x + 7, self.y - 35, 8, 20), 2)
        
        # Havuç kollar
        # Sol kol
        pygame.draw.polygon(screen, ORANGE, [
            (self.x - 25, self.y + 5),
            (self.x - 35, self.y - 5),
            (self.x - 32, self.y - 8),
            (self.x - 22, self.y + 2)
        ])
        # Sağ kol
        pygame.draw.polygon(screen, ORANGE, [
            (self.x + 25, self.y + 5),
            (self.x + 35, self.y - 5),
            (self.x + 32, self.y - 8),
            (self.x + 22, self.y + 2)
        ])
        
        # Vücut
        pygame.draw.ellipse(screen, WHITE, (self.x - 15, self.y + 10, 30, 25))
        pygame.draw.ellipse(screen, BLACK, (self.x - 15, self.y + 10, 30, 25), 2)
    
    def draw_aim_arrow(self, screen, mouse_pos):
        # Mouse'a doğru ok çiz
        dx = mouse_pos[0] - self.x
        dy = mouse_pos[1] - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance > 0:
            # Normalize et
            dx /= distance
            dy /= distance
            
            # Ok başlangıç noktası (oyuncunun kenarı)
            arrow_start_x = self.x + dx * (self.size + 10)
            arrow_start_y = self.y + dy * (self.size + 10)
            
            # Ok ucu
            arrow_end_x = arrow_start_x + dx * 30
            arrow_end_y = arrow_start_y + dy * 30
            
            # Ok çizgisi
            pygame.draw.line(screen, RED, 
                           (arrow_start_x, arrow_start_y), 
                           (arrow_end_x, arrow_end_y), 3)
            
            # Ok başı
            angle = math.atan2(dy, dx)
            arrow_head_size = 8
            
            # Ok başının noktaları
            head_point1_x = arrow_end_x - arrow_head_size * math.cos(angle - 0.5)
            head_point1_y = arrow_end_y - arrow_head_size * math.sin(angle - 0.5)
            
            head_point2_x = arrow_end_x - arrow_head_size * math.cos(angle + 0.5)
            head_point2_y = arrow_end_y - arrow_head_size * math.sin(angle + 0.5)
            
            pygame.draw.polygon(screen, RED, [
                (arrow_end_x, arrow_end_y),
                (head_point1_x, head_point1_y),
                (head_point2_x, head_point2_y)
            ])
    
    def collides_with(self, other):
        dx = self.x - other.x
        dy = self.y - other.y
        distance = math.sqrt(dx*dx + dy*dy)
        return distance < (self.size + other.size)

class Carrot:
    def __init__(self, x, y, angle, speed, damage, size):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = speed
        self.damage = damage
        self.size = size
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
    
    def draw(self, screen):
        # Havuç şekli çiz
        points = []
        for i in range(6):
            angle = i * math.pi / 3 + self.angle
            if i % 2 == 0:
                radius = self.size
            else:
                radius = self.size * 0.7
            
            px = self.x + math.cos(angle) * radius
            py = self.y + math.sin(angle) * radius
            points.append((px, py))
        
        pygame.draw.polygon(screen, ORANGE, points)
        pygame.draw.polygon(screen, BLACK, points, 2)
        
        # Havuç yaprağı
        leaf_x = self.x - math.cos(self.angle) * self.size
        leaf_y = self.y - math.sin(self.angle) * self.size
        pygame.draw.circle(screen, GREEN, (int(leaf_x), int(leaf_y)), self.size // 3)
    
    def collides_with(self, other):
        dx = self.x - other.x
        dy = self.y - other.y
        distance = math.sqrt(dx*dx + dy*dy)
        return distance < (self.size + other.size)

class Potato:
    def __init__(self, x, y, speed_multiplier=1.0, max_health: int = 5):
        self.x = x
        self.y = y
        self.max_health = max_health
        self.health = self.max_health
        self.size = 20
        self.speed = 1.5 * speed_multiplier
        self.anger_level = random.uniform(0, math.pi * 2)  # Sinirli animasyon için
    
    def update(self, target_x, target_y):
        # Oyuncuya doğru hareket et
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance > 0:
            self.x += (dx / distance) * self.speed
            self.y += (dy / distance) * self.speed
        
        self.anger_level += 0.2  # Animasyon için
    
    def take_damage(self, damage):
        self.health -= damage
    
    def draw(self, screen):
        # Sinirli patates animasyonu
        shake_x = math.sin(self.anger_level) * 2
        shake_y = math.cos(self.anger_level * 1.3) * 2
        
        draw_x = int(self.x + shake_x)
        draw_y = int(self.y + shake_y)
        
        # Patates vücudu
        pygame.draw.ellipse(screen, (139, 69, 19), 
                          (draw_x - self.size, draw_y - self.size//2, 
                           self.size*2, self.size))
        pygame.draw.ellipse(screen, BLACK, 
                          (draw_x - self.size, draw_y - self.size//2, 
                           self.size*2, self.size), 2)
        
        # Sinirli gözler
        eye_color = RED if self.anger_level % (math.pi) < math.pi/2 else (255, 100, 100)
        pygame.draw.circle(screen, eye_color, (draw_x - 8, draw_y - 5), 4)
        pygame.draw.circle(screen, eye_color, (draw_x + 8, draw_y - 5), 4)
        
        # Kaşlar (sinirli)
        pygame.draw.line(screen, BLACK, (draw_x - 12, draw_y - 12), (draw_x - 4, draw_y - 8), 3)
        pygame.draw.line(screen, BLACK, (draw_x + 4, draw_y - 8), (draw_x + 12, draw_y - 12), 3)
        
        # Ağız (sinirli)
        pygame.draw.arc(screen, BLACK, (draw_x - 8, draw_y + 2, 16, 10), 0, math.pi, 3)
        
        # Can barı
        if self.health < self.max_health:
            bar_width = 30
            bar_height = 4
            bar_x = draw_x - bar_width // 2
            bar_y = draw_y - self.size - 10
            
            # Can barı arkaplanı
            pygame.draw.rect(screen, GRAY, (bar_x, bar_y, bar_width, bar_height))
            
            # Can barı
            health_ratio = self.health / self.max_health
            pygame.draw.rect(screen, RED, (bar_x, bar_y, bar_width * health_ratio, bar_height))
    
    def collides_with(self, other):
        dx = self.x - other.x
        dy = self.y - other.y
        distance = math.sqrt(dx*dx + dy*dy)
        return distance < (self.size + other.size)

class DeadPotato:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.timer = 180  # 3 saniye (60 FPS'de)
        self.size = 20
    
    def update(self):
        self.timer -= 1
    
    def draw(self, screen):
        # Ölü patates (solgun)
        alpha = max(0, min(255, self.timer * 2))  # Yavaşça kaybol
        
        # Geçici surface oluştur alpha için
        temp_surface = pygame.Surface((self.size * 2, self.size))
        temp_surface.set_alpha(alpha)
        temp_surface.fill((100, 50, 25))  # Solgun kahverengi
        
        screen.blit(temp_surface, (self.x - self.size, self.y - self.size//2))
        
        # X gözler
        if alpha > 100:
            pygame.draw.line(screen, BLACK, 
                           (self.x - 10, self.y - 8), (self.x - 6, self.y - 4), 2)
            pygame.draw.line(screen, BLACK, 
                           (self.x - 6, self.y - 8), (self.x - 10, self.y - 4), 2)
            pygame.draw.line(screen, BLACK, 
                           (self.x + 6, self.y - 8), (self.x + 10, self.y - 4), 2)
            pygame.draw.line(screen, BLACK, 
                           (self.x + 10, self.y - 8), (self.x + 6, self.y - 4), 2)

class Button:
    def __init__(self, x, y, width, height, text, action):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action

# Oyunu başlat
if __name__ == "__main__":
    game = Game()
    game.run()