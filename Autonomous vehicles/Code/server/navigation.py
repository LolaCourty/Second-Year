import cv2
import numpy as np


minimap = 255*np.ones((600, 500, 3))


def clear_minimap():
    global minimap
    minimap = 255*np.ones((600, 500, 3))

def get_minimap():
    return minimap

def display_image(img, title=""):
    cv2.imshow(title, img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def update_minimap(x, y, actor="robot", direction="N"):
    global minimap

    interval = (470-30)//4
    if np.all(minimap == 255*np.ones((600, 500, 3), dtype="uint8")):
        minimap = cv2.rectangle(minimap, (30, 30), (470, 470), (0, 0, 0), 3)
        for i in range(1, 4):
            minimap = cv2.line(minimap, (30+interval*i, 30),
                               (30+interval*i, 470), (0, 0, 0), 3)
        for i in range(1, 4):
            minimap = cv2.line(minimap, (30, 30+interval*i),
                               (470, 30+interval*i), (0, 0, 0), 3)
        minimap = cv2.line(minimap, (300, 520),
                           (470, 520), (0, 0, 0), 3)
    circle_x = 30 + interval*x
    circle_y = 30 + interval*y
    if actor == "robot":
        minimap = cv2.circle(
            minimap, (circle_x, circle_y), 15, (255, 255, 0), -1)
        if direction == "E":
            minimap = cv2.circle(
                minimap, (circle_x + 10, circle_y), 4, (0, 255, 255), -1)
        elif direction == "W":
            minimap = cv2.circle(
                minimap, (circle_x - 10, circle_y), 4, (0, 255, 255), -1)
        elif direction == "N":
            minimap = cv2.circle(
                minimap, (circle_x, circle_y-10), 4, (0, 255, 255), -1)
        if direction == "S":
            minimap = cv2.circle(
                minimap, (circle_x, circle_y + 10), 4, (0, 255, 255), -1)
    elif actor == "villain":
        minimap = cv2.circle(
            minimap, (circle_x, circle_y), 15, (255, 0, 0), -1)
        if direction == "E":
            minimap = cv2.circle(
                minimap, (circle_x + 10, circle_y), 4, (0, 255, 255), -1)
        elif direction == "W":
            minimap = cv2.circle(
                minimap, (circle_x - 10, circle_y), 4, (0, 255, 255), -1)
        elif direction == "N":
            minimap = cv2.circle(
                minimap, (circle_x, circle_y-10), 4, (0, 255, 255), -1)
        if direction == "S":
            minimap = cv2.circle(
                minimap, (circle_x, circle_y + 10), 4, (0, 255, 255), -1)
    elif actor == "obstacle":
        minimap = cv2.rectangle(
            minimap, (circle_x-15, circle_y-15), (circle_x+15, circle_y+15), (0, 0, 255), -1)


if __name__ == "__main__":
    update_minimap(3, 2, "robot", "W")
    update_minimap(2, 4, "villain")
    update_minimap(0, 1, "obstacle")
    display_image(get_minimap())
