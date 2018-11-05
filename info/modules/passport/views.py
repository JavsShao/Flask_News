# 注册和登录
from . import passport_blue
from flask import request,abort,current_app,make_response,jsonify, session
from info.utils.captcha.captcha import captcha
from info import redis_store, constants, response_code, db
import json, re, random, datetime
from info.libs.yuntongxun.sms import CCP
from info.models import User


@passport_blue.route('/register',methods=['POST'])
def register():
    """
        1. 获取参数和判断是否有值
        2. 从redis中获取指定手机号对应的短信验证码的
        3. 校验验证码
        4. 初始化 user 模型，并设置数据并添加到数据库
        5. 保存当前用户的状态
        6. 返回注册的结果
        :return:
        """

    # 1. 获取参数和判断是否有值
    json_data = request.json
    mobile = json_data.get("mobile")
    sms_code = json_data.get("smscode")
    password = json_data.get("password")

    if not all([mobile, sms_code, password]):
        # 参数不全
        return jsonify(errno=RET.PARAMERR, errmsg="参数不全")

    # 2. 从redis中获取指定手机号对应的短信验证码的
    try:
        real_sms_code = redis_store.get("SMS_" + mobile)
    except Exception as e:
        current_app.logger.error(e)
        # 获取本地验证码失败
        return jsonify(errno=RET.DBERR, errmsg="获取本地验证码失败")

    if not real_sms_code:
        # 短信验证码过期
        return jsonify(errno=RET.NODATA, errmsg="短信验证码过期")

    # 3. 校验验证码
    if sms_code != real_sms_code:
        return jsonify(errno=RET.DATAERR, errmsg="短信验证码错误")
    # 删除短信验证码
    try:
        redis_store.delete("SMS_" + mobile)
    except Exception as e:
        current_app.logger.error(e)

    # 4. 初始化 user 模型，并设置数据并添加到数据库
    user = User()
    user.nick_name = mobile
    user.mobile = mobile
    # 对密码进行处理
    user.password = password

    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        # 数据保存错误
        return jsonify(errno=RET.DATAERR, errmsg="数据保存错误")
    # 5. 保存用户登录状态
    session["user_id"] = user.id
    session["nick_name"] = user.nick_name
    session["mobile"] = user.mobile

    # 6. 返回注册结果
    return jsonify(errno=RET.OK, errmsg="OK")

@passport_blue.route('/sms_code', methods=['POST'])
def sms_code():
    """发送短信
    1.接受参数（手机号，图片验证码，uuid）
    2.校验参数是否齐全，手机号是否合法
    3.查询服务器存储的图片验证码
    4.跟客户端传入的图片验证码对比
    5.如果对比成功，生成短信验证码，并发送短信
    6.存储短信验证码到redis,方便注册时比较
    7.响应短信验证码发送的结果
    """
    # 1.接受参数（手机号，图片验证码，uuid）
    # '{'mobile':'17600992168','image_code':'asdc','image_code_id':'uuid'}'
    json_str = request.data
    json_dict = json.loads(json_str)
    mobile = json_dict.get('mobile')
    image_code_client = json_dict.get('image_code')
    image_code_id = json_dict.get('image_code_id')

    # 2.校验参数是否齐全，手机号是否合法
    if not all([mobile, image_code_client, image_code_id]):
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='缺少参数')
    if not re.match(r'^1[345678][0-9]{9}$', mobile):
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='手机号格式错误')

    # 3.查询服务器存储的图片验证码
    try:
        image_code_server = redis_store.get('ImageCode:'+image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=response_code.RET.DBERR, errmsg='查询图片验证码失败')
    if not image_code_server:
        return jsonify(errno=response_code.RET.NODATA, errmsg='图片验证码不存在')

    # 4.跟客户端传入的图片验证码对比
    if image_code_server.lower() != image_code_client.lower():
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='输入验证码有误')

    # 5.如果对比成功，生成短信验证码，并发送短信
    # '%06d' : 如果不够6位，补0.比如:28-->000028
    sms_code = '%06d' % random.randint(0, 999999)
    current_app.logger.debug(sms_code)
    # result = CCP().send_template_sms(mobile, [sms_code, 5], 1)
    # if result != 0:
    #     return jsonify(errno=response_code.RET.THIRDERR, errmsg='发送短信验证码失败')

    # 6.存储短信验证码到redis,方便注册时比较
    try:
        redis_store.set('SMS:'+mobile, sms_code, constants.SMS_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=response_code.RET.DBERR, errmsg='保存短信验证码失败')

    # 7.响应短信验证码发送的结果
    return jsonify(errno=response_code.RET.OK, errmsg='发送短信验证码成功')


@passport_blue.route('/image_code', methods=['GET'])
def image_code():
    """提供图片验证码
    1.接受参数（uuid）
    2.校验参数（判断uuid是否为空）
    3.生成图片验证码
    4.保存图片验证码到redis
    5.修改image的ContentType = 'image/jpg'
    6.响应图片验证码
    """
    # 1.接受参数（uuid）
    imageCodeId = request.args.get('imageCodeId')

    # 2.校验参数（判断uuid是否为空）
    if not imageCodeId:
        abort(403)

    # 3.生成图片验证码
    name,text,image = captcha.generate_captcha()
    current_app.logger.debug(text)

    # 4.保存图片验证码到redis
    try:
        redis_store.set('ImageCode:'+imageCodeId, text, constants.IMAGE_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
        abort(500)

    # 5.修改image的ContentType = 'image/jpg'
    response = make_response(image)
    response.headers['Content-Type'] = 'image/jpg'

    # 6.响应图片验证码
    return response