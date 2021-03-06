from nose.tools import *

import numpy as np
import pixelhouse as ph
import tempfile
import itertools
import cv2


class Canvas_Test:
    def blank_doesnt_modify_in_place_test(self):

        """ blank_doesnt_modify_in_place_test:
            If the canvas has not had anything painted on it, its sum is 0
            If the canvas has been blanked out, its sum is 0
            Otherwise, its sum should be > 0
        """

        canvas = ph.Canvas()
        assert_true(canvas.img.sum() == 0)
        canvas += ph.circle()
        assert_true(canvas.img.sum() > 0)
        canvas.blank()
        assert_true(canvas.img.sum() > 0)
        assert_true(canvas.blank().img.sum() == 0)

    def hstack_test(self):

        """ hstack_test:
            Draw an image, stack it, and make sure it's the same as the
            numpy operation.
        """

        C1 = ph.Canvas()
        C2 = ph.Canvas()

        C1 += ph.circle()
        C2 += ph.rectangle()

        # Make sure something was drawn
        assert_true(C1.img.sum() != 0)
        assert_true(C2.img.sum() != 0)

        X = ph.hstack([C1, C2])

        img_stack = np.hstack([C1.img, C2.img])
        assert_true(np.isclose(img_stack, X.img).all())

    def vstack_test(self):

        """ vstack_test:
            Draw an image, stack it, and make sure it's the same as the
            numpy operation.
        """

        C1 = ph.Canvas()
        C2 = ph.Canvas()

        C1 += ph.circle()
        C2 += ph.rectangle()

        # Make sure something was drawn
        assert_true(C1.img.sum() != 0)
        assert_true(C2.img.sum() != 0)

        X = ph.vstack([C1, C2])

        img_stack = np.vstack([C1.img, C2.img])
        assert_true(np.isclose(img_stack, X.img).all())

    def gridstack_test(self):

        """ dstack_test:
            Draw an image, stack it, and make sure it's the same as the
            numpy operation.
        """

        C1 = ph.Canvas()
        C2 = ph.Canvas()
        C3 = ph.Canvas()

        C1 += ph.circle()
        C2 += ph.rectangle()
        C3 += ph.circle(x=1)

        # Make sure something was drawn
        assert_true(C1.img.sum() != 0)
        assert_true(C2.img.sum() != 0)
        assert_true(C3.img.sum() != 0)

        X = ph.gridstack([[C1, C2], [C2, C3]])

        img_stack = np.vstack(
            [np.hstack([C1.img, C2.img]), np.hstack([C2.img, C3.img])]
        )

        assert_true(np.isclose(img_stack, X.img).all())

    def get_set_item_test(self):
        """ get_set_item_test:
            Test pixel access like a numpy array.
        """

        C = ph.Canvas(bg="k")

        assert_true(C[20:30, 50:60].sum() == 0)

        # Set a 10x10 block red
        C[20:30, 50:60] = [255, 0, 0, 0]
        assert_equal(C[20:30, 50:60].sum(), 255 * 100)

    def print_statement_test(self):
        """ print_statement_test:
            Make sure we can print the object
        """
        width, height, extent = 105, 207, 3

        C = ph.Canvas(width, height, extent=extent)
        s1 = C.__repr__()
        s2 = f"Canvas (w/h) {height}x{width}, extent {extent}"
        assert_equal(s1, s2)

    def layer_test(self):
        """ layer_test:
            Test if layers work by testing order of operations
        """
        C1 = ph.Canvas()
        C2 = ph.Canvas()

        C1 += ph.circle(color="r")
        C1 += ph.circle(y=1, color="b")
        C1 += ph.transform.translate(x=1)

        C2 += ph.circle(color="r")
        with C2.layer() as CX:
            CX += ph.circle(y=1, color="b")
            CX += ph.transform.translate(x=1)

        img1, img2 = C1.img, C2.img

        # First make sure something was drawn in each case
        assert_true(img1.sum() > 0)
        assert_true(img2.sum() > 0)

        # Now check that they aren't equal
        assert_false((img1 == img2).all())

    def grid_coordinates_test(self):
        """ grid_coordinates_test:
            Test if we can get the grid coordinates, do twice to test cache.
        """
        C = ph.Canvas()
        coords = C.grid_coordinates()
        coords = C.grid_coordinates()

        assert_true(len(coords), 3)

    def grid_points_test(self):
        """ grid_points_test:
            Test if we can get the grid coordinates, do twice to test cache.
        """
        C = ph.Canvas()
        pts = C.grid_points()
        pts = C.grid_points()

        assert_true(len(pts), 2)

    @raises(FileNotFoundError)
    def load_missing_file_test(self):
        """ load_missing_file_test
            Raise an exception if a file is missing
        """
        C = ph.load("THIS_IS_A_MISSING_FILE.png")
        alpha = C.alpha.sum()

        assert alpha.sum() > 0

    def load_transparent_test(self):
        """ load_transparent_test:
            Load an image with a known transparent channel.
        """
        C = ph.load("tests/tree.png")
        alpha = C.alpha.sum()

        assert alpha.sum() > 0

    def set_alpha_value_test(self):
        """ set_alpha_value_test
            Set the alpha channel to a specific value
        """
        C = ph.Canvas()
        C.alpha = 120

        assert_equal(C.alpha.mean(), 120)

    def set_rgb_value_test(self):
        """ set_rgb_value_test
            Set the rgb channel to a specific value
        """
        C = ph.Canvas()
        C.rgb = 120

        assert_equal(C.alpha.mean(), 0)
        assert_equal(C.rgb.mean(), 120)

    def set_img_value_from_string_test(self):
        """ set_rgb_value_from_string_test
            Set the rgb channel to a specific value from a string
        """
        C = ph.Canvas()
        C.img = "r"

        assert_equal(C[:, :, 0].mean(), 255)
        assert_equal(C[:, :, 1].mean(), 0)
        assert_equal(C[:, :, 2].mean(), 0)
        assert_equal(C[:, :, 3].mean(), 255)

        C.img = 32
        assert_equal(C.img.mean(), 32)

    def set_img_value_from_vector_test(self):
        """ set_rgb_value_from_vector_test
            Set the rgb channel to a specific value from a vector
        """
        C = ph.Canvas()
        C.img = [1, 2, 3, 4]

        assert_equal(C[:, :, 0].mean(), 1)
        assert_equal(C[:, :, 1].mean(), 2)
        assert_equal(C[:, :, 2].mean(), 3)
        assert_equal(C[:, :, 3].mean(), 4)

    def save_load_test(self):
        """ save_load_test:
            Create an image, save it to a tmp location and try to load it
            back in. Make sure we check in PNG (lossless) and don't try to
            check the alpha channel.
        """
        C = ph.Canvas(bg="yellow")
        C += ph.circle(color="g")

        C2 = ph.Canvas()

        with tempfile.NamedTemporaryFile(suffix=".png") as F:
            C.save(F.name)
            C2.load(F.name)

        dist = C.img[:, :, :3] - C2.img[:, :, :3]
        dist = dist.astype(float) / 255
        assert_equal(dist.sum(), 0)

    def direct_load_test(self):
        """ direct_load_test:
            Load an image without creating a canvas.
        """
        C = ph.Canvas(bg="yellow")
        C += ph.circle(color="g")

        C2 = ph.Canvas()

        with tempfile.NamedTemporaryFile(suffix=".png") as F:
            C.save(F.name)
            C2 = ph.load(F.name)

        dist = C.img[:, :, :3] - C2.img[:, :, :3]
        dist = dist.astype(float) / 255
        assert_equal(dist.sum(), 0)

    def combine_canvas_test(self):
        """ combine_canvas_test:
            Try to add two canvas together with blend, add, subtract modes.
        """
        C1 = ph.Canvas()
        C1 += ph.circle(color="w")

        C2 = ph.Canvas()
        C2 += ph.circle(x=-0.5, color="b")

        C3 = C1.copy().combine(C2, mode="blend")
        C4 = C1.copy().combine(C2, mode="add")
        C5 = C1.copy().combine(C2, mode="subtract")

        # Now check that none of them are equal
        for x, y in itertools.combinations([C1, C3, C4, C5], r=2):
            assert_false((x.img == y.img).all())

    def check_length_test(self):
        """ check_length_test:
            For animation reasons, a canvas should always have a length of 2.
        """
        canvas = ph.Canvas()
        assert_true(len(canvas), 2)

    def draw_mode_using_add_test(self):
        """ draw_mode_using_add_test:
            Make sure we can draw with the "add" or "subtract" modes
        """
        canvas = ph.Canvas()
        canvas += ph.circle(mode="add")

    def check_non_antialiased_linetype_test(self):
        """ check_non_antialiased_linetype_test:
            Check the defaults for CV2 antialiasing.
        """
        assert_true(ph.Canvas.get_lineType(True), cv2.LINE_AA)
        assert_true(ph.Canvas.get_lineType(False), 8)

    @raises(ValueError)
    def bad_width_combine_canvas_test(self):
        C1 = ph.Canvas(100, 200)
        C2 = ph.Canvas(150, 200)
        C1.combine(C2)

    @raises(ValueError)
    def bad_height_combine_canvas_test(self):
        C1 = ph.Canvas(100, 200)
        C2 = ph.Canvas(100, 250)
        C1.combine(C2)

    @raises(ValueError)
    def bad_mode_combine_canvas_test(self):
        C1 = ph.Canvas()
        C2 = ph.Canvas()
        C1.combine(C2, mode="NothingToSeeHere")

    @raises(TypeError)
    def bad_type_iadd_canvas_test(self):
        C1 = ph.Canvas(100, 200)
        C1 += 3

    def resize_up_test(self):
        """ resize_up_test:
            After scaling by 2x, it should be 400 pixels.
        """
        C = ph.Canvas(width=200, height=200)
        C += ph.rectangle(x=0.5, y=0.25, x1=0.75, y1=0.75)

        assert_true(C.width == 200)
        assert_true(C.height == 200)
        C.resize(fx=2)

        assert_true(C.width == 400)
        assert_true(C.height == 400)

    def resize_exact_test(self):
        """ resize_exact_test:
            After scaling, it should have these exact dimensions
        """
        C = ph.Canvas(width=200, height=200)
        C += ph.rectangle(x=0.5, y=0.25, x1=0.75, y1=0.75)
        C.resize(output_size=(100, 50))

        assert_true(C.width == 100)
        assert_true(C.height == 50)

    def resize_animation_test(self):
        """ resize_animation_test:
            Check that resizing an animation doesn't fail
        """
        C = ph.Animation()
        C.resize(2.0)

    @raises(ValueError)
    def resize_set_both_exact_and_scale_test(self):
        """ resize_set_both_exact_and_scale_test:
         Raise an error if both values are set
        """
        C = ph.Canvas()
        C.resize(fx=2.0, output_size=(100, 50))

    def create_from_single_channel_img_test(self):
        """ create_from_single_channel_img_test:
         Create a canvas from a single channel image
        """
        img = 37 * np.ones(shape=(100, 200)).astype(np.uint8)
        C = ph.Canvas(img=img)

        assert_equal(C.rgb.mean(), 37)
        assert_equal(C.alpha.mean(), 0)

    def create_from_rgb_channel_img_test(self):
        """ create_from_rgb_channel_img_test:
         Create a canvas from a rgb channel image
        """
        img = 37 * np.ones(shape=(100, 200, 3)).astype(np.uint8)
        C = ph.Canvas(img=img)

        assert_equal(C.rgb.mean(), 37)
        assert_equal(C.alpha.mean(), 0)

    def create_from_rgba_channel_img_test(self):
        """ create_from_rgba_channel_img_test:
         Create a canvas from a rgba channel image
        """
        img = 37 * np.ones(shape=(100, 200, 4)).astype(np.uint8)
        C = ph.Canvas(img=img)

        assert_equal(C.rgb.mean(), 37)
        assert_equal(C.alpha.mean(), 37)
