#!usr/bin/env python3

name  = 'db_logger_operation'

import time
import threading
import necstdb

import rospy
import std_msgs.msg

class db_logger_operation(object):

    def __init__(self):
        self.data_list = []
        self.table_dict = {}
        self.db_path = ''
        self.sub_path = rospy.Subscriber(
            name = '/logger_path',
            data_class = std_msgs.msg.String,
            callback = self.callback_path,
            queue_size = 1,
        )
        
        self.db = necstdb.opendb('/home/exito/data/logger/')
        self.th = threading.Thread(target= self.loop)

        self.th.start()
        pass



    def regist(self, data):
        if 
            self.data_list.append('data': data)
        else: pass
      
        return

    def loop(self):
       
        while True:    
            if len(self.data_list) == 0:
                self.db.close()
                pass
                    
                if rospy.is_shutdown():
                    break
                time.sleep(0.01)
                continue

            d = self.data_list.pop(0)
            table_name = d['topic'].replace('/','-')
            
            if type(d['msg']['data']) is list:
                table_data = [d['time'],*d['msg']['data']]

            elif type(d['msg']['data']) is tuple:
                table_data = [d['time'],*d['msg']['data']]
            
            else: 
                table_data = [d['time'],*d['msg']['data']]
            
            db.create_table(table_name,
                            {'data':[
                                {
                                   ' key': 'timestamp',
                                   'format': 'd',
                                   'size': 8,
                                },
                                {
                                    'key': 'data',
                                    'format': '32768f',
                                    'size': 131072,
                                },],
                            'memo': 'generated by necstdb node',
                            'version': '0.2.0',})
            
            if table_name not in self.table_dict:
                self.table_dict[table_name] = db.open(table.name, mode = 'ab')
                pass
            
            self.table_dict[table_name].append(*table_data)
            
            continue 
        return            

        
