from utils.image_utils import *

EXTERNAL_DIAMETER_SENSOR = 40
INTERNAL_DIAMETER_SENSOR = 20
EXTERNAL_DIAMETER_DUT = 20
INTERNAL_DIAMETER_DUT = 7

EXTERNAL_COLOR = 100
INTERNAL_COLOR = 240
MAX_MATCHS = 3

SENSOR_BOTTOM_DIST_MM = 65
SENSOR_LEFT_DIST_MM = 46

DUT_BOTTOM_DIST_MM = 38
DUT_RIGHT_DIST_MM = 26

# Find fiducial points in image
image = cv2.imread('images/fid_test_1.png')

pattern_sensor = create_pattern(EXTERNAL_DIAMETER_SENSOR, INTERNAL_DIAMETER_SENSOR, EXTERNAL_COLOR,INTERNAL_COLOR)
pattern_dut = create_pattern(EXTERNAL_DIAMETER_DUT, INTERNAL_DIAMETER_DUT, EXTERNAL_COLOR,INTERNAL_COLOR)
grey_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

match_img_sensor = cv2.matchTemplate(grey_image, pattern_sensor, cv2.TM_CCOEFF_NORMED)
found_points_sensor = find_points(match_img_sensor, MAX_MATCHS)
match_img_dut = cv2.matchTemplate(grey_image, pattern_dut, cv2.TM_CCOEFF_NORMED)
found_points_dut = find_points(match_img_dut, MAX_MATCHS)

paint_matched_points(image, found_points_sensor, EXTERNAL_DIAMETER_SENSOR, (0,0,255))
paint_matched_points(image, found_points_dut, EXTERNAL_DIAMETER_DUT, (0,255,0))


cv2.namedWindow('Result', cv2.WINDOW_NORMAL)
cv2.imshow('Result', image)

# Transform from pixel-Space to mm-Space



cv2.waitKey(0)
cv2.destroyAllWindows()