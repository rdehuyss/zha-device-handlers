"""
 * TS0601 ZG-204ZM
 * _TZE200_kb5noeto
 * Works with HA 2024.11 - updated by @txip (Update 2) 
 * https://de.aliexpress.com/item/1005006174074799.html ("Color": Mmwave PIR)
 * https://github.com/13717033460/zigbee-herdsman-converters/blob/6c9cf1b0de836ec2172d569568d3c7fe75268958/src/devices/tuya.ts#L5730-L5762
 * https://www.zigbee2mqtt.io/devices/ZG-204ZM.html
 * https://smarthomescene.com/reviews/zigbee-battery-powered-presence-sensor-zg-204zm-review/
 * https://doc.szalarm.com/zg-205ZL/cntop_zigbee_sensor.js
 * https://github.com/Koenkk/zigbee2mqtt/issues/21919
"""

import logging
from typing import Final

from zigpy.quirks.v2 import QuirkBuilder

import zigpy.types as t
from zigpy.zcl.foundation import ZCLAttributeDef
from zigpy.zcl.clusters.measurement import (
    IlluminanceMeasurement,
    OccupancySensing,
)
from zigpy.zcl.clusters.security import IasZone
from zigpy.quirks.v2.homeassistant import EntityPlatform, EntityType

from zhaquirks.tuya import (
    TuyaLocalCluster,
    TuyaPowerConfigurationCluster2AAA,
)
from zhaquirks.tuya.mcu import TuyaMCUCluster, DPToAttributeMapping

class HumanMotionState(t.enum8):
    """Human Motion State values"""
    none = 0x00
    large_move = 0x01
    small_move = 0x02
    breathe = 0x03

class MotionDetectionMode(t.enum8):
    """Motion detection mode values"""
    Only_PIR = 0x00
    PIR_radar = 0x01
    Only_radar = 0x02

    @staticmethod
    def converter(value):
        """" If value  is None, Only_PIR should be returned """
                
        if value is None:
            return MotionDetectionMode.Only_PIR
        return value


class TuyaOccupancySensing(OccupancySensing, TuyaLocalCluster):
    """Tuya local OccupancySensing cluster."""


class TuyaIlluminanceMeasurement(IlluminanceMeasurement, TuyaLocalCluster):
    """Tuya local IlluminanceMeasurement cluster."""

class HumanPresenceSensorManufCluster(TuyaMCUCluster):
    """Human Presence Sensor ZG-204ZM (PIR+mmWave, battery)"""

    # Tuya Data points
    # "1":"Human Presence State", (presence_state, Enum, none|presence)
    # "2":"Stationary detection sensitivity", (sensitivity, Integer, 0-10, unit=x, step=1)
    # "3":"Minimum detection distance", (near_detection, Integer, 0-1000, unit=cm, step=1) (NOT AVAILABLE IN TUYA SMART LIFE APP)
    # "4":"Stationary detection distance", (far_detection, Integer, 0-1000, unit=cm, step=1)
    # "101":"Human Motion State", (human_motion_state, Enum, none|large_move|small_move|breathe)
    # "102":"Presence Keep Time", (presence_time, 10-28800, unit=s, step=1)
    # "106":"Illuminance Value", (illuminance_value, Integer, 0-6000, unit=lux )
    # "107":"Indicator", (indicator, Boolean)
    # "112":"Reset setting", (reset_setting, Boolean)
    # "121":"Battery", (battery, Integer, -1-100, step=1, unit=%)
    # "122":"Motion detection ", (motion_detection_mode, Enum, Only_PIR|PIR_radar|Only_radar) (NOT AVAILABLE IN TUYA SMART LIFE APP)
    # "123":"Motion detection sensitivity", (motion_detection_sen, Integer, 0-10, step=1, unit=x) (NOT AVAILABLE IN TUYA SMART LIFE APP)
    # "124":"ver" (ver, Integer, 0-100, step=1) (NOT AVAILABLE IN TUYA SMART LIFE APP)


    class AttributeDefs(TuyaMCUCluster.AttributeDefs):
        """Tuya DataPoints attributes"""

        # Human presence state (mapped to the OccupancySensing cluster)
        #presence_state: Final = ZCLAttributeDef(
        #    id=0xEF01, # DP 1
        #    type=Occupancy,
        #    access="rp",
        #    is_manufacturer_specific=True,
        #)

        # Stationary detection sensitivity
        sensitivity: Final = ZCLAttributeDef(
            id=0x0002, # DP 2
            type=t.uint16_t,
            is_manufacturer_specific=True,
        )
        # Minimum detection distance
        near_detection: Final = ZCLAttributeDef(
            id=0x0003, # DP 3
            type=t.uint16_t,
            is_manufacturer_specific=True,
        )
        # Stationary detection distance
        far_detection: Final = ZCLAttributeDef(
            id=0x0004, # DP 4
            type=t.uint16_t,
            is_manufacturer_specific=True,
        )
        # Human motion state
        human_motion_state: Final = ZCLAttributeDef(
            id=0x0101, # DP 101
            type=HumanMotionState,
            access="rp",
            is_manufacturer_specific=True,
        )
        # Presence keep time
        presence_time: Final = ZCLAttributeDef(
            id=0x0102, # DP 102
            type=t.uint16_t,
            is_manufacturer_specific=True,
        )
        # Illuminance value
        illuminance_value: Final = ZCLAttributeDef(
            id=0x0106, # DP 106
            type=t.uint16_t,
            access="rp",
            is_manufacturer_specific=True,
        )
        # Indicator
        indicator: Final = ZCLAttributeDef(
            id=0x0107, # DP 107
            type=t.Bool,
            is_manufacturer_specific=True,
        )
        # Reset setting
        reset_setting: Final = ZCLAttributeDef(
            id=0x0112, # DP 112
            type=t.Bool,
            is_manufacturer_specific=True,
        )
        # Battery (also provided by the TuyaPowerConfigurationCluster2AAA)
        battery: Final = ZCLAttributeDef(
            id=0x0121, # DP 121
            type=t.int16s,
            is_manufacturer_specific=True,
        )
        # Motion detection
        motion_detection_mode: Final = ZCLAttributeDef(
            id=0x0122, # DP 122
            type=MotionDetectionMode,
            is_manufacturer_specific=True,
        )
        # Motion detection sensitivity
        motion_detection_sen: Final = ZCLAttributeDef(
            id=0x0123, # DP 123
            type=t.uint16_t,
            is_manufacturer_specific=True,
        )
        # ver
        ver: Final = ZCLAttributeDef(
            id=0x0124, # DP 124
            type=t.uint16_t,
            is_manufacturer_specific=True,
        )

    dp_to_attribute: dict[int, DPToAttributeMapping] = {
        1: DPToAttributeMapping(
            TuyaOccupancySensing.ep_attribute,
            "occupancy",
        ),
        2: DPToAttributeMapping(
            TuyaMCUCluster.ep_attribute,
            "sensitivity",
            # Value in Tuya App after Factory reset is 6
            converter=lambda x: x if x is not None else 6
        ),
        3: DPToAttributeMapping(
            TuyaMCUCluster.ep_attribute,
            "near_detection",
            # Guessing a default of 0
            converter=lambda x: x if x is not None else 0
        ),
        4: DPToAttributeMapping(
            TuyaMCUCluster.ep_attribute,
            "far_detection",
            # Value in Tuya App after Factory reset is 600cm
            converter=lambda x: x if x is not None else 600
        ),
        101: DPToAttributeMapping(
            TuyaMCUCluster.ep_attribute,
            "human_motion_state",
            converter=HumanMotionState
        ),
        102: DPToAttributeMapping(
            TuyaMCUCluster.ep_attribute,
            "presence_time",
            # Value in Tuya App is 30 after Factory reset
            converter=lambda x: x if x is not None else 30
        ),
        106: DPToAttributeMapping(
            TuyaMCUCluster.ep_attribute,
            "illuminance_value",
        ),
        107: DPToAttributeMapping(
            TuyaMCUCluster.ep_attribute,
            "indicator",
        ),
        112: DPToAttributeMapping(
            TuyaMCUCluster.ep_attribute,
            "reset_setting",
        ),
        121: DPToAttributeMapping(
            TuyaMCUCluster.ep_attribute,
            "battery",
        ),
        122: DPToAttributeMapping(
            TuyaMCUCluster.ep_attribute,
            "motion_detection_mode",
            converter=MotionDetectionMode,
        ),
        123: DPToAttributeMapping(
            TuyaMCUCluster.ep_attribute,
            "motion_detection_sen",
            # Guessing a default of 10
            converter=lambda x: x if x is not None else 10
        ),
        124: DPToAttributeMapping(
            TuyaMCUCluster.ep_attribute,
            "ver",
        ),
    }

    data_point_handlers = {
        1: "_dp_2_attr_update",
        2: "_dp_2_attr_update",
        3: "_dp_2_attr_update",
        4: "_dp_2_attr_update",
        101: "_dp_2_attr_update",
        102: "_dp_2_attr_update",
        106: "_dp_2_attr_update",
        107: "_dp_2_attr_update",
        112: "_dp_2_attr_update",
        121: "_dp_2_attr_update",
        122: "_dp_2_attr_update",
        123: "_dp_2_attr_update",
        124: "_dp_2_attr_update",
    }

(
    QuirkBuilder("_TZE200_kb5noeto", "TS0601")
    .skip_configuration()
    .removes(IasZone.cluster_id)
    .adds(HumanPresenceSensorManufCluster)
    .adds(TuyaOccupancySensing)
    .replaces(TuyaPowerConfigurationCluster2AAA)
    .replaces(TuyaIlluminanceMeasurement)
    .number(
        HumanPresenceSensorManufCluster.AttributeDefs.sensitivity.name,
        HumanPresenceSensorManufCluster.cluster_id,
        step=1,
        min_value=1,
        max_value=10,
        fallback_name="Sensitivity",
        translation_key="sensitivity"
    )
    .number(
        HumanPresenceSensorManufCluster.AttributeDefs.near_detection.name,
        HumanPresenceSensorManufCluster.cluster_id,
        step=1,
        min_value=0,
        max_value=1000,
        fallback_name="Near Detection",
        translation_key="near_detection"
    )
    .number(
        HumanPresenceSensorManufCluster.AttributeDefs.far_detection.name,
        HumanPresenceSensorManufCluster.cluster_id,
        step=1,
        min_value=0,
        max_value=1000,
        fallback_name="Far Detection",
        translation_key="far_detection"
    )
    .enum(
        HumanPresenceSensorManufCluster.AttributeDefs.human_motion_state.name,
        HumanMotionState,
        HumanPresenceSensorManufCluster.cluster_id,
        entity_platform=EntityPlatform.SENSOR,
        entity_type=EntityType.STANDARD,
        fallback_name="Human Motion State",
        translation_key="human_motion_state"
    )
    .number(
        HumanPresenceSensorManufCluster.AttributeDefs.presence_time.name,
        HumanPresenceSensorManufCluster.cluster_id,
        step=1,
        min_value=10,
        max_value=28800,
        fallback_name="Presence Time",
        translation_key="presence_time"
    )
    .switch(
        HumanPresenceSensorManufCluster.AttributeDefs.indicator.name,
        HumanPresenceSensorManufCluster.cluster_id,
        fallback_name="Indicator",
        translation_key="indicator"
    )
#    .binary_sensor(
#        HumanPresenceSensorManufCluster.AttributeDefs.reset_setting.name,
#        HumanPresenceSensorManufCluster.cluster_id
#    )
    .enum(
        HumanPresenceSensorManufCluster.AttributeDefs.motion_detection_mode.name,
        MotionDetectionMode,
        HumanPresenceSensorManufCluster.cluster_id,
        fallback_name="Motion Detection Mode",
        translation_key="motion_detection_mode"
    )
    .number(
        HumanPresenceSensorManufCluster.AttributeDefs.motion_detection_sen.name,
        HumanPresenceSensorManufCluster.cluster_id,
        step=1,
        min_value=0,
        max_value=10,
        fallback_name="Motion Detection Sensitivity",
        translation_key="motion_detection_sen"
    )
#    .number(
#        HumanPresenceSensorManufCluster.AttributeDefs.ver.name,
#        HumanPresenceSensorManufCluster.cluster_id,
#        step=1,
#        min_value=0,
#        max_value=10
#    )
    .add_to_registry()
)
