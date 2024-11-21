import pygame

# 화면 크기 설정
width = 1100
height = 900

# 색상 설정
gray = (100, 100, 100)
darkgray = (77, 77, 77)
green = (3, 94, 21)
red = (255, 0, 0)
white = (255, 255, 255)
yellow = (255, 232, 0)
black = (0, 0, 0)

# 배경 색상 상태 변수
background_color = green

# 도로 설정
road_width = 700
marker_width = 10
marker_height = 50
lane_start_x = (width - road_width) // 2
lanes = [(lane_start_x + 50) + i * 100 for i in range(7)]

# 도로 & 엣지 마커
road = (lane_start_x, 0, road_width, height)
left_edge_marker = (lane_start_x - 5, 0, marker_width, height)
right_edge_marker = (lane_start_x + road_width - 5, 0, marker_width, height)
lane_marker_move_y = 0

#플레이어 초기설정
player_x = lanes[3]
player_y = height - 100
base_speed = 5
player_speed = 5
forward_speed = base_speed

# 차량의 이전 위치를 저장할 리스트 및 최대 잔상 개수 설정
trail_positions = []
max_trail_length = 7  # 잔상의 최대 개수

# 프레임 설정
fps = 60

# 게임 설정
gameover = False
running = True
max_speed = 20
acceleration_rate = 2
collision_speed_decrease = 5 + int(forward_speed / 2)
lives = 3
score = 0
delta_t = 1 / fps 
speed_color = white

# 게임 기록 리스트 초기화
high_scores = []

# 게임시작상태
game_started = False

# 충돌 설정
crash_visible = False
crash_display_time = 30
crash_timer = 0

# 충돌 후 무적상태 설정
invincible = False
invincibility_duration = 180  # 3초
invincibility_timer = 0
blink_interval = 10  # 깜빡임 간격

# 이미지 설정
heart_image = pygame.image.load('resources/images/heart.png')
heart_image = pygame.transform.scale(heart_image, (40, 40))
car_image = pygame.image.load('resources/images/car.png')
image_filenames = ['pickup_truck.png', 'semi_trailer.png', 'taxi.png', 'van.png']
vehicle_images = [pygame.image.load(f'resources/images/{filename}') for filename in image_filenames]
crash = pygame.image.load('resources/images/crash.png')
crash_rect = crash.get_rect()