import pygame
import math
import random
import time

# Pygame'i başlat
pygame.init()
pygame.mixer.init()

# Sabitler
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

# Renkler
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BROWN = (139, 69, 19)
ORANGE = (255, 165, 0)
GRAY = (128, 128, 128)
DARK_GREEN = (0, 100, 0)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Hitler Bıyıklı Tavşan Shooter")
        self.clock = pygame.time.Clock()
        
        # Oyun durumu
        self.running = True
        self.paused = False
        self.game_over = False
        self.sound_enabled = True
        self.music_enabled = True
        
        # Oyuncu
        self.player = {
            'x': SCREEN_WIDTH // 2,
            'y': SCREEN_HEIGHT // 2,
            'health': 1000,
            'max_health': 1000,
            'radius': 30
        }
        
        # Oyun istatistikleri
        self.killed_potatoes = 0
        self.level = 1
        self.level_up_requirement = 10
        self.game_time = 0
        self.start_time = time.time()
        
        # Geliştirmeler
        self.upgrades = {
            'speed': {'level': 0, 'cost': 5, 'multiplier': 1.3},
            'damage': {'level': 0, 'cost': 5, 'multiplier': 1.3},
            'size': {'level': 0, 'cost': 8, 'multiplier': 1.0},
            'multi': {'level': 0, 'cost': 15, 'multiplier': 2.0}
        }
        
        # Havuçlar ve patatesler
        self.carrots = []
        self.potatoes = []
        
        # Spawn zamanlaması
        self.last_potato_spawn = 0
        self.potato_spawn_rate = 2000  # millisaniye
        
        # Mouse pozisyonu
        self.mouse_pos = (0, 0)
        
        # Ses efektleri (placeholder)
        try:
            # Basit ses efektleri oluştur
            self.create_sound_effects()
            self.play_background_music()
        except:
            print("Ses sistemi başlatılamadı")
    
    def create_sound_effects(self):
        """Basit ses efektleri oluştur"""
        # Placeholder sesler - gerçek ses dosyaları yerine
        pass
    
    def play_background_music(self):
        """Arkaplan müziği çal"""
        if self.music_enabled:
            try:
                # Placeholder müzik
                pass
            except:
                pass
    
    def get_total_power(self):
        """Toplam gücü hesapla"""
        total_power = 1.0
        for upgrade_type, upgrade in self.upgrades.items():
            if upgrade_type != 'size':  # Size çarpan sağlamaz
                total_power *= (upgrade['multiplier'] ** upgrade['level'])
        return total_power
    
    def get_carrot_damage(self):
        """Havuç hasarını hesapla"""
        base_damage = 40
        damage_multiplier = self.upgrades['damage']['multiplier'] ** self.upgrades['damage']['level']
        return int(base_damage * damage_multiplier)
    
    def get_carrot_speed(self):
        """Havuç hızını hesapla"""
        base_speed = 300
        speed_multiplier = self.upgrades['speed']['multiplier'] ** self.upgrades['speed']['level']
        return base_speed * speed_multiplier
    
    def get_carrot_size(self):
        """Havuç boyutunu hesapla"""
        base_size = 8
        size_multiplier = 1.2 ** self.upgrades['size']['level']
        return int(base_size * size_multiplier)
    
    def get_carrot_count(self):
        """Fırlatılacak havuç sayısını hesapla"""
        return self.upgrades['multi']['level'] + 1
    
    def shoot_carrot(self, target_x, target_y):
        """Havuç fırlat"""
        if self.paused or self.game_over:
            return
            
        # Yön hesapla
        dx = target_x - self.player['x']
        dy = target_y - self.player['y']
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance > 0:
            dx /= distance
            dy /= distance
            
            carrot_count = self.get_carrot_count()
            speed = self.get_carrot_speed()
            
            # Çoklu havuç için açı hesapla
            if carrot_count == 1:
                angles = [0]
            else:
                spread = 0.3  # radyan
                angles = []
                for i in range(carrot_count):
                    angle_offset = (i - (carrot_count - 1) / 2) * spread / (carrot_count - 1)
                    angles.append(angle_offset)
            
            for angle_offset in angles:
                # Açıyı uygula
                cos_offset = math.cos(angle_offset)
                sin_offset = math.sin(angle_offset)
                
                new_dx = dx * cos_offset - dy * sin_offset
                new_dy = dx * sin_offset + dy * cos_offset
                
                carrot = {
                    'x': self.player['x'],
                    'y': self.player['y'],
                    'dx': new_dx * speed,
                    'dy': new_dy * speed,
                    'damage': self.get_carrot_damage(),
                    'size': self.get_carrot_size()
                }
                self.carrots.append(carrot)
    
    def spawn_potato(self):
        """Patates spawn et"""
        # Ekranın kenarından rastgele bir nokta seç
        side = random.choice(['top', 'bottom', 'left', 'right'])
        
        if side == 'top':
            x = random.randint(0, SCREEN_WIDTH)
            y = -50
        elif side == 'bottom':
            x = random.randint(0, SCREEN_WIDTH)
            y = SCREEN_HEIGHT + 50
        elif side == 'left':
            x = -50
            y = random.randint(0, SCREEN_HEIGHT)
        else:  # right
            x = SCREEN_WIDTH + 50
            y = random.randint(0, SCREEN_HEIGHT)
        
        # Patates seviyesine göre can hesapla
        potato_health = 200 + (self.level - 1) * 50
        
        potato = {
            'x': x,
            'y': y,
            'health': potato_health,
            'max_health': potato_health,
            'radius': 25,
            'speed': 50 + self.level * 10,
            'dead': False,
            'death_time': 0
        }
        self.potatoes.append(potato)
    
    def update_carrots(self, dt):
        """Havuçları güncelle"""
        for carrot in self.carrots[:]:
            carrot['x'] += carrot['dx'] * dt
            carrot['y'] += carrot['dy'] * dt
            
            # Ekran dışına çıkanları kaldır
            if (carrot['x'] < -100 or carrot['x'] > SCREEN_WIDTH + 100 or
                carrot['y'] < -100 or carrot['y'] > SCREEN_HEIGHT + 100):
                self.carrots.remove(carrot)
    
    def update_potatoes(self, dt):
        """Patatesleri güncelle"""
        current_time = pygame.time.get_ticks()
        
        for potato in self.potatoes[:]:
            if potato['dead']:
                # Ölü patates zamanı
                if current_time - potato['death_time'] > 2000:  # 2 saniye
                    self.potatoes.remove(potato)
                continue
            
            # Oyuncuya doğru hareket et
            dx = self.player['x'] - potato['x']
            dy = self.player['y'] - potato['y']
            distance = math.sqrt(dx**2 + dy**2)
            
            if distance > 0:
                dx /= distance
                dy /= distance
                potato['x'] += dx * potato['speed'] * dt
                potato['y'] += dy * potato['speed'] * dt
            
            # Oyuncuyla çarpışma kontrolü
            player_distance = math.sqrt((potato['x'] - self.player['x'])**2 + 
                                      (potato['y'] - self.player['y'])**2)
            if player_distance < potato['radius'] + self.player['radius']:
                self.player['health'] -= 100
                potato['dead'] = True
                potato['death_time'] = current_time
                
                if self.player['health'] <= 0:
                    self.game_over = True
    
    def check_collisions(self):
        """Çarpışmaları kontrol et"""
        current_time = pygame.time.get_ticks()
        
        for carrot in self.carrots[:]:
            for potato in self.potatoes[:]:
                if potato['dead']:
                    continue
                
                distance = math.sqrt((carrot['x'] - potato['x'])**2 + 
                                   (carrot['y'] - potato['y'])**2)
                
                if distance < carrot['size'] + potato['radius']:
                    # Hasar ver
                    potato['health'] -= carrot['damage']
                    
                    # Patates öldü mü?
                    if potato['health'] <= 0:
                        potato['dead'] = True
                        potato['death_time'] = current_time
                        self.killed_potatoes += 1
                        
                        # Level kontrolü
                        if self.killed_potatoes >= self.level_up_requirement:
                            self.level += 1
                            self.level_up_requirement = int(self.level_up_requirement * 1.5)
                    
                    # Havuç yok olacak mı?
                    if carrot['damage'] <= potato['max_health']:
                        self.carrots.remove(carrot)
                        break
    
    def buy_upgrade(self, upgrade_type):
        """Geliştirme satın al"""
        upgrade = self.upgrades[upgrade_type]
        if self.killed_potatoes >= upgrade['cost']:
            self.killed_potatoes -= upgrade['cost']
            upgrade['level'] += 1
            upgrade['cost'] = int(upgrade['cost'] * 1.5)
    
    def draw_player(self):
        """Oyuncuyu çiz"""
        # Tavşan gövdesi (büyük daire)
        pygame.draw.circle(self.screen, WHITE, 
                         (int(self.player['x']), int(self.player['y'])), 
                         self.player['radius'])
        pygame.draw.circle(self.screen, BLACK, 
                         (int(self.player['x']), int(self.player['y'])), 
                         self.player['radius'], 2)
        
        # Hitler bıyığı
        mustache_rect = pygame.Rect(self.player['x'] - 10, self.player['y'] - 5, 20, 8)
        pygame.draw.rect(self.screen, BLACK, mustache_rect)
        
        # Kulaklar
        pygame.draw.ellipse(self.screen, WHITE, 
                          (self.player['x'] - 35, self.player['y'] - 45, 15, 30))
        pygame.draw.ellipse(self.screen, WHITE, 
                          (self.player['x'] + 20, self.player['y'] - 45, 15, 30))
        
        # Havuç kollar
        pygame.draw.ellipse(self.screen, ORANGE, 
                          (self.player['x'] - 50, self.player['y'] - 10, 20, 8))
        pygame.draw.ellipse(self.screen, ORANGE, 
                          (self.player['x'] + 30, self.player['y'] - 10, 20, 8))
    
    def draw_arrow(self):
        """Mouse yönünü gösteren ok çiz"""
        if self.paused or self.game_over:
            return
            
        dx = self.mouse_pos[0] - self.player['x']
        dy = self.mouse_pos[1] - self.player['y']
        angle = math.atan2(dy, dx)
        
        # Ok pozisyonu
        arrow_distance = 50
        arrow_x = self.player['x'] + math.cos(angle) * arrow_distance
        arrow_y = self.player['y'] + math.sin(angle) * arrow_distance
        
        # Ok çiz
        arrow_length = 20
        arrow_end_x = arrow_x + math.cos(angle) * arrow_length
        arrow_end_y = arrow_y + math.sin(angle) * arrow_length
        
        pygame.draw.line(self.screen, RED, (arrow_x, arrow_y), 
                        (arrow_end_x, arrow_end_y), 3)
        
        # Ok başı
        arrow_head_length = 8
        arrow_head_angle = 0.5
        
        head1_x = arrow_end_x - math.cos(angle - arrow_head_angle) * arrow_head_length
        head1_y = arrow_end_y - math.sin(angle - arrow_head_angle) * arrow_head_length
        head2_x = arrow_end_x - math.cos(angle + arrow_head_angle) * arrow_head_length
        head2_y = arrow_end_y - math.sin(angle + arrow_head_angle) * arrow_head_length
        
        pygame.draw.line(self.screen, RED, (arrow_end_x, arrow_end_y), 
                        (head1_x, head1_y), 3)
        pygame.draw.line(self.screen, RED, (arrow_end_x, arrow_end_y), 
                        (head2_x, head2_y), 3)
    
    def draw_background(self):
        """Arkaplan çiz"""
        self.screen.fill(GREEN)
        
        # Çimen (orta alan)
        grass_rect = pygame.Rect(200, 150, SCREEN_WIDTH - 400, SCREEN_HEIGHT - 300)
        pygame.draw.rect(self.screen, DARK_GREEN, grass_rect)
        
        # Ağaçlar (placeholder)
        for i in range(15):
            tree_x = random.randint(0, SCREEN_WIDTH)
            tree_y = random.randint(0, SCREEN_HEIGHT)
            if (tree_x < 200 or tree_x > SCREEN_WIDTH - 200 or 
                tree_y < 150 or tree_y > SCREEN_HEIGHT - 150):
                pygame.draw.circle(self.screen, BROWN, (tree_x, tree_y), 15)
    
    def draw_carrots(self):
        """Havuçları çiz"""
        for carrot in self.carrots:
            pygame.draw.circle(self.screen, ORANGE, 
                             (int(carrot['x']), int(carrot['y'])), 
                             carrot['size'])
    
    def draw_potatoes(self):
        """Patatesleri çiz"""
        for potato in self.potatoes:
            if potato['dead']:
                # Ölü patates
                pygame.draw.circle(self.screen, GRAY, 
                                 (int(potato['x']), int(potato['y'])), 
                                 potato['radius'])
            else:
                # Canlı patates
                pygame.draw.circle(self.screen, BROWN, 
                                 (int(potato['x']), int(potato['y'])), 
                                 potato['radius'])
                
                # Sinirli yüz
                eye_size = 3
                pygame.draw.circle(self.screen, RED, 
                                 (int(potato['x'] - 8), int(potato['y'] - 8)), eye_size)
                pygame.draw.circle(self.screen, RED, 
                                 (int(potato['x'] + 8), int(potato['y'] - 8)), eye_size)
                
                # Can barı
                bar_width = 40
                bar_height = 6
                bar_x = potato['x'] - bar_width // 2
                bar_y = potato['y'] - potato['radius'] - 15
                
                # Arkaplan
                pygame.draw.rect(self.screen, RED, 
                               (bar_x, bar_y, bar_width, bar_height))
                
                # Can
                health_ratio = potato['health'] / potato['max_health']
                health_width = int(bar_width * health_ratio)
                pygame.draw.rect(self.screen, GREEN, 
                               (bar_x, bar_y, health_width, bar_height))
    
    def draw_ui(self):
        """Kullanıcı arayüzünü çiz"""
        font = pygame.font.Font(None, 36)
        small_font = pygame.font.Font(None, 24)
        
        # Can barı (alt)
        bar_width = 400
        bar_height = 30
        bar_x = (SCREEN_WIDTH - bar_width) // 2
        bar_y = SCREEN_HEIGHT - 50
        
        pygame.draw.rect(self.screen, GRAY, (bar_x, bar_y, bar_width, bar_height))
        health_ratio = max(0, self.player['health'] / self.player['max_health'])
        health_width = int(bar_width * health_ratio)
        pygame.draw.rect(self.screen, RED, (bar_x, bar_y, health_width, bar_height))
        
        # Öldürülen patates sayısı (sol üst)
        killed_text = font.render(f"Patates: {self.killed_potatoes}", True, BLACK)
        pygame.draw.circle(self.screen, WHITE, (100, 50), 60)
        pygame.draw.circle(self.screen, BLACK, (100, 50), 60, 2)
        text_rect = killed_text.get_rect(center=(100, 50))
        self.screen.blit(killed_text, text_rect)
        
        # Geliştirmeler (sağ üst)
        upgrade_y = 30
        upgrade_names = ['Hız', 'Güç', 'Boyut', 'Çoklu']
        upgrade_keys = ['speed', 'damage', 'size', 'multi']
        
        for i, (name, key) in enumerate(zip(upgrade_names, upgrade_keys)):
            upgrade = self.upgrades[key]
            x = SCREEN_WIDTH - 200
            y = upgrade_y + i * 60
            
            # Buton
            button_rect = pygame.Rect(x, y, 180, 50)
            color = GREEN if self.killed_potatoes >= upgrade['cost'] else GRAY
            pygame.draw.rect(self.screen, color, button_rect)
            pygame.draw.rect(self.screen, BLACK, button_rect, 2)
            
            # Metin
            text = f"{name} Lv{upgrade['level']}"
            cost_text = f"Maliyet: {upgrade['cost']}"
            
            name_surface = small_font.render(text, True, BLACK)
            cost_surface = small_font.render(cost_text, True, BLACK)
            
            self.screen.blit(name_surface, (x + 5, y + 5))
            self.screen.blit(cost_surface, (x + 5, y + 25))
        
        # Oyun bilgileri (sağ üst, en sağ)
        info_x = SCREEN_WIDTH - 150
        info_y = 30
        
        time_text = small_font.render(f"Süre: {int(self.game_time)}s", True, BLACK)
        level_text = small_font.render(f"Level: {self.level}", True, BLACK)
        power_text = small_font.render(f"Güç: {self.get_total_power():.1f}", True, BLACK)
        
        self.screen.blit(time_text, (info_x, info_y))
        self.screen.blit(level_text, (info_x, info_y + 25))
        self.screen.blit(power_text, (info_x, info_y + 50))
    
    def draw_pause_menu(self):
        """Duraklama menüsünü çiz"""
        # Yarı şeffaf arkaplan
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Menü
        menu_width = 400
        menu_height = 300
        menu_x = (SCREEN_WIDTH - menu_width) // 2
        menu_y = (SCREEN_HEIGHT - menu_height) // 2
        
        pygame.draw.rect(self.screen, WHITE, (menu_x, menu_y, menu_width, menu_height))
        pygame.draw.rect(self.screen, BLACK, (menu_x, menu_y, menu_width, menu_height), 3)
        
        font = pygame.font.Font(None, 48)
        
        # Butonlar
        button_width = 200
        button_height = 50
        button_x = menu_x + (menu_width - button_width) // 2
        
        buttons = [
            ("Devam", menu_y + 50),
            ("Ses", menu_y + 120),
            ("Müzik", menu_y + 190),
            ("Çıkış", menu_y + 260)
        ]
        
        for text, y in buttons:
            button_rect = pygame.Rect(button_x, y - 25, button_width, button_height)
            pygame.draw.rect(self.screen, GRAY, button_rect)
            pygame.draw.rect(self.screen, BLACK, button_rect, 2)
            
            text_surface = font.render(text, True, BLACK)
            text_rect = text_surface.get_rect(center=button_rect.center)
            self.screen.blit(text_surface, text_rect)
    
    def draw_game_over(self):
        """Oyun bitti ekranını çiz"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        font = pygame.font.Font(None, 72)
        info_font = pygame.font.Font(None, 36)
        
        # Başlık
        title = font.render("OYUN BİTTİ", True, RED)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 150))
        self.screen.blit(title, title_rect)
        
        # İstatistikler
        stats = [
            f"Level: {self.level}",
            f"Öldürülen Patates: {self.killed_potatoes}",
            f"Süre: {int(self.game_time)} saniye",
            f"Toplam Güç: {self.get_total_power():.1f}",
            f"Geliştirmeler:",
            f"  Hız: {self.upgrades['speed']['level']}",
            f"  Güç: {self.upgrades['damage']['level']}",
            f"  Boyut: {self.upgrades['size']['level']}",
            f"  Çoklu: {self.upgrades['multi']['level']}"
        ]
        
        y = 250
        for stat in stats:
            text = info_font.render(stat, True, WHITE)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, y))
            self.screen.blit(text, text_rect)
            y += 35
        
        # Butonlar
        button_width = 200
        button_height = 50
        
        restart_rect = pygame.Rect(SCREEN_WIDTH // 2 - 220, 580, button_width, button_height)
        quit_rect = pygame.Rect(SCREEN_WIDTH // 2 + 20, 580, button_width, button_height)
        
        pygame.draw.rect(self.screen, GREEN, restart_rect)
        pygame.draw.rect(self.screen, RED, quit_rect)
        pygame.draw.rect(self.screen, BLACK, restart_rect, 2)
        pygame.draw.rect(self.screen, BLACK, quit_rect, 2)
        
        restart_text = info_font.render("Tekrar Oyna", True, BLACK)
        quit_text = info_font.render("Çıkış", True, BLACK)
        
        restart_text_rect = restart_text.get_rect(center=restart_rect.center)
        quit_text_rect = quit_text.get_rect(center=quit_rect.center)
        
        self.screen.blit(restart_text, restart_text_rect)
        self.screen.blit(quit_text, quit_text_rect)
    
    def handle_events(self):
        """Olayları işle"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE and not self.game_over:
                    self.paused = not self.paused
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Sol tık
                    if self.game_over:
                        # Oyun bitti ekranında buton kontrolü
                        mouse_x, mouse_y = event.pos
                        restart_rect = pygame.Rect(SCREEN_WIDTH // 2 - 220, 580, 200, 50)
                        quit_rect = pygame.Rect(SCREEN_WIDTH // 2 + 20, 580, 200, 50)
                        
                        if restart_rect.collidepoint(mouse_x, mouse_y):
                            self.restart_game()
                        elif quit_rect.collidepoint(mouse_x, mouse_y):
                            self.running = False
                    
                    elif self.paused:
                        # Pause menüsünde buton kontrolü
                        mouse_x, mouse_y = event.pos
                        menu_x = (SCREEN_WIDTH - 400) // 2
                        button_x = menu_x + 100
                        
                        buttons = [
                            (button_x, 325, "continue"),  # Devam
                            (button_x, 395, "sound"),     # Ses
                            (button_x, 465, "music"),     # Müzik
                            (button_x, 535, "quit")       # Çıkış
                        ]
                        
                        for bx, by, action in buttons:
                            if (bx <= mouse_x <= bx + 200 and 
                                by - 25 <= mouse_y <= by + 25):
                                if action == "continue":
                                    self.paused = False
                                elif action == "sound":
                                    self.sound_enabled = not self.sound_enabled
                                elif action == "music":
                                    self.music_enabled = not self.music_enabled
                                elif action == "quit":
                                    self.running = False
                    
                    elif not self.paused:
                        # Geliştirme butonları kontrolü
                        mouse_x, mouse_y = event.pos
                        upgrade_keys = ['speed', 'damage', 'size', 'multi']
                        
                        for i, key in enumerate(upgrade_keys):
                            button_rect = pygame.Rect(SCREEN_WIDTH - 200, 30 + i * 60, 180, 50)
                            if button_rect.collidepoint(mouse_x, mouse_y):
                                self.buy_upgrade(key)
                                break
                        else:
                            # Havuç fırlat
                            self.shoot_carrot(mouse_x, mouse_y)
            
            elif event.type == pygame.MOUSEMOTION:
                self.mouse_pos = event.pos
    
    def restart_game(self):
        """Oyunu yeniden başlat"""
        self.__init__()
    
    def update(self, dt):
        """Oyunu güncelle"""
        if self.paused or self.game_over:
            return
        
        # Oyun zamanını güncelle
        self.game_time = time.time() - self.start_time
        
        # Patates spawn
        current_time = pygame.time.get_ticks()
        spawn_rate = max(500, self.potato_spawn_rate - self.level * 100)
        
        if current_time - self.last_potato_spawn > spawn_rate:
            self.spawn_potato()
            self.last_potato_spawn = current_time
        
        # Nesneleri güncelle
        self.update_carrots(dt)
        self.update_potatoes(dt)
        self.check_collisions()
    
    def draw(self):
        """Oyunu çiz"""
        self.draw_background()
        self.draw_player()
        self.draw_arrow()
        self.draw_carrots()
        self.draw_potatoes()
        self.draw_ui()
        
        if self.paused:
            self.draw_pause_menu()
        elif self.game_over:
            self.draw_game_over()
    
    def run(self):
        """Ana oyun döngüsü"""
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0  # Delta time in seconds
            
            self.handle_events()
            self.update(dt)
            self.draw()
            
            pygame.display.flip()
        
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()