from flask import request, abort, current_app, make_response

from info import redis_store, constants
from info.utils.captcha import captcha
from . import passport_blue


@passport_blue.route('/image_code',methods=['GET'])
def image_code():
    '''提供图片验证码'''
    '''
    1.接受参数（uuid）
    2.校验参数（判断uuid是否为空）
    3.生成图片验证码
    4.保存图片验证码到redis
    5.修改image的ContentType = ‘image/jpg’
    6.响应图片验证码
    '''
    # 1.接受参数（uuid）
    imageCodeId = request.args.get('imageCodeId')

    # 2.校验阐述（判断uuid是否为空）
    if not imageCodeId:
        abort(403)

    # 3.生成图片验证码
    name, text, image = captcha.captcha.generate_captcha()

    # 4.保存图片验证码到redis
    try:
        redis_store.set('ImageCode:' + imageCodeId, text, constants.IMAGE_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
        abort(500)

    # 5.修改image的ContentType = ‘image/jpg’
    response = make_response(image)
    response.headers['Content-Type'] = 'image/jpg'

    # 5.响应图片验证码
    return response
