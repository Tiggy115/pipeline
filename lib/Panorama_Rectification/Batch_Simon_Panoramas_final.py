import glob
import skimage.io
import numpy as np
from PIL import Image
import os.path
import skimage.io

import skimage.io
from lib.Panorama_Rectification.Panos.Pano_rectification import simon_rectification
from lib.Panorama_Rectification.Panos.Pano_project import render_imgs

from lib.Panorama_Rectification.Panos.Pano_visualization import R_heading, draw_all_vp_and_hl_color, draw_all_vp_and_hl_bi, \
    draw_sphere_zenith, R_roll, R_pitch
from lib.Panorama_Rectification.Panos.Pano_zp_hvp import calculate_consensus_zp
from lib.Panorama_Rectification.Panos.Pano_consensus_vis import draw_consensus_zp_hvps, draw_consensus_rectified_sphere, \
    draw_center_hvps_rectified_sphere, draw_center_hvps_on_panorams
import lib.Panorama_Rectification.Pano_hvp
from lib.Panorama_Rectification.Panos.Pano_histogram import calculate_histogram
from lib.Panorama_Rectification.Panos.Pano_project import project_facade_for_refine


########## add new random seed
# np.random.seed(1)

def render_facades(root):
    print("Start rectify \n")
    plot_redundant = False
    save_directly = True

    out = "out"

    new_count = 5

    tmp_count = str(new_count)

    out_folder = os.path.join(root, out)
    Img_folder = os.path.join(root, 'Pano_input/')
    inter_Dir = os.path.join(root, out, 'Pano_hl_z_vp/')

    imageList = glob.glob(Img_folder + '*.png')
    imageList.sort()

    rendering_output_folder = os.path.join(root, out, 'Rendering')
    if not os.path.exists(rendering_output_folder):
        os.makedirs(rendering_output_folder)

    # for im_path in ['/home/zhup/Desktop/GSV_Pano_val/Val/images/9wG3a9VOkwTSqnq6zsbdSQ.jpg']:
    # for im_path in imageList[10*new_count:10*(new_count+1)]:
    for im_path in imageList:
        print(im_path)
        im = Image.open(im_path)
        # rendering_img_base = os.path.join(rendering_output_folder, os.path.splitext(os.path.basename(im_path))[0])
        rendering_img_base = os.path.join(rendering_output_folder, os.path.splitext(os.path.basename(im_path))[0])

        thread_num = 1
        thread = str(thread_num) + '/'
        tmp_folder = os.path.join(root, 'tmp', thread)

        if not os.path.exists(tmp_folder):
            os.makedirs(tmp_folder)
        removelist = glob.glob(tmp_folder + '*.jpg')
        for i in removelist:
            os.remove(i)

        # render_num = 16
        render_num = 4
        start = int(-render_num / 2) + 1
        end = render_num + start
        degree = 360 / render_num
        panorama_img = skimage.io.imread(im_path)
        coordinates_list = []

        tilelist = render_imgs(panorama_img, tmp_folder, save_directly)
        if not save_directly:
            tilelist = glob.glob(tmp_folder + '*.jpg')
            tilelist.sort()

        hl = []
        hvps = []
        hvp_groups = []
        z = []
        z_group = []
        ls = []
        z_homo = []
        hvp_homo = []
        ls_homo = []

        name = im_path.split(sep="/")
        name = name[len(name) - 1]

        for i in range(len(tilelist)):
            [tmp_hl, tmp_hvps, tmp_hvp_groups, tmp_z, tmp_z_group, tmp_ls, tmp_z_homo, tmp_hvp_homo, tmp_ls_homo,
             params] = simon_rectification(tilelist[i], i, inter_Dir, root, tmp_count, name)
            hl.append(tmp_hl)
            hvps.append(tmp_hvps)
            hvp_groups.append(tmp_hvp_groups)
            z.append(tmp_z)
            z_group.append(tmp_z_group)
            ls.append(tmp_ls)
            z_homo.append(tmp_z_homo)
            hvp_homo.append(tmp_hvp_homo)
            ls_homo.append(tmp_ls_homo)

        # print('get all the zenith points')

        removelist = glob.glob(tmp_folder + '*.jpg')
        for i in removelist:
            #os.remove(i)
            pass

        ####################### Get all the zenith points from all the (8) viewpoints

        zenith_points = np.array([R_heading(np.pi / 2 * (i - 1)).dot(zenith) for i, zenith in enumerate(z_homo)])
        points2 = np.array([R_heading(np.pi / 2 * (i - 1)).dot(np.array([0., 0., 1.])) for i in range(len(z_homo))])
        hv_points = [(R_heading(np.pi / 2 * (i - 1)).dot(hv_p.T)).T for i, hv_p in enumerate(hvp_homo)]

        if plot_redundant:
            draw_all_vp_and_hl_color(zenith_points, hv_points, im.copy(), root)

            draw_all_vp_and_hl_bi(zenith_points, hv_points, im.copy(), root)
            # draw_zenith_on_top_color(zenith_points, root)
            # draw_zenith_on_top_bi(zenith_points, root)
            draw_sphere_zenith(zenith_points, hv_points, root)

        ####################### Calculate the consensus zenith point

        [zenith_consensus, best_zenith] = calculate_consensus_zp(zenith_points, method='svd')

        # Transform the zenith points back to original homogeneous coordinates
        # zenith_consensus_org = np.array(
        #     [R_heading(-np.pi / 6 * (i - 5)).dot(zenith) for i, zenith in enumerate(zenith_consensus)])
        zenith_consensus_org = np.array(
            [R_heading(-np.pi / 2 * (i - 1)).dot(zenith) for i, zenith in enumerate(zenith_consensus)])

        result_list = []
        for i in range(len(zenith_consensus_org)):
            # result = Pano_hvp.hvp_from_zenith(ls_homo[i], zenith_consensus_org[i], params)

            result = Panorama_Rectification.Pano_hvp.get_all_hvps(ls_homo[i], zenith_consensus_org[i], params)
            result_list.append(result)

        hvps_consensus_org = []
        for i in range(len(result_list)):
            # hvps_consensus_org.append(result_list[i]['hvp_homo'])
            hvps_consensus_org.append(result_list[i])

        hvps_consensus_uni = [(R_heading(np.pi / 2 * (i - 1)).dot(hv_p.T)).T for i, hv_p in
                              enumerate(hvps_consensus_org)]

        if plot_redundant:
            draw_consensus_zp_hvps(best_zenith, hvps_consensus_uni, im.copy(), root)

        ####################### Calculate pitch and roll
        pitch = np.arctan(best_zenith[2] / best_zenith[1])
        roll = - np.arctan(best_zenith[0] / np.sign(best_zenith[1]) * np.hypot(best_zenith[1], best_zenith[2]))

        hvps_consensus_rectified = [R_roll(-roll).dot(R_pitch(-pitch).dot(vp.T)).T for vp in hvps_consensus_uni]

        if plot_redundant:
            draw_consensus_rectified_sphere(hvps_consensus_rectified, root)

        ###################### Calculate horizontal VP histogram

        final_hvps_rectified = calculate_histogram(hvps_consensus_rectified, root, plot_redundant)

        # final_hvps_rectified = [np.array([1.,0.,0.]), np.array([0.,0.,1.])]
        # pitch = 0
        # roll = 0

        # rrd = np.random.rand() * np.pi
        # final_hvps_rectified = [np.array([np.sin(rrd), 0., np.cos(rrd)]), np.array([np.sin(np.pi/2 + rrd), 0., np.cos(np.pi/2 + rrd)])]
        # pitch = 0
        # roll = 0

        # Test whether the main vanishing point is near 90 degrees to the second vanishing point

        # if len(final_hvps_rectified) == 2:
        #     hvp1 = final_hvps_rectified[0]
        #     hvp2 = final_hvps_rectified[1]
        #     if np.abs(hvp1.dot(hvp2)) > np.sin(np.radians(5)):
        #         final_hvps_rectified = [final_hvps_rectified[0]]

        if plot_redundant:
            draw_center_hvps_rectified_sphere(np.array(final_hvps_rectified), root)
            draw_center_hvps_on_panorams(best_zenith, np.array(final_hvps_rectified), im.copy(), pitch, roll, root)

        # Draw rectified panorama

        from lib.Panorama_Rectification.Panos.Pano_new_pano import create_new_panorama, draw_new_panorama
        if plot_redundant:
            new_pano_path = create_new_panorama(im_path, pitch, roll, root)
            draw_new_panorama(new_pano_path, np.array(final_hvps_rectified), root)

        ###################### Rendering images from panoramas

        project_facade_for_refine(np.array(final_hvps_rectified), im.copy(), pitch, roll, im_path, out_folder, tmp_folder,
                                  rendering_img_base, tmp_count)
        print(100)


if __name__ == '__main__':
    render_facades('.')
