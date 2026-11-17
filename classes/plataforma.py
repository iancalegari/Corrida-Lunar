import pygame


class Plataforma:

    def __init__(self, x, y, largura, altura, visivel=True):

        self.rect = pygame.Rect(
            x,
            y,
            largura,
            altura
        )
        self.visivel = visivel

    def desenhar(self, tela, camera_x):

        if not self.visivel:
            return

        x = self.rect.x - camera_x

        pygame.draw.rect(
            tela,
            (110, 115, 130),
            (x, self.rect.y, self.rect.width, self.rect.height)
        )

        # Parte de cima da superfície lunar
        pygame.draw.rect(
            tela,
            (180, 180, 190),
            (x, self.rect.y, self.rect.width, 6)
        )
