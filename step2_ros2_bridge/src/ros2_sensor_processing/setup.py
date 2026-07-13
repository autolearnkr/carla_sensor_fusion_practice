import os
from glob import glob
from setuptools import setup

package_name = 'ros2_sensor_processing'

setup(
    name=package_name,
    version='1.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Student',
    maintainer_email='student@todo.todo',
    description='ROS2 camera and lidar pre-processing pipelines.',
    license='Apache License 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'camera_pipeline_node = ros2_sensor_processing.camera_pipeline_node:main',
            'lidar_filter_tobyte_node = ros2_sensor_processing.lidar_filter_tobyte_node:main',
            'lidar_filter_create_cloud_node = ros2_sensor_processing.lidar_filter_create_cloud_node:main',
        ],
    },
)
