import pygame

def play_bgm():
    # 배경 음악 로드 및 무한 반복 재생
    pygame.mixer.music.load('resources/musics/main_bgm.wav')
    pygame.mixer.music.play(loops=-1)