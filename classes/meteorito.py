import pygame


class Meteorito:

    def __init__(self, x, chao_y, velocidade=7, tipo="baixo"):

        imagem = pygame.image.load("assets/images/meteorito.png").convert_alpha()
        largura = int(imagem.get_width() * 0.32)
        altura = int(imagem.get_height() * 0.32)
        self.imagem = pygame.transform.scale(imagem, (largura, altura))

        self.velocidade = velocidade

        # hitbox menor pra ficar justo no pulo
        self.rect = pygame.Rect(0, 0, int(largura * 0.70), int(altura * 0.70))
        if tipo == "alto":
            self.rect.bottomleft = (x, chao_y - 150)
        else:
            self.rect.bottomleft = (x, chao_y - 25)

    def atualizar(self):

        self.rect.x -= self.velocidade

    def desenhar(self, tela, camera_x):

        x = self.rect.centerx - camera_x - self.imagem.get_width() // 2
        y = self.rect.bottom - self.imagem.get_height()
        tela.blit(self.imagem, (x, y))
