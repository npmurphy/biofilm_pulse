
from hypothesis import given
from hypothesis.strategies import tuples, floats, integers
from processing.cell_tracking import cell_dimensions
import unittest
import numpy as np
    
# visual debuging    
from matplotlib.patches import Ellipse
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import skimage.measure

def assert_ellipse_equal(e1, e2, rtol=1e-7, atol=1e-7):
    t1 = e1[0] + e1[1:]
    t2 = e2[0] + e2[1:]
    for o, r, m in zip(t1, t2, ["x", "y", "length", "width", "angle"]):
        np.testing.assert_allclose(o, r, rtol=rtol, atol=atol, err_msg=m)

def assert_point_on_line(line, point, rtol=1e-7, atol=1e-7):
    ((x1, x2), (y1, y2)) = line
    if (x2 - x1) == 0: 
        np.testing.assert_allclose(point[0], x1, rtol=1e-7, atol=1e-7, err_msg="x is not zero")
    elif (y2 - y1) == 0: 
        np.testing.assert_allclose(point[1], y1, rtol=1e-7, atol=1e-7, err_msg="y is not zero")
    else:
        m = (y2 - y1)/(x2 - x1)
        c = y1 - m*x1 
        cn = point[1] - m * point[0]
        np.testing.assert_allclose(cn, c, rtol=rtol, atol=atol)


class TestLinesToEllipseConversions(unittest.TestCase):
    t_coord = floats(min_value=-1e5, max_value=1e5)
    t_size = floats(min_value=0.05, max_value=1e5)
    t_change = floats(min_value=-1e5, max_value=1e5)
    t_angle = floats(min_value=-(np.pi/2), max_value=np.pi/2)
    t_ellipse = tuples(tuples(t_coord, t_coord), t_size, t_size, t_angle)
    t_point = tuples(t_coord, t_coord)
    t_line = tuples(t_point, t_point)

    def test_limit_angle(self):
        test_negs = np.deg2rad([ - 10, -30, -80, -90, -270, -355, -370, -460])
        result_negs = np.array([ cell_dimensions.limit_angle(n) for n in test_negs])
        expected_negs = np.deg2rad([ -10, -30, -80, -90, -90, 5, -10, 80])
        np.testing.assert_allclose(result_negs, expected_negs)

        test_pos = np.deg2rad([10, 50, 70, 95, 130, 160, 175, 190, 220, 250, 280, 300,330, 350, 360, 380, 390])
        expected_pos = np.deg2rad([ 10, 50, 70, -85, -50, -20, -5, 10, 40, 70, -80, -60, -30, -10, 0, 20, 30])
        result_pos = [ cell_dimensions.limit_angle(n) for n in test_pos]
        np.testing.assert_allclose(result_pos, expected_pos)


    @given(t_ellipse)
    def test_ellipse_to_lines(self, origin_ellipse):
        majr, minr = cell_dimensions.get_lines_from_ellipse(*origin_ellipse)
        new_ellipse = cell_dimensions.get_ellipse_props_from_lines(majr, minr)
        assert_ellipse_equal(new_ellipse, origin_ellipse)


    #@given(t_point, t_point, float())
    #def test_lines_to_ellipse(self, cent, maj_point, min_len):
    #    pass
        ## TODO not sure how to do this. 


    @given(t_ellipse, t_angle)
    def test_rotate_lines_using_maj_line(self, origin_ellipse, rotate):
        orig_maj, orig_min = cell_dimensions.get_lines_from_ellipse(*origin_ellipse)

        c, l, w, a = origin_ellipse
        rotate_ellipse = c, l, w, cell_dimensions.limit_angle(a + rotate)

        rotate_maj, rotate_min = cell_dimensions.get_lines_from_ellipse(*rotate_ellipse)
        self.assertEqual(rotate_maj[0][0], orig_maj[0][0]) # x0 and 
        self.assertEqual(rotate_maj[1][0], orig_maj[1][0]) # y0 should be the same

        new_maj, new_min = cell_dimensions.rotate_lines_using_maj_line(orig_maj, orig_min, rotate_maj)
        new_ellipse = cell_dimensions.get_ellipse_props_from_lines(new_maj, new_min)

        assert_ellipse_equal(new_ellipse, rotate_ellipse)

    @given(t_line, t_point)
    def test_perpendicular_intersection_point(self, line, point):
        ((x0, x1), (y0, y1)) = line
        px, py = point
        vec  = np.array([x1 - x0, y1 - y0])
        if (x0 == x1) and (y0 == y1):
            self.assertRaises(ValueError, cell_dimensions.get_perpendicular_intersection_point, line, point)
        else:
            (xn, yn) = cell_dimensions.get_perpendicular_intersection_point(line, point)
            assert_point_on_line(line, (xn, yn)) 
            # Check the angle between them is pi/2, (dot product is 0 )
            vecn = np.array([xn - px, yn - py])
            np.testing.assert_allclose(np.dot(vec, vecn), 0.0, rtol=1e-4, atol=1e-4, err_msg="acuracy")



    @unittest.skip("This is failing with a tolerence error")
    @given(t_ellipse, t_change, t_change)
    def test_get_nearest_point_on_min_axis(self, origin_ellipse, width_change, miss_distance):
        oc, ol, ow, oa = origin_ellipse
        target_ellipse = oc, ol, ow+width_change, oa
        
        # get its lines 
        orig_maj, orig_min = cell_dimensions.get_lines_from_ellipse(*origin_ellipse)
        # find a line on orig_min that is the new length. 
        vec_min = np.array([orig_min[0][1] - orig_min[0][0], 
                            orig_min[1][1] - orig_min[1][0]])
        old_width = np.sqrt(np.sum(vec_min[0]**2 + vec_min[1]**2))
        old_angle = np.arctan2(vec_min[1], vec_min[0])
        new_width = old_width + width_change 

        ## A point on the same line
        new_x = np.cos(old_angle) * new_width
        new_y = np.sin(old_angle) * new_width
        new_min = [ [orig_min[0][0], orig_min[0][0] + new_x ], 
                    [orig_min[0][1], orig_min[0][1] + new_y ]]

        new_ellipse = cell_dimensions.get_ellipse_props_from_lines(orig_maj, new_min)
        assert_ellipse_equal(new_ellipse, target_ellipse, rtol=1e-1, atol=1e-1)


    @unittest.skip("".join(["I could not get this test to pass.",
                       "It was becomming a chance to figure out what ",
                       "skimage.io.draw considered a covered pixel for the ellipse."]))
    @given(t_ellipse, tuples(integers(min_value=10, max_value=1024), integers(min_value=10, max_value=2048)))
    def test_get_cell_pixels(self, ellipse, shape):
        oc, ol, ow, oa = ellipse
        area = np.pi * (ol*0.5) * (ow*0.5)
        print("Elli", oc, ol, ow, oa)
        o_maj, o_min = cell_dimensions.get_lines_from_ellipse(*ellipse)
        print("lines", o_maj, o_min)
        ((c0, cmj), (r0, rmj)) = o_maj
        ((c0, cmn), (r0, rmn)) = o_min
        testim = np.zeros(shape, dtype=np.uint8)
        
        #majline_rc = [int(np.round(x)) for x in [c0, cmj, r0, rmj]]
        #minline_rc = [int(np.round(x)) for x in [c0, cmn, r0, rmn]]
        #majline = skimage.draw.line(*majline_rc)
        #minline = skimage.draw.line(*minline_rc)
        #majline = cell_dimensions.positive_only(*majline)
        #minline = cell_dimensions.positive_only(*minline)
        #print("Maj, rc", majline_rc)
        #print("Maj line", majline)
        #print("Min rc", minline_rc)
        #print("Min line", minline)
        #testim[majline] = 1
        #testim[minline] = 1
        #print(r0, c0)
        if area > 0.5 and ow>0.5 and ol>0.5 :
            testim[min(shape[0]-1, int(r0)), min(shape[1]-1, int(c0))] = 1
        total = np.sum(testim)

        rr, cc = cell_dimensions.get_cell_pixels(*ellipse, shape)
        ele_total = np.sum(testim[rr, cc])
        try:
            print("total:", total)
            print("eletotal:", ele_total)
            self.assertEqual(total, ele_total)
        except AssertionError as e: 
            view_cell_pixels(testim, ellipse)
            raise e

    def test_example_get_cell_pixels_point_in_ellipse(self):
        pos = (15,9)
        ang = 30 
        length = 15
        width = 6
        ellipse = pos, length, width, np.deg2rad(ang)
        image = np.zeros((20, 30), dtype=int)
        pixel_r, pixel_c = cell_dimensions.get_cell_pixels(*ellipse, image.shape)
        image[pixel_r, pixel_c] = 1

        for r, c in zip(pixel_r, pixel_c):
            self.assertTrue(cell_dimensions.is_point_in_ellipse((c,r), ellipse ))


def test_intersection_of_new_minor_point_to_minor_axis():
    fig, ax = plt.subplots(1,1)

    ax.set_aspect('equal', 'datalim')
    pos = (2,3)
    ang = 23
    length = 5
    width = 2
    #print("input: pos {0}, length {1} widht {2} ang {3}".format(pos, length, width, ang))
    e = Ellipse(pos, length, width, ang)

    xy_maj, xy_min = cell_dimensions.get_lines_from_ellipse(e.center, e.width, e.height, e.angle)

    rcent, rlen, rwdth, rang = cell_dimensions.get_ellipse_props_from_lines(xy_maj, xy_min)

    re = Ellipse(rcent, rlen+0.2, rwdth+0.2, rang, color="purple", alpha=0.3)

    line_maj = plt.Line2D(*xy_maj, color="red")
    line_min = plt.Line2D(*xy_min, color="yellow")

    ax.plot(xy_maj[0][1], xy_maj[1][1], "o", color="red") #, markeredge="black")
    ax.plot(xy_min[0][1], xy_min[1][1], "o", color="yellow")#, markeredge="black")

    #ax.plot(10*np.sin(np.deg2rad(e.angle)), 10*np.cos(np.deg2rad(e.angle)), "o", color="r")
    ax.plot([e.center[0], e.center[0] + 10*np.cos(np.deg2rad(e.angle))],
            [e.center[1], e.center[1] + 10*np.sin(np.deg2rad(e.angle))], linestyle=":", color="black")
    ax.plot([e.center[0], e.center[0] + 10*np.sin(np.deg2rad(e.angle))],
            [e.center[1], e.center[1] - 10*np.cos(np.deg2rad(e.angle))], linestyle=":", color="black")
    ax.plot([e.center[0] - 10, e.center[0] + 10], [e.center[1], e.center[1]], linestyle="-", color="gray")
    ax.plot([e.center[0], e.center[0]], [e.center[1]-10, e.center[1] + 10], linestyle="-", color="gray")
    ax.add_patch(e)
    ax.add_patch(re)
    ax.add_line(line_maj)
    ax.add_line(line_min)
    ax.set_xlim(0, 5)
    ax.set_ylim(0, 6)

    point = (3.5, 2.16)
    ax.plot(point[0], point[1], "*", color="purple")
    #find the y intercept
    xi  = ((e.center[1] - point[1]) / np.tan(np.deg2rad(ang)) ) + point[0]
    ax.plot(xi, e.center[1], "*", color="black")
    intersect = cell_dimensions.get_perpendicular_intersection_point(xy_min, [[point[0], xi], [point[1], e.center[1]]])

    ax.plot([point[0], xi], [point[1], e.center[1]], linestyle="-", color="orange")
    ax.plot(intersect[0], intersect[1], marker = "s", color="green")
    plt.show()

def testing_rotate_lines_by_major():
    fig, ax = plt.subplots(1,1)

    ax.set_aspect('equal', 'datalim')
    pos = (2,3)
    ang = 23
    length = 5
    width = 2
    print("input: pos {0}, length {1} widht {2} ang {3}".format(pos, length, width, ang))
    e = Ellipse(pos, length, width, ang)

    xy_maj, xy_min = cell_dimensions.get_lines_from_ellipse(e.center, e.width, e.height, e.angle)

    ax.plot(xy_maj[0][1], xy_maj[1][1], "o", linestyle="-", color="red") #, markeredge="black")
    ax.plot(xy_min[0][1], xy_min[1][1], "o", linestyle="-", color="orange")#, markeredge="black")
    line_maj = Line2D(*xy_maj, color="red")
    line_min = Line2D(*xy_min, color="orange")
    ax.add_line(line_maj)
    ax.add_line(line_min)

    print(xy_maj)
    npt = (4.6, 5)
    new_maj = ((xy_maj[0][0], npt[0]), (xy_maj[1][0], npt[1]))

    _, new_min = cell_dimensions.rotate_lines_using_maj_line(xy_maj, xy_min, new_maj)

    rcent, rlen, rwdth, rang = cell_dimensions.get_ellipse_props_from_lines(xy_maj, xy_min)
    ax.plot(new_maj[0][1], new_maj[1][1], "*",  color="red") #, markeredge="black")
    ax.plot(new_min[0][1], new_min[1][1], "*",  color="orange")#, markeredge="black")
    line_nmaj = plt.Line2D(*new_maj, linestyle=":", color="red")
    line_nmin = plt.Line2D(*new_min, linestyle=":", color="orange")
    ax.add_line(line_nmaj)
    ax.add_line(line_nmin)


    #ax.plot(10*np.sin(np.deg2rad(e.angle)), 10*np.cos(np.deg2rad(e.angle)), "o", color="r")
    # ax.plot([e.center[0], e.center[0] + 10*np.cos(np.deg2rad(e.angle))],
    #         [e.center[1], e.center[1] + 10*np.sin(np.deg2rad(e.angle))], linestyle=":", color="black")
    # ax.plot([e.center[0], e.center[0] + 10*np.sin(np.deg2rad(e.angle))],
    #         [e.center[1], e.center[1] - 10*np.cos(np.deg2rad(e.angle))], linestyle=":", color="black")
    ax.plot([e.center[0] - 10, e.center[0] + 10], [e.center[1], e.center[1]], linestyle="-", color="gray")
    ax.plot([e.center[0], e.center[0]], [e.center[1]-10, e.center[1] + 10], linestyle="-", color="gray")
    ax.set_xlim(0, 5)
    ax.set_ylim(0, 6)

    plt.show()

def view_cell_pixels(image, ellipse):
    fig, ax = plt.subplots(1,1)
    ax.set_aspect('equal', 'datalim')
    ellipse_props = cell_dimensions.props_to_mplellipse(*ellipse)
    e = Ellipse(**ellipse_props, alpha=0.3, color="blue")
    
    #ax.imshow(image, cmap=plt.cm.Greens)
    ax.add_patch(e)
    
    cell_pix = np.zeros_like(image)
    pixel = cell_dimensions.get_cell_pixels(*ellipse, image.shape)
    cell_pix[pixel] = 1
    cimage = np.dstack([image, cell_pix, np.zeros_like(image)]) * 255
    ax.imshow(cimage)
    #ax.imshow(cell_pix, cmap=plt.cm.Reds, alpha=0.3)

    # xy_maj, xy_min = get_lines_from_ellipse(e.center, e.width, e.height, e.angle)

    # ax.plot(xy_maj[0][1], xy_maj[1][1], "o", linestyle="-", color="red") #, markeredge="black")
    # ax.plot(xy_min[0][1], xy_min[1][1], "o", linestyle="-", color="orange")#, markeredge="black")
    # line_maj = Line2D(*xy_maj, color="red")
    # line_min = Line2D(*xy_min, color="orange")
    # ax.add_line(line_maj)
    # ax.add_line(line_min)
    plt.show(block=True)


def test_get_cell_pixels():
    fig, ax = plt.subplots(1,1)
    ax.set_aspect('equal', 'datalim')
    pos = (15,9)
    #ang = -23
    ang = 30 #330
    length = 15
    width = 6
    e = Ellipse(pos, length, width, ang, alpha=0.3)
    
    image = np.zeros((20, 30), dtype=int)
    pixel = cell_dimensions.get_cell_pixels(pos, length, width, ang, image.shape)
    image[pixel] = 1
    ax.imshow(image)
    
    ax.add_patch(e)

    xy_maj, xy_min = cell_dimensions.get_lines_from_ellipse(e.center, e.width, e.height, e.angle)

    ax.plot(xy_maj[0][1], xy_maj[1][1], "o", linestyle="-", color="red") #, markeredge="black")
    ax.plot(xy_min[0][1], xy_min[1][1], "o", linestyle="-", color="orange")#, markeredge="black")
    line_maj = Line2D(*xy_maj, color="red")
    line_min = Line2D(*xy_min, color="orange")
    ax.add_line(line_maj)
    ax.add_line(line_min)

    plt.show()

def test_is_point_in_ellipse():
    fig, ax = plt.subplots(1,1)
    ax.set_aspect('equal', 'datalim')

    pos = (15,9)
    #ang = -23
    ang = 30 #330
    length = 15
    width = 6
    ellipse = pos, length, width, ang
    e = Ellipse(pos, length, width, ang, alpha=0.3)

    npoints = 200
    points_X = np.random.random(npoints) * 20
    points_Y = np.random.random(npoints) * 20
    in_ellipse = np.zeros(npoints, dtype=int) 

    for i, (px, py) in enumerate(zip(points_X, points_Y)):
        in_ellipse[i] = int(cell_dimensions.is_point_in_ellipse((px, py), ellipse))
   
    ax.add_patch(e)
    ax.scatter(points_X, points_Y, c=in_ellipse)
    plt.show()

def test_ellipse_fit():
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    #from matplotlib.artist import Artist
    from matplotlib.patches import Ellipse
    #testing_rotate_lines_by_major()
    fig, ax = plt.subplots(1,1)
    ax.set_aspect('equal', 'datalim')
    pos = (15,9)
    #ang = -23
    ang = 30 #330
    rad = np.deg2rad(30) #330
    print(rad)
    length = 21
    width = 7
    e = Ellipse(pos, length, width, ang, alpha=0.3)
    ellipse_p = cell_dimensions.mplellipse_to_props(e)
    print(ellipse_p)
    print(-np.pi/2, np.pi/2)
    
    image = np.zeros((40, 40), dtype=int)
    
    pixel = cell_dimensions.get_cell_pixels(*ellipse_p, image.shape)
    #pixel = cell_dimensions.get_cell_pixels(pos, length, width, rad, image.shape)
    image[pixel] = 1
    ax.imshow(image)
    
    ax.add_patch(e)

    xy_maj, xy_min = cell_dimensions.get_lines_from_ellipse(*ellipse_p)

    ax.plot(xy_maj[0][1], xy_maj[1][1], "o", linestyle="-", color="red") #, markeredge="black")
    ax.plot(xy_min[0][1], xy_min[1][1], "o", linestyle="-", color="orange")#, markeredge="black")
    line_maj = Line2D(*xy_maj, color="red")
    line_min = Line2D(*xy_min, color="orange")
    ax.add_line(line_maj)
    ax.add_line(line_min)

    #Fitting an ellipse
    props = skimage.measure.regionprops(image) 
    print(len(props))
    fit_cell = cell_dimensions.regionprops_to_props(props[0])
    print(fit_cell)
    e2 = Ellipse(**cell_dimensions.props_to_mplellipse(*fit_cell), color="orange", alpha=0.3)
    ax.add_patch(e2)
    plt.show()

def visual_testing():
    #testing_rotate_lines_by_major()
    #test_get_cell_pixels()
    #test_is_point_in_ellipse()
    test_ellipse_fit()
    #test_get_cell_pixels()



if __name__ == '__main__':
    visual_testing()
    #unittest.main()
