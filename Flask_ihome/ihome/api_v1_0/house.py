# coding:utf-8

from flask import current_app, jsonify, g, request
from . import api
from ihome import redis_store, db
from ihome.models import Area, Facility, House
from ihome.utils.response_code import RET
from ihome import constants
from ihome.utils.commons import login_require
import json


# GET /api/v1.0/area_info
@api.route('/area_info', methods=["GET"])
def get_area_info():
    """获取城区信息"""
    # 先尝试从缓存中查询数据
    try:
        resp_json_str = redis_store.get("areas_info")
    except Exception as e:
        current_app.logger.error(e)
    else:
        if resp_json_str is not None:
            current_app.logger.info("hit redis area info")
            return resp_json_str, 200, {"Content-Type": "application/json"}

    # 如果未能从缓存中获得数据
    # 从数据库查询地区信息
    try:
        areas = Area.query.all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errcode=RET.DBERR, errmsg="数据库异常")
    areas_dict_list = []
    for area in areas:
        areas_dict_list.append(area.to_dict())

    # 组织保存的数据
    resp_dict = dict(errcode=RET.OK, errmsg="查询成功", data={"areas": areas_dict_list})
    # 将数据转换成json格式，方便在查取到数据后，可以直接返回
    resp_json_str = json.dumps(resp_dict)
    # 保存到缓存
    try:
        redis_store.setex("areas_info", constants.AREA_INFO_REDIS_CACHE_EXPIRE, resp_json_str)
    except Exception as e:
        current_app.logger.error(e)
    return resp_json_str, 200, {"Content-Type": "application/json"}


# POST  /api/v1.0/houses/info
@api.route('/houses/info', methods=["POST"])
@login_require
def save_house_info():
    """保存房屋信息"""
    """
    前段发送过来的json数据
     {
        "title":"",
        "price":"",
        "area_id":"1",
        "address":"",
        "room_count":"",
        "acreage":"",
        "unit":"",
        "capacity":"",
        "beds":"",
        "deposit":"",
        "min_days":"",
        "max_days":"",
        "facility":["7","8"]
    }
    """
    user_id = g.user_id
    house_data = request.get_json()
    if house_data is None:
        return jsonify(errcode=RET.PARAMERR, errmsg="参数缺失")
    title = house_data.get('title')
    price = house_data.get('price')
    area_id = house_data.get('area_id')
    address = house_data.get('address')
    room_count = house_data.get('room_count')
    acreage = house_data.get('acreage')
    unit = house_data.get('unit')
    capacity = house_data.get('capacity')
    beds = house_data.get("beds")
    deposit = house_data.get('deposit')
    min_days = house_data.get('min_days')
    max_days = house_data.get('max_days')
    # 校验参数
    if not all([title, price, area_id, address, room_count, acreage, unit, capacity, deposit, min_days, max_days]):
        return jsonify(errcode=RET.DATAEXIST, errmsg="参数不完整")
    # 验证城区是否存在
    try:
        area = Area.query.get(area_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(RET.DBERR, errmsg="数据库异常")
    if area is None:
        return jsonify(RET.PARAMERR, errmsg="城区信息有误")
    # 处理金钱:
    # １.因为在数据库中，金钱的单位是分
    # 2.有可能用户输入的不是数字
    try:
        price = int(float(price)*100)
        deposit = input(float(deposit)*100)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(RET.PARAMERR, errmsg="金钱信息有误")

    # 将数据保存在数据库中
    house = House(
        user_id=user_id,
        area_id=area_id,
        title=title,
        price=price,
        address=address,
        room_count=room_count,
        acreage=acreage,
        unit=unit,
        capacity=capacity,
        deds=beds,
        deposit=deposit,
        min_days=min_days,
        max_days=max_days
    )

    # 配套设施信息
    facility_id_list = house_data.get("facility")
    if facility_id_list:
        # 表明用户勾选了配套设施
        try:
            facility_obj_list = Facility.query.filter(Facility.id.in_(facility_id_list).all())
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errcode=RET.DBERR, errmsg="数据库异常")
        if facility_obj_list:
            house.capacity = facility_obj_list

    try:
        db.session.add()
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errcode=RET.DBERR, errmsg="房屋信息保存失败")

    return jsonify(errcode=RET.OK, errmsg="保存成功", data={"house_id": house.id})
