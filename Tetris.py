from time import sleep
from numpy import rot90
from threading import Thread
from random import choice
from os import listdir
import pygame
pygame.init()

SQUARE_SIZE = 40
IMAGES = {name[:-4]: pygame.transform.scale(pygame.image.load(f"Images/{name}"), (SQUARE_SIZE, SQUARE_SIZE))
          for name in listdir('Images')}


class Block:
    def __init__(self, screen: pygame.Surface, image: pygame.Surface, dimensions, *coords):
        self.coords = [list(coord) for coord in coords]
        self.image = image
        self.screen = screen
        self.dimensions = dimensions
        self.block_rotate = False
        self.block_down = False
        self.block_right = False
        self.block_left = False

    def show(self, x, y):
        min_x = min([coord[0] for coord in self.coords])
        max_x = max([coord[0] for coord in self.coords])
        min_y = min([coord[1] for coord in self.coords])
        max_y = max([coord[1] for coord in self.coords])
        qtd_x = max_x - min_x + 1
        qtd_y = max_y - min_y + 1
        for sqr in self.coords:
            sqr_x = (sqr[0] - min_x) * SQUARE_SIZE
            sqr_y = (sqr[1] - min_y) * SQUARE_SIZE
            coords = (int(sqr_x + x - qtd_x * SQUARE_SIZE / 2), int(sqr_y + y - qtd_y * SQUARE_SIZE / 2))
            self.screen.blit(self.image, coords)

    def rotate(self, fixed):
        if self.block_rotate:
            return
        anterior = self.coords.copy()
        matriz = [[0 for _ in range(self.dimensions[0])] for _ in range(self.dimensions[1])]
        min_x = min([coord[0] for coord in self.coords])
        min_y = min([coord[1] for coord in self.coords])
        for point in self.coords:
            matriz[point[0]-min_x][point[1]-min_y] = 1
        matriz = rot90(matriz)
        self.coords = []
        for x in range(self.dimensions[0]):
            for y in range(self.dimensions[1]):
                if matriz[x][y]:
                    self.coords.append([x+min_x, y+min_y])

        for coord in self.coords:
            if coord in [block[:2] for block in fixed]:
                for pt in self.coords:
                    pt[1] -= 1
            elif coord[0] > 9:
                self.left()
            elif coord[0] < 0:
                self.right()
            else:
                continue
            break
        for coord in self.coords:
            if coord in [block[:2] for block in fixed]:
                for pt in self.coords:
                    pt[1] -= 1
            elif coord[0] > 9:
                self.left()
            elif coord[0] < 0:
                self.right()
            else:
                continue
            break
        for coord in self.coords:
            if coord in [block[:2] for block in fixed] or not 0 <= coord[0] <= 9:
                self.coords = anterior
                break

        self.dimensions = self.dimensions[::-1]
        self.block_rotate = True
        sleep(0.1)
        self.block_rotate = False

    def blit(self):
        for sqr in self.coords:
            self.screen.blit(self.image, (sqr[0]*SQUARE_SIZE, sqr[1]*SQUARE_SIZE))

    def right(self):
        if self.block_right:
            return
        for blk in self.coords:
            blk[0] += 1

    def left(self):
        if self.block_left:
            return
        for blk in self.coords:
            blk[0] -= 1

    def down(self):
        if self.block_down:
            return
        for blk in self.coords:
            blk[1] += 1
        return True


class T(Block):
    def __init__(self, screen):
        super().__init__(screen, IMAGES["T"], (2, 3), (4, 0), (5, 0), (6, 0), (5, 1))


class Z(Block):
    def __init__(self, screen):
        super().__init__(screen, IMAGES["Z"], (2, 3), (4, 0), (5, 0), (5, 1), (6, 1))


class S(Block):
    def __init__(self, screen):
        super().__init__(screen, IMAGES["S"], (2, 3), (4, 1), (5, 1), (5, 0), (6, 0))


class J(Block):
    def __init__(self, screen):
        super().__init__(screen, IMAGES["J"], (2, 3), (4, 0), (5, 0), (6, 0), (6, 1))


class L(Block):
    def __init__(self, screen):
        super().__init__(screen, IMAGES["L"], (2, 3), (4, 1), (5, 1), (6, 1), (6, 0))


class Line(Block):
    def __init__(self, screen):
        super().__init__(screen, IMAGES["Line"], (1, 4), (4, 0), (5, 0), (6, 0), (7, 0))


class Square(Block):
    def __init__(self, screen):
        super().__init__(screen, IMAGES["Square"], (2, 2), (4, 0), (5, 0), (5, 1), (4, 1))


class Game:
    def __init__(self):
        self.dp_height = 20 * SQUARE_SIZE
        self.dp_width = 16 * SQUARE_SIZE
        self.tela: pygame.Surface = pygame.display.set_mode((self.dp_width, self.dp_height), pygame.FULLSCREEN)
        self.next = choice([Square, Line, Z, S, L, J, T])(self.tela)
        self.block = NotImplemented
        self.new_block()
        self.running = True
        self.keys_pressed = []
        self.fixados = []
        self.touch_frames = 0
        self.points = 0

    def event_handler(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                self.keys_pressed.append(event.key)
            elif event.type == pygame.KEYUP:
                try:
                    self.keys_pressed.remove(event.key)
                except ValueError:
                    pass
        self.block.block_down = False
        self.block.block_left = False
        self.block.block_right = False
        fix_coords = [coord[:2] for coord in self.fixados]
        for sqr in self.block.coords:
            if [sqr[0], sqr[1]+1] in fix_coords or sqr[1] == 19:
                self.block.block_down = True
            if [sqr[0]+1, sqr[1]] in fix_coords or sqr[0] == 9:
                self.block.block_right = True
            if [sqr[0]-1, sqr[1]] in fix_coords or sqr[0] == 0:
                self.block.block_left = True

        if self.block.block_down:
            self.touch_frames += 1
        else:
            self.touch_frames = 0

        if self.touch_frames == 100:
            self.fixados.extend([[coord[0], coord[1], self.block.image] for coord in self.block.coords])
            self.delete_line()
            self.new_block()
            self.touch_frames = 0

    def delete_line(self):
        ys = [0 for _ in range(20)]
        for coord in self.fixados:
            ys[coord[1]] += 1
        deletions = []
        for y in range(len(ys)):
            if ys[y] == 10:
                deletions.append(y)
        self.fixados = [coord for coord in self.fixados if coord[1] not in deletions]
        for coord in self.fixados:
            for deletion in deletions:
                if coord[1] < deletion:
                    coord[1] += 1
        self.points += int(len(deletions)**1.5 * 10)

    def move_handler(self):
        for key in self.keys_pressed:
            if key == pygame.K_LEFT:
                self.block.left()
            elif key == pygame.K_RIGHT:
                self.block.right()
            elif key == pygame.K_UP:
                Thread(target=self.block.rotate, kwargs={"fixed": self.fixados}).start()
            elif key == pygame.K_DOWN:
                if self.block.down():
                    self.points += 1

    def blit(self):
        for block in self.fixados:
            self.tela.blit(block[2], (block[0] * SQUARE_SIZE, block[1] * SQUARE_SIZE))

        pygame.draw.rect(self.tela, (100, 100, 100), ((10*SQUARE_SIZE, 0), (6*SQUARE_SIZE, 20*SQUARE_SIZE)))
        pygame.draw.rect(self.tela, (10, 10, 10), ((11 * SQUARE_SIZE, SQUARE_SIZE), (4 * SQUARE_SIZE, 4 * SQUARE_SIZE)))
        self.next.show(SQUARE_SIZE*13, SQUARE_SIZE*3)
        points_img = pygame.font.SysFont('Agency FB', 40, True).render(f"Points: {self.points}", True, (255, 255, 255))
        self.tela.blit(points_img, (SQUARE_SIZE*11, SQUARE_SIZE*8))

    def loop(self):
        frames = 1
        fpdown = 100
        while self.running:
            self.tela.fill((30, 30, 30))
            if frames % int(fpdown) == 0:
                self.block.down()
            self.event_handler()
            if frames % 5 == 0:
                self.move_handler()
            if frames % 3000 == 0 and fpdown > 20:
                fpdown *= 0.80

            self.block.blit()
            self.blit()
            pygame.display.update()
            frames += 1
            sleep(0.01)

    def new_block(self):
        self.block = self.next
        self.next = choice([Square, Line, Z, S, L, J, T])(self.tela)


gm = Game()
gm.loop()
print(gm.points)
