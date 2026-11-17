import math
import pygame


class Fragmento:

    def __init__(self, x, y_base):

        imagem = pygame.image.load("assets/images/fragmento.png").convert_alpha()
        largura = int(imagem.get_width() * 0.85)
        altura = int(imagem.get_height() * 0.85)
        self.imagem = pygame.transform.scale(imagem, (largura, altura))

        self.y_base = y_base
        self.tempo = 0.0

        self.rect = self.imagem.get_rect(topleft=(x, y_base))

    def atualizar(self):

        # sobe e desce
        self.tempo += 0.08
        self.rect.y = self.y_base + int(math.sin(self.tempo) * 10)

    def desenhar(self, tela, camera_x):

        x = self.rect.x - camera_x
        tela.blit(self.imagem, (x, self.rect.y))
