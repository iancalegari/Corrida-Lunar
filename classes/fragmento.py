import math
import pygame

from settings import VALOR_FRAGMENTO, VALOR_FRAGMENTO_ESPECIAL


class Fragmento:

    def __init__(self, x, y_base, especial=False):

        imagem = pygame.image.load("assets/images/fragmento.png").convert_alpha()
        largura = int(imagem.get_width() * 0.85)
        altura = int(imagem.get_height() * 0.85)
        self.imagem = pygame.transform.scale(imagem, (largura, altura))

        self.especial = especial
        self.valor = VALOR_FRAGMENTO_ESPECIAL if especial else VALOR_FRAGMENTO

        if self.especial:
            self.imagem_especial = self.imagem.copy()
            self.imagem_especial.fill((255, 210, 60, 255), special_flags=pygame.BLEND_RGBA_MULT)

            self.imagem_especial_pisca = self.imagem_especial.copy()
            self.imagem_especial_pisca.fill((110, 110, 110, 0), special_flags=pygame.BLEND_RGBA_ADD)

        self.y_base = y_base
        self.tempo = 0.0

        self.rect = self.imagem.get_rect(topleft=(x, y_base))

    def atualizar(self):

        # sobe e desce
        self.tempo += 0.08
        self.rect.y = self.y_base + int(math.sin(self.tempo) * 10)

    def desenhar(self, tela, camera_x):

        x = self.rect.x - camera_x
        if self.especial:
            piscar = int(self.tempo * 1.5) % 2 == 0
            sprite = self.imagem_especial_pisca if piscar else self.imagem_especial
            tela.blit(sprite, (x, self.rect.y))
        else:
            tela.blit(self.imagem, (x, self.rect.y))
