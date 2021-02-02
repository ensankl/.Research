import os
import subprocess
import numpy as np
import cv2


def imagePreprocessing(fn):

    filename = fn

    # get file name without file type
    filenotype = os.path.splitext(filename)[0]
    img = cv2.imread(filename)

    # launch a window to select region to grabcut
    cv2.namedWindow("Image", 2)

    # resize it to fit on screen
    cv2.resizeWindow("Image", 500, 500)
    r = cv2.selectROI("Image", img, False, False)

    mask = np.zeros(img.shape[:2], np.uint8)

    bgdModel = np.zeros((1, 65), np.float64)
    fgdModel = np.zeros((1, 65), np.float64)

    rect = r
    cv2.grabCut(img, mask, rect, bgdModel, fgdModel, 3, cv2.GC_INIT_WITH_RECT)

    mask2 = np.where((mask == 2)|(mask == 0), 0, 1).astype('uint8')
    img = img*mask2[:, :, np.newaxis]

    outputfile = str(filenotype)+'_cropped'+'.png'

    cv2.imwrite(outputfile, img)

    cv2.imwrite('grabcut-mask.jpg', mask2)

    # generate mask from grabcut output
    cmd = ['C:/Program Files/ImageMagick-7.0.10-Q16/mogrify', '-fuzz',
           '2%', '-fill', 'white', '-opaque', '#060606', 'grabcut-mask.jpg']

    subprocess.call(cmd, shell=True)
    # apply mask using imagemagick
    cmd = ['C:/Program Files/ImageMagick-7.0.10-Q16/convert', outputfile, 'grabcut-mask.jpg',
           '-alpha', 'off', '-compose', 'CopyOpacity', '-composite', '-trim', outputfile]

    subprocess.call(cmd, shell=True)

    # cleanup
    cmd = ['del', 'grabcut-mask.jpg']

    subprocess.call(cmd, shell=True)
    return outputfile