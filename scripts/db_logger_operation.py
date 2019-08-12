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
        t1 = time.time()
        self.sub_path = rospy.Subscriber(
            name = '/logger_path',
            data_class = std_msgs.msg.String,
            callback = self.callback_path,
            queue_size = 1,
        )

        self.th = threading.Thread(target= self.loop)
        self.th.start()
        pass

    def callback_path(self, req):
        self.db_path = req.data
        if self.db_path != '':
            t1 = time.time()
            self.db = necstdb.opendb(self.db_path)
            self.close_tables()
        else:
            while len(self.data_list)!=0:
                time.sleep(0.1)
                continue
            t2 = time.time()
            self.close_tables()
            pass
        print(t2-t1)
        return

    def close_tables(self):
        tables = self.table_dict
        self.table_dict = {}
        [tables[name].close() for name in tables]
        return

    def regist(self, data):
        if self.db_path != '':
            self.data_list.append(data)
            pass
        return

    def loop(self):

        while True:
            time.sleep(0.01)
            if len(self.data_list) ==0:
                if rospy.is_shutdown():
                    break
                continue

            d = self.data_list.pop(0)

            table_name = d['topic'].replace('/', '-')
            table_data = [d['received_time']]
            table_info = [{'key': 'timestamp',
                           'format': 'd',
                           'size': 8}]

            for slot in d['slots']:
                if slot['type'].startswith('bool'):
                    info = {'format': 'c', 'size': 1}

                elif slot['type'].startswith('byte'):
                    info = {'format': 's', 'size': len(slot['value'])}

                elif slot['type'].startswith('char'):
                    info = {'format': 'c', 'size': 1}

                elif slot['type'].startswith('float32'):
                    info = {'format': 'f', 'size': 4}

                elif slot['type'].startswith('float64'):
                    info = {'format': 'd', 'size': 8}

                elif slot['type'].startswith('int8'):
                    info = {'format': 'b', 'size': 1}

                elif slot['type'].startswith('int16'):
                    info = {'format': 'h', 'size': 2}

                elif slot['type'].startswith('int32'):
                    info = {'format': 'i', 'size': 4}

                elif slot['type'].startswith('int64'):
                    info = {'format': 'q', 'size': 8}

                elif slot['type'].startswith('string'):
                    info = {'format': 's', 'size': len(slot['value'])}
                    slot['value'] = slot['value'].encode()

                elif slot['type'].startswith('uint8'):
                    info = {'format': 'B', 'size': 1}

                elif slot['type'].startswith('unit16'):
                    info = {'format': 'H', 'size': 2}

                elif slot['type'].startswith('unit32'):
                    info = {'format': 'I', 'size': 4}

                elif slot['type'].startswith('unit64'):
                    info = {'format': 'Q', 'size': 8}
                else:
                    continue

                if isinstance(slot['value'], tuple):
                    # for MultiArray
                    dlen = len(slot['value'])
                    info['format'] = '{0:d}{1:s}'.format(dlen, info['format'])
                    info['size'] *= dlen
                    table_data += slot['value']
                else:
                    table_data += [slot['value']]
                    pass

                info['key'] = slot['key']
                table_info.append(info)
                continue

            self.db.create_table(table_name,
                            {'data': table_info,
                             'memo': 'generated by db_logger_operation',
                             'version': necstdb.__version__,})

            if table_name not in self.table_dict:
                self.table_dict[table_name] = self.db.open_table(table_name, mode='ab')
                pass

            self.table_dict[table_name].append(*table_data)
            continue
        return
