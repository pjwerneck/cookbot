# -*- coding: utf-8 -*-

from __future__ import division

import colorsys


rgb_to_hsv = colorsys.rgb_to_hsv

hsv_to_rgb = colorsys.hsv_to_rgb



def rgb_to_xyz(*rgb):
    r, g, b = rgb

    r = r / 255
    g = g / 255
    b = b / 255

    if r > 0.04045:
        r = ((r + 0.055 ) / 1.055 ) ** 2.4
    else:
        r = r / 12.92

    if g > 0.04045:
        g = ((g + 0.055) / 1.055) ** 2.4
    else:
        g = g / 12.92

    if b > 0.04045:
        b = ((b + 0.055 ) / 1.055 ) ** 2.4
    else:
        b = b / 12.92

    r *= 100
    g *= 100
    b *= 100

    # Observer. = 2°, Illuminant = D65
    x = r * 0.4124 + g * 0.3576 + b * 0.1805
    y = r * 0.2126 + g * 0.7152 + b * 0.0722
    z = r * 0.0193 + g * 0.1192 + b * 0.9505

    return (x, y, z)


def xyz_to_rgb(*xyz):
    x, y, z = xyz

    x = x / 100      #  //X from 0 to  95.047      (Observer = 2°, Illuminant = D65)
    y = y / 100      #  //Y from 0 to 100.000
    z = z / 100      #  //Z from 0 to 108.883

    r = x *  3.2406 + y * -1.5372 + z * -0.4986
    g = x * -0.9689 + y *  1.8758 + z *  0.0415
    b = x *  0.0557 + y * -0.2040 + z *  1.0570

    if r > 0.0031308:
        r = 1.055 * ( r ** ( 1 / 2.4 ) ) - 0.055
    else:
        r = 12.92 * r

    if g > 0.0031308:
        g = 1.055 * ( g ** ( 1 / 2.4 ) ) - 0.055
    else:
        g = 12.92 * g

    if b > 0.0031308:
        b = 1.055 * ( b ** ( 1 / 2.4 ) ) - 0.055
    else:
        b = 12.92 * b

    r = r * 255
    g = g * 255
    b = b * 255

    return tuple(int(round(v)) for v in (r, g, b))


def xyz_to_lab(*xyz):
    X, Y, Z = xyz

    var_X = X / 95.047  # Observer= 2°, Illuminant= D65
    var_Y = Y / 100.000
    var_Z = Z / 108.883

    if ( var_X > 0.008856 ):
        var_X = var_X ** ( 1/3 )
    else:
        var_X = ( 7.787 * var_X ) + ( 16 / 116 )

    if ( var_Y > 0.008856 ):
        var_Y = var_Y ** ( 1/3 )
    else:
        var_Y = ( 7.787 * var_Y ) + ( 16 / 116 )

    if ( var_Z > 0.008856 ):
        var_Z = var_Z ** ( 1/3 )
    else:
        var_Z = ( 7.787 * var_Z ) + ( 16 / 116 )

    L = ( 116 * var_Y ) - 16
    A = 500 * ( var_X - var_Y )
    B = 200 * ( var_Y - var_Z )

    return (L, A, B)


def lab_to_xyz(*lab):
    L, A, B = lab

    var_Y = ( L + 16 ) / 116
    var_X = A / 500 + var_Y
    var_Z = var_Y - B / 200

    if ( var_Y ** 3 > 0.008856 ):
        var_Y = var_Y ** 3
    else:
        var_Y = ( var_Y - 16 / 116 ) / 7.787

    if ( var_X ** 3 > 0.008856 ):
        var_X = var_X ** 3
    else:
        var_X = ( var_X - 16 / 116 ) / 7.787

    if ( var_Z ** 3 > 0.008856 ):
        var_Z = var_Z ** 3
    else:
        var_Z = ( var_Z - 16 / 116 ) / 7.787

    ref_X =  95.047     # Observer= 2°, Illuminant= D65
    ref_Y = 100.000
    ref_Z = 108.883

    Y = ref_Y * var_Y
    Z = ref_Z * var_Z

    X = ref_X * var_X

    return (X, Y, Z)


def rgb_to_lab(*rgb):
    return xyz_to_lab(*rgb_to_xyz(*rgb))


def lab_to_rgb(*lab):
    return xyz_to_rgb(*lab_to_xyz(*lab))
