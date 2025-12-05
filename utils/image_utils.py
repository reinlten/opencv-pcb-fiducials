import cv2
import numpy as np
import math

def is_close_point(points, new_point, minimum_distance):
    for point in points:
        distance = np.sqrt((point[0] - new_point[0])**2 + (point[1] - new_point[1])**2)
        if distance < minimum_distance:
            return True
    return False

def create_pattern(external_diameter,internal_diameter, color_external, color_internal):
    external_radius = external_diameter // 2
    internal_radius = internal_diameter // 2

    pattern = np.zeros((external_diameter,external_diameter), dtype=np.uint8)
    cv2.circle(pattern, (external_radius,external_radius), external_radius, (color_external,color_external,color_external), cv2.FILLED)
    cv2.circle(pattern, (external_radius,external_radius), internal_radius, (color_internal ,color_internal,color_internal), cv2.FILLED)    
    return pattern    

def find_points(match_img, points_to_find):
    found_points = []
    threshold = 1
    while len(found_points) < points_to_find and threshold > 0:
        loc = np.where( match_img >= threshold)
        for pt in zip(*loc[::-1]):
            if not is_close_point(found_points, pt, 50):
                found_points.append(pt)              
                if len(found_points) == points_to_find:
                    break
        threshold -= 0.01
    return found_points

def paint_matched_points(image, points, external_diameter, color):
    for point in points:
        bottom_left_corner = (point[0] + external_diameter, point[1] + external_diameter)
        cv2.rectangle(image, point, bottom_left_corner, color, 2)

def find_left_top_point(points):
    sorted_points = sorted(points, key=lambda p: p[0])
    leftmost_points = sorted_points[:2]
    left_top_point = min(leftmost_points, key=lambda p: p[1])
    return left_top_point

def find_left_bottom_point(points):
    sorted_points = sorted(points, key=lambda p: p[0])
    leftmost_points = sorted_points[:2]
    left_bottom_point = max(leftmost_points, key=lambda p: p[1])
    return left_bottom_point

def find_right_top_point(points):
    sorted_points = sorted(points, key=lambda p: p[0], reverse=True)
    rightmost_points = sorted_points[:2]
    right_top_point = min(rightmost_points, key=lambda p: p[1])
    return right_top_point

def find_right_bottom_point(points):
    sorted_points = sorted(points, key=lambda p: p[0], reverse=True)    
    rightmost_points = sorted_points[:2]    
    right_bottom_point = max(rightmost_points, key=lambda p: p[1])
    return right_bottom_point

def draw_ltr(image, segments, points, fids, dut_bot_dist, dut_right_dist, ext_diam):
    for seg in segments:
        x1, y1, x2, y2, width, layer = seg
        x1, y1, x2, y2, width = map(float, [x1, y1, x2, y2, width])

        lb_tf = np.array(find_left_bottom_point(points)) #px
        rb_tf = np.array(find_right_bottom_point(points)) #px
        rt_tf = np.array(find_right_top_point(points)) #px

        lb = np.array(find_left_bottom_point(fids)) #mm
        rb = np.array(find_right_bottom_point(fids)) #mm
        rt = np.array(find_right_top_point(fids)) #mm

        p1 = np.array([x1,y1]) #mm
        p2 = np.array([x2,y2]) #mm

        vec_1 = rb_tf - rt_tf #px
        vec_2 = lb_tf - rb_tf #px

        px_per_mm_bot = np.linalg.norm(vec_2) / dut_bot_dist
        px_per_mm_right = np.linalg.norm(vec_1) / dut_right_dist
        print(f"mm/px bottom_l_r:{dut_bot_dist/np.linalg.norm(vec_2)}")
        print(f"mm/px bottom_l_r:{dut_right_dist/np.linalg.norm(vec_1)}")

        p1_tf = rt_tf+(p1-rt)[1]*px_per_mm_right*vec_1/np.linalg.norm(vec_1)+(rb-p1)[0]*px_per_mm_bot*vec_2/np.linalg.norm(vec_2)+ext_diam/2+1
        p2_tf = rt_tf+(p2-rt)[1]*px_per_mm_right*vec_1/np.linalg.norm(vec_1)+(rb-p2)[0]*px_per_mm_bot*vec_2/np.linalg.norm(vec_2)+ext_diam/2+1

        p1_tf = (int(p1_tf[0]),int(p1_tf[1]))
        p2_tf = (int(p2_tf[0]),int(p2_tf[1]))

        print(f"{p1_tf}, {p2_tf}")

        cv2.line(image, p1_tf, p2_tf, (0,0,255), 1)





def draw_magsens_pos(image, points, sens_bot_dist, sens_left_dist):
    lb = np.array(find_left_bottom_point(points))
    lt = np.array(find_left_top_point(points))
    rb = np.array(find_right_bottom_point(points))

    vec_1 = lb-lt
    vec_2 = rb-lb

    px_per_mm_bot = np.linalg.norm(vec_2)/sens_bot_dist
    px_per_mm_left = np.linalg.norm(vec_1)/sens_left_dist
    #print(f"mm/px bottom_l_r:{sens_bot_dist/np.linalg.norm(vec_2)}")
    #print(f"mm/px bottom_l_r:{sens_left_dist/np.linalg.norm(vec_1)}")

    for i in range(6):
        for j in range(4):
            sens_pos_px = lt+px_per_mm_left*(14+j*6)*vec_1/np.linalg.norm(vec_1)+vec_2*(9+i*6)*px_per_mm_bot/np.linalg.norm(vec_2)
            #TODO: HARDCODED OFFSET +1PX. HIGHER RES -> DELETE?
            sens_pos_px = (int(sens_pos_px[0]+1), int(sens_pos_px[1]+1))
            bottom_left_sens_pos_px = (sens_pos_px[0]+40, sens_pos_px[1]+40)

            print(sens_pos_px)

            cv2.rectangle(image, sens_pos_px, bottom_left_sens_pos_px, (0,0,255), 2)




def calculate_angle(points):
    x1, y1 = find_left_top_point (points)
    x2, y2 = find_right_bottom_point (points)
    
    radians_angle = math.atan2(y2 - y1, x2 - x1)
    degrees_angle = math.degrees(radians_angle)

    return degrees_angle    

def align_image(image, angle, found_points, external_diameter):
    angle_found = calculate_angle(found_points)
    print(f"angle found {angle_found}")

    (height, width) = image.shape[:2]
    center = (width // 2, height // 2)

    print(angle_found)
    M = cv2.getRotationMatrix2D(center, angle_found-angle, 1.0)
    aligned_image = cv2.warpAffine(image, M, (width, height))
    
    found_points_rotated = []
    for point in found_points:
        point_homogeneous = np.array([point[0], point[1], 1])
        rotated_point = M.dot(point_homogeneous)
        found_points_rotated.append(rotated_point[:2])
    
    alpha = math.radians(angle_found-angle)
    x1 = -external_diameter//2*(1-math.cos(alpha) - math.sin(alpha))
    y1 = external_diameter//2*(math.cos(alpha) - math.sin(alpha)-1)
    
    adjusted_points = [(x +x1, y +y1) for x, y in found_points_rotated]
    adjusted_points = [
        (int(round(point[0])), int(round(point[1])))
        for point in adjusted_points  
    ]
    
    return aligned_image, adjusted_points

def paint_cutout_border(image, found_points_rotated, external_diameter, distance_top_left_corner, distance_bottom_right_corner):
    left_top_point = find_left_top_point (found_points_rotated)
    right_bottom_point =find_right_bottom_point (found_points_rotated)

    top_left = (left_top_point[0] - distance_top_left_corner[0] +external_diameter//2 , left_top_point[1] - distance_top_left_corner[1]+external_diameter//2)
    bottom_right = (right_bottom_point[0] + distance_bottom_right_corner[0]+external_diameter//2, right_bottom_point[1] + distance_bottom_right_corner[1]+external_diameter//2)
    
    image = cv2.rectangle(image, top_left, bottom_right, (0, 255, 0), 2)
    return image

def crop_image(image, found_points_rotated, external_diameter, distance_top_left_corner, distance_bottom_right_corner):
    left_top_point = find_left_top_point (found_points_rotated)
    right_bottom_point =find_right_bottom_point (found_points_rotated)

    top_left = (left_top_point[0] - distance_top_left_corner[0] +external_diameter//2 , left_top_point[1] - distance_top_left_corner[1]+external_diameter//2)
    bottom_right = (right_bottom_point[0] + distance_bottom_right_corner[0]+external_diameter//2, right_bottom_point[1] + distance_bottom_right_corner[1]+external_diameter//2)
    
    cropped_image = image[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]
    return cropped_image