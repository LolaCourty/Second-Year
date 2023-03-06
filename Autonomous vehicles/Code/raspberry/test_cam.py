import cv2
import numpy as np
from numpy.lib.function_base import disp
import time

print(cv2.CAP_DSHOW)
cap = cv2.VideoCapture(0 + cv2.CAP_DSHOW)
if not cap.isOpened():
    raise IOError("Cannot open webcam")


cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
cap.set(cv2.CAP_PROP_FPS, 10)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

zone_width = 300
zone_top = 150
speed = 100
steer_ratio = 100

isRunning = False

current_pos = (0, 0)
direction = "N"
path = []


def display_image(img, title=""):
    cv2.imshow(title, img)


def compute_intersection_direction(next_coord):
    """says if the robot should go right left or straight at the next intersection"""
    if next_coord[0] < current_pos[0]:
        # W
        if next_coord[1] < current_pos[1]:
            # NW
            if direction == "N":
                next_turn = "W"
            else:
                next_turn = "N"
        else:
            # SW
            if direction == "S":
                next_turn = "W"
            else:
                next_turn = "S"
    else:
        # E
        if next_coord[1] < current_pos[1]:
            # NE
            if direction == "N":
                next_turn = "E"
            else:
                next_turn = "N"
        else:
            # SE
            if direction == "S":
                next_turn = "E"
            else:
                next_turn = "S"
    
    return next_turn


def cross_intersection(serial_file, intersection_direction):
    """goes on the intersection and face the proper direction"""
    helpers.reset_encoder(serial_file)
    helpers.move(serial_file,100,0)
    time.sleep(2)
    helpers.move(serial_file,0,0)
    right_enc = helpers.read_encoder_r(serial_file)
    left_enc = helpers.read_encoder_l(serial_file)
    return str(right_enc) + "/" + str(left_enc)


def card_to_number(card_dir):
    if card_dir == "N":
        return 0
    elif card_dir == "E":
        return 1
    elif card_dir == "S":
        return 2
    else:
        return 3


def card_to_rel(card_dir):
    rel_of_card = ["F", "R", "B", "L"]  # Assuming card_dir == "N"
    
    shift = card_to_number(direction)

    # Shift the list
    for i in range(shift):
        rel_of_card.insert(0, rel_of_card.pop())

    return rel_of_card[card_to_number(card_dir)]


def card_to_rel(card_dir):
    pass


def expected_intersection(coords):
    res = []
    x, y = coords
    if x < 8:
        res += ["E"]
    if x > 0:
        res += ["W"]
    if y < 8:
        res += ["S"]
    if x > 0:
        res += ["N"]
    return res


def find_intersection(img, contour, zone_left, zone_right, drive_robot, serial_file):
    h, w = img.shape[:2]

    img = cv2.line(img, (zone_left, zone_top), (zone_right, zone_top),
                   (255, 0, 0), thickness=3)
    img = cv2.line(img, (zone_left, zone_top), (zone_left, h),
                   (255, 0, 0), thickness=3)
    img = cv2.line(img, (zone_right, zone_top), (zone_right, h),
                   (255, 0, 0), thickness=3)
    contour = contour[0]
    old_x = contour[0, 0, 0]
    old_y = contour[0, 0, 1]
    top_counter = 0
    right_counter = 0
    left_counter = 0
    for [[x, y]] in contour[1:]:
        if y >= zone_top or old_y >= zone_top:
            if (zone_right <= x and zone_right >= old_x) or (zone_right >= x and zone_right <= old_x):
                # line is coming from the right
                right_counter += 1
                img = cv2.line(img, (old_x, old_y), (x, y),
                               (0, 0, 255), thickness=3)
            if (zone_left <= x and zone_left >= old_x) or (zone_left >= x and zone_left <= old_x):
                # line is coming from the left
                left_counter += 1
                img = cv2.line(img, (old_x, old_y), (x, y),
                               (0, 0, 255), thickness=3)
        if (x <= zone_right and x >= zone_left) or (old_x <= zone_right and old_x >= zone_left):
            if (y <= zone_top and old_y >= zone_top) or (y >= zone_top and old_y <= zone_top):
                # line is coming from the top
                top_counter += 1
                img = cv2.line(img, (old_x, old_y), (x, y),
                               (0, 255, 255), thickness=3)
        old_x = x
        old_y = y
    # print("top : ", top_counter, ", right : ",right_counter, ", left : ", left_counter)
    nb_directions = int(bool(top_counter)) + int(bool(right_counter)) + int(bool(left_counter))
    # print("NB DIRECTIONS : ", nb_directions)

    if nb_directions > 1 or top_counter == 0:
        pass
        #print("INTERSECTION DETECTED!")

    return img


def center_line(img, contour, cx, cy, serial_file, drive_robot):
    h, w = img.shape[:2]
    zone_left = int(w/2) - int(zone_width/2)
    zone_right = int(w/2) + int(zone_width/2)
    img = find_intersection(img, contour, zone_left,
                            zone_right, drive_robot, serial_file)

    if drive_robot:
        # continuous line centering
        middle_line = w / 2
        dist = (cx - middle_line)/middle_line
        ratio = -(steer_ratio/100)*dist
        helpers.move(serial_file, speed=speed, ratio=ratio)

    return img


def pre_processing(img):
    # Compute image gradient to find edges
    laplacian = cv2.Laplacian(img,cv2.CV_64F)
    blur = cv2.blur(laplacian, (5, 5))

    
    blur = cv2.convertScaleAbs(blur,alpha=255/blur.max()) # Convert image back to uint
    # Gray scale    

    # Take the highest values
    # threshold: 180 is the threshold, 255 is the value replaced if we are higher than the threshold

    # Remove noise
    # kernel_erode = np.ones((2, 2), np.uint8)
    # eroded_mask = cv2.erode(blur, kernel_erode, iterations=1)
    # kernel_dilate = np.ones((4, 4), np.uint8)
    # dilated_mask = cv2.dilate(eroded_mask, kernel_dilate, iterations=1)
    
    blur = cv2.cvtColor(blur,cv2.COLOR_BGR2GRAY)
    ret,blur = cv2.threshold(blur,60,255,cv2.THRESH_BINARY)
    return blur

def process_image(img, serial_file, drive_robot=True):
    global zone_width
    global zone_top
    h, w = img.shape[:2]

    pre_processed_img = pre_processing(img)
    # Find the different contours
    return pre_processed_img


    # Sort by area (keep only the biggest one)
    contour = sorted(contours, key=cv2.contourArea, reverse=True)[:1]

    if len(contour) > 0:
        image_contour = cv2.drawContours(img, contour, 0, (0, 255, 0), 3)

        M = cv2.moments(contour[0])
        # Centroid
        cx = int(M['m10']/M['m00'])
        cy = int(M['m01']/M['m00'])
        processed_image = cv2.circle(image_contour, (cx, cy), 20, (255, 0, 0), 2)
        processed_image = center_line(processed_image, contour, cx, cy, serial_file, drive_robot)
        return processed_image

    else:
        pass
        return img


def go_to_target(serial_file, pos_dest, pos_init, direction_init):
    global isRunning
    isRunning = True
    # isRunning is set to False in abort_auto

    global current_pos, direction
    current_pos = pos_init
    direction = direction_init
    # PATHFINDING init(current_pos, pos_dest)
    #init((0,0), (4,4))[1:]
    global path
    path = [(1, 0), (2, 0), (3, 0), (4, 0),(4, 1), (4, 2), (4, 3), (4, 4)]

    while isRunning:
        ret, frame = cap.read()
        if frame is not None:
            frame = process_image(frame, serial_file, True)
        else:
            print("Unable to access camera!!")
            break


def get_feedback_image():
    ret, frame = cap.read()
    if frame is None:
        return
    frame = process_image(frame, None, False)
    return frame


def abort_auto():
    global isRunning
    isRunning = False


def set_zone_width(w):
    global zone_width
    zone_width = w


def set_steer_ratio(r):
    global steer_ratio
    steer_ratio = r


def set_zone_top(t):
    global zone_top
    zone_top = t


def set_speed(s):
    global speed
    speed = s


if __name__ == "__main__":

    while True:
        img = get_feedback_image()
        if img is not None:
            display_image(img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
          break
