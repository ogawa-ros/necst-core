#!usr/bin/env python3

name  = 'db_logger_always'

import time
import threading
import necstdb

import rospy
import std_msgs.msg

class db_logger_always(object):

        self.db_path = ''
        self.last_append_time = 0
        self.current_topic_list =[]
        self.data_list =[]

        self.th = threading.Thread(target= self.loop)
        self.th.start()

        pass

    def regist(self, data):
        if data["time"] -  self.last_append_time >= 10:
            self.data_list.append({'path': self.db_path, 'data': data})
            pass
        return

    def loop(self):
       
        while True:    
            if len(self.data_list) == 0:
                self.db.finalize()
                pass
                    
                if rospy.is_shutdown():
                    break
                time.sleep(0.01)
                continue
            
            d = self.data_list.pop(0)
            
            if d["topic"] not in self.current_topic_list:
                self.db.insert(d)
                self.curret_topic_list.append(d["topic"])
            else:
                self.last_append_time = d["time"]
                self.current_topic_list =[]
                self.data_list =[]
            continue 
        return   