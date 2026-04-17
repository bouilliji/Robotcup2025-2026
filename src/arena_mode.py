def arene_init(self):
    print("arene init")
    self.motor.setMotor(0, 0)
    self.raisearm(False)
    self.grab(False)
    
    self.captured = 0

def raisearm(self, up):
    if up:
        self.servo_raising.go_to(20)
    else:
        self.servo_raising.go_to(160)

def slow_servo(self, servo, t, prec, pos_ini, pos_cib):
    # not instant servo turn (temps,nombre d'étape,position initial, position visée)
    for i in range(prec):
        servo.go_to(pos_ini - ((pos_ini - pos_cib) / prec) * i)
        time.sleep(t / prec)

def grab(self, state):
    # grab de la pince
    if state:
        self.servo_pliers.go_to(100)
        self.state_grab = True

    else:
        self.servo_pliers.go_to(0)
        self.state_grab = False

def recherche_ball(self):
    while True:
        print("recherche balls")
        self.motor.setMotor(0, -40)
        time.sleep(0.10)
        self.motor.setMotor(0, 0)
        res = self.analyse_yolo()
        ob = self.read_result(res)
        if len(ob) > 0 :                               #ball detecter
            if ob[0]["label"]==True or self.captured > 1 : #priosise les ball vivante
                return

def analyse_yolo(self):
    print("analyse yolo")
    # cam.capture_image()
    pict = self.cam.frame()  # get PIL image
    # self.cam.save() # save cam content
    results = self.model.predict(pict, verbose=False, conf=0.5)

    # frame = results[0].plot()

    # cv2.imwrite("img.png",frame)
    #pict.save("img.jpg")

    return results

def dist_milieu(self, x1, x2):
    mid = (x1 + x2) / 2
    return mid - 320

def read_result(self, results):
    objects = []
    result = results[0]

    for i, box in enumerate(result.boxes):
        cls_id = int(box.cls)
        # label = self.model.names[cls_id]
        # conf = float(box.conf)
        x1, y1, x2, y2 = box.xyxy[0].tolist()

        if cls_id == 0:
            objects.insert(
                0,
                {
                    "width": abs(y2 - y1),
                    "mid_dist": self.dist_milieu(x1, x2),
                    "lab": True,
                },
            )
        else:
            objects.append(
                {
                    "width": abs(y2 - y1),
                    "mid_dist": self.dist_milieu(x1, x2),
                    "lab": False,
                }
            )
    return objects

def grab_ball(self):
    while True:
        res = self.analyse_yolo()
        balls = self.read_result(res)

        if len(balls) > 0:
            ball = balls[0]
            mid = ball["mid_dist"]
            width = ball["width"]
            label = ball["lab"]

            m = min(abs(mid), 100) * 0.01
            if mid > 30:
                self.motor.setMotor(30, -30)
                time.sleep(0.2 * m)
                self.motor.setMotor(0, 0)
                print("go right")

            elif mid < -30:
                self.motor.setMotor(-30, 30)
                time.sleep(0.2 * m)
                self.motor.setMotor(0, 0)
                print("go left")

            else:
                print("go forward")
                if width < 140:
                    self.motor.setMotor(-40, -40)
                    time.sleep(0.2)
                    self.motor.setMotor(0, 0)
                else:
                    self.lock_in_ball()
                    return label

        else:
            print("no ball detected")
            self.motor.setMotor(30, 30)
            time.sleep(0.2)
            self.motor.setMotor(0, 0)

def deliver_ball(self, ball_alive):
    while True:
        pass

def lock_in_ball(self):
    self.motor.setMotor(-40, -40)
    time.sleep(0.5)
    self.motor.setMotor(0, 0)

    self.grab(True)

    self.has_ball = True
    
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