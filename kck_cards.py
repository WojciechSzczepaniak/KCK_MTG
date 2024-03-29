import numpy as np
import cv2 as cv
from pathlib import Path
import os.path



def resizeImage(image, size, proportional):
    if proportional:
        h, w = image.shape[:2]
        factor = min(size[0] / h, size[1] / w)
        return cv.resize(image, None, fx = factor, fy = factor)
    return cv.resize(image, None, size)

def drawContours(image, contours):
    for i in range(0, len(contours)):
        color = (0, 0, 0)
        cv.drawContours(image, contours, i, color, -1)
        #cv.fillPoly(image, pts=[contours], color=(255, 255, 255))
        M = cv.moments(contours[i])
        cx = int(M['m10']/M['m00'])
        cy = int(M['m01']/M['m00'])
        cv.circle(image, (cx, cy), 2, (255, 255, 255), 2)
    return image

def getContours(image):
    _, thresh = cv.threshold(image, 127, 255, 0) #127
    contours, _ = cv.findContours(thresh, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

    return contours

def thresholding(image):
    image = cv.adaptiveThreshold(image, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY_INV, 1551, 25)
    image = cv.medianBlur(image, 3)
    return image

def alterColors(image):
    image = cv.cvtColor(image, cv.COLOR_BGR2HSV)
    image[:,:,1] = 0
    image[:,:,0] = 0
    image = cv.cvtColor(image, cv.COLOR_HSV2BGR)
    image = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    image = np.clip(image, 0, 148)
    return image

def morphImage(image):
    kernel = np.ones((3, 3), np.uint8)
    image = cv.dilate(image, kernel, iterations = 2) #2
    image = cv.morphologyEx(image, cv.MORPH_OPEN, kernel)
    return image

def processImage(image,mask):
    mask = resizeImage(mask, (1200,  1200), True)
    image = resizeImage(image, (1200, 1200), True)
    gray = alterColors(mask)
    thresh = thresholding(gray)
    thresh_plus = morphImage(thresh)
    contours = getContours(thresh_plus)

    mask = drawContours(mask, contours)

    _,mask = cv.threshold(mask, 0, 255,cv.THRESH_BINARY)

    kernel = np.ones((3, 3), np.uint8)
    mask = cv.erode(mask,kernel,iterations=4)

    image = cv.bitwise_or(image, mask)
    image = resizeImage(image, (800,  600), True)
    #cv.imshow('nazwa', image)
    #cv.waitKey(0)
    return image

def find4Coordinate(conture):
    gray = alterColors(conture)
    edged = cv.Canny(gray, 75, 200)

    kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE,(9,9))
    edged = cv.dilate(edged,kernel)


    cnts = cv.findContours(edged.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)


    #cnts = cnts[0] if imutils.is_cv2() else cnts[1]
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    cnts = sorted(cnts, key=cv.contourArea, reverse=True)[:5]

    for c in cnts:
        peri = cv.arcLength(c, True)
        approx = cv.approxPolyDP(c, 0.02 * peri, True)
        if len(approx) == 4:
            #screenCnt = approx
            screenCnt = c
            break
        else:
            screenCnt = []



    end=[]
    for i in screenCnt:
        end.append(i[0])

    return end


def order_points(pts):
    rect = np.zeros((4, 2), dtype="float32")
    s = np.sum(pts,axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    return rect

def four_point_transform(image, pts):
    rect = order_points(pts)
    (tl, tr, br, bl) = rect
    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    maxWidth = max(int(widthA), int(widthB))
    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    maxHeight = max(int(heightA), int(heightB))
    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]], dtype="float32")
    M = cv.getPerspectiveTransform(rect, dst)
    warped = cv.warpPerspective(image, M, (maxWidth, maxHeight))
    return warped

def usuwanie(path):
    for filename in os.listdir(path):
        os.unlink(os.path.join(path, filename))

def main():
    images = []
    images_zmienione = []
    images_pure = []
    save_path = Path('data/')
    save_path_zmienione = Path('zmienione/')
    save_path_pure = Path('pure/')
    save_path_resized = Path('pure_rotated_resize/')

    usuwanie(save_path_zmienione)
    usuwanie(save_path_pure)
    usuwanie(save_path_resized)


    for filename in os.listdir(save_path):
        images.append(os.path.join(save_path,Path(filename)))
        images_zmienione.append(os.path.join(save_path_zmienione, Path(filename)))
        images_pure.append(os.path.join(save_path_pure, Path(filename)))

    contures = []

    for i in range(len(images)):
        oldImage = cv.imread(images[i])
        image = processImage(oldImage,oldImage)
        cv.imwrite(images_zmienione[i], image)

        tmp = find4Coordinate(image)
        if tmp != []:
            contures.append(tmp)
            transfo = four_point_transform(image, tmp)
            #to nie bedzie działało jak trzeba inaczej trzeba resizowac
            #transfo = resizeImage(transfo, (450, 300), True)
            cv.imwrite(images_pure[i],transfo)
        else:
            pass



    # imgs = [PIL.Image.open(i) for i in images_zmienione]
    #
    # min_shape = sorted([(np.sum(i.size), i.size) for i in imgs])[0][1]
    # imgs_comb = np.hstack((np.asarray(i.resize(min_shape)) for i in imgs))
    #
    # imgs_comb = PIL.Image.fromarray(imgs_comb)
    # imgs_comb.save('all_cards.jpg')

if __name__== "__main__":
  main()