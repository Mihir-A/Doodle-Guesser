import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'
from threading import Thread
import pygame, sys, time
import numpy as np

class_names = []
class_guessed = []

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0 , 0)
GREEN = (0, 255, 0)

NUMSQUARES = 28
SQUAREWIDTH = 20
MAXFPS = 60

font = None
start_time = time.time()
end_time = time.time()

def main():

     pygame.display.init()

     screen = pygame.display.set_mode((int(NUMSQUARES * SQUAREWIDTH * 2), (NUMSQUARES + 2) * SQUAREWIDTH))
     pygame.display.set_caption("Doodle Prediction")

     file_directory = os.path.dirname(os.path.abspath(sys.argv[0]))
     os.chdir(file_directory)

     global font
     pygame.font.init()
     font = pygame.font.Font(os.path.join(os.getcwd(), 'freesansbold.ttf'), 28)

     grid = np.zeros((NUMSQUARES, NUMSQUARES), dtype=int)


     model = load_screen(screen)
     with open('data/labels.lbl', 'r') as file:
          for line in file:
               class_names.append(line.strip())
     global class_guessed
     class_guessed = [False] * len(class_names)

     running = True
     md = False

     probability = 0
     guess = 0

     global start_time
     start_time = time.time()

     while running:
          pygame.time.Clock().tick(MAXFPS)
          for event in pygame.event.get():

               if event.type == pygame.QUIT:
                    running = False
                    return
               
               if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    x, y = click_to_idx(pygame.mouse.get_pos(), SQUAREWIDTH)
                    if x >= 0 and x < NUMSQUARES and y >= 0 and y < NUMSQUARES:
                         md = True
                         down = not grid[y][x]

               if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    md = False
                    centered = center(grid)
                    guess, probability = predict(centered, model)
                    verify(guess, probability)

               if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    clear_grid(grid)
                    centered = center(grid)
                    guess, probability = predict(centered, model)
                    
          x, y = click_to_idx(pygame.mouse.get_pos(), SQUAREWIDTH)
          if md and x >= 0 and x < NUMSQUARES and y >= 0 and y < NUMSQUARES:
               try:
                    grid[y][x] = down
                    grid[y + 1][x] = down
                    grid[y + 1][x + 1] = down
                    grid[y][x + 1] = down
               except:
                    pass

          screen.fill(WHITE)
          draw_grid(screen, NUMSQUARES, SQUAREWIDTH, grid)
          draw_text(screen, guess, probability)
          pygame.display.flip()

def draw_grid(screen, numSqaures, width, grid):
     for x in range(0, numSqaures):
          for y in range(0, numSqaures):
               if grid[y][x] == True:
                    pygame.draw.rect(screen, BLACK, (x * width, y * width, width, width))
               else:
                    pygame.draw.rect(screen, BLACK, (x * width, y * width, width, width), width=1)

def click_to_idx(point, width):
     return (int(point[0] / width), int(point[1] / width))

def predict(grid, model):
     predict = model.predict(np.array([grid]), verbose=0)
     return (class_names[np.argmax(predict)], np.max(predict))

def verify(guess, probability):
     if probability > 0.75:
          class_guessed[class_names.index(guess)] = True

def center(list):
     sumX = 0
     sumY = 0
     count = 0
     for x in range(len(list)):
          for y in range(len(list[x])):
               if (list[x][y] == 1):
                    sumX += x
                    sumY += y
                    count += 1

     if (count == 0):
          return list
     xTranslate = 14 - sumX//count
     yTranslate = 14 - sumY//count
     new = np.zeros((28, 28))

     for x in range(len(list)):
          for y in range(len(list[x])):
               try:
                    if (list[x][y] == 1):
                         new[int(x + xTranslate)][int(y + yTranslate)] = 1
               except:
                    pass
     return new

def draw_text(screen, guess, probability):
     draw_info_text(screen, font)
     
     if probability > 0.75:
          infotext = font.render('Prediction: ' + str(guess) + ' (' + str(round(probability * 100, 2)) + '% sure)', True, BLACK)
     else:
          infotext = font.render('Prediction: Not sure', True, BLACK)
     textRect = infotext.get_rect()
     textRect.midleft = (0, 580)


     screen.blit(infotext, textRect)

def draw_info_text(screen, font):
     max_width = 580
     infotext = "Info: A doodle guesser. Press space to clear the canvas. See how quickly you can draw all of the follow objects: "
     words = infotext.split()
     lines = []
     current_line = ""
     for word in words:
          test_line = current_line + word + " "
          if font.size(test_line)[0] <= max_width:
               current_line = test_line
          else:
               lines.append(current_line)
               current_line = word + " "

     lines.append(current_line)

     y = 0
     for line in lines:
         text_surface = font.render(line, True, BLACK)
         screen.blit(text_surface, (565, y))
         y += int(font.get_linesize() * 1)

     for i in range(len(class_names)):
          text_surface = font.render(class_names[i], True, GREEN if class_guessed[i] else RED)
          screen.blit(text_surface, (565, y))
          y += int(font.get_linesize() * 1)

     end_time = end_time if all(class_guessed) else time.time()
     text_surface = font.render("Time: " + str(round(end_time - start_time, 1)), True, BLACK)
     screen.blit(text_surface, (565, y))


def clear_grid(grid):
     for x in range(0, len(grid)):
          for y in range(0, len(grid)):
               grid[y][x] = False

def load_screen(screen):
     modela = [None]
     loading_thread = Thread(target=load_model, args=(modela,))
     loading_thread.start()

     while loading_thread.is_alive():
          for event in pygame.event.get():
               if event.type == pygame.QUIT:
                    exit(0)

          screen.fill(WHITE)
          text_surface = font.render("Loading Model...", True, BLACK)
          text_rect = text_surface.get_rect(center=(NUMSQUARES * SQUAREWIDTH, ((NUMSQUARES + 2) * SQUAREWIDTH) / 2))

          screen.blit(text_surface, text_rect)
          pygame.display.flip()
     return modela[0]

def load_model(model):
     from keras.models import load_model
     model[0] = load_model('doodleModel.h5')

if __name__ == '__main__':
    main()