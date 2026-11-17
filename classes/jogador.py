import pygame

from settings import (
    GRAVIDADE,
    FORCA_PULO,
    VELOCIDADE_JOGADOR
)


# criando a classe para o personagem
class Jogador:

    def __init__(self, x, y):

        # aumentando as imagens pra ficar do tamanho certo
        escala = 1.15

        # sprites dele andando
        escala_andando = 1.10
        self.frames_andando = []
        for i in range(1, 8):
            img = pygame.image.load(f"assets/images/personagem/andando{i}.png").convert_alpha()
            img = pygame.transform.scale(img, (int(img.get_width() * escala_andando), int(img.get_height() * escala_andando)))
            self.frames_andando.append(img)

        # sprites dele pulando
        escala_pulando = 1.25
        self.frames_pulando = []
        for i in range(1, 8):
            img = pygame.image.load(f"assets/images/personagem/pulando{i}.png").convert_alpha()
            img = pygame.transform.scale(img, (int(img.get_width() * escala_pulando), int(img.get_height() * escala_pulando)))
            self.frames_pulando.append(img)

        # sprites dele caindo
        escala_caindo = 0.85
        self.frames_caindo = []
        for i in range(1, 3):
            img = pygame.image.load(f"assets/images/personagem/caindo{i}.png").convert_alpha()
            img = pygame.transform.scale(img, (int(img.get_width() * escala_caindo), int(img.get_height() * escala_caindo)))
            self.frames_caindo.append(img)

        # sprite dele agachado
        img_agachar = pygame.image.load("assets/images/personagem/agaixar1.png").convert_alpha()
        img_agachar = img_agachar.subsurface(img_agachar.get_bounding_rect())
        self.sprite_agachado = pygame.transform.scale(
            img_agachar,
            (int(img_agachar.get_width() * 0.31), int(img_agachar.get_height() * 0.31))
        )

        self.frame_atual = 0.0
        self.velocidade_animacao = 0.15
        self.olhando_direita = True
        self.esta_andando = False
        self.agachado = False
        self.morto = False
        self.timer_gameover = 0

        self.altura_normal = 180
        self.altura_agachado = 135
        self.rect = pygame.Rect(x, y, 100, self.altura_normal)
        self.pos_y = float(y)

        self.velocidade_x = VELOCIDADE_JOGADOR
        self.velocidade_y = 0.0
        self.no_chao = False

    def pular(self):

        if self.no_chao:
            self.velocidade_y = FORCA_PULO
            self.no_chao = False
            self.frame_atual = 0.0

    def atualizar(self, teclas, plataformas):

        quer_agachar = teclas[pygame.K_DOWN] or teclas[pygame.K_s]
        self.agachado = quer_agachar and self.no_chao

        nova_altura = self.altura_agachado if self.agachado else self.altura_normal
        if self.rect.height != nova_altura:
            base = self.rect.bottom
            self.rect.height = nova_altura
            self.rect.bottom = base
            self.pos_y = float(self.rect.y)

        movimento_x = 0

        if not self.agachado:
            if teclas[pygame.K_a] or teclas[pygame.K_LEFT]:
                movimento_x = -self.velocidade_x
                self.olhando_direita = False

            if teclas[pygame.K_d] or teclas[pygame.K_RIGHT]:
                movimento_x = self.velocidade_x
                self.olhando_direita = True

        self.esta_andando = movimento_x != 0
        self.rect.x += movimento_x

        if self.rect.left < 0:
            self.rect.left = 0

        self.velocidade_y += GRAVIDADE

        if self.velocidade_y > 9:
            self.velocidade_y = 9

        self.pos_y += self.velocidade_y
        self.rect.y = round(self.pos_y)

        self.no_chao = False

        for plataforma in plataformas:

            if self.rect.colliderect(plataforma.rect):

                if self.velocidade_y > 0:
                    self.rect.bottom = plataforma.rect.top
                    self.pos_y = float(self.rect.y)
                    self.velocidade_y = 0.0
                    self.no_chao = True

        # pe ta encostado no chao?
        if not self.no_chao and self.velocidade_y >= 0:
            pe = self.rect.move(0, 1)
            for plataforma in plataformas:
                if pe.colliderect(plataforma.rect):
                    self.no_chao = True
                    self.velocidade_y = 0.0
                    break

        if not self.no_chao:
            self.frame_atual = (self.frame_atual + self.velocidade_animacao) % len(self.frames_pulando)
        elif self.esta_andando:
            self.frame_atual = (self.frame_atual + self.velocidade_animacao) % len(self.frames_andando)
        else:
            self.frame_atual = 0.0

    def atualizar_gameover(self, plataformas):

        self.timer_gameover += 1

        # Se morreu no ar, cai 
        self.velocidade_y += GRAVIDADE
        if self.velocidade_y > 9:
            self.velocidade_y = 9

        self.pos_y += self.velocidade_y
        self.rect.y = round(self.pos_y)

        for plataforma in plataformas:
            if self.rect.colliderect(plataforma.rect) and self.velocidade_y > 0:
                self.rect.bottom = plataforma.rect.top
                self.pos_y = float(self.rect.y)
                self.velocidade_y = 0.0
                break

    def desenhar(self, tela, camera_x, piscando_vermelho=False):

        if self.morto:
            if self.timer_gameover < 15:
                sprite = self.frames_caindo[0]
            else:
                sprite = self.frames_caindo[1]
        elif self.agachado:
            sprite = self.sprite_agachado
        elif not self.no_chao:
            sprite = self.frames_pulando[int(self.frame_atual)]
        else:
            sprite = self.frames_andando[int(self.frame_atual)]

        # vira o sprite pro lado certo
        if not self.olhando_direita:
            sprite = pygame.transform.flip(sprite, True, False)

        # pisca vermelho qnd toma dano
        if piscando_vermelho:
            sprite = sprite.copy()
            sprite.fill((255, 65, 65, 255), special_flags=pygame.BLEND_RGBA_MULT)

        sprite_rect = sprite.get_rect(
            midbottom=(self.rect.centerx - camera_x, self.rect.bottom)
        )
        tela.blit(sprite, sprite_rect)
