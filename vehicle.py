import pygame
from pygame.locals import *
import math
from settings import *
from collision import get_rotated_points

class Vehicle(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        pygame.sprite.Sprite.__init__(self)
        image_scale = 37 / image.get_rect().width
        new_width = int(image.get_rect().width * image_scale)
        new_height = int(image.get_rect().height * image_scale)
        self.original_image = pygame.transform.scale(image, (new_width, new_height))
        self.image = self.original_image
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.angle = 0

    def get_convex_hull(self):
        return get_rotated_points(self.rect, self.angle)

    def rotate(self, angle):
        self.angle = angle
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

class PlayerVehicle(Vehicle):
    def __init__(self, x, y):
        # car_image = pygame.image.load('./python-car-game/images/car.png')
        super().__init__(car_image, x, y)
        self.bounce_vector = [0, 0]
        self.return_to_position = False

    def update(self, keys, forward_speed):
        target_y = height - 150  # 고정된 복귀 위치

        if self.bounce_vector[0] != 0 or self.bounce_vector[1] != 0:
            self.rect.x += int(self.bounce_vector[0])
            self.rect.y += int(self.bounce_vector[1])
            self.bounce_vector[0] *= 0.9
            self.bounce_vector[1] *= 0.9
            if abs(self.bounce_vector[0]) < 0.5 and abs(self.bounce_vector[1]) < 0.5:
                self.bounce_vector = [0, 0]
                self.return_to_position = True  # 복귀 시작

        # 부드럽게 target_y로 복귀
        if self.return_to_position:
            delta_y = target_y - self.rect.y
            if abs(delta_y) > 1:
                self.rect.y += delta_y * 0.1  # 점진적으로 이동
            else:
                self.rect.y = target_y  # 고정된 위치로 설정
                self.return_to_position = False  # 복귀 완료

        # 기본 이동 로직 유지
        lateral_speed = player_speed + int(forward_speed / 5)
        if keys[K_LEFT]:
            self.rect.x -= lateral_speed
            self.rotate(min(self.angle + 5, 15))
        elif keys[K_RIGHT]:
            self.rect.x += lateral_speed
            self.rotate(max(self.angle - 5, -15))
        else:
            if self.angle > 0:
                self.rotate(self.angle - 5)
            elif self.angle < 0:
                self.rotate(self.angle + 5)
        if keys[K_UP]:
            forward_speed += acceleration_rate * delta_t
            forward_speed = min(forward_speed, max_speed)  # 최대 속도 제한
        else:
            forward_speed -= acceleration_rate * delta_t
            forward_speed = max(forward_speed, base_speed)  # 최소 속도 제한
        if self.rect.x < lanes[0] - 50:
            self.rect.x = lanes[0] - 50
        elif self.rect.x > lanes[-1]:
            self.rect.x = lanes[-1]
        return forward_speed
    def handle_collision(self, forward_speed, collision_dx, collision_dy):
        # 속도에 따른 튕김 거리 계산 (속도가 낮을수록 짧게 튕기고, 최대 속도에서 많이 튕김)
        bounce_distance = min(50 + (forward_speed / max_speed) * 100, 150)

        # 충돌 방향에 따라 튕김 벡터 설정
        collision_distance = math.hypot(collision_dx, collision_dy)
        if collision_distance != 0:
            collision_dx /= collision_distance
            collision_dy /= collision_distance

        # 속도에 비례하는 튕김 벡터 적용
        self.bounce_vector = [collision_dx * bounce_distance, collision_dy * bounce_distance]