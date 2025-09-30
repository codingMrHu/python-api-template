from datetime import datetime
from typing import Optional

from app.api.errcode.user import UserValidateError
from app.api.resp import UnifiedResponseModel, resp_200, resp_500
from app.api.services.audit_log import AuditLogService
from app.api.services.captcha import verify_captcha
from app.api.services.user_service import gen_user_jwt, get_login_user
from app.api.utils import get_request_ip, random_str
from app.db import dao
from app.db.models.user import AdminRole, DefaultRole, User, UserCreate, UserLogin, UserLoginRead, UserRead, UserUpdate
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi_jwt_auth import AuthJWT

# build router
router = APIRouter(prefix="/user", tags=["User"])


@router.post("/regist", response_model=UnifiedResponseModel[UserRead])
async def regist(*, request: Request, user: UserCreate):
    # 验证码校验
    if False:
        if not user.captcha_key or not await verify_captcha(user.captcha, user.captcha_key):
            raise HTTPException(status_code=500, detail="验证码错误")

    db_user = User.model_validate(user)

    # check if user already exist
    user_exists = dao.select_one(User, *[User.user_name == db_user.user_name])
    if user_exists:
        raise HTTPException(status_code=500, detail="用户名已存在")

    user_exists = dao.select_one(User, *[User.phone_number == db_user.phone_number])
    if user_exists:
        raise HTTPException(status_code=500, detail="手机号码已存在")

    salt = random_str(10, digits=True)
    db_user.salt = salt
    db_user.password = User.encrypt_password(db_user.password, salt)

    # 判断下admin用户是否存在
    admin = dao.select_one(User, *[User.id == 1])
    if admin:
        db_user.role = DefaultRole
    else:
        db_user.id = 1
        db_user.role = AdminRole
    dao.insert(db_user)

    AuditLogService.insert_user(db_user, get_request_ip(request))

    return resp_200(db_user)


@router.post("/login", response_model=UnifiedResponseModel[UserLoginRead])
async def login(*, request: Request, user: UserLogin, Authorize: AuthJWT = Depends()):
    # 验证码校验
    # if settings.get_from_db('use_captcha'):
    #     if not user.captcha_key or not await verify_captcha(user.captcha, user.captcha_key):
    #         raise HTTPException(status_code=500, detail='验证码错误')

    db_user = dao.select_one(User, *[User.phone_number == user.phone_number])
    # 检查密码
    if not db_user or (db_user.password != User.encrypt_password(user.password, db_user.salt)):
        return UserValidateError.return_resp()

    if 1 == db_user.delete:
        raise HTTPException(status_code=500, detail="该账号已被禁用，请联系管理员")

    access_token, refresh_token = gen_user_jwt(db_user)

    # Set the JWT cookies in the response
    Authorize.set_access_cookies(access_token)
    Authorize.set_refresh_cookies(refresh_token)

    # 设置登录用户当前的cookie, 比jwt有效期多一个小时
    # redis_client.set(USER_CURRENT_SESSION.format(db_user.user_id), access_token, ACCESS_TOKEN_EXPIRE_TIME + 3600)
    db_user.current_token = access_token

    # 更新token
    db_user.last_login_time = datetime.now()
    dao.update(User, db_user)

    # 记录审计日志
    AuditLogService.user_login(db_user, get_request_ip(request))

    return resp_200(db_user)


@router.get("/info", response_model=UnifiedResponseModel[UserRead])
async def get_info(login_user: User = Depends(get_login_user)):
    # check if user already exist
    return resp_200(login_user)


@router.post("/logout", status_code=201)
async def logout(Authorize: AuthJWT = Depends(), login_user: User = Depends(get_login_user)):
    Authorize.jwt_required()
    Authorize.unset_jwt_cookies()
    login_user.current_token = ""
    dao.update(User, login_user)
    return resp_200()


@router.get("/list", response_model=UnifiedResponseModel[UserRead])
async def list_user(
    *,
    name: Optional[str] = None,
    page_num: Optional[int] = 1,
    page_size: Optional[int] = 10,
    login_user: User = Depends(get_login_user),
):
    if login_user.is_admin:
        filters = []
        if name:
            filters.append(User.user_name.like(f"%{name}%"))
        data, page = dao.select_page(User, page_num, page_size, *filters, order_by=[User.id.desc()])

        return resp_200(data=data, page=page)
    else:
        return resp_500(message="用户没有权限")


@router.put("/update", response_model=UnifiedResponseModel[UserRead])
async def update(*, request: Request, user: UserUpdate, login_user: User = Depends(get_login_user)):
    if not login_user.is_admin and user.id != login_user.id:
        raise HTTPException(status_code=500, detail="无修改权限")

    update_user = dao.select_one(User, User.id == user.id)
    if not update_user:
        raise HTTPException(status_code=500, detail="用户不存在")

    if user.id != login_user.id:
        AuditLogService.update_user(update_user, get_request_ip(request), "管理员修改账户信息")
    else:
        AuditLogService.update_user(update_user, get_request_ip(request), "修改账户")

    salt = random_str(10, digits=True)
    if not login_user.is_admin:
        if update_user.user_name != user.user_name:
            update_user.user_name = user.user_name
        if user.password:
            update_user.salt = salt
            update_user.password = User.encrypt_password(user.password, salt)
        dao.update(User, update_user)
    else:
        if user.user_name:
            update_user.user_name = user.user_name
        if user.password:
            update_user.salt = salt
            update_user.password = User.encrypt_password(user.password, salt)
        if user.delete is not None:
            update_user.delete = user.delete
        dao.update(User, update_user)

    return resp_200(update_user)


# @router.get('/get_captcha', status_code=200)
# async def get_captcha():
#     # generate captcha
#     chr_all = string.ascii_letters + string.digits
#     chr_4 = ''.join(random.sample(chr_all, 4))
#     image = ImageCaptcha().generate_image(chr_4)
#     # 对image 进行base 64 编码
#     buffered = BytesIO()
#     image.save(buffered, format='PNG')

#     capthca_b64 = b64encode(buffered.getvalue()).decode()
#     logger.info('get_captcha captcha_char={}', chr_4)
#     # generate key, 生成简单的唯一id，
#     key = 'capthca_' + uuid.uuid4().hex[:8]
#     redis_client.set(key, chr_4, expiration=300)

#     # 增加配置，是否必须使用验证码
#     return resp_200({
#         'captcha_key': key,
#         'captcha': capthca_b64,
#         'user_capthca': True
#     })


# @router.get('/public_key', status_code=200)
# async def get_rsa_publish_key():
#     # redis 存储
#     key = 'rsa_'
#     # redis lock
#     if redis_client.setNx(key, 1):
#         # Generate a key pair
#         (pubkey, privkey) = rsa.newkeys(512)

#         # Save the keys to strings
#         redis_client.set(key, (pubkey, privkey), 3600)
#     else:
#         pubkey, privkey = redis_client.get(key)

#     pubkey_str = pubkey.save_pkcs1().decode()

#     return resp_200({'public_key': pubkey_str})


# @router.post('/create', status_code=200)
# async def create_user(*,
#                       request: Request,
#                       admin_user: UserPayload = Depends(get_admin_user),
#                       req: UserCreate):
#     """
#     超级管理员创建用户
#     """
#     logger.info(f'create_user username={admin_user.user_name}, username={req.user_name}')
#     data = []
#     return resp_200(data=data)
