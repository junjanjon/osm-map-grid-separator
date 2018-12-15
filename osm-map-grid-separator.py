#!/usr/bin/env python3

import os
import subprocess
from sys import exit
import math

# 度 (角度) から小数点付き度を計算する
class ArcDegree:
    def __init__(self , degree, minute, second):
        self.degree = degree
        self.minute = minute
        self.second = second

    def decimal_degree(self):
        return (self.degree * 1.0)+ (self.minute * 1.0 / 60) + (self.second * 1.0 / 3600)

def get_file_path(prefix, x, y):
	filename = "MAP_%d_%d.osm.pbf" % (x, y)
	dir_path = os.path.join('output', prefix)
	if not os.path.exists(dir_path):
		os.mkdir(dir_path)
	filepath = os.path.join(dir_path, filename)
	return filepath

def osmium_separator(south, west, north, east, out_filepath, ref_filepath):
	if os.path.exists(out_filepath):
		return
	cmd = "osmium extract --bbox %f,%f,%f,%f -o %s %s" % (west, south, east, north, out_filepath, ref_filepath)
	print(cmd)
	subprocess.getoutput(cmd)

def get_area(x, y, center_xl, center_yl, around_degree):
	target_center_xl = center_xl + (x * around_degree)
	target_center_yl = center_yl + (y * around_degree)
	west = target_center_xl - around_degree * 0.5
	east = target_center_xl + around_degree * 0.5
	south = target_center_yl - around_degree * 0.5
	north = target_center_yl + around_degree * 0.5
	result = {
		'center_x': target_center_xl,
		'center_y': target_center_yl,
		'west': west,
		'east': east,
		'south': south,
		'north': north,
	}
	return result

# 経度で区切ったファイル名の取得
def get_line_sep_filepath(x):
	filename = 'japan_l_%d.pbf' % (x)
	dir_path = os.path.join('output', 'line')
	if not os.path.exists(dir_path):
		os.mkdir(dir_path)
	filepath = os.path.join(dir_path, filename)
	return filepath

# 経度緯度で区切ったファイル名の取得
def get_block_sep_filepath(x, y):
	filename = 'japan_b_%d_%d.pbf' % (x, y)
	dir_path = os.path.join('output', 'block')
	if not os.path.exists(dir_path):
		os.mkdir(dir_path)
	filepath = os.path.join(dir_path, filename)
	return filepath

# 緯度経度のブロックに分割
def convert_block():
	root_filepath = 'japan-latest.osm.pbf'

	for x in range(120, 150):
		line_filepath = get_line_sep_filepath(x)
		osmium_separator(20, x - 0.1, 50, x + 1.1, line_filepath, root_filepath)

		for y in range(20, 50):
			block_filepath = get_block_sep_filepath(x, y)
			osmium_separator(y - 0.1, x - 0.1, y + 1.1, x + 1.1, block_filepath, line_filepath)


def separator_around(center_xl, center_yl, around_degree, around_n):
	total = (around_n * 2) * (around_n * 2)
	count = 0
	for x in range(-around_n, around_n + 1):
		for y in range(-around_n, around_n + 1):
			count = count + 1
			print(count, " / ", total)
			area = get_area(x, y, center_xl, center_yl, around_degree)
			xl = math.floor(area['center_x'])
			yl = math.floor(area['center_y'])
			# データ元とするファイル名を取得
			block_filepath = get_block_sep_filepath(xl, yl)
			prefix = 'map_%d_%d' % (xl, yl)
			out_filepath = get_file_path(prefix, x, y)
			osmium_separator(area['south'], area['west'], area['north'], area['east'], out_filepath, block_filepath)


# 日本経緯度原点
## 経度：東経139度44分28秒8869
## 緯度：北緯 35度39分29秒1572
center_xl = ArcDegree(139, 44, 28.8869).decimal_degree()
center_yl = ArcDegree( 35, 39, 29.1572).decimal_degree()

# 3kmの経緯度
around_degree = (1.0 / 90) * 3 # 1度=90km としている


# 緯度経度のブロックに分割
convert_block()
# 1つずつのグリッドに分割
separator_around(center_xl, center_yl, around_degree, 250)
