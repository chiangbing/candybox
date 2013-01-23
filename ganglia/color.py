#!/usr/bin/env python2
# -*- coding: utf-8 -*-


class ParseColorError(BaseException):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return "invalid color representation: %s" % self.msg


class Color(object):
    '''Simple color representation.'''

    def __init__(self, red, green, blue):
        self.red = red
        self.green = green
        self.blue = blue

    def __str__(self):
        return '#%02x%02x%02x' % (self.red, self.green, self.blue)

    def __add__(self, other):
        '''Overlay two colors to make a new color.'''
        red = min(255, self.red + other.red)
        green = min(255, self.green + other.green)
        blue = min(255, self.blue + other.blue)
        return Color(red, green, blue)

    def __sub__(self, other):
        '''Substract a color to make a new color.'''
        red = max(0, self.red - other.red)
        green = max(0, self.green - other.green)
        blue = max(0, self.blue - other.blue)
        return Color(red, green, blue)


def parse(color_str):
    '''Parse a hex color code to Color.'''
    if color_str[0] != '#':
        raise ParseColorError('"%s"should start with "#"' % color_str)
    elif len(color_str) != 7 and len(color_str) != 9:
        raise ParseColorError(
            '"%s" should be a length of 7 or 9' % color_str)
    red = int(color_str[1:3], 16)
    green = int(color_str[3:5], 16)
    blue = int(color_str[5:7], 16)
    return Color(red, green, blue)


# Built-in colors
LIGHTCORAL = Color(240, 128, 128)
ROSYBROWN = Color(188, 143, 143)
INDIANRED = Color(205, 92, 92)
RED = Color(255, 0, 0)
FIREBRICK = Color(178, 34, 34)
BROWN = Color(165, 42, 42)
DARKRED = Color(139, 0, 0)
MAROON = Color(128, 0, 0)
MISTYROSE = Color(255, 228, 225)
SALMON = Color(250, 128, 114)
TOMATO = Color(255, 99, 71)
DARKSALMON = Color(233, 150, 122)
CORAL = Color(255, 127, 80)
ORANGERED = Color(255, 69, 0)
LIGHTSALMON = Color(255, 160, 122)
SIENNA = Color(160, 82, 45)
SEASHELL = Color(255, 245, 238)
CHOCOLATE = Color(210, 105, 30)
SADDLEBROWN = Color(139, 69, 19)
SANDYBROWN = Color(244, 164, 96)
PEACHPUFF = Color(255, 218, 185)
PERU = Color(205, 133, 63)
LINEN = Color(250, 240, 230)
BISQUE = Color(255, 228, 196)
DARKORANGE = Color(255, 140, 0)
BURLYWOOD = Color(222, 184, 135)
ANTIQUEWHITE = Color(250, 235, 215)
TAN = Color(210, 180, 140)
NAVAJOWHITE = Color(255, 222, 173)
BLANCHEDALMOND = Color(255, 235, 205)
PAPAYAWHIP = Color(255, 239, 213)
MOCCASIN = Color(255, 228, 181)
ORANGE = Color(255, 165, 0)
WHEAT = Color(245, 222, 179)
OLDLACE = Color(253, 245, 230)
FLORALWHITE = Color(255, 250, 240)
DARKGOLDENROD = Color(184, 134, 11)
GOLDENROD = Color(218, 165, 32)
CORNSILK = Color(255, 248, 220)
GOLD = Color(255, 215, 0)
LEMONCHIFFON = Color(255, 250, 205)
KHAKI = Color(240, 230, 140)
PALEGOLDENROD = Color(238, 232, 170)
DARKKHAKI = Color(189, 183, 107)
IVORY = Color(255, 255, 240)
LIGHTYELLOW = Color(255, 255, 224)
BEIGE = Color(245, 245, 220)
LIGHTGOLDENRODYELLOW = Color(250, 250, 210)
YELLOW = Color(255, 255, 0)
OLIVE = Color(128, 128, 0)
OLIVEDRAB = Color(107, 142, 35)
YELLOWGREEN = Color(154, 205, 50)
DARKOLIVEGREEN = Color(85, 107, 47)
GREENYELLOW = Color(173, 255, 47)
CHARTREUSE = Color(127, 255, 0)
LAWNGREEN = Color(124, 252, 0)
DARKSEAGREEN = Color(143, 188, 139)
HONEYDEW = Color(240, 255, 240)
PALEGREEN = Color(152, 251, 152)
LIGHTGREEN = Color(144, 238, 144)
LIME = Color(0, 255, 0)
LIMEGREEN = Color(50, 205, 50)
FORESTGREEN = Color(34, 139, 34)
GREEN = Color(0, 128, 0)
DARKGREEN = Color(0, 100, 0)
SEAGREEN = Color(46, 139, 87)
MEDIUMSEAGREEN = Color(60, 179, 113)
SPRINGGREEN = Color(0, 255, 127)
MINTCREAM = Color(245, 255, 250)
MEDIUMSPRINGGREEN = Color(0, 250, 154)
MEDIUMAQUAMARINE = Color(102, 205, 170)
AQUAMARINE = Color(127, 255, 212)
TURQUOISE = Color(64, 224, 208)
LIGHTSEAGREEN = Color(32, 178, 170)
MEDIUMTURQUOISE = Color(72, 209, 204)
AZURE = Color(240, 255, 255)
LIGHTCYAN = Color(224, 255, 255)
PALETURQUOISE = Color(175, 238, 238)
AQUA = Color(0, 255, 255)
CYAN = Color(0, 255, 255)
DARKCYAN = Color(0, 139, 139)
TEAL = Color(0, 128, 128)
DARKSLATEGRAY = Color(47, 79, 79)
DARKTURQUOISE = Color(0, 206, 209)
CADETBLUE = Color(95, 158, 160)
POWDERBLUE = Color(176, 224, 230)
LIGHTBLUE = Color(173, 216, 230)
DEEPSKYBLUE = Color(0, 191, 255)
SKYBLUE = Color(135, 206, 235)
LIGHTSKYBLUE = Color(135, 206, 250)
STEELBLUE = Color(70, 130, 180)
ALICEBLUE = Color(240, 248, 255)
DODGERBLUE = Color(30, 144, 255)
LIGHTSLATEGRAY = Color(119, 136, 153)
SLATEGRAY = Color(112, 128, 144)
LIGHTSTEELBLUE = Color(176, 196, 222)
CORNFLOWERBLUE = Color(100, 149, 237)
ROYALBLUE = Color(65, 105, 225)
GHOSTWHITE = Color(248, 248, 255)
LAVENDER = Color(230, 230, 250)
BLUE = Color(0, 0, 255)
MEDIUMBLUE = Color(0, 0, 205)
DARKBLUE = Color(0, 0, 139)
MIDNIGHTBLUE = Color(25, 25, 112)
NAVY = Color(0, 0, 128)
SLATEBLUE = Color(106, 90, 205)
DARKSLATEBLUE = Color(72, 61, 139)
MEDIUMSLATEBLUE = Color(123, 104, 238)
MEDIUMPURPLE = Color(147, 112, 219)
BLUEVIOLET = Color(138, 43, 226)
INDIGO = Color(75, 0, 130)
DARKORCHID = Color(153, 50, 204)
DARKVIOLET = Color(148, 0, 211)
MEDIUMORCHID = Color(186, 85, 211)
THISTLE = Color(216, 191, 216)
PLUM = Color(221, 160, 221)
VIOLET = Color(238, 130, 238)
FUCHSIA = Color(255, 0, 255)
MAGENTA = Color(255, 0, 255)
DARKMAGENTA = Color(139, 0, 139)
PURPLE = Color(128, 0, 128)
ORCHID = Color(218, 112, 214)
MEDIUMVIOLETRED = Color(199, 21, 133)
DEEPPINK = Color(255, 20, 147)
HOTPINK = Color(255, 105, 180)
LAVENDERBLUSH = Color(255, 240, 245)
PALEVIOLETRED = Color(219, 112, 147)
CRIMSON = Color(220, 20, 60)
PINK = Color(255, 192, 203)
LIGHTPINK = Color(255, 182, 193)
WHITE = Color(255, 255, 255)
SNOW = Color(255, 250, 250)
WHITESMOKE = Color(245, 245, 245)
GAINSBORO = Color(220, 220, 220)
LIGHTGRAY = Color(211, 211, 211)
SILVER = Color(192, 192, 192)
DARKGRAY = Color(169, 169, 169)
GRAY = Color(128, 128, 128)
DIMGRAY = Color(105, 105, 105)
BLACK = Color(0, 0, 0)
