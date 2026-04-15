import cv2 as cv
from time import sleep



def grille_pix(px:int, py:int, ecart:int, nb:int):
    offset = (nb // 2) * ecart
    
    pix = []
    for x in range(nb):
        for y in range(nb):
            pix.append((px - offset + x * ecart,
                        py - offset + y * ecart))
    return pix

class Camera:
    def __init__(self):
        self.camera = cv.VideoCapture(0)

    def frame(self):
        ret, frame = self.camera.read()
        return frame
    
    def save(self,frame):
        cv.imwrite("photo.jpg", frame)
        
    def get_pixel_color(self, frame, x, y):
        b, g, r = frame[y, x]
        return int(r), int(g), int(b)
    
    
    def grille_verte(self, frame, pixels):
        vert = 0
        
        for x, y in pixels:
            r, g, b = self.get_pixel_color(frame, x, y)
            
            if g > 150 and g > r and g > b:
                vert += 1
                
        return vert > len(pixels)/2
    
    def grille_rouge(self, frame, pixels):
        rouge = 0
        
        for x, y in pixels:
            r, g, b = self.get_pixel_color(frame, x, y)
            
            if r > 150 and r > b and r > g:
                rouge += 1
                
        return rouge > len(pixels)/2

    def release(self):
        self.camera.release()
        cv.destroyAllWindows()


if __name__ == "__main__":
    cam = Camera()
    
    gri = grille_pix(100,100,5,10)
    try:
        while True:
            frame = cam.frame()
            
            for pix in gri:
                x,y = pix
                frame = cam.write_pixel(frame, x, y)
                
                
            cam.save(frame)

    except KeyboardInterrupt:
        print("Arrêt manuel")

    except Exception as e:
        print(f"Erreur : {e}")

    finally:
        cam.release() 