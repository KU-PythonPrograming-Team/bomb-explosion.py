import pygame
import random

pygame.init()

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Bomberman Game")
        self.clock = pygame.time.Clock()
        self.player = Player(50, 50, 5)
        self.bombs = []
        self.walls = []
        self.explosions = []  # 폭발 리스트 추가
        self.running = True
        self.create_walls()

    def create_walls(self):
        for _ in range(10):
            x = random.randint(0, 15) * 50
            y = random.randint(0, 11) * 50
            destructible = random.choice([True, False])
            self.walls.append(Wall(x, y, destructible))

    def start(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            self.handle_key_input()
            self.update()
            self.update_bombs()
            pygame.display.flip()
            self.clock.tick(60)

    def handle_key_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.player.move('left', self.walls)
        if keys[pygame.K_RIGHT]:
            self.player.move('right', self.walls)
        if keys[pygame.K_UP]:
            self.player.move('up', self.walls)
        if keys[pygame.K_DOWN]:
            self.player.move('down', self.walls)
        if keys[pygame.K_SPACE]:
            self.player.place_bomb(self.bombs)

    def update(self):
        self.screen.fill((0, 0, 0))
        self.screen.blit(self.player.image, (self.player.x, self.player.y))
        for wall in self.walls:
            wall.draw(self.screen)
        for bomb in self.bombs:
            bomb.draw(self.screen)
        self.update_explosions()  # 폭발 업데이트 및 화면에 표시

    def update_bombs(self):
        for bomb in self.bombs[:]:
            bomb.update()
            if bomb.timer <= 0:
                bomb.explode(self.walls, self.explosions)  # 폭발 발생 시 explosions 리스트 전달
                self.bombs.remove(bomb)

    def update_explosions(self):
        for explosion in self.explosions[:]:
            explosion.update()
            explosion.draw(self.screen)
            if explosion.is_finished():
                self.explosions.remove(explosion)

    def quit(self):
        pygame.quit()

class Player:
    def __init__(self, x, y, speed):
        self.x = x
        self.y = y
        self.lives = 3
        self.speed = speed
        self.image = pygame.Surface((50, 50))
        self.image.fill((0, 0, 255))
        self.bombs_count = 1

    def move(self, direction, walls):
        new_x, new_y = self.x, self.y  # 새 위치 저장

        match direction:
            case 'left':
                new_x -= self.speed
            case 'right':
                new_x += self.speed
            case 'up':
                new_y -= self.speed
            case 'down':
                new_y += self.speed
            case _:
                return  # 움직이지 않을 때

        # 벽과 충돌할 때
        if not self.check_collision(new_x, new_y, walls):
            if 0 <= new_x <= 800 - 50:  # 화면의 왼쪽과 오른쪽 경계
                self.x = new_x
            if 0 <= new_y <= 600 - 50:  # 화면의 위쪽과 아래쪽 경계
                self.y = new_y  # 충돌이 없을 경우 위치 업데이트

    def check_collision(self, new_x, new_y, walls):
        player_rect = pygame.Rect(new_x, new_y, 50, 50)  # 플레이어 충돌 범위 이미지
        for wall in walls:
            wall_rect = pygame.Rect(wall.x, wall.y, 50, 50)  # 벽 충돌 범위 이미지
            if player_rect.colliderect(wall_rect):
                return True  # 충돌감지
        return False  # 충돌 x

    def place_bomb(self, bombs):
        if len(bombs) < self.bombs_count:  # 설치할 수 있는 폭탄 개수 제한
            bomb = Bomb(self.x, self.y, timer=3)  # 3초 타이머로 폭탄 생성
            bombs.append(bomb)
            print(f"Bomb placed at ({self.x}, {self.y})")  # 콘솔에 폭탄 설치 위치 출력

class Bomb:
    def __init__(self, x, y, timer):
        self.x = x
        self.y = y
        self.timer = timer
        self.image = pygame.Surface((30, 30))
        self.image.fill((255, 0, 0))
        self.font = pygame.font.Font(None, 36)

    def update(self):
        if self.timer > 0:
            self.timer -= 1 / 60

    def explode(self, walls, explosions):
        print(f"Bomb at ({self.x}, {self.y}) exploded!")
        explosion = Explosion(self.x, self.y, radius=1)  # 폭발 객체 생성
        explosions.append(explosion)
        self.handle_explosion(walls)

    def handle_explosion(self, walls):
        explosion_radius = 50
        explosion_area = pygame.Rect(self.x - explosion_radius, self.y - explosion_radius, 
                                     explosion_radius * 2 + 50, explosion_radius * 2 + 50)

        for wall in walls[:]:
            wall_rect = pygame.Rect(wall.x, wall.y, 50, 50)
            if explosion_area.colliderect(wall_rect):
                if wall.destructible:
                    walls.remove(wall)  # 파괴 가능한 벽 제거
                    print(f"Wall at ({wall.x}, {wall.y}) destroyed by explosion!")

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))
        if self.timer > 0:
            timer_text = self.font.render(str(int(self.timer)), True, (255, 255, 255))
            text_rect = timer_text.get_rect(center=(self.x + 15, self.y + 15))
            screen.blit(timer_text, text_rect)

class Explosion:
    def __init__(self, x, y, radius, duration=1):
        self.x = x
        self.y = y
        self.radius = radius
        self.duration = duration
        self.timer = duration
        self.image = pygame.Surface((50, 50), pygame.SRCALPHA)
        self.image.fill((255, 165, 0, 128))

    def update(self):
        self.timer -= 1 / 60

    def draw(self, screen):
        for i in range(self.radius + 1):
            screen.blit(self.image, (self.x - i * 50, self.y))
            screen.blit(self.image, (self.x + i * 50, self.y))
            screen.blit(self.image, (self.x, self.y - i * 50))
            screen.blit(self.image, (self.x, self.y + i * 50))

    def is_finished(self):
        return self.timer <= 0

class Wall:
    def __init__(self, x, y, destructible):
        self.x = x
        self.y = y
        self.destructible = destructible
        self.image = pygame.Surface((50, 50))  # 벽 크기 조정
        if self.destructible:
            self.image.fill((101, 67, 33))  # 파괴 가능한 벽: 짙은 갈색
        else:
            self.image.fill((139, 69, 19))  # 파괴 불가능한 벽: 갈색

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

class Item:
    def __init__(self, x, y, type):
        self.x = x
        self.y = y
        self.type = type

    def apply_effect(self, player):
        # 아이템 효과 적용
        pass

class Board:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = [[None for _ in range(width)] for _ in range(height)]

    def place_element(self, element, x, y):
        pass

    def remove_element(self, x, y):
        pass

class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def move(self):
        pass

    def die(self):
        pass

# 게임 실행
game = Game()
game.start()
game.quit()
