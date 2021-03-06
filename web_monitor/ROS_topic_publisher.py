#!/usr/bin/env python3

import rospy
import rosnode
import time
import json
from std_msgs.msg import Float64
from std_msgs.msg import Int64
from std_msgs.msg import Float32
from std_msgs.msg import Int32
from std_msgs.msg import String


rospy.init_node("topic_publisher")

data_dict = {}
name_list = []
frame_list = []

def create_list():
    global name_list
    tmp_name = []
    try:
        pub_name = rospy.get_published_topics()
    except Exception as e:
        pub_name = []
        rospy.logerr(e)
    for name, frame in pub_name:
        name = name.split("'")[0]
        if frame == "std_msgs/Float64":
            data_dict[name] = None
            rospy.Subscriber(name, Float64, _record, callback_args = name)
            print("regist")
        elif frame == "std_msgs/Int64":
            data_dict[name] = None
            rospy.Subscriber(name, Int64, _record, callback_args = name)
            print("regist")
        elif frame == "std_msgs/Float32":
            data_dict[name] = None
            rospy.Subscriber(name, Float32, _record, callback_args = name)
            print("regist")
        elif frame == "std_msgs/Int32":
            data_dict[name] = None
            rospy.Subscriber(name, Int32, _record, callback_args = name)
            print("regist")
        else:
            pass
        tmp_name.append("/"+name)
    name_list.extend(tmp_name)
    return

def _record(req, arg):
    global data_dict
    data_dict[arg] = req.data
    return

pub = rospy.Publisher("topic_record",String, queue_size=1)
create_list()
time.sleep(3.)
while not rospy.is_shutdown():
    create_list()
    time.sleep(0.001)
    #for key in data_dict.keys():
    pub_dict = {}
    for key, value in sorted(data_dict.items()):
        pub_dict[key] = value
    bb = json.dumps(pub_dict)
    pub.publish(data=bb)
    time.sleep(0.5)
