from fastapi import FastAPI, Query
from pymysql.err import IntegrityError
from pydantic import BaseModel,Field
from my_sql import MySQLHandler
from fastapi.middleware.cors import CORSMiddleware
from config.mysql_config import mysql_config
from typing import Optional
import cfun

# 初始化 FastAPI 应用
app = FastAPI()

# 配置 CORS 中间件
origins = [
    "*",
    "http://127.0.0.1:8000",  # 这里可以根据实际情况添加允许的域名
    # 可以添加更多允许的域名，例如 "http://example.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有 HTTP 方法
    allow_headers=["*"],  # 允许所有请求头
)



def initdb():
    # 初始化数据库连接
    db_handler = MySQLHandler(**mysql_config)
    db_handler.connect()
    return db_handler

def filter_empty_keys(input_dict):
    return {key: value for key, value in input_dict.items() if value or value is not None}

# 定义数据模型
class DouyinHaoUrl(BaseModel):
    url: str
    touser: str = ''
    keyword: str = ''
    level: str = ''
    hangye: str = ''
    hangye_type: str = ''
    islisten: int = 0
    is_history: int = 0
    is_listen_user: int = 0
    is_run:int = 0

class DouyinKeyWord(BaseModel):
    keywords: str
    type: int = 1
    status: int = 0

# 创建记录
@app.post("/douyin_hao_url/")
def create_douyin_hao_url(item: DouyinHaoUrl):
    db_handler = initdb()
    data = item.dict()
    data['hangye_type'] = cfun.get_hangye_type(data['hangye'])
    data['status'] = 1
    try:
        rows_affected = db_handler.insert('craw_douyin_hao_url', data)
        if rows_affected > 0:
            return {"message": "添加成功"}
        return {"message": "信息已存在或添加失败"}
    except IntegrityError as e:
        return {"message": f"Integrity error: {e}"}

# 获取所有记录，支持查询和分页
@app.get("/douyin_hao_url/")
def get_all_douyin_hao_urls(
    url: str | None = Query(None, description="Filter by url"),
    status: int | None = Query(None, description="Filter by status"),
    touser: str | None = Query(None, description="Filter by touser"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, description="Number of items per page")
):
    db_handler = initdb()
    conditions = []
    params = []

    if url:
        # 使用 LIKE 进行模糊查询
        conditions.append("url LIKE %s")
        params.append(f"%{url}%")
    if status is not None:
        conditions.append("status = %s")
        params.append(status)
    if touser:
        # 使用 LIKE 进行模糊查询
        conditions.append("touser LIKE %s")
        params.append(f"%{touser}%")
    where_clause = " AND ".join(conditions)
    if where_clause:
        where_clause = "WHERE " + where_clause

    offset = (page - 1) * page_size
    query = f"SELECT * FROM craw_douyin_hao_url {where_clause} order by id desc LIMIT %s OFFSET %s"
    count_query = f"SELECT COUNT(*) as total_count FROM craw_douyin_hao_url {where_clause}"
    count_result = db_handler.execute_query(count_query)
    total_count = count_result[0]['total_count'] if count_result else 0
    params.extend([page_size, offset])


    # 计算总页数
    total_pages = (total_count + page_size - 1)
    results = db_handler.execute_query(query, params)
    return {
        "current_page": page,
        "page_size": page_size,
        "total_count": total_count,
        "total_pages": total_pages,
        "data": results
    }

# 获取单个记录
@app.get("/douyin_hao_url/{item_id}")
def get_douyin_hao_url(item_id: int):
    db_handler = initdb()
    condition = f"id = {item_id}"
    results = db_handler.execute_query(f"SELECT * FROM craw_douyin_hao_url WHERE {condition}")
    if results:
        return results[0]
    return {"message": "信息不存在"}

# 更新记录
@app.put("/douyin_hao_url/{item_id}")
def update_douyin_hao_url(item_id: int, item: DouyinHaoUrl):
    db_handler = initdb()
    data = item.dict()
    data = filter_empty_keys(data)
    condition = f"id = {item_id}"
    rows_affected = db_handler.update('craw_douyin_hao_url', data, condition)
    if rows_affected > 0:
        return {"message": "操作成功"}
    return {"message": "信息不存在或修改失败"}

# 删除记录
@app.delete("/douyin_hao_url/{item_id}")
def delete_douyin_hao_url(item_id: int):
    db_handler = initdb()
    condition = f"id = {item_id}"
    rows_affected = db_handler.delete('craw_douyin_hao_url', condition)
    if rows_affected > 0:
        return {"message": "删除成功"}
    return {"message": "信息不存在或删除成功"}



# 定义数据模型
class DouyinUrl(BaseModel):
    url: Optional[str] = Field(None, description="抖音链接")
    keyword: Optional[str] = Field(None, description="品牌名")
    level: Optional[str] = Field(None, description="级别")
    hangye: Optional[str] = Field(None, description="行业")
    hangye_type: Optional[str] = Field(None, description="行业类型")
    type: Optional[str] = Field(None, description="类型")
    status: Optional[int] = Field(None, description="状态")

# 创建记录
@app.post("/douyin_url/")
def create_douyin_url(item: DouyinUrl):
    db_handler = initdb()
    data = item.dict()
    data['hangye_type'] = cfun.get_hangye_type(data['hangye'])
    data['status'] = 1
    try:
        rows_affected = db_handler.insert('craw_douyin_url', data)
        if rows_affected > 0:
            return {"message": "添加成功"}
        return {"message": "信息已存在或添加失败"}
    except IntegrityError as e:
        return {"message": f"Integrity error: {e}"}


# 获取所有记录，支持查询和分页
@app.get("/douyin_url/")
def get_all_douyin_urls(
    url: str | None = Query(None, description="Filter by url (fuzzy search)"),
    status: int | None = Query(None, description="Filter by status"),
    keyword: str | None = Query(None, description="Filter by keyword (fuzzy search)"),
    level: str | None = Query(None, description="Filter by level"),
    touser: str | None = Query(None, description="Filter by touser (fuzzy search)"),
    hangye: str | None = Query(None, description="Filter by hangye (fuzzy search)"),
    hangye_type: str | None = Query(None, description="Filter by hangye_type (fuzzy search)"),
    type: str | None = Query(None, description="Filter by type (fuzzy search)"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, description="Number of items per page")
):
    db_handler = initdb()
    conditions = []
    params = []

    if url:
        conditions.append("url LIKE %s")
        params.append(f"%{url}%")
    if status is not None:
        conditions.append("status = %s")
        params.append(status)
    if keyword:
        conditions.append("keyword LIKE %s")
        params.append(f"%{keyword}%")
    if level:
        conditions.append("level = %s")
        params.append(level)
    if touser:
        conditions.append("touser LIKE %s")
        params.append(f"%{touser}%")
    if hangye:
        conditions.append("hangye LIKE %s")
        params.append(f"%{hangye}%")
    if hangye_type:
        conditions.append("hangye_type LIKE %s")
        params.append(f"%{hangye_type}%")
    if type:
        conditions.append("type LIKE %s")
        params.append(f"%{type}%")

    where_clause = " AND ".join(conditions)
    if where_clause:
        where_clause = "WHERE " + where_clause

    offset = (page - 1) * page_size
    query = f"SELECT * FROM craw_douyin_url {where_clause} order by id desc LIMIT %s OFFSET %s"
    count_query = f"SELECT COUNT(*) as total_count FROM craw_douyin_url {where_clause}"
    count_result = db_handler.execute_query(count_query)
    total_count = count_result[0]['total_count'] if count_result else 0
    params.extend([page_size, offset])



    # 计算总页数
    total_pages = (total_count + page_size - 1)
    results = db_handler.execute_query(query, params)
    return {
        "current_page": page,
        "page_size": page_size,
        "total_count": total_count,
        "total_pages": total_pages,
        "data": results
    }



# 获取单个记录
@app.get("/douyin_url/{item_id}")
def get_douyin_url(item_id: int):
    db_handler = initdb()
    condition = f"id = {item_id}"
    results = db_handler.execute_query(f"SELECT * FROM craw_douyin_url WHERE {condition}")
    if results:
        return results[0]
    return {"message": "信息不存在"}


# 更新记录
@app.put("/douyin_url/{item_id}")
def update_douyin_url(item_id: int, item: DouyinUrl):
    db_handler = initdb()
    data = item.dict()
    data = filter_empty_keys(data)
    print(data)
    condition = f"id = {item_id}"
    rows_affected = db_handler.update('craw_douyin_url', data, condition)
    if rows_affected > 0:
        return {"message": "操作成功"}
    return {"message": "信息不存在或修改失败"}


# 删除记录
@app.delete("/douyin_url/{item_id}")
def delete_douyin_url(item_id: int):
    db_handler = initdb()
    condition = f"id = {item_id}"
    rows_affected = db_handler.delete('craw_douyin_url', condition)
    if rows_affected > 0:
        return {"message": "删除成功"}
    return {"message": "信息不存在或删除成功"}


# 历史记录begin
# 定义数据模型
class DouyinHistoryUrl(BaseModel):
    url: str =''
    touser: str = ''
    keyword: str = ''
    level: str = ''
    hangye: str = ''
    hangye_type: str = ''

# 创建记录
@app.post("/douyin_history_url/")
def create_douyin_history_url(item: DouyinHistoryUrl):
    db_handler = initdb()
    data = item.dict()
    try:
        rows_affected = db_handler.insert('craw_douyin_history_url', data)
        if rows_affected > 0:
            return {"message": "添加成功"}
        return {"message": "信息已存在或添加失败"}
    except IntegrityError as e:
        return {"message": f"Integrity error: {e}"}

# 获取所有记录，支持查询和分页
@app.get("/douyin_history_url/")
def get_all_douyin_history_urls(
    url: str | None = Query(None, description="Filter by url"),
    status: int | None = Query(None, description="Filter by status"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, description="Number of items per page")
):
    db_handler = initdb()
    conditions = []
    params = []

    if url:
        # 使用 LIKE 进行模糊查询
        conditions.append("url LIKE %s")
        params.append(f"%{url}%")
    if status is not None:
        conditions.append("status = %s")
        params.append(status)
    where_clause = " AND ".join(conditions)
    if where_clause:
        where_clause = "WHERE " + where_clause

    offset = (page - 1) * page_size
    query = f"SELECT * FROM craw_douyin_history_url {where_clause} order by id desc LIMIT %s OFFSET %s"
    count_query = f"SELECT COUNT(*) as total_count FROM craw_douyin_history_url {where_clause}"
    count_result = db_handler.execute_query(count_query)
    total_count = count_result[0]['total_count'] if count_result else 0
    params.extend([page_size, offset])



    # 计算总页数
    total_pages = (total_count + page_size - 1)
    results = db_handler.execute_query(query, params)
    return {
        "current_page": page,
        "page_size": page_size,
        "total_count": total_count,
        "total_pages": total_pages,
        "data": results
    }

# 获取单个记录
@app.get("/douyin_history_url/{item_id}")
def get_douyin_history_url(item_id: int):
    db_handler = initdb()
    condition = f"id = {item_id}"
    results = db_handler.execute_query(f"SELECT * FROM craw_douyin_history_url WHERE {condition}")
    if results:
        return results[0]
    return {"message": "信息不存在"}

# 更新记录
@app.put("/douyin_history_url/{item_id}")
def update_douyin_history_url(item_id: int, item: DouyinHistoryUrl):
    db_handler = initdb()
    data = item.dict()
    data = filter_empty_keys(data)
    if data:
        condition = f"id = {item_id}"
        rows_affected = db_handler.update('craw_douyin_history_url', data, condition)
        if rows_affected > 0:
            return {"message": "操作成功"}
    return {"message": "信息不存在或修改失败"}

# 删除记录
@app.delete("/douyin_history_url/{item_id}")
def delete_douyin_history_url(item_id: int):
    db_handler = initdb()
    condition = f"id = {item_id}"
    rows_affected = db_handler.delete('craw_douyin_history_url', condition)
    if rows_affected > 0:
        return {"message": "删除成功"}
    return {"message": "信息不存在或删除成功"}
# 历史记录end

#直播begin
# 定义数据模型
class DouyinLive(BaseModel):
    liveid: Optional[str] = Field(None, description="直播链接")
    name: Optional[str] = Field(None, description="直播名称")
    status: Optional[int] = Field(None, description="状态")
    islisten: Optional[int] = Field(None, description="是否监听")
    touser: Optional[str] = Field(None, description="提醒人")

# 创建记录
@app.post("/douyin_live/")
def create_douyin_live(item: DouyinLive):
    db_handler = initdb()
    data = item.dict()
    try:
        data = filter_empty_keys(data)
        rows_affected = db_handler.insert('craw_lives', data)
        if rows_affected > 0:
            return {"message": "添加成功"}
        return {"message": "信息已存在或添加失败"}
    except IntegrityError as e:
        return {"message": f"Integrity error: {e}"}

# 更新记录
@app.put("/douyin_live/{item_id}")
def update_douyin_live(item_id: int, item: DouyinLive):
    db_handler = initdb()
    data = item.dict()
    data = filter_empty_keys(data)
    print(data)
    condition = f"id = {item_id}"
    rows_affected = db_handler.update('craw_lives', data, condition)
    if rows_affected > 0:
        return {"message": "操作成功"}
    return {"message": "信息不存在或修改失败"}
# 获取所有记录，支持查询和分页
@app.get("/douyin_live/")
def get_all_douyin_lives(
    liveid: str | None = Query(None, description="Filter by liveid"),
    addtime_from: str | None = Query(None, description=""),
    addtime_to: str | None = Query(None, description=""),
    lastlistentime_from: str | None = Query(None, description=""),
    lastlistentime_to: str | None = Query(None, description=""),
    lasttixingtime_from: str | None = Query(None, description=""),
    lasttixingtime_to: str | None = Query(None, description=""),
    name: str | None = Query(None, description="Filter by name"),
    status: int | None = Query(None, description="Filter by status"),
    touser: str | None = Query(None, description="Filter by touser"),
    islisten: int | None = Query(None, description=""),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, description="Number of items per page")
):
    db_handler = initdb()
    conditions = []
    params = []

    if liveid:
        # 使用 LIKE 进行模糊查询
        conditions.append("liveid LIKE %s")
        params.append(f"%{liveid}%")
    if addtime_from:
        conditions.append("addtime >= %s")
        params.append(f"{addtime_from}")
    if addtime_to:
        conditions.append("addtime <= %s")
        params.append(f"{addtime_to}")
    if lastlistentime_from:
        conditions.append("lastlistentime >= %s")
        params.append(f"{lastlistentime_from}")
    if lastlistentime_to:
        conditions.append("lastlistentime <= %s")
        params.append(f"{lastlistentime_to}")

    if lasttixingtime_from:
        conditions.append("lasttixingtime >= %s")
        params.append(f"{lasttixingtime_from}")
    if lasttixingtime_to:
        conditions.append("lasttixingtime <= %s")
        params.append(f"{lasttixingtime_to}")

    if name:
        conditions.append("name LIKE %s")
        params.append(f"%{name}%")
    if status is not None:
        conditions.append("status = %s")
        params.append(status)
    if islisten is not None:
        conditions.append("islisten = %s")
        params.append(islisten)
    if touser:
        # 使用 LIKE 进行模糊查询
        conditions.append("touser LIKE %s")
        params.append(f"%{touser}%")
    where_clause = " AND ".join(conditions)
    if where_clause:
        where_clause = "WHERE " + where_clause

    offset = (page - 1) * page_size
    query = f"SELECT * FROM craw_lives {where_clause} order by id desc LIMIT %s OFFSET %s"

    count_query = f"SELECT COUNT(*) as total_count FROM craw_lives {where_clause}"
    count_result = db_handler.execute_query(count_query)
    total_count = count_result[0]['total_count'] if count_result else 0

    params.extend([page_size, offset])

    

    # 计算总页数
    total_pages = (total_count + page_size - 1)
    results = db_handler.execute_query(query, params)
    return {
        "current_page": page,
        "page_size": page_size,
        "total_count": total_count,
        "total_pages": total_pages,
        "data": results
    }

# 周波
@app.get("/douyin_livedetail/")
def get_douyin_livedetail(
    liveid: str | None = Query(None, description="Filter by liveid"),
    name: str | None = Query(None, description="Filter by name"),
    status: int | None = Query(None, description="Filter by status"),
    updatetime_from: str | None = Query(None, description=""),
    updatetime_to: str | None = Query(None, description=""),
    export: int | None = Query(0, description="是否导出"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, description="Number of items per page")
):
    db_handler = initdb()
    conditions = []
    params = []

    if liveid:
        # 使用 LIKE 进行模糊查询
        conditions.append("a.liveid = %s")
        params.append(liveid)
    if name:
        conditions.append("b.name LIKE %s")
        params.append(f"%{name}%")
    if status is not None:
        conditions.append("a.status = %s")
        params.append(status)
    if updatetime_from:
        conditions.append("a.updatetime >= %s")
        params.append(f"{updatetime_from}")
    if updatetime_to:
        conditions.append("a.updatetime <= %s")
        params.append(f"{updatetime_to}")
    where_clause = " AND ".join(conditions)
    if where_clause:
        where_clause = "WHERE " + where_clause
    if export:
        query = f"SELECT a.id,a.liveid as '直播id',b.name as '直播名称',a.nickname as '抖音昵称',a.sec_uid as '主页链接',a.updatetime as '更新时间',a.create_time as '创建时间',a.type as '类型',a.text as '内容',IF( a.unique_id, a.unique_id, a.short_id ) as '抖音号',a.phone as '手机号',a.signature as '介绍文字',a.address as '地址',a.avatar as '头像图片',a.cover as '门头图片',a.status as '状态'  FROM craw_douyin_live_user a left join craw_lives b on a.liveid = b.liveid {where_clause} order by a.id desc"
        datas  = db_handler.execute_query(query, params)
        # print(datas)
        return cfun.export_to_csv(datas)

    else:
        offset = (page - 1) * page_size
        query = f"SELECT a.*,b.name,IF( a.unique_id, a.unique_id, a.short_id ) as tunique_id FROM craw_douyin_live_user a left join craw_lives b on a.liveid = b.liveid {where_clause} order by a.id desc LIMIT %s OFFSET %s"
        print(query)

        count_query = f"SELECT COUNT(*) as total_count FROM craw_douyin_live_user a left join craw_lives b on a.liveid = b.liveid {where_clause}"
        print(count_query)
        count_result = db_handler.execute_query(count_query,params)
        total_count = count_result[0]['total_count'] if count_result else 0
        print(total_count)

        params.extend([page_size, offset])

        # 计算总页数
        total_pages = (total_count + page_size - 1)
        results = db_handler.execute_query(query, params)
        return {
            "current_page": page,
            "page_size": page_size,
            "total_count": total_count,
            "total_pages": total_pages,
            "data": results
        }
# 获取单个记录
@app.get("/douyin_live/{item_id}")
def get_douyin_live(item_id: int):
    db_handler = initdb()
    condition = f"id = {item_id}"
    results = db_handler.execute_query(f"SELECT * FROM craw_lives WHERE {condition}")
    if results:
        return results[0]
    return {"message": "信息不存在"}

# 更新记录
@app.put("/douyin_live/{item_id}")
def update_douyin_live(item_id: int, item: DouyinLive):
    db_handler = initdb()
    data = item.dict()
    condition = f"id = {item_id}"
    rows_affected = db_handler.update('craw_lives', data, condition)
    if rows_affected > 0:
        return {"message": "操作成功"}
    return {"message": "信息不存在或修改失败"}

# 删除记录
@app.delete("/douyin_live/{item_id}")
def delete_douyin_live(item_id: int):
    db_handler = initdb()
    condition = f"id = {item_id}"
    rows_affected = db_handler.delete('craw_lives', condition)
    if rows_affected > 0:
        return {"message": "删除成功"}
    return {"message": "信息不存在或删除成功"}
#直播end

# 添加关键词
@app.post("/douyin_keyword/")
def create_douyin_keyword(item: DouyinKeyWord):
    db_handler = initdb()
    post = item.dict()
    keywords = post['keywords'].splitlines()
    data = []
    for kw in keywords:
        data.append([kw,post['type'],post['status']])
    try:
        rows_affected = db_handler.insertAll('craw_douyin_keyword',['keyword','type','status'],data)
        if rows_affected > 0:
            return {"message": "添加成功"}
        return {"message": "信息已存在或添加失败"}
    except IntegrityError as e:
        return {"message": f"Integrity error: {e}"}

@app.get("/keywords/")
def get_douyin_keywords(
    keyword: Optional[str] = Query(None, description="Filter by keyword"),
    type: Optional[int] = Query(None, description=""),
    status: Optional[int] = Query(None, description=""),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, description="Number of items per page")
    ):
    db_handler = initdb()
    conditions = []
    params = []

    if keyword:
        # 使用 LIKE 进行模糊查询
        conditions.append("keyword LIKE %s")
    if type:
        conditions.append("type = %s")
        params.append(type)
    if status:
        conditions.append("status = %s")
        params.append(status)

    where_clause = " AND ".join(conditions)
    if where_clause:
        where_clause = "WHERE " + where_clause

    offset = (page - 1) * page_size
    query = f"SELECT * FROM craw_douyin_keyword {where_clause} order by id desc LIMIT %s OFFSET %s"
    count_query = f"SELECT COUNT(*) as total_count FROM craw_douyin_keyword {where_clause}"
    count_result = db_handler.execute_query(count_query)
    total_count = count_result[0]['total_count'] if count_result else 0
    params.extend([page_size, offset])



    # 计算总页数
    total_pages = (total_count + page_size - 1)
    results = db_handler.execute_query(query, params)
    return {
        "current_page": page,
        "page_size": page_size,
        "total_count": total_count,
        "total_pages": total_pages,
        "data": results
    }

# 删除记录
@app.delete("/keywords/{item_id}")
def delete_douyin_keyword(item_id: int):
    db_handler = initdb()
    condition = f"id = {item_id}"
    rows_affected = db_handler.delete('craw_douyin_keyword', condition)
    if rows_affected > 0:
        return {"message": "删除成功"}
    return {"message": "信息不存在或删除成功"}

@app.get("/douyin_hao_fans")
def export_douyin_hao_fans(
    hid: int = Query(0, description="抖音号id"),
    export: int = Query(0, description="是否导出")):
    db_handler = initdb()
    if not hid:
        return 'id不存在'
    query = f"SELECT a.nickname as '被采集用户昵称',a.unique_id as '被采集用户抖音号',b.url as '主页链接',b.nickname as '昵称',b.signature as '主页介绍',b.phone as '号码',b.addtime as '采集时间' FROM craw_douyin_hao_fans as b left join craw_douyin_hao_url as a on b.hid=a.id where a.id={hid}"
    # print(query)
    datas = db_handler.execute_query(query)
    # print(datas)
    if len(datas) > 0:
        if export:
            return cfun.export_to_csv(datas)
        else:    
            return datas
    else:
        return datas

@app.get("/isfans_douyin_hao/{itemid_id}")
def isfans_douyin_hao(itemid_id: int):
    if not itemid_id:
        return {"message": "id不存在"}
    db_handler = initdb()
    condition = f"id = {itemid_id}"
    data = {}
    data['is_fans'] = 1
    rows_affected = db_handler.update('craw_douyin_hao_url', data, condition)
    if rows_affected > 0:
        return {"message": "修改成功"}
    return {"message": "信息不存在或修改失败"}
    
if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)