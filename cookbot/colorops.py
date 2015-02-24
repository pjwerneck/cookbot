# -*- coding: utf-8 -*-
from __future__ import division

import colorsys
import math
import itertools

# Conversions

rgb_to_hsv = colorsys.rgb_to_hsv

hsv_to_rgb = colorsys.hsv_to_rgb


def rgb_to_xyz(*rgb):
    rgb = (v / 255 for v in rgb)
    rgb = ((((v + 0.055) / 1.055) ** 2.4) if v > 0.04045 else v / 12.92 for v in rgb)

    r, g, b = (v*100 for v in rgb)

    x = r * 0.4124 + g * 0.3576 + b * 0.1805
    y = r * 0.2126 + g * 0.7152 + b * 0.0722
    z = r * 0.0193 + g * 0.1192 + b * 0.9505

    return (x, y, z)


def xyz_to_rgb(*xyz):
    x, y, z = (v / 100 for v in xyz)

    r = x *  3.2406 + y * -1.5372 + z * -0.4986
    g = x * -0.9689 + y *  1.8758 + z *  0.0415
    b = x *  0.0557 + y * -0.2040 + z *  1.0570

    rgb = (((1.055 * (v ** (1 / 2.4))) - 0.055) if v > 0.0031308 else 12.92 * v for v in (r, g, b))
    rgb = (int(round(v * 255)) for v in rgb)

    return rgb


def xyz_to_lab(*xyz):
    ref = (95.047, 100.000, 108.883)

    xyz = (v/r for (v, r) in zip(xyz, ref))

    x, y, z = ((v ** (1 / 3)) if v > 0.008856 else ((7.787 * v) + (16 / 116)) for v in xyz)

    L = (116 * y) - 16
    A = 500 * (x - y)
    B = 200 * (y - z)

    return (L, A, B)


def lab_to_xyz(*lab):
    L, A, B = lab

    y = ( L + 16 ) / 116
    x = A / 500 + y
    z = y - B / 200

    xyz = (((v ** 3)) if v > 0.008856 else ((v - 16 / 116) / 7.787) for v in (x, y, z))

    ref = (95.047, 100.000, 108.883)

    x, y, z = (v*r for (v, r) in zip(xyz, ref))

    return (x, y, z)


def rgb_to_lab(*rgb):
    return xyz_to_lab(*rgb_to_xyz(*rgb))


def lab_to_rgb(*lab):
    return xyz_to_rgb(*lab_to_xyz(*lab))



# delta

def delta_c(c1, c2):
    l1, a1, b1 = c1
    l2, a2, b2 = c2

    return math.sqrt((a2 ** 2) + (b2 ** 2)) - math.sqrt((a1 ** 2) + (b1 ** 2))

def delta_h(c1, c2):
    l1, a1, b1 = c1
    l2, a2, b2 = c2

    xDE = delta_c(c1, c2)

    return math.sqrt((a2 - a1) ** 2) + ((b2 - b1) ** 2) - (xDE ** 2)


def rgb_delta(rgb1, rgb2):
    # http://www.compuphase.com/cmetric.htm
    r1, g1, b1 = rgb1
    r2, g2, b2 = rgb2

    rmean = (r1 + r2) // 2

    r = r1 - r2
    g = g1 - g2
    b = b1 - b2

    f = (((512 + rmean)*r*r) >> 8) + 4*g*g + (((767 - rmean)*b*b) >> 8)

    return math.sqrt(f)


def delta_hist(ha, hb):
    n = len(ha)

    return math.sqrt(sum((a - b) ** 2 for (a, b) in zip(ha, hb)) / n)

def delta_hist_im(ima, imb):
    ha = ima.histogram()
    hb = imb.histogram()

    n = len(ha)

    return math.sqrt(sum((a - b) ** 2 for (a, b) in zip(ha, hb)) / n)


def delta_chi_square(ha, hb):
    return sum([(((a - b) ** 2) / a) for (a, b) in zip(ha, hb) if a])


def histx(im):
    h = im.histogram()
    return math.sqrt(sum([(x**2) * (i+1) for (i, x) in enumerate(h)]) / len(h))


def origin_dist(im, color):
    # this is used to identify active red buttons in the panel
    w, h = im.size

    return sum(math.sqrt(sum(map(lambda x: pow(x, 2), divmod(i, w)))) for (i, p) in enumerate(im.getdata()) if p == color)

