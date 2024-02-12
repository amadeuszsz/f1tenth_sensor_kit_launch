# Copyright 2023 Amadeusz Szymko
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from yaml import safe_load

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.actions import IncludeLaunchDescription
from launch.actions import OpaqueFunction
from launch.launch_description_sources import FrontendLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch.substitutions import PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def launch_setup(context, *args, **kwargs):
    pkg_prefix = FindPackageShare('f1tenth_sensor_kit_launch')
    joy_config = PathJoinSubstitution([pkg_prefix, 'config/joy/joy_controller.param.yaml'])
    with open(LaunchConfiguration('vehicle_param_file').perform(context), 'r') as f:
        vehicle_info_param = safe_load(f)['/**']['ros__parameters']

    joy_controller = Node(
        package='joy_controller',
        executable='joy_controller',
        name='joy_controller',
        parameters=[
            joy_config,
            {
                'steer_ratio': vehicle_info_param['max_steer_angle']
            }
        ],
        remappings=[
            ('input/joy', 'joy'),
            ('input/odometry', '/localization/kinematic_state'),
            ('output/control_command', '/external/selected/control_cmd'),
            ('output/external_control_command', '/api/external/set/command/remote/control'),
            ('output/shift', '/api/external/set/command/remote/shift'),
            ('output/turn_signal', '/api/external/set/command/remote/turn_signal'),
            ('output/heartbeat', '/api/external/set/command/remote/heartbeat'),
            ('output/gate_mode', '/control/gate_mode_cmd'),
            ('output/vehicle_engage', '/vehicle/engage'),
            ('service/emergency_stop', '/api/autoware/set/emergency'),
            ('service/autoware_engage', '/api/autoware/set/engage')
        ],
        output='screen'
    )

    joy_node = Node(
        package='joy',
        executable='joy_node',
        name='joy_node',
        parameters=[
            {
                'autorepeat_rate': 1.0,
                'deadzone': 0.0
            }
        ],
        output='screen'
    )

    return [
        joy_controller,
        joy_node
    ]


def generate_launch_description():
    declared_arguments = []

    def add_launch_arg(name: str, default_value: str = None):
        declared_arguments.append(
            DeclareLaunchArgument(name, default_value=default_value)
        )

    add_launch_arg('vehicle_param_file')

    return LaunchDescription([
        *declared_arguments,
        OpaqueFunction(function=launch_setup)
    ])
