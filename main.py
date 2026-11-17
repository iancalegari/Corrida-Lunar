import os
import random
import sys
import pygame

from settings import *
from classes.jogador import Jogador
from classes.plataforma import Plataforma
from classes.fragmento import Fragmento
from classes.meteorito import Meteorito


pygame.init()

tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption(TITULO)

relogio = pygame.time.Clock()

fonte = pygame.font.Font("assets/fonts/PressStart2P.ttf", 18)
fonte_titulo = pygame.font.Font("assets/fonts/PressStart2P.ttf", 36)

# logo do jogo e tela inicial
img_logo = pygame.image.load("assets/images/personagem/logo.png").convert_alpha()
img_logo = img_logo.subsurface(img_logo.get_bounding_rect())
logo_hud = pygame.transform.scale(
    img_logo,
    (int(img_logo.get_width() * 0.30), int(img_logo.get_height() * 0.30))
)

img_telainicial = pygame.image.load("assets/images/telainicial.png").convert()
if img_telainicial.get_size() != (LARGURA, ALTURA):
    img_telainicial = pygame.transform.scale(img_telainicial, (LARGURA, ALTURA))

# imagens de fundo
img_background = pygame.image.load("assets/images/background.png").convert()
img_estrelas = pygame.image.load("assets/images/estrelas.png").convert_alpha()
img_piso = pygame.image.load("assets/images/piso.png").convert_alpha()

# sprites da vida (1 a 5)
imagens_vida = {}
for i in range(1, 6):
    img_vida = pygame.image.load(f"assets/images/personagem/vida{i}.png").convert_alpha()
    escala_vida = 0.45
    img_vida = pygame.transform.scale(
        img_vida,
        (int(img_vida.get_width() * escala_vida), int(img_vida.get_height() * escala_vida))
    )
    imagens_vida[i] = img_vida

# musica e efeitos sonoros
pygame.mixer.music.load("assets/sounds/musica.mp3")
pygame.mixer.music.set_volume(0.10)
pygame.mixer.music.play(-1)

som_pulo = pygame.mixer.Sound("assets/sounds/pulando.mp3")
som_pulo.set_volume(0.25)
som_dano = pygame.mixer.Sound("assets/sounds/dano.mp3")
som_dano.set_volume(0.25)


# altura do chao
CHAO_Y = 885
CAMINHO_RECORDE = os.path.join("data", "recorde.txt")


def carregar_recorde():
    if os.path.exists(CAMINHO_RECORDE):
        with open(CAMINHO_RECORDE, "r") as f:
            texto = f.read().strip()
            if texto.isdigit():
                return int(texto)
    return 0


def salvar_recorde(valor):
    with open(CAMINHO_RECORDE, "w") as f:
        f.write(str(valor))


# chao invisivel pro personagem andar em cima do piso.png
plataformas = [
    Plataforma(0, CHAO_Y, 1_000_000, ALTURA - CHAO_Y, visivel=False)
]

jogador = Jogador(100, CHAO_Y - 180)
fragmentos = []
meteoritos = []

camera_x = 0
pontos = 0
distancia_max_x = 0
vidas = VIDAS_INICIAIS
recorde = carregar_recorde()
invulneravel_timer = 0
proximo_fragmento_x = 650
timer_meteorito = 90

menu = True
game_over = False
rodando = True


def reiniciar_jogo():
    global jogador, fragmentos, meteoritos, camera_x
    global pontos, distancia_max_x, vidas, invulneravel_timer
    global proximo_fragmento_x, timer_meteorito, game_over

    jogador = Jogador(100, CHAO_Y - 180)
    fragmentos = []
    meteoritos = []
    camera_x = 0
    pontos = 0
    distancia_max_x = 0
    vidas = VIDAS_INICIAIS
    invulneravel_timer = 0
    proximo_fragmento_x = 650
    timer_meteorito = 90
    game_over = False


def desenhar_texto(texto, fonte_usada, cor, x, y, cor_sombra=(75, 80, 95)):
    sombra = fonte_usada.render(texto, True, cor_sombra)
    frente = fonte_usada.render(texto, True, cor)
    tela.blit(sombra, (x + 3, y + 3))
    tela.blit(frente, (x, y))


def desenhar_item_hud(rotulo, valor, x, y):
    desenhar_texto(rotulo, fonte, AMARELO, x, y, cor_sombra=(110, 45, 10))
    largura_rotulo = fonte.size(rotulo)[0]
    desenhar_texto(str(valor), fonte, BRANCO, x + largura_rotulo, y, cor_sombra=(75, 80, 95))


def desenhar_camada_parallax(imagem, fator, y=0):

    largura_img = imagem.get_width()
    deslocamento = -(camera_x * fator) % largura_img

    tela.blit(imagem, (deslocamento - largura_img, y))
    tela.blit(imagem, (deslocamento, y))


# faz o fundo andar em velocidades diferentes
def desenhar_fundo():

    desenhar_camada_parallax(img_background, 0.1)
    desenhar_camada_parallax(img_estrelas, 0.3)
    desenhar_camada_parallax(img_piso, 1.0, y=100)


# loop principal do jogo
while rodando:

    relogio.tick(FPS)

    for evento in pygame.event.get():

        if evento.type == pygame.QUIT:
            rodando = False

        if evento.type == pygame.KEYDOWN:

            if menu and evento.key == pygame.K_RETURN:
                menu = False

            elif game_over and evento.key == pygame.K_RETURN:
                reiniciar_jogo()

            elif not menu and not game_over and evento.key in (pygame.K_SPACE, pygame.K_UP):
                if jogador.no_chao:
                    som_pulo.play()
                jogador.pular()

            elif evento.key == pygame.K_ESCAPE:
                rodando = False

    if menu:

        tela.blit(img_telainicial, (0, 0))

    elif game_over:

        jogador.atualizar_gameover(plataformas)
        # desenha tudo na tela
        desenhar_fundo()

        for fragmento in fragmentos:
            fragmento.desenhar(tela, camera_x)

        for meteorito in meteoritos:
            meteorito.desenhar(tela, camera_x)

        jogador.desenhar(tela, camera_x)

        distancia_metros = distancia_max_x // 10
        titulo = fonte_titulo.render("FIM DE JOGO", True, VERMELHO)
        resumo = fonte.render(
            f"Distância: {distancia_metros} m  |  Pontos: {pontos}  |  Recorde: {recorde}",
            True,
            BRANCO
        )
        instrucao = fonte.render("Pressione ENTER para jogar novamente", True, AMARELO)

        tela.blit(titulo, (LARGURA // 2 - titulo.get_width() // 2, 340))
        tela.blit(resumo, (LARGURA // 2 - resumo.get_width() // 2, 420))
        tela.blit(instrucao, (LARGURA // 2 - instrucao.get_width() // 2, 470))

    else:

        teclas = pygame.key.get_pressed()

        jogador.atualizar(teclas, plataformas)

        camera_x = max(0, jogador.rect.centerx - LARGURA // 2)
        distancia_max_x = max(distancia_max_x, jogador.rect.x - 100)

        # spawna fragmentos na frente
        while proximo_fragmento_x < camera_x + LARGURA + 400:
            fragmentos.append(Fragmento(proximo_fragmento_x, CHAO_Y - 135))
            proximo_fragmento_x += random.randint(420, 760)

        # meteorito pode vir embaixo ou em cima
        timer_meteorito -= 1
        if timer_meteorito <= 0:
            velocidade_meteorito = random.randint(7, 10)
            tipo_meteorito = random.choice(["baixo", "alto"])
            meteoritos.append(
                Meteorito(
                    camera_x + LARGURA + 80,
                    CHAO_Y,
                    velocidade=velocidade_meteorito,
                    tipo=tipo_meteorito
                )
            )
            timer_meteorito = random.randint(95, 165)

        for fragmento in fragmentos[:]:
            fragmento.atualizar()

            if jogador.rect.colliderect(fragmento.rect):
                pontos += VALOR_FRAGMENTO
                if pontos > recorde:
                    recorde = pontos
                    salvar_recorde(recorde)
                fragmentos.remove(fragmento)
            elif fragmento.rect.right < camera_x - 200:
                fragmentos.remove(fragmento)

        if invulneravel_timer > 0:
            invulneravel_timer -= 1

        for meteorito in meteoritos[:]:
            meteorito.atualizar()

            # tomou dano do meteorito
            if invulneravel_timer == 0 and jogador.rect.colliderect(meteorito.rect):
                som_dano.play()
                vidas -= 1
                invulneravel_timer = 60
                meteoritos.remove(meteorito)
                if vidas <= 0:
                    jogador.morto = True
                    game_over = True
            elif meteorito.rect.right < camera_x - 200:
                meteoritos.remove(meteorito)

        # desenha tudo na tela
        desenhar_fundo()

        for fragmento in fragmentos:
            fragmento.desenhar(tela, camera_x)

        for meteorito in meteoritos:
            meteorito.desenhar(tela, camera_x)

        piscando_vermelho = invulneravel_timer > 0 and (invulneravel_timer // 5) % 2 == 0
        jogador.desenhar(tela, camera_x, piscando_vermelho=piscando_vermelho)

        distancia_metros = distancia_max_x // 10
        tela.blit(logo_hud, (24, 20))
        desenhar_item_hud("DISTÂNCIA: ", f"{distancia_metros} m", 24, 84)
        desenhar_item_hud("PONTOS: ", pontos, 24, 114)
        desenhar_item_hud("RECORDE: ", recorde, 24, 144)

        if vidas in imagens_vida:
            img_vida = imagens_vida[vidas]
            x_vida = LARGURA - img_vida.get_width() - 24
            tela.blit(img_vida, (x_vida, 20))

            rotulo_vida = "VIDA: "
            valor_vida = f"{vidas}/{VIDAS_INICIAIS}"
            largura_texto = fonte.size(rotulo_vida + valor_vida)[0]
            y_texto = 20 + img_vida.get_height() // 2 - 9
            desenhar_item_hud(rotulo_vida, valor_vida, x_vida - largura_texto - 14, y_texto)

    pygame.display.flip()


pygame.quit()
sys.exit()
