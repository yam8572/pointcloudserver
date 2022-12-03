import open3d as o3d

source_fileDir="source/"
source = o3d.io.read_point_cloud(source_fileDir+"cloud_bin_10.ply")

# visualize colored point cloud
o3d.visualization.draw_geometries([source])
# o3d.visualization.draw_geometries([source],zoom=1,
#                                   front=[0.6452, -0.3036, -0.7011],
#                                   lookat=[1.9892, 2.0208, 1.8945],
#                                   up=[-0.2779, -0.9482, 0.1556])