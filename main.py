# -*- coding: utf-8 -*-
from PIL import Image, ImageDraw
import numpy as np
import math
from scipy import signal
import ncc

# 
def MakePyramid(image, minsize):
    retlist = []
    retlist.append(image)
    im = image
    width, height = im.size
    nwidth = width * 0.75
    nheight = height * 0.75
    while nwidth > minsize and nheight > minsize:
        newim = im.resize((int(nwidth),int(nheight)), Image.BICUBIC)
        retlist.append(newim)
        nwidth, nheight = newim.size
        nwidth = nwidth * 0.75
        nheight = nheight * 0.75
    return retlist

#
def ShowPyramid(pyramid):
    width = 0
    height = 0
    for pyr in pyramid:
        w, h = pyr.size
        height = max(height, h)
        width = width + w
    image = Image.new("L", (width, height), 255)
    offset_x = 0
    offset_y = 0
    for pyr in pyramid:
        image.paste(pyr,(offset_x,offset_y))
        w, h = pyr.size
        offset_x = offset_x + w
    image.show() 

im = Image.open('template.jpg')
pyramid = MakePyramid(im, 15)
ShowPyramid(pyramid)

# 
template = Image.open('judybats.jpg')

def normxcorr2D(image, template):
    """
    Normalized cross-correlation for 2D PIL images

    Inputs:
    ----------------
    template    The template. A PIL image.  Elements cannot all be equal.

    image       The PIL image.

    Output:
    ----------------
    nxcorr      Array of cross-correlation coefficients, in the range
                -1.0 to 1.0.

                Wherever the search space has zero variance under the template,
                normalized cross-correlation is undefined.
    """

    # (one-time) normalization of template
    t = np.asarray(template, dtype=np.float64)
    t = t - np.mean(t)
    norm = math.sqrt(np.sum(np.square(t)))
    t = t / norm

    # create filter to sum values under template
    sum_filter = np.ones(np.shape(t))

    # get image
    a = np.asarray(image, dtype=np.float64)
    #also want squared values
    aa = np.square(a)

    # compute sums of values and sums of values squared under template
    a_sum = signal.correlate2d(a, sum_filter, 'same')
    aa_sum = signal.correlate2d(aa, sum_filter, 'same')
    # Note:  The above two lines could be made more efficient by
    #        exploiting the fact that sum_filter is separable.
    #        Even better would be to take advantage of integral images

    # compute correlation, 't' is normalized, 'a' is not (yet)
    numer = signal.correlate2d(a, t, 'same')
    # (each time) normalization of the window under the template
    denom = np.sqrt(aa_sum - np.square(a_sum)/np.size(t))

    # wherever the denominator is near zero, this must be because the image
    # window is near constant (and therefore the normalized cross correlation
    # is undefined). Set nxcorr to zero in these regions
    tol = np.sqrt(np.finfo(denom.dtype).eps)
    nxcorr = np.where(denom < tol, 0, numer/denom)

    # if any of the coefficients are outside the range [-1 1], they will be
    # unstable to small variance in a or t, so set them to zero to reflect
    # the undefined 0/0 condition
    nxcorr = np.where(np.abs(nxcorr-1.) > np.sqrt(np.finfo(nxcorr.dtype).eps),nxcorr,0)

    return nxcorr

ratio = int(15/37*50)
minitemplate = im.resize((15,ratio), Image.BICUBIC)
def FindTemplate(pyramid, template, threshold):
    for pyr in pyramid:
        arr = normxcorr2D(pyr,template)
        width, height = pyr.size
        for x in range(0, width):
            for y in range(0, height):
                if arr[y][x] > threshold:
                    origwidth, origheight = pyramid[0].size
                    w = x/width*origwidth
                    h = y/height*origheight
                    draw = ImageDraw.Draw(pyramid[0])
                    draw.line((w-15,h+15,w+15,h+15),fill="red",width=2)
                    draw.line((w-15,h-15,w+15,h-15),fill="red",width=2)
                    draw.line((w-15,h-15,w-15,h+15),fill="red",width=2)
                    draw.line((w+15,h-15,w+15,h+15),fill="red",width=2)
    pyramid[0].show()
newTemplate = MakePyramid(template, 30)        
FindTemplate(newTemplate, minitemplate, 0.58)
# 5 
threshold = 0.58
# students
students = Image.open('students.jpg')
newTemplate = MakePyramid(students, 30)        
FindTemplate(newTemplate, minitemplate, threshold)
# tree
tree = Image.open('tree.jpg')
newTemplate = MakePyramid(tree, 30)        
FindTemplate(newTemplate, minitemplate, threshold)
# family
family = Image.open('family.jpg')
newTemplate = MakePyramid(family, 30)        
FindTemplate(newTemplate, minitemplate, threshold)
# fans
fans = Image.open('fans.jpg')
newTemplate = MakePyramid(fans, 30)        
FindTemplate(newTemplate, minitemplate, threshold)
# sports
sports = Image.open('sports.jpg')
newTemplate = MakePyramid(sports, 30)        
FindTemplate(newTemplate, minitemplate, threshold)

                            