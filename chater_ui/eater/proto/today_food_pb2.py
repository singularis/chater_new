# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: today_food.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x10today_food.proto"P\n\x08\x43ontains\x12\x15\n\rcarbohydrates\x18\x01 \x01(\x01\x12\x0c\n\x04\x66\x61ts\x18\x02 \x01(\x01\x12\x10\n\x08proteins\x18\x03 \x01(\x01\x12\r\n\x05sugar\x18\x04 \x01(\x01"v\n\x04\x44ish\x12\x0c\n\x04time\x18\x01 \x01(\x03\x12\x11\n\tdish_name\x18\x02 \x01(\t\x12\x1e\n\x16\x65stimated_avg_calories\x18\x03 \x01(\x05\x12\x13\n\x0bingredients\x18\x04 \x03(\t\x12\x18\n\x10total_avg_weight\x18\x05 \x01(\x05"\\\n\x0bTotalForDay\x12\x1b\n\x08\x63ontains\x18\x01 \x01(\x0b\x32\t.Contains\x12\x18\n\x10total_avg_weight\x18\x02 \x01(\x05\x12\x16\n\x0etotal_calories\x18\x03 \x01(\x05"d\n\tTodayFood\x12\x1b\n\x0c\x64ishes_today\x18\x01 \x03(\x0b\x32\x05.Dish\x12#\n\rtotal_for_day\x18\x02 \x01(\x0b\x32\x0c.TotalForDay\x12\x15\n\rperson_weight\x18\x03 \x01(\x02\x62\x06proto3'
)

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, "today_food_pb2", globals())
if _descriptor._USE_C_DESCRIPTORS == False:

    DESCRIPTOR._options = None
    _CONTAINS._serialized_start = 20
    _CONTAINS._serialized_end = 100
    _DISH._serialized_start = 102
    _DISH._serialized_end = 220
    _TOTALFORDAY._serialized_start = 222
    _TOTALFORDAY._serialized_end = 314
    _TODAYFOOD._serialized_start = 316
    _TODAYFOOD._serialized_end = 416
# @@protoc_insertion_point(module_scope)
