import numpy as np
import cv2
import pandas as pd
from typing import Tuple, Union
import math

from common_utils.constants import IMG_WIDTH, IMG_HEIGHT


def rotate(
        image: np.ndarray, angle: float, background: Union[int, Tuple[int, int, int]]
) -> np.ndarray:
    old_width, old_height = image.shape[:2]
    angle_radian = math.radians(angle)
    width = abs(np.sin(angle_radian) * old_height) + abs(np.cos(angle_radian) * old_width)
    height = abs(np.sin(angle_radian) * old_width) + abs(np.cos(angle_radian) * old_height)

    image_center = tuple(np.array(image.shape[1::-1]) / 2)
    rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
    rot_mat[1, 2] += (width - old_width) / 2
    rot_mat[0, 2] += (height - old_height) / 2
    return cv2.warpAffine(image, rot_mat, (int(round(height)), int(round(width))), borderValue=background)


def convert_to_binary(img_grayscale):
    # adaptiveMethod=cv2.ADAPTIVE_THRESH_MEAN_C or cv2.ADAPTIVE_THRESH_GAUSSIAN_C
    img_binary = cv2.adaptiveThreshold(img_grayscale,
                                       maxValue=255,
                                       adaptiveMethod=cv2.ADAPTIVE_THRESH_MEAN_C,
                                       thresholdType=cv2.THRESH_BINARY,
                                       blockSize=15,
                                       C=8)
    return img_binary


def get_pd_val(result, name, index):
    return result[name].values.tolist()[index]


def get_coor_4(df_result):
    if len(df_result) == 3:
        dict_edge = {}
        dict_coord = {'coor_corner0': [get_pd_val(df_result, 'xcenter', 0),
                                       get_pd_val(df_result, 'ycenter', 0)],
                      'coor_corner1': [get_pd_val(df_result, 'xcenter', 1),
                                       get_pd_val(df_result, 'ycenter', 1)],
                      'coor_corner2': [get_pd_val(df_result, 'xcenter', 2),
                                       get_pd_val(df_result, 'ycenter', 2)]}
        dict_edge['edge_01'] = abs(
            np.linalg.norm(np.array(dict_coord['coor_corner0']) - np.array(dict_coord['coor_corner1'])))
        dict_edge['edge_02'] = abs(
            np.linalg.norm(np.array(dict_coord['coor_corner0']) - np.array(dict_coord['coor_corner2'])))
        dict_edge['edge_12'] = abs(
            np.linalg.norm(np.array(dict_coord['coor_corner1']) - np.array(dict_coord['coor_corner2'])))

        list_path = sorted([dict_edge['edge_01'], dict_edge['edge_12'], dict_edge['edge_02']])

        name_longest_path = list(dict_edge.keys())[list(dict_edge.values()).index(list_path[-1])]

        name_corner_1 = name_longest_path[-2]
        name_corner_2 = name_longest_path[-1]
        name_corner_3 = 'coor_corner' + '012'.replace(name_corner_1, '').replace(name_corner_2, '')
        name_corner_1 = 'coor_corner' + name_corner_1
        name_corner_2 = 'coor_corner' + name_corner_2

        mid_point = [(dict_coord[name_corner_1][0] + dict_coord[name_corner_2][0]) / 2,
                     (dict_coord[name_corner_1][1] + dict_coord[name_corner_2][1]) / 2]
        coor_corner4 = [abs(mid_point[0] * 2 - dict_coord[name_corner_3][0]),
                        abs(mid_point[1] * 2 - dict_coord[name_corner_3][1])]
        df_coor4 = pd.DataFrame(
            {'xcenter': [coor_corner4[0]], 'ycenter': [coor_corner4[1]], 'width': ['0'], 'height': ['0'],
             'confidence': ['1'], 'class': ['0'], 'name': ['corner']})
        df_result = pd.concat([df_result, df_coor4], ignore_index=True, axis=0)
    return df_result


def get_char_appear2(text_string):
    list_char = [char for char in str(text_string)]
    list_unique_char = list(set(list_char))
    for u_char in list_unique_char:
        if list_char.count(u_char) == 2:
            return u_char
    return ''


def angle_between_vectors_degrees(u, v):
    """Return the angle between two vectors in any dimension space,
    in degrees."""
    return np.degrees(
        math.acos(abs(np.dot(u, v)) / (abs(np.linalg.norm(u)) * abs(np.linalg.norm(v)))))


def check_remove_same_name_path(idx, idx2, key1, key2, dict_2, list_coor):
    if idx != idx2 and (key1 + key2) not in list(dict_2.keys()) and (key2 + key1) not in list(
            dict_2.keys()):
        if list_coor:
            if key1 not in list_coor and key2 in list_coor:
                return True
        else:
            return True
    return False


def update_coord_dict(dict_1, dict_2, update_func, list_coor=None):
    for idx, (key1, val1) in enumerate(list(dict_1.items())):
        for idx2, (key2, val2) in enumerate(list(dict_1.items())):
            if check_remove_same_name_path(idx, idx2, key1, key2, dict_2, list_coor):
                dict_2[key1 + key2] = update_func(val1, val2)
    return dict_2


def create_point_to_line(val_1, val_2):
    return val_1 - val_2


def create_pair_line(val_1, val_2):
    return [val_1, val_2]


def check_duplicate_square(coor_square2, coor_square, coor_1_temp, coor_2_temp, coor_1, coor_2):
    return coor_square2 != coor_square and coor_1_temp in [coor_1, coor_2] and coor_2_temp in [coor_1, coor_2]


def check_duplicate_pair(pair):
    if abs(pair[0][0]) == abs(pair[1][0]) and abs(pair[0][1]) == abs(pair[1][1]):
        return True
    if abs(pair[0][0]) == abs(pair[1][1]) and abs(pair[0][1]) == abs(pair[1][0]):
        return True
    return False


def find_forth_corner(dict_pair_left, coor_square, coor_1, coor_2, threshold):
    for key, pair in list(dict_pair_left.items()):
        if check_duplicate_pair(pair):
            continue

        if abs(angle_between_vectors_degrees(pair[0], pair[1]) - 90) < threshold:
            coor_square2 = get_char_appear2(key)
            if coor_square2 != '':
                coor_1_temp = str(key).replace(coor_square2, '')[0]
                coor_2_temp = str(key).replace(coor_square2, '')[1]
                if check_duplicate_square(coor_square2, coor_square, coor_1_temp, coor_2_temp, coor_1, coor_2):
                    return coor_square2
    return None


def init_dict_coord(df_detect_result):
    dict_coord = {}
    for i in range(0, len(df_detect_result)):
        dict_coord[str(i)] = np.array(
            [get_pd_val(df_detect_result, 'xcenter', i), get_pd_val(df_detect_result, 'ycenter', i)])
    return dict_coord


def remove_corner_5_outside(df_wh, df_xy):
    boundary_x_min = int(df_xy['ymin'].values.tolist()[0])
    boundary_x_max = int(df_xy['xmax'].values.tolist()[0])
    boundary_y_min = int(df_xy['ymin'].values.tolist()[0])
    boundary_y_max = int(df_xy['ymax'].values.tolist()[0])
    return df_wh[((boundary_x_min <= df_wh['xcenter']) & (df_wh['xcenter'] <= boundary_x_max)) & (
            (boundary_y_min <= df_wh['ycenter']) & (df_wh['ycenter'] <= boundary_y_max))]


def remove_corner_5(df_detect_result, threshold=10):
    result = []

    dict_coord = init_dict_coord(df_detect_result)
    dict_path = {}
    dict_pair = {}

    dict_path = update_coord_dict(dict_coord, dict_path, create_point_to_line)
    dict_pair = update_coord_dict(dict_path, dict_pair, create_pair_line)

    list_coord = []
    dict_path_left = {}
    dict_pair_left = {}

    for key, pair in list(dict_pair.items()):
        if check_duplicate_pair(pair):
            continue

        if abs(angle_between_vectors_degrees(pair[0], pair[1]) - 90) < threshold:
            coord_square = get_char_appear2(key)
            if coord_square != '':
                coord_1 = str(key).replace(coord_square, '')[0]
                coord_2 = str(key).replace(coord_square, '')[1]

                if len(list_coord) == 0:
                    list_coord.append(coord_square)
                    list_coord.append(coord_1)
                    list_coord.append(coord_2)

                    dict_path_left = update_coord_dict(dict_coord, dict_path_left, create_point_to_line,
                                                       list_coor=list_coord)
                    dict_pair_left = update_coord_dict(dict_path_left, dict_pair_left, create_pair_line)

                    forth_corner = find_forth_corner(dict_pair_left, coord_square, coord_1, coord_2, threshold)
                    if forth_corner:
                        list_coord.append(forth_corner)

                    if len(list_coord) == 4:
                        break
                    elif len(list_coord) == 3:
                        list_coord = []

    for i in list_coord:
        result.append(
            {'xcenter': dict_coord[i][0], 'ycenter': dict_coord[i][1], 'width': 0, 'height': 0,
             'confidence': 1, 'class': '0', 'name': 'corner'})

    if result:
        return pd.DataFrame(result)
    else:
        return df_detect_result


def change_coor_from_df(dataframe, type_corner):
    x_c, y_c = float(get_pd_val(dataframe, 'xcenter', 0)), float(get_pd_val(dataframe, 'ycenter', 0))
    width, height = float(get_pd_val(dataframe, 'width', 0)), float(get_pd_val(dataframe, 'height', 0))
    x_center, y_center = None, None
    if type_corner == 'top_left':
        x_center = max(x_c - 20 - width / 2, 0)
        y_center = max(y_c - 20 - height / 2, 0)
    if type_corner == 'top_right':
        x_center = x_c + width / 2
        y_center = y_c - height / 2
    if type_corner == 'bot_left':
        x_center = x_c - width / 2
        y_center = y_c + height / 2
    if type_corner == 'bot_right':
        x_center = x_c + width / 2
        y_center = y_c + height / 2
    if type_corner == 'top_mid':
        x_center = x_c
        y_center = y_c - height / 2
    if type_corner == 'bot_mid':
        x_center = x_c
        y_center = y_c + height / 2
    return x_center, y_center


def horizontal_image(coor_dict):
    edge_top = abs(np.linalg.norm(np.array(coor_dict['top_left']) - np.array(coor_dict['top_right'])))
    edge_left = abs(np.linalg.norm(np.array(coor_dict['top_left']) - np.array(coor_dict['bottom_left'])))
    if edge_top < edge_left:
        # # Rotate right
        # coor_dict_hoz = {'top_left': coor_dict['bottom_left'], 'top_right': coor_dict['top_left'],
        #                  'bottom_left': coor_dict['bottom_right'], 'bottom_right': coor_dict['top_right']}
        # Rotate left
        coor_dict_hoz = {'top_left': coor_dict['top_right'], 'top_right': coor_dict['bottom_right'],
                         'bottom_left': coor_dict['top_left'], 'bottom_right': coor_dict['bottom_left']}
        print('Image now is horizontal')
        return coor_dict_hoz
    else:
        return coor_dict


def get_type(df_result):
    df_result = df_result.sort_values(by=['confidence'], ascending=False)
    if len(df_result) > 1:
        df_result = df_result.iloc[[0]]
    return df_result


def get_coord_one_df(df_result, coord_type):
    if coord_type == 'xywh':
        return int(df_result['xcenter'].values.tolist()[0]), int(df_result['ycenter'].values.tolist()[0]), \
            int(df_result['width'].values.tolist()[0]), int(df_result['height'].values.tolist()[0])
    if coord_type == 'xyxy':
        return int(df_result['xmin'].values.tolist()[0]), int(df_result['ymin'].values.tolist()[0]), \
            int(df_result['xmax'].values.tolist()[0]), int(df_result['ymax'].values.tolist()[0])


def crop_img_without_corner(df_result, img):
    xc, yc, width, height = get_coord_one_df(df_result, 'xywh')
    x = max(int(xc - width / 2) - 20, 0)
    y = max(int(yc - height / 2) - 20, 0)
    return img[y:y + height + 55, x:x + width + 55]


def flip_img_with_condition(df_type, con_1, con_2, x_c_img_crop, y_c_img_crop):
    if len(df_type):
        x, y, w, h = get_coord_one_df(df_type, 'xywh')
        if ((x - x_c_img_crop) > 0) == con_1 and ((y - y_c_img_crop) > 0) == con_2:
            return True
    else:
        return None


def is_flip(df_result, img_crop, card_type):
    x_c_img_crop, y_c_img_crop = img_crop.shape[1] / 2, img_crop.shape[0] / 2
    do_flip = False
    if 'front' in card_type:
        df_badge = df_result[df_result['name'] == 'badge']
        do_flip = flip_img_with_condition(df_badge, True, True, x_c_img_crop, y_c_img_crop)
    if card_type == '12_new_back':
        df_finger_print = df_result[df_result['name'] == 'finger_print']
        do_flip = flip_img_with_condition(df_finger_print, False, True, x_c_img_crop, y_c_img_crop)
    if card_type in ['12_old_back', '9_back']:
        df_finger_print = df_result[df_result['name'] == 'finger_print']
        do_flip = flip_img_with_condition(df_finger_print, True, False, x_c_img_crop, y_c_img_crop)
    return do_flip


def horizontal_img_without_corner(df_result, img):
    width = df_result['width'].values.tolist()[0]
    height = df_result['height'].values.tolist()[0]
    true_ratio = width / height
    if true_ratio < 1:
        img = rotate(img, 90, (0, 0, 0))
    return img


def get_coord_6_point(df_result):
    corner_df = df_result[(df_result['name'].isin(['corner']))]
    corner = get_coor_corners(corner_df)

    mid_corner_df = df_result[(df_result['name'].isin(['mid_corner']))]
    mid_corner = get_mid_corners(mid_corner_df)

    coord = {**corner, **mid_corner}

    return coord


def get_mid_corners(df_result):
    df_result = get_mid_coor_2(df_result)
    if len(df_result) == 2:
        mean_ymin = df_result.describe()['ycenter']['mean']

        top_df = df_result[(df_result['ycenter'] < mean_ymin)]
        bot_df = df_result[(df_result['ycenter'] > mean_ymin)]

        top_df.sort_values(by=['ycenter'], ascending=True)
        bot_df.sort_values(by=['ycenter'], ascending=True)

        top_mid = change_coor_from_df(top_df.head(1), 'top_mid')
        bot_mid = change_coor_from_df(bot_df.head(1), 'bot_mid')

        return {
            'top_mid': top_mid,
            'bottom_mid': bot_mid,
        }
    else:
        return {}


def get_mid_coor_2(df_result):
    return df_result


def get_coor_corners(dataframe_result):
    dataframe_result = get_coor_4(dataframe_result)
    if len(dataframe_result) == 4:
        mean_xmin = dataframe_result.describe()['xcenter']['mean']

        left_df = dataframe_result[(dataframe_result['xcenter'] < mean_xmin)]
        right_df = dataframe_result[(dataframe_result['xcenter'] > mean_xmin)]

        y_left_list = sorted(left_df['ycenter'].values.tolist())
        y_right_list = sorted(right_df['ycenter'].values.tolist())

        top_left_df = left_df[left_df['ycenter'] == y_left_list[0]]
        top_left = change_coor_from_df(top_left_df, 'top_left')

        bottom_left_df = left_df[left_df['ycenter'] == y_left_list[1]]
        bottom_left = change_coor_from_df(bottom_left_df, 'bot_left')

        top_right_df = right_df[right_df['ycenter'] == y_right_list[0]]
        top_right = change_coor_from_df(top_right_df, 'top_right')

        bottom_right_df = right_df[right_df['ycenter'] == y_right_list[1]]
        bottom_right = change_coor_from_df(bottom_right_df, 'bot_right')

        return {
            'top_left': top_left,
            'bottom_left': bottom_left,
            'top_right': top_right,
            'bottom_right': bottom_right
        }
    else:
        return {}


def perspective_transform(image, source_points):
    dest_points = np.float32([[0, 0], [IMG_WIDTH, 0], [IMG_WIDTH, IMG_HEIGHT], [0, IMG_HEIGHT]])
    m = cv2.getPerspectiveTransform(source_points, dest_points)
    dst = cv2.warpPerspective(image, m, (IMG_WIDTH, IMG_HEIGHT))
    return dst


def align_image(image, coordinate_dict):
    coordinate_dict = horizontal_image(coordinate_dict)

    top_left_point = coordinate_dict['top_left']
    top_right_point = coordinate_dict['top_right']
    bottom_right_point = coordinate_dict['bottom_right']
    bottom_left_point = coordinate_dict['bottom_left']

    source_points = np.float32([top_left_point, top_right_point, bottom_right_point, bottom_left_point])

    # transform image and crop
    crop = perspective_transform(image, source_points)
    return crop


def results_to_dataframe(boxes, scores, class_name):
    x_centers = []
    y_centers = []
    widths = []
    heights = []
    class_names = []
    confs = []
    score = max(scores)
    for idx in range(len(boxes)):
        if score == scores[idx]:
            xc, yc, w, h = boxes[idx]
            x_centers.append(xc)
            y_centers.append(yc)
            widths.append(w)
            heights.append(h)
            class_names.append(str(class_name[idx]))
            confs.append(float(scores[idx]))
            break

    data = {'xcenter': x_centers, 'ycenter': y_centers, 'width': widths,
            'height': heights, 'name': class_names, 'confidence': confs}
    # print(data)
    return pd.DataFrame(data)


def align_image_6_point(image, coordinate_dict):
    coordinate_dict = horizontal_image(coordinate_dict)

    top_left_point = coordinate_dict['top_left']
    top_right_point = coordinate_dict['top_right']
    bottom_right_point = coordinate_dict['bottom_right']
    bottom_left_point = coordinate_dict['bottom_left']
    top_mid_point = coordinate_dict['top_mid']
    bottom_mid_point = coordinate_dict['bottom_mid']

    left_source_points = np.float32([top_left_point, top_mid_point, bottom_mid_point, bottom_left_point])
    right_source_points = np.float32([top_mid_point, top_right_point, bottom_right_point, bottom_mid_point])
    # transform image and crop
    crop_left = perspective_transform(image, left_source_points)
    crop_right = perspective_transform(image, right_source_points)

    return crop_left, crop_right
