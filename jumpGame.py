import pygame
import random

class JumpGame:

    winSize = (800, 800)
    fontObj = None

    def __init__(self):
        pygame.init()
        pygame.font.init()
        JumpGame.fontObj = pygame.font.Font('SDMiSaeng.ttf', 64)
        
        self.win = pygame.display.set_mode(JumpGame.winSize)
        pygame.display.set_caption("Jump Game")

        self.run = True
        self.win_run = True
        self.dTime = 20

        self.pObj = Player(self.win)
        self.wObj = Wall()

    def moveManager(self):
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_LEFT]:
            self.pObj.move("left")
        if keys[pygame.K_RIGHT]:
            self.pObj.move("right")
        if not(self.pObj.isJump) and self.pObj.isGround:
            if keys[pygame.K_SPACE]:
                self.pObj.isJump = True
                self.pObj.isGround = False
        elif self.pObj.isJump:
            self.pObj.move("jump", wObj = self.wObj)
        if not(self.pObj.isJump):
            self.pObj.move("fall", wObj = self.wObj)
                    
    def gameStart(self):
        while self.win_run:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.win_run = False

            if self.run:
                pygame.time.delay(self.dTime)
                
                self.moveManager()
                self.wObj.createWall(self.win)
                
                self.win.fill((0, 0, 0))
                
                self.wObj.draw(self.win)
                self.pObj.draw()
                self.pObj.scorePrint()

                self.gameoverCheck()
                
                pygame.display.update()
            else:
                self.gameover()

        pygame.quit()

    def gameoverCheck(self):
        if self.pObj.playerDead:
            textSurfaceObj = JumpGame.fontObj.render("R : 다시하기 / Q : 끄기", True, (255, 255, 255))
            textRectObj = textSurfaceObj.get_rect()
            textRectObj.center = (JumpGame.winSize[0]/2, JumpGame.winSize[1]/2)

            self.win.blit(textSurfaceObj, textRectObj)
            self.run = False

    def gameover(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_r]:
            self.pObj = Player(self.win)
            self.wObj = Wall()

            self.run = True
        if keys[pygame.K_q]:
            self.win_run = False

class Player:

    pSize = (20, 20)
    vel = 5
    jDegree = 0.03
    pH_limit = 400

    def __init__(self, win):
        self.win = win
        
        self.x, self.y = 300, (JumpGame.winSize[1] - 50)
        self.isJump = False
        self.isGround = True
        self.fallCount = 1
        self.jumpCount = 20

        self.player_h = 0
        self.max_wh = 0

        self.score = 0
        self.playerDead = False

    def draw(self):
        pygame.draw.rect(self.win,
                         (255, 255, 255),
                         (self.x, self.y, Player.pSize[0], Player.pSize[1]))

    def move(self, moveType, wObj = None):
        if moveType is "left" and self.x > 0:
            self.x -= Player.vel
        if moveType is "right" and self.x < JumpGame.winSize[0] - Player.pSize[0]:
            self.x += Player.vel
        if moveType is "jump":
            if self.jumpCount > 0:
                jump = (self.jumpCount ** 2) * Player.jDegree

                if (self.y - jump) < Player.pH_limit:
                    degree = abs(self.y - jump - Player.pH_limit)
                    
                    wObj.moveWall(JumpGame.winSize[1], degree)
                    self.y = Player.pH_limit
                else:
                    self.y -= jump
                    
                self.jumpCount -= 1

                self.heightManager(jp = jump)
            else:
                self.isJump = False
                self.jumpCount = 20
        if moveType is "fall":
            fall = (self.fallCount ** 2) * Player.jDegree
            status = self.groundCheck(wObj, fall)

            if status is "air":
                self.isGround = False
                
                self.heightManager(fl = fall)
                
                self.y += fall
                if self.fallCount < 20:
                    self.fallCount += 1
            elif status is "ground":
                if self.score is 0:
                    tmp = self.y
                    self.y = JumpGame.winSize[1] - Player.pSize[1]

                    self.heightManager(fl = (self.y - tmp))
                else:
                    self.playerDead = True
            else:
                tmp = self.y
                self.y = wObj.walls_p[status][1] - Player.pSize[1]

                self.heightManager(fl = (self.y - tmp))

                self.scoreManager(self.player_h)

    def heightManager(self, jp = 0, fl = 0):
        if fl is 0:
            self.player_h += jp
        else:
            self.player_h -= fl

    def scoreManager(self, height):
        if self.max_wh + 1 < height:
            self.max_wh = height
            self.score += 1

    def scorePrint(self):
        textSurfaceObj = JumpGame.fontObj.render(str(self.score) + " 점", True, (255, 255, 255))
        textRectObj = textSurfaceObj.get_rect()
        textRectObj.center = (JumpGame.winSize[0]/2, 35)

        self.win.blit(textSurfaceObj, textRectObj)
        
    def groundCheck(self, wObj, fall):
        if self.y + fall >= (JumpGame.winSize[1] - Player.pSize[1]) and \
        self.y <= (JumpGame.winSize[1] - Player.pSize[1]):
            self.isGround = True
            self.fallCount = 1

            return "ground"
        else:
            for x in range(len(wObj.walls_p)):
                if ((wObj.walls_p[x][0] - Player.pSize[0]) <= self.x <= (wObj.walls_p[x][0] + wObj.walls_s[x][0])) and \
                self.y + fall >= (wObj.walls_p[x][1] - Player.pSize[1]) and \
                self.y <= (wObj.walls_p[x][1] - Player.pSize[1]):
                    self.isGround = True
                    self.fallCount = 1

                    return x
            else:
                return "air"
    
class Wall:

    def __init__(self):
        self.walls_s = list([(150, 20)])
        self.walls_p = list([[250, JumpGame.winSize[1]-20]])
        self.walls_c = list([(0,255,255)])

        self.w_interval = 160
        self.h_interval = 80
        self.mh_interval = 50

        self.max_width = 150
        self.max_height = 80
        self.minimum_s = 30

    def draw(self, win):
        for x in range(len(self.walls_p)):
            pygame.draw.rect(win,
                             self.walls_c[len(self.walls_c) - 1 - x],
                             (self.walls_p[len(self.walls_p) - 1 - x][0],
                              self.walls_p[len(self.walls_p) - 1 - x][1],
                              self.walls_s[len(self.walls_s) - 1 - x][0],
                              self.walls_s[len(self.walls_s) - 1 - x][1]))

    def createWall(self, win):
        while True:
            last_x = self.walls_p[len(self.walls_p)-1][0]
            last_y = self.walls_p[len(self.walls_p)-1][1]
            last_w = self.walls_s[len(self.walls_s)-1][0]

            if self.walls_p[len(self.walls_p)-1][1] < (-1 * self.max_height):
                break

            self.walls_s.append((random.randint(self.minimum_s, self.max_width),
                                 random.randint(self.minimum_s, self.max_height)))

            left_x = last_x - self.w_interval - self.walls_s[len(self.walls_s)-1][0] 
            right_x = last_x + last_w + self.w_interval

            if left_x < 0:
                left_x = 0
            if (right_x + self.minimum_s) > JumpGame.winSize[0]:
                right_x = JumpGame.winSize[0] - self.minimum_s

            self.walls_p.append([random.randint(left_x, right_x),
                                 random.randint(int(round(last_y - self.h_interval)), int(round(last_y - self.mh_interval)))])
            self.walls_c.append(tuple([random.randint(30, 225) for x in range(3)]))

    def moveWall(self, winHeight, degree):
        check = False
        
        for x in self.walls_p:
            x[1] += degree

            if x[1] > winHeight:
                check = True

        if check:
            del self.walls_p[0]
            del self.walls_s[0]
            del self.walls_c[0]
            
            
test = JumpGame()

test.gameStart()
