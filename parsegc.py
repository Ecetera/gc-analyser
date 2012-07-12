#!/usr/bin/python

# TODO: Add support for additional GC configs
#       Add parsing support for Full GC events
#       Add support for remaining CMS events if applicable

import re

timestamp = re.compile(r"""
    (\d+\.\d+): (.*)
    """, re.VERBOSE)
gcentry = re.compile(r"""
    \s*\[GC\ (\d+\.\d+)?:\ \[[A-Za-z]+:
    \ (\d+)K->(\d+)K\((\d+)K\),\ (\d+\.\d+)\ secs\]
    \s*(\d+)K->(\d+)K\((\d+)K\),\ (\d+\.\d+)\ secs\]
    \s*\[Times:\ user=(\d+\.\d+)\ sys=(\d+\.\d+),?\ real=(\d+\.\d+)\ secs\].*
    """, re.VERBOSE)


class ParseGCLog(object):        

    def parse_file(self, file):
        gclog = open(file, "r")
        return self.parse_data(gclog)
            
    def parse_data(self, data):
        gcdata = []
        gclog = data.readlines()
        for line in gclog:
            result = self.parse(line)
            if result:
                gcdata.append(result)
        return gcdata

    def parse(self, line):
        ts = timestamp.match(line)
        if ts:
            #print "timestamp: " + ts.group(1)
            #print "remaining: " + ts.group(ts.lastindex)
            entry = ts.group(ts.lastindex)
            gc = gcentry.match(entry)
            if gc:
                #print "gc timestamp: " + gc.group(1)
                #print "younggen util pre: " + gc.group(2)
                #print "younggen util post: " + gc.group(3)
                #print "younggen size post: " + gc.group(4)
                #print "younggen duration:" + gc.group(5)
                #print "heap util pre: " + gc.group(6)
                #print "heap util post: " + gc.group(7)
                #print "heap size post: " + gc.group(8)
                #print "gc duration: " + gc.group(9)
                #print "user: " + gc.group(10)
                #print "sys: " + gc.group(11)
                #print "real: " + gc.group(12)
                #print gc.groups()

                result = ParNewGCEntry(ts.group(1), *gc.groups())

                return result
            else:
                #print "Ignoring unsupported GC entry: " + entry
                return None
        else:
            #print "Ignoring line: " + line
            return None


class GCEntry(object):

    def __init__(self,
                timestamp):
        self.timestamp = timestamp

    def __eq__(self, 
                other):
        if type(other) is type(self):
            return self.__dict__ == other.__dict__
        return False

    def get_attr(self):
        return self.__dict__

    def get_attr_keys(self):
        return self.__dict__.keys()

    def get_attr_values(self):
        return self.__dict__.values()

    def get_attr_value(self, key):
        return self.__dict__[key]

    def get_attr_values(self, dict):
        for key in dict:
            if key in self.__dict__:
                dict[key] = self.__dict__[key]
        return dict

    # TODO: Check JVM source to confirm 1024 not 1000 should be used
    def to_bytes(self, value):
        return str(int(value) << 10)

class ParNewGCEntry(GCEntry):

    def __init__(self, 
                timestamp,
                gc_timestamp, 
                yg_util_pre,
                yg_util_post,
                yg_size_post,
                yg_pause_time,
                heap_util_pre, 
                heap_util_post, 
                heap_size_post, 
                pause_time,
                user_time,
                sys_time,
                real_time):
        super(ParNewGCEntry, self).__init__(timestamp)
        self.gc_timestamp = gc_timestamp
        self.yg_util_pre = self.to_bytes(yg_util_pre)
        self.yg_util_post = self.to_bytes(yg_util_post)
        self.yg_size_post = self.to_bytes(yg_size_post)
        self.yg_pause_time = yg_pause_time
        self.heap_util_pre = self.to_bytes(heap_util_pre)
        self.heap_util_post = self.to_bytes(heap_util_post)
        self.heap_size_post = self.to_bytes(heap_size_post)
        self.pause_time = pause_time
        self.user_time = user_time
        self.sys_time = sys_time
        self.real_time = real_time
        self.yg_reclaimed = str(int(self.yg_util_pre) - int(self.yg_util_post))
        self.heap_reclaimed = str(int(self.heap_util_pre) - int(self.heap_util_post))

