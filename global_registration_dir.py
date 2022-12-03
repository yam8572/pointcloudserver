
import open3d as o3d
import numpy as np
import copy
import sys

def draw_registration_result(source, target, transformation):
    source_temp = copy.deepcopy(source)
    target_temp = copy.deepcopy(target)
    source_temp.paint_uniform_color([1, 0, 0])
    target_temp.paint_uniform_color([0, 1, 0])
    source_temp.transform(transformation)
    # o3d.visualization.draw_geometries([source_temp, target_temp],
    #                                   zoom=1,
    #                                   front=[0.6452, -0.3036, -0.7011],
    #                                   lookat=[1.9892, 2.0208, 1.8945],
    #                                   up=[-0.2779, -0.9482, 0.1556])

def write_point_cloud(pcd,pcd2,transformation):
    source_temp = copy.deepcopy(pcd)
    target_temp = copy.deepcopy(pcd2)
    source_temp.transform(transformation)
    new_point = source_temp + target_temp
    
    return new_point
    
    
    
def preprocess_point_cloud(pcd, voxel_size):
    print(":: Downsample with a voxel size %.3f." % voxel_size)
    pcd_down = pcd.voxel_down_sample(voxel_size)

    radius_normal = voxel_size * 2
    print(":: Estimate normal with search radius %.3f." % radius_normal)
    pcd_down.estimate_normals(
        o3d.geometry.KDTreeSearchParamHybrid(radius=radius_normal, max_nn=30))

    radius_feature = voxel_size * 5
    print(":: Compute FPFH feature with search radius %.3f." % radius_feature)
    pcd_fpfh = o3d.pipelines.registration.compute_fpfh_feature(
        pcd_down,
        o3d.geometry.KDTreeSearchParamHybrid(radius=radius_feature, max_nn=100))
    return pcd_down, pcd_fpfh

def prepare_dataset(voxel_size,sour,tar):
    print(":: Load two point clouds and disturb initial pose.")

    #demo_icp_pcds = o3d.data.DemoICPPointClouds()
    source = o3d.io.read_point_cloud(sour)
    target = o3d.io.read_point_cloud(tar)
    trans_init = np.asarray([[0.0, 0.0, 1.0, 0.0], [1.0, 0.0, 0.0, 0.0],
                             [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 0.0, 1.0]])
    #source.transform(trans_init)
    draw_registration_result(source, target, np.identity(4))

    source_down, source_fpfh = preprocess_point_cloud(source, voxel_size)
    target_down, target_fpfh = preprocess_point_cloud(target, voxel_size)
    return source, target, source_down, target_down, source_fpfh, target_fpfh


def execute_global_registration(source_down, target_down, source_fpfh,
                                target_fpfh, voxel_size):
    distance_threshold = voxel_size * 1.5
    print(":: RANSAC registration on downsampled point clouds.")
    print("   Since the downsampling voxel size is %.3f," % voxel_size)
    print("   we use a liberal distance threshold %.3f." % distance_threshold)
    result = o3d.pipelines.registration.registration_ransac_based_on_feature_matching(
        source_down, target_down, source_fpfh, target_fpfh, True,
        distance_threshold,
        o3d.pipelines.registration.TransformationEstimationPointToPoint(False),
        3, [
            o3d.pipelines.registration.CorrespondenceCheckerBasedOnEdgeLength(
                0.9),
            o3d.pipelines.registration.CorrespondenceCheckerBasedOnDistance(
                distance_threshold)
        ], o3d.pipelines.registration.RANSACConvergenceCriteria(100000, 0.999))
    return result


voxel_size = 0.05  # means 5cm for this dataset
source_fileDir="source/"
result_fileDir="result/"
pcd_arg1=source_fileDir+str(sys.argv[1]) # input 1
pcd_arg2=source_fileDir+str(sys.argv[2]) # input 2
pcd_arg3=result_fileDir+str(sys.argv[3]) # output 1
pcds = [pcd_arg1,pcd_arg2]
# pcds = ['cloud_bin_0.pcd','cloud_bin_1.pcd']
source, target, source_down, target_down, source_fpfh, target_fpfh = prepare_dataset(
    voxel_size,pcds[0],pcds[1])

result_ransac = execute_global_registration(source_down, target_down,
                                            source_fpfh, target_fpfh,
                                            voxel_size)

print('fitness = ',result_ransac.fitness,' rmse = ',result_ransac.inlier_rmse)

result = write_point_cloud(source,target,result_ransac.transformation)

# o3d.io.write_point_cloud(result_fileDir+'new_cloud_bin.pcd',result)
# o3d.io.write_point_cloud(result_fileDir+'new_cloud_bin.ply',result)
o3d.io.write_point_cloud(pcd_arg3 + '.pcd',result)
o3d.io.write_point_cloud(pcd_arg3 + '.ply',result)
print(result)

draw_registration_result(source_down, target_down, result_ransac.transformation)

#source, target, source_down, target_down, source_fpfh, target_fpfh = prepare_dataset(
#    voxel_size,pcds[3],pcds[2])
#
#result_ransac = execute_global_registration(source_down, target_down,
#                                           source_fpfh, target_fpfh,
#                                            voxel_size)
#
#print('fitness = ',result_ransac.fitness,' rmse = ',result_ransac.inlier_rmse)
#
#draw_registration_result(source_down, target_down, result_ransac.transformation)


# In[ ]:




