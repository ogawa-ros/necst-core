#!/usr/bin/env python3

import time
import datetime
import threading
from pathlib import Path
from typing import Any, Dict, Tuple

import necstdb
import rospy


class db_logger_always:
    def __init__(self) -> None:
        self.db_dir = Path.home() / "data" / "always"
        self.db_path_date = ""
        self.data_list = []

        self.th = threading.Thread(target=self.loop)
        self.th.start()

    def regist(self, data) -> None:
        self.data_list.append(data)
        return

    def close_tables(self) -> None:
        tables = self.table_dict
        self.receive_time_dict = {}
        self.table_dict = {}
        [tables[name].close() for name in tables]

    def check_date(self) -> None:
        now = datetime.now()
        if self.db_path_date != "{0:%Y%m}/{0:%Y%m%d}.necstdb".format(now):
            self.db_path_date = "{0:%Y%m}/{0:%Y%m%d}.necstdb".format(now)
            self.close_tables()
            self.db = necstdb.opendb(self.db_dir / self.db_path_date, mode="w")
            pass
        return

    def loop(self) -> None:
        while True:
            if len(self.data_list) == 0:
                self.close_tables()
                if rospy.is_shutdown():
                    break
                time.sleep(0.01)
                continue

            d = self.data_list.pop(0)
            # data_list: Dict[str, Any]
            #  - "topic": str
            #  - "received_time": float
            #  - "slots": Dict[str, Any]
            #   - "key": str
            #   - "type": str
            #   - "value": Union[Any, List[Any]]
            self.check_date()

            if d["topic"] not in self.receive_time_dict:
                self.receive_time_dict[d["topic"]] = d["received_time"]
            elif self.receive_time_dict[d["topic"]] - d["received_time"] < 10:
                continue  # Skip time inconsistent data.
            else:
                self.receive_time_dict[d["topic"]] = d["received_time"]
                pass

            table_name = d["topic"].replace("/", "-").strip("-")
            table_data = [d["received_time"]]
            table_info = [{"key": "received_time", "format": "d", "size": 8}]

            for slot in d["slots"]:
                data, info = self.create_info(slot)

                table_info.append(info)
                table_data.extend(data)

            if table_name not in self.table_dict:
                self.db.create_table(
                    table_name,
                    {
                        "data": table_info,
                        "memo": "generated by db_logger_always",
                        "version": necstdb.__version__,
                    },
                )
                self.table_dict[table_name] = self.db.open_table(table_name, mode="ab")
                pass

            self.table_dict[table_name].append(*table_data)
        return

    @staticmethod
    def create_info(slot: Dict[str, Any]) -> Tuple[Any, Dict[str, Any]]:
        conversion_table = {
            "bool": lambda d: (d, "?", 1),
            "byte": lambda d: (d, f"{len(d)}s", 1 * len(d)),
            "char": lambda d: (d, "c", 1),
            "float32": lambda d: (d, "f", 4),
            "float64": lambda d: (d, "d", 8),
            "int8": lambda d: (d, "b", 1),
            "int16": lambda d: (d, "h", 2),
            "int32": lambda d: (d, "i", 4),
            "int64": lambda d: (d, "q", 8),
            "uint8": lambda d: (d, "B", 1),
            "uint16": lambda d: (d, "H", 2),
            "uint32": lambda d: (d, "I", 4),
            "uint64": lambda d: (d, "Q", 8),
            "string": lambda d: (bytes(d), f"{len(d)}s", 1 * len(d)),
        }
        for k in conversion_table.keys():
            if slot["type"].find(k) != -1:
                data, format_, size = conversion_table[k](slot["value"])

        if isinstance(data, tuple):
            if isinstance(data, (str, bytes)):
                format_ = format_ * len(data)  # Because 5s5s5s is ok, but 35s is not.
            else:
                format_ = f"{len(data)}{format_}"
            size *= len(data)
            data = list(data)
        else:
            data = [data]
        return data, {"key": slot["key"], "format": format_, "size": size}
