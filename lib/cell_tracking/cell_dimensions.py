
import numpy as np
import skimage.draw

# WARNING!!! 
# When we plot the angles on a normal axis everything is fine. 
# But in an image 0 is at the top so all the angles have to multiplied by -1. 
# so 20 degress

# Also this code assumes x, y, but we nearly always use rows and cols
def positive_only(rows, cols):
    neg_mask = (rows>=0) & (cols>=0)
    return rows[neg_mask], cols[neg_mask]

def regionprops_to_props(p):
    # Skimage.measure.regionprops converted to this format
    center = rc2xy(*p["centroid"])
    length = p["major_axis_length"]
    width = p["minor_axis_length"]
    angle = p["orientation"]
    return (center, length, width, limit_angle(angle*-1))


def mplellipse_to_props(e):
    return e.center, e.width, e.height, limit_angle(np.deg2rad(e.angle))

def props_to_mplellipse(center, length, width, angle):
    return {"xy": center, "width": length, "height":width, "angle":np.rad2deg(angle)} 

def set_mplellipse_props(e, xy:(float,float), length:float, width:float, angle:float):
    e.center = xy 
    e.width = length 
    e.height = width 
    e.angle = np.rad2deg(angle)
    return e

def rc2xy(r,c):
    return c, r

def e_rc2xy(center_rc, length, width, angle):
    return rc2xy(*center_rc), length, width, angle

def get_cell_pixels(center_xy, length, width, angle, image_shape):
    col, row = center_xy
    # The angles are correct assuming 0 is down 
    # but in images, zero is up! 
    #rot = np.deg2rad(angle*-1)
    rot = -angle
    #rot = np.deg2rad(angle)
    pixels = skimage.draw.ellipse(row, col, width/2, length/2, shape=image_shape, rotation=rot)
    # if a cell is at the edge the coordinates go negative so wrap around.
    return positive_only(*pixels)

def rotate_lines_using_maj_line(old_maj, old_min, new_maj):
    assert(old_maj[0][0] == old_min[0][0])
    assert(old_maj[1][0] == old_min[1][0])
    assert(old_min[0][0] == new_maj[0][0])
    assert(old_min[1][0] == new_maj[1][0])
    ((x0, nxmj), (y0, nymj)) = new_maj 
    old_ellipse = get_ellipse_props_from_lines(old_maj, old_min)
    width = old_ellipse[2]
    new_angle = np.arctan2((nymj - y0), (nxmj - x0))
    orthognal = new_angle - np.pi/2 #np.deg2rad(90)
    nxmn = np.cos(orthognal) * (width * 0.5)
    nymn = np.sin(orthognal) * (width * 0.5)
    return new_maj, ((x0, x0 + nxmn), (y0, y0 + nymn))


def get_nearest_point_on_min_axis(ellipse, point):
    _, line_min = get_lines_from_ellipse(*ellipse)
    ix, iy = get_perpendicular_intersection_point(line_min, point)
    return (ix, iy)

# def old_get_nearest_point_on_min_axis(ellipse, point):
#     # first find another point on the line 
#     # we chosoe the ellispe center y plane
#     center, _, _, angle = ellipse
#     xi  = ((center[1] - point[1]) / np.tan(angle)) + point[0]
#     xy_maj, xy_min = get_lines_from_ellipse(ellipse)
#     # then find where the two lines intersect
#     intersect = get_intersection_point(xy_min, [[point[0], xi], [point[1], center[1]]])
#     return intersect


def distance_between_points(p0, p1):
    (x0, y0) = p0
    (x1, y1) = p1
    vec = np.array([x1 - x0, y1 - y0])
    return np.sqrt(np.sum(vec**2))

def get_perpendicular_intersection_point(line, p):
    ((x0, x1), (y0, y1)) = line
    px, py = p
    line_start = (x0, y0) 
    line_end = (x1, y1)
    if (x0 == x1) and (y0 == y1):
        raise ValueError("Lines points cannot be the point")

    line_mag = distance_between_points(line_start, line_end)
 
    u = (((px - x0) * (x1 - x0)) + 
         ((py - y0) * (y1 - y0))) / line_mag**2
 
    # if u < 0.0 or u > 1:
    #     raise ValueError("closest point does not fall within the line segment") 
 
    ix = x0 + u * (x1 - x0)
    iy = y0 + u * (y1 - y0)
 
    return ix, iy

# def get_intersection_point(line1, line2):
#     ((x0, x1), (y0, y1)) = line1
#     ((x2, x3), (y2, y3)) = line2

#     nline1 = [ (x0, y0), (x1, y1)]
#     nline2 = [ (x2, y2), (x3, y3)]
    
#     vec1 = np.array([x1 - x0, y1 - y0])
#     vec2 = np.array([x3 - x2, y3 - y2])
#     dot_p = np.dot(vec1, vec2)
#     print("DOT", dot_p)
#     if dot_p == 1:
#         raise ValueError("parallel lines")
#     len1 = np.sqrt(np.sum(vec1**2))
#     len2 = np.sqrt(np.sum(vec2**2))
#     print("Len", len1, len2)
#     if (len1 ==0 ) or (len2 ==0):
#         raise ValueError("Line with length 0")
#     if all([ p in nline2 for p in nline1]):
#         raise ValueError("Lines are co-incident")


#     # from here http://paulbourke.net/geometry/pointlineplane/
#     # Denominator for ua and ub are the same,
#     d = (line2[1][1] - line2[1][0]) * (line1[0][1] - line1[0][0]) - \
#         (line2[0][1] - line2[0][0]) * (line1[1][1] - line1[1][0]) 
#     #n_a and n_b are calculated as seperate values for readability
#     n_a = (line2[0][1] - line2[0][0]) * (line1[1][0] - line2[1][0]) - \
#           (line2[1][1] - line2[1][0]) * (line1[0][0] - line2[0][0])
#     # n_b = (line1[0][1] - line1[0][1]) * (line1[1][0] - line2[1][0]) - \
#     #       (line1[1][1] - line1[1][0]) * (line1[0][0] - line2[0][0])

#     # Calculate the intermediate fractional point that the lines potentially intersect.
#     print(n_a, d)
#     ua = n_a / d
#     #ub = n_b / d

#     #The fractional point will be between 0 and 1 inclusive if the lines
#     #intersect.  If the fractional calculation is larger than 1 or smaller
#     #than 0 the lines would need to be longer to intersect.
#     #print((ua >= 0d) and (ua <= 1d) && ub >= 0d && ub <= 1d)
#     #ptIntersection.X = L1.X1 + (ua * (L1.X2 - L1.X1));
#     xi = line1[0][0] + (ua * (line1[0][1] - line1[0][0] ))
#     #ptIntersection.Y = L1.Y1 + (ua * (L1.Y2 - L1.Y1));
#     yi = line1[1][0] + (ua * (line1[1][1] - line1[1][0])) 
#     return (xi, yi)

def is_point_in_ellipse(point, ellipse):
    px, py = point 
    center, length, width, alpha = ellipse 
    cx, cy = center
    #alpha =  np.deg2rad(angle) 
    sina = np.sin(alpha)
    cosa = np.cos(alpha)
    a = length/2
    b = width/2

    part1 = ((cosa*(px - cx) + sina * (py - cy))**2) / (a**2)
    part2 = ((sina*(px - cx) - cosa * (py - cy))**2) / (b**2)

    return (part1 + part2) <= 1
    

def get_ellipse_props_from_lines(line_maj:((float, float),(float,float)),
                                 line_min:((float, float),(float,float))):
    ((x0, xmj), (y0, ymj)) = line_maj 
    ((x0, xmn), (y0, ymn)) = line_min

    ### Check same origin
    np.testing.assert_approx_equal(line_maj[1][0], line_min[1][0])
    np.testing.assert_approx_equal(line_maj[1][0], line_min[1][0])
    #### Check they are perpendicular
    vec_maj = np.array([xmj - x0, ymj - y0])
    vec_min = np.array([xmn - x0, ymn - y0])
    dot_p = np.dot(vec_maj, vec_min)
    np.testing.assert_allclose(dot_p, 0.0, rtol=1e-3, atol=1e-3) 
    #### end check

    center = (x0, y0)
    angle = np.arctan2(vec_maj[1], vec_maj[0]) # y/x
    #costh = np.cos(angle)
    #length = np.abs(2 * ((xmj-x0)/costh))
    length = np.sqrt(np.sum(vec_maj**2)) * 2
    #width_a = np.abs(2*((ymn-y0)/costh))
    width = np.sqrt(np.sum(vec_min**2)) * 2

    # if np.isclose(costh, 0, 0.02):
    #     sinth = np.sin(angle)
    #     length = np.abs(2 * (ymj-y0)/sinth)
    #     width = np.abs(2*((xmn-x0)/sinth))
    return center, length, width, angle #np.rad2deg(angle)


def limit_angle(angle):
    """
     takes any angle (in radians) and maps to to the betwen pi/2 and - pi/2
    """
    if angle < 0:
        crankback = -(angle // (2*np.pi))
        angle += crankback * 2 * np.pi

    divs = angle // (np.pi/2)
    remainder = angle % (np.pi/2)
    ans = angle
    if divs % 2 == 0: #0 to 90 and 180 to 270. 
        ans = remainder
    else: # 90 - 180, and 270 to 360
        ans = (-np.pi/2) + remainder 
    return ans



def get_lines_from_ellipse(xy:(float,float), length:float, width:float, angle:float):
    x0, y0 = xy
    #orientation = np.deg2rad(angle)
    orientation = angle
    assert(length>0)
    assert(width>0)
    assert(abs(orientation) <= np.pi/2)
    coso = np.cos(orientation)
    sino = np.sin(orientation)
    hl = length / 2
    hw = width / 2
    x1 = x0 + (coso * hl) 
    y1 = y0 + (sino * hl)
    x2 = x0 + (sino * hw) 
    y2 = y0 - (coso * hw) 
    line_maj = ((x0, x1), (y0, y1))
    line_min = ((x0, x2), (y0, y2))
    return line_maj, line_min


def get_axis_lines_from_ellipse(xy:(float,float), length:float, width:float, angle:float):
    """
        returns the major axis and minor axis lines in the form [[x1, x2], [y1, y2]]
    """
    x0, y0 = xy
    #orientation = np.deg2rad(angle)
    orientation = angle
    assert(length>0)
    assert(width>0)
    assert(abs(orientation) <= np.pi/2)
    coso = np.cos(orientation)
    sino = np.sin(orientation)
    hl = length / 2
    hw = width / 2
    xr = x0 + (coso * hl) 
    xl = x0 - (coso * hl) 

    xright = x0 + (sino * hw) 
    xleft = x0 - (sino * hw)
    y_min_left = y0 + (coso * hw) 

    ybot = y0 + (sino * hl) 
    ytop = y0 - (sino * hl) 
    
    y2 = y0 - (coso * hw) 

    line_maj = ((xl, xr), (ytop, ybot))
    line_min = ((xleft, xright), (y_min_left, y2))
    #line_min_real = ((x0, x2), (y0, y2))

    return line_maj, line_min

def get_ellispe_from_extrema(major_points:((float,float), (float,float)),
                             minor_points:((float,float), (float,float))):
    """
        returns the ellipse from the points of the major axis and minor axis lines [[x1, y1], [x2, y2]]
    """

    xmjt, ymjt = major_points[0]
    xmjb, ymjb = major_points[1]
    xmnl, ymnl = minor_points[0]
    xmnr, ymnr = minor_points[1]

    vec_maj = np.array([xmjt - xmjb, ymjt - ymjb])
    vec_min = np.array([xmnl - xmnr, ymnl - ymnr])
    dot_p = np.dot(vec_maj, vec_min)
    np.testing.assert_allclose(dot_p, 0.0, rtol=1e-3, atol=1e-3)

    center = get_perpendicular_intersection_point(([xmjt, xmjb], [ymjt, ymjb]), (xmnr, ymnr))
    angle = np.arctan2(vec_maj[1], vec_maj[0]) # y/x
    length = np.sqrt(np.sum(vec_maj**2))
    width = np.sqrt(np.sum(vec_min**2))
    return center, length, width, angle 


if __name__ == "__main__":
    pass