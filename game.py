import pygame
from pygame.locals import *
import random
import math
from settings import *
from vehicle import Vehicle, PlayerVehicle
from collision import polygon_collision
from bgm import play_bgm

# 초기화
pygame.init()
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('감동의 아우토반')

# 배경 음악 시작
play_bgm()

# 스프라이트 그룹 초기화
player_group = pygame.sprite.Group()
vehicle_group = pygame.sprite.Group()

# 플레이어 생성
player = PlayerVehicle(player_x, player_y)
player_group.add(player)

clock = pygame.time.Clock()
while running:
    clock.tick(fps)

    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        if event.type == KEYDOWN:
            if event.key in (K_LEFT, K_RIGHT, K_UP):
                game_started = True

    if game_started:
        keys = pygame.key.get_pressed()
        forward_speed = player.update(keys, forward_speed)

    screen.fill(background_color)
    pygame.draw.rect(screen, gray, road)
    pygame.draw.rect(screen, yellow, left_edge_marker)
    pygame.draw.rect(screen, yellow, right_edge_marker)

    if lane_marker_move_y >= marker_height * 2:
        lane_marker_move_y = 0
    for y in range(marker_height * -2, height, marker_height * 2):
        for lane_x in lanes:
            pygame.draw.rect(screen, white, (lane_x, y + lane_marker_move_y, marker_width, marker_height))

    # 깜빡임 효과를 위해 플레이어를 그리지 않음
    if invincible and (invincibility_timer // blink_interval) % 2 == 0:
        pass  
    else:
        player_group.draw(screen)

    if game_started and len(vehicle_group) < 5:
        if random.randint(0, 10) == 0:  # 생성 빈도를 높이기 위해 상한을 줄임
            # 새로운 장애물이 기존 장애물과 겹치지 않는 위치를 찾을 때까지 반복
            safe_to_place = False
            attempt = 0  # 시도 횟수 제한
            while not safe_to_place and attempt < 10:
                x_position = random.randint(lane_start_x + 20, lane_start_x + road_width - 20)  # 도로 영역 내 무작위 위치
                y_position = -50  # 장애물의 초기 y 위치
                
                # 잠재적 새 위치의 안전성을 확인
                safe_to_place = True
                for vehicle in vehicle_group:
                    if abs(vehicle.rect.x - x_position) < 80 and abs(vehicle.rect.y - y_position) < 80:
                        safe_to_place = False
                        break
                attempt += 1  # 시도 횟수 증가

            # 안전한 위치가 확보되면 장애물 생성
            if safe_to_place:
                image = random.choice(vehicle_images)
                vehicle = Vehicle(image, x_position, y_position)
                vehicle_group.add(vehicle)

    # 속도 계산 및 속도 표시 텍스트 표시(km/h 단위)
    converted_speed = int((forward_speed / max_speed) * 300)  # 최고 속도를 300km/h로 환산
    speed_font = pygame.font.Font(pygame.font.get_default_font(), 30)
    speed_text = speed_font.render(f"{converted_speed} km/h", True, speed_color)
    screen.blit(speed_text, (width - 150, height - 50))

    # 속도가 최대치일 경우 효과 추가
    if forward_speed >= max_speed:
        lane_marker_move_y += forward_speed * 4
        speed_color = red 
        score_increase = 2
        # 가속감이 느껴지도록 차량 주변에 효과 선 배치
        line_x_start = player.rect.centerx + random.randint(-50, 50)
        line_y_start = player.rect.centery + random.randint(-50, 50)
        line_x_end = line_x_start + random.randint(-10, 10)
        line_y_end = line_y_start + random.randint(20, 40)
        pygame.draw.line(screen, white, (line_x_start, line_y_start), (line_x_end, line_y_end), 2)
        # 가속감이 느껴지도록 화면 전체에 효과 선 배치
        line_x_start = random.randint(0, width)
        line_y_start = random.randint(0, height)
        line_x_end = line_x_start + random.randint(-10, 10)
        line_y_end = line_y_start + random.randint(200, 300)
        pygame.draw.line(screen, white, (line_x_start, line_y_start), (line_x_end, line_y_end), 1)
    else:
        lane_marker_move_y += forward_speed * 2
        speed_color = white
        score_increase = 1

    # 점수 증가 시, score_increase(2배 이벤트)를 적용
    for vehicle in vehicle_group:
        vehicle.rect.y += forward_speed
        if vehicle.rect.top >= height:
            vehicle.kill()
            score += score_increase

    # 최대속도에서 좌우 이동시, 차량 잔상효과 추가(차량각도 반영)
    if forward_speed >= max_speed and player.angle != 0:
        trail_offset_distance = 0 
        if player.angle > 0:  # 왼쪽으로 이동 중일 때 오른쪽에 잔상 생성
            trail_position = (player.rect.centerx + trail_offset_distance, player.rect.centery)
        elif player.angle < 0:  # 오른쪽으로 이동 중일 때 왼쪽에 잔상 생성
            trail_position = (player.rect.centerx - trail_offset_distance, player.rect.centery)
        else:
            trail_position = player.rect.center

        # 잔상 위치 및 각도를 trail_positions 리스트에 추가
        trail_positions.append((trail_position, player.angle))
        if len(trail_positions) > max_trail_length: # trail_positions이 max_trail_length를 초과하면 가장 오래된 위치를 제거(최대 잔상개수 유지)
            trail_positions = trail_positions[-max_trail_length:]  # 마지막 max_trail_length개의 잔상만 유지

        # 각 잔상에 점진적 투명도 설정
        for i, (position, angle) in enumerate(trail_positions):
            trail_alpha = int(255 * (i / max_trail_length))
            trail_surface = pygame.transform.rotate(player.original_image, angle)  # 잔상에 회전 반영
            trail_surface.set_alpha(trail_alpha)
            screen.blit(trail_surface, trail_surface.get_rect(center=position))
    # 최대 속도가 아닐 때 또는 직진 중일 때는 잔상 리스트 초기화
    else:
        trail_positions.clear()
    
    # 점수 및 남은목숨 표시
    vehicle_group.draw(screen)
    font = pygame.font.Font(pygame.font.get_default_font(), 30)
    score_text = font.render(f'Score: {score}', True, white)
    screen.blit(score_text, (25, 25))
    for i in range(lives):
        screen.blit(heart_image, (25 + i * 50, height - 60))

    # 게임실행 시 초기화면 설정
    if not game_started:
        pygame.draw.rect(screen, black, (220, height / 2 - 200, width - 440, 410), border_radius=25)
        pygame.draw.rect(screen, darkgray, (225, height / 2 - 195, width - 450, 400), border_radius=20)
        start_font = pygame.font.SysFont("malgungothic", 30, bold=True)
        sub_font = pygame.font.SysFont("malgungothic", 20, bold=True)
        text1 = start_font.render("감동의 아우토반입니다!", True, white)
        text2 = start_font.render("느려터진 거북이들을 피해 질주하세요!", True, white)
        text3 = sub_font.render("앞, 또는 좌우 방향키를 눌러 시작하세요", True, white)
        text4 = sub_font.render("↑ : 가속페달       ← : 좌측이동      → : 우측이동", True, white)
        text5 = sub_font.render("저속주행하는 겁쟁이들은 나가라!", True, red)
        text6 = sub_font.render("최고속도에서는 score증가량 2배 이벤트!", True, red)
        text_rect1 = text1.get_rect(center=(width / 2, height / 2 - 140))
        text_rect2 = text2.get_rect(center=(width / 2, height / 2 - 90))
        text_rect3 = text3.get_rect(center=(width / 2, height / 2))
        text_rect4 = text4.get_rect(center=(width / 2, height / 2 + 40))
        text_rect5 = text5.get_rect(center=(width / 2, height / 2 + 120))
        text_rect6 = text6.get_rect(center=(width / 2, height / 2 + 150))
        screen.blit(text1, text_rect1)
        screen.blit(text2, text_rect2)
        screen.blit(text3, text_rect3)
        screen.blit(text4, text_rect4)
        screen.blit(text5, text_rect5)
        screen.blit(text6, text_rect6)

    if game_started and not invincible:
        player_hull = player.get_convex_hull()
        collision_occurred = False
        for vehicle in vehicle_group:
            vehicle_hull = vehicle.get_convex_hull()
            if polygon_collision(player_hull, vehicle_hull):
                collision_occurred = True
                vehicle.kill()
                collision_dx = player.rect.centerx - vehicle.rect.centerx
                collision_dy = player.rect.centery - vehicle.rect.centery
                collision_distance = math.hypot(collision_dx, collision_dy)
                if collision_distance != 0:
                    collision_dx /= collision_distance
                    collision_dy /= collision_distance

                bounce_distance = min(forward_speed * 10, 150)
                player.bounce_vector = [collision_dx * bounce_distance * 0.2, collision_dy * bounce_distance * 0.2]
                break

        if collision_occurred:
            lives -= 1
            forward_speed = max(forward_speed - collision_speed_decrease, base_speed)
            if lives <= 0:
                gameover = True
            invincible = True
            invincibility_timer = invincibility_duration
            crash_rect.center = player.rect.center
            crash_visible = True
            crash_timer = crash_display_time

    if invincible:
        invincibility_timer -= 1
        if invincibility_timer <= 0:
            invincible = False

    if crash_visible:
        screen.blit(crash, crash_rect)
        crash_timer -= 1
        if crash_timer <= 0:
            crash_visible = False
    # 목숨 0개 도달
    if lives <= 0:
        high_scores.append(score) # 현재 점수를 기록
        high_scores = sorted(high_scores, reverse=True)[:5] # 점수를 내림차순으로 정렬하여 상위 5개만 유지
        pygame.draw.rect(screen, black, (220, height / 2 - 200, width - 440, 410), border_radius=25)
        pygame.draw.rect(screen, darkgray, (225, height / 2 - 195, width - 450, 400), border_radius=20)
        font = pygame.font.SysFont("malgungothic", 30, bold=True)
        text1 = font.render('감동의 아우토반에서 도태되셨습니다...', True, white)
        text2 = font.render('다시하시겠습니까? (Y 또는 N 을 누르세요)', True, white)
        text_rect1 = text1.get_rect(center=(width / 2, height / 2 - 140))
        text_rect2 = text2.get_rect(center=(width / 2, height / 2 - 90))
        screen.blit(text1, text_rect1)
        screen.blit(text2, text_rect2)
        for i in range(5):
            score_text = f"{i + 1}위 - {high_scores[i] if i < len(high_scores) else '---'}점"
            score_render = font.render(score_text, True, white)
            score_rect = score_render.get_rect(center=(width / 2, height / 2 + (i * 35)))
            screen.blit(score_render, score_rect)
        gameover = True
    pygame.display.update()
 
    while gameover:
        clock.tick(fps)
        for event in pygame.event.get():
            if event.type == QUIT:
                gameover = False
                running = False
            if event.type == KEYDOWN:
                if event.key == K_y:
                    gameover = False
                    forward_speed = base_speed
                    score = 0
                    lives = 3
                    vehicle_group.empty()
                    player.rect.center = [player_x, player_y]
                    player.initial_y = player_y  # 초기 y 위치 재설정
                    game_started = False
                    
                    # 충돌 모션 및 회전 상태 초기화
                    crash_visible = False
                    crash_timer = 0
                    invincible = False
                    invincibility_timer = 0
                    
                    # 플레이어 상태 초기화
                    player.angle = 0  # 각도 초기화
                    player.image = player.original_image  # 이미지 원상복구
                    player.bounce_vector = [0, 0]  # 충돌 이동 벡터 초기화
                    player.return_to_position = False  # 원래 위치로의 복귀 중지
                elif event.key == K_n:
                    gameover = False
                    running = False
pygame.quit()