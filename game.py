import pygame
import time
import math

def scale_image(img,factor):
    size = round(img.get_width()*factor),round(img.get_height()*factor)
    return pygame.transform.scale(img,size)
def blitz_rotate_center(win ,image ,top_left,angle):
    rotated_image =pygame.transform.rotate(image,angle)
    new_rect =rotated_image.get_rect(center=image.get_rect(topleft=top_left).center)
    win.blit(rotated_image,new_rect.topleft)

GRASS = scale_image(pygame.image.load("grass.jpg"),2.5)
TRACK = scale_image(pygame.image.load("track.png"),0.8)
TRACK_BORDER = scale_image(pygame.image.load("track-border.png"),0.8)
TRACK_BORDER_MASK = pygame.mask.from_surface(TRACK_BORDER)
FINISH = scale_image (pygame.image.load("finish.png"),0.7)
FINISH_MASK = pygame.mask.from_surface(FINISH)
FINISH_POSITION =(125,250)
RED_CAR = scale_image(pygame.image.load("red-car.png"),0.5)
GREEN_CAR = scale_image(pygame.image.load("green-car.png"),0.5)

WIDTH ,HEIGHT =TRACK.get_width(),TRACK.get_height()
WIN = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("Racing Game ")

FPS =60
PATH =[(149, 106), (105, 62), (54, 104), (54, 398), (302, 652), (351, 594), (360, 496), (406, 433), (485, 434), (530, 526), (545, 638), (652, 639), (646, 371), (593, 318), (390, 322), (348, 274), (397, 222), (611, 226), (654, 169), (642, 77), (275, 70), (238, 140), (245, 266), (233, 354), (165, 342), (143, 255), (145, 193)]

class AbstractCar:
    def __init__(self,max_vel,rotation_vel):
        self.img =self.IMG
        self.max_vel = max_vel
        self.vel =0
        self.rotation_vel=rotation_vel *2
        self.angle =0
        self.x ,self.y = self.START_POS
        self.acce  = 0.1

    def rotate(self,left=False,right=False):
        if left:
            self.angle += self.rotation_vel
        elif right:
            self.angle -=self.rotation_vel

    def draw(self,win):
        blitz_rotate_center(win,self.img,(self.x ,self.y),self.angle)

    def move_forward(self):
        self.vel =min(self.vel+self.acce,self.max_vel)
        self.move()

    def move_backward(self):
        self.vel =max(self.vel-self.acce,-self.max_vel/2)
        self.move()

    def move(self):
        radians = math.radians(self.angle)
        vertical =math.cos(radians)*self.vel
        horizontal=math.sin(radians)*self.vel

        self.y -=vertical
        self.x -=horizontal

    def collide(self,mask,x=0,y=0):
        car_mask =pygame.mask.from_surface(self.img)
        offset=(int(self.x-x),int(self.y-y))
        poi =mask.overlap(car_mask,offset)
        return poi
    
    def reset(self):
        self.x,self.y =self.START_POS
        self.angle=0
        self.vel=0

    
class PlayerCar(AbstractCar):
    IMG=RED_CAR
    START_POS =(162,200)

    def reduce_speed(self):
        self.vel=max(self.vel-self.acce/2,0)
        self.move()
    
    def bounce(self):
        self.vel = -self.vel
        self.move()

class Computercar(AbstractCar):
    IMG=GREEN_CAR
    START_POS = (135,200)

    def __init__(self,max_vel,rotation_vel,path=[]):
        super().__init__(max_vel,rotation_vel)
        self.path = path
        self.current_point =0
        self.vel = max_vel
    def draw_points(self,win):
        for point in self.path:
            pygame.draw.circle(win,(128, 128, 128),point,5)
    def draw(self,win):
        super().draw(win)
        self.draw_points(win)
    def calculate_angle(self):
        target_x ,target_y = self.path[self.current_point]
        x_diff =target_x-self.x
        y_diff =target_y -self.y

        if y_diff ==0:
            desired_radian_angle = math.pi/2
        else:
            desired_radian_angle = math.atan(x_diff/y_diff)
        if target_y > self.y:
            desired_radian_angle +=math.pi

        difference_in_angle =self.angle - math.degrees(desired_radian_angle)
        if difference_in_angle >=180 :
            difference_in_angle -=360

        if difference_in_angle>0:
            self.angle -= min(self.rotation_vel ,abs(difference_in_angle))
        else:
            self.angle += min(self.rotation_vel ,abs(difference_in_angle))
    def update_path_point(self):
        target = self.path[self.current_point]  
        rect =pygame.Rect(self.x,self.y,self.img.get_width(),self.img.get_height())
        if rect.collidepoint(*target):
            self.current_point +=1         

    def move(self):
        if self.current_point >=len(self.path):
            return
        
        self.calculate_angle()
        self.update_path_point()
        super().move()

def draw(win,images,player_car,computer_car):
    for img,pos in images:
        win.blit(img,pos)

    player_car.draw(win)
    computer_car.draw(win)
    pygame.display.update()

def move_player(player_car):
    keys =pygame.key.get_pressed()
    moved =False
    if keys[pygame.K_a]:
        player_car.rotate(left=True)
    if keys[pygame.K_d]:
        player_car.rotate(right=True)
    if keys[pygame.K_w]:
        moved=True
        player_car.move_forward()
    if keys[pygame.K_s]:
        moved=True
        player_car.move_backward()
    if not moved:
        player_car.reduce_speed()
    
clock =pygame.time.Clock()
images =[(GRASS,(0,0)),(TRACK,(0,0)),(FINISH,FINISH_POSITION),(TRACK_BORDER,(0,0))]

player_car =PlayerCar(2,2)
computer_car =Computercar(1,1,PATH)

run =True
while run:
    clock.tick(FPS)
    draw(WIN,images,player_car,computer_car)

    for event in pygame.event.get():
        if event.type ==pygame.QUIT:
            run =False
            break
        if event.type ==pygame.MOUSEBUTTONDOWN :
            pos =pygame.mouse.get_pos()
            computer_car.path.append(pos)
    move_player(player_car)
    computer_car.move()

    if player_car.collide(TRACK_BORDER_MASK)!=None:
          player_car.bounce()
    finish_poi_collide = player_car.collide(FINISH_MASK,*FINISH_POSITION)
    if finish_poi_collide !=None:
        if finish_poi_collide[1]==0:
         player_car.bounce()
        else:
            player_car.reset()
            print("Finished")
print(computer_car.path)
pygame.quit()
