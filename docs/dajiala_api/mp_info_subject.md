# 获取公众号主体信息

## OpenAPI Specification

```yaml
openapi: 3.0.1
info:
  title: ''
  description: ''
  version: 1.0.0
paths:
  /fbmain/monitor/v3/principal_info:
    post:
      summary: 获取公众号主体信息
      deprecated: false
      description: |-
        |                 状态码                 |          说明          |
        |:-----------------------------------:|:--------------------:|
        | {"message":"Internal Server Error"} |     网络错误，请重试1~3次     |
        |                  0                  |          成功          |
        |              103, 104               |     请求频繁，请2秒后再试      |
        |                 105                 |       文章被发布者删除       |
        |                 106                 | 文章违规，被系统删除 或公众号已永久封号 |
        |                 107                 |    公众号被迁移，文章无法打开     |


        ### 返回结果
        | 字段 | 说明 |
        | --- | --- |
        | ['data']['change_info_list'] | 公众号的改名记录 |
        | ['data']['reg_time'] | 公众号注册时间 |
        | ['data']['reg_time_stamp'] | 注册时间时间戳 |
        | ['data']['registered_id'] |  公众号的营业执照号或组织机构代码证 |
        | ['data']['auth_3rd_list'] |  公众号第三方授权 |
        | ['data']['verify_customer_type'] | 认证类型  企业认证 政府认证 媒体认证 |
        | ['data']['gh_id'] | 公众号原始id |
        | ['data']['customer_type'] | 个人 企业 政府 媒体 其他组织 |
        | ['data']['registered_country'] |  公众号运营所属国家 |
        | ['data']['company_name'] |  公众号主体信息(公司名字) |
        | ['data']['province'] | 个人号所在省份（企业号为空） |
        | ['data']['gender'] | 公众号个人号的性别（企业号为空） |
        | ['data']['wx_id'] |  公众号的wxid（如果没设置此值等于gh_id） |
        | ['data']['owner_name'] | 主体名字  （公司名字） |
        | ['data']['verify_status'] | 公众号认证状态（未认证，个人认证，已认证，认证过期） |
        | ['data']['desc'] | 公众号简介信息 |
        | ['data']['service_phone'] | 公众号客服热线 |
        | ['data']['last_login_country'] | 上次登陆国家 |
        | ['data']['last_login_province'] | 上次登陆省份 |
        | ['data']['name'] | 此值等于  主体的名字 |
        | ['data']['verify_date'] |  公众号通过认证的时间 |
        | ['data']['nick_name'] |   最后一次认证公众号的名字，可能不是当前的名字 |
      tags:
        - 公众号账号搜索和账号基本信息
      parameters: []
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                biz:
                  type: string
                  description: >-
                    biz调用参数名biz(0.5元/次)  注意：biz、 url、 name 任选一个填入，如果都填，优先使用biz
                    然后 url 最后 wxid
                url:
                  type: string
                  description: 文章长链接 (0.5元/次)  、文章短链接 (0.52元/次)
                wxid:
                  type: string
                  description: 微信ID/微信号名称 (0.5元/次)
                key:
                  type: string
                  description: 极致了官网 key
                verifycode:
                  type: string
                  description: 附加码 (如设置了附加码verifycode，则此参数为必选，如未设置则为非必选)
              x-apifox-orders:
                - biz
                - url
                - wxid
                - key
                - verifycode
              required:
                - verifycode
                - key
              description: biz、url、wxid 三个参数任选其一，至少传入一个。
            example:
              biz: ''
              url: >-
                https://mp.weixin.qq.com/s?__biz=MzI3OTE0NDIyNw==&mid=2247497162&idx=1&sn=742958142ac23f382f7e2873611a3fd9&chksm=ea8d0a49d9e29a19b7eeb150246e15de297f4cbfebbc4403e143c2caf96f5563849b4e1f9f08#rd
              wxid: ''
              key: '{{key}}'
              verifycode: ''
      responses:
        '200':
          description: ''
          content:
            application/json:
              schema:
                type: object
                properties:
                  code:
                    type: integer
                  msg:
                    type: string
                  data:
                    type: object
                    properties:
                      auth_3rd_list:
                        type: array
                        items:
                          type: string
                        description: ' 公众号第三方授权'
                      desc:
                        type: string
                        description: 公众号简介信息
                      gender:
                        type: string
                        description: 公众号个人号的性别（企业号为空）
                      gh_id:
                        type: string
                        description: ' 公众号原始id'
                      nick_name:
                        type: string
                        description: ' 最后一次认证公众号的名字，可能不是当前的名字'
                      reg_time:
                        type: string
                        description: 公众号注册时间
                      registered_country:
                        type: string
                        description: ' 公众号运营所属国家'
                      registered_id:
                        type: string
                        description: ' 公众号的营业执照号或组织机构代码证'
                      service_phone:
                        type: string
                        description: 公众号客服热线
                      verify_date:
                        type: string
                        description: ' 公众号通过认证的时间'
                      verify_status:
                        type: string
                        description: 公众号认证状态（未认证，个人认证，已认证，认证过期）
                      wx_id:
                        type: string
                        description: ' 公众号的wxid（如果没设置此值等于gh_id）'
                      change_info_list:
                        type: array
                        items:
                          type: string
                        description: ' 公众号的改名记录'
                      reg_time_stamp:
                        type: integer
                        description: 注册时间时间戳
                      verify_customer_type:
                        type: string
                        description: 认证类型  企业认证 政府认证 媒体认证
                      customer_type:
                        type: string
                        description: 个人 企业 政府 媒体 其他组织
                      company_name:
                        type: string
                        description: ' 公众号主体信息(公司名字)'
                      province:
                        type: string
                        description: 个人号所在省份（企业号为空）
                      owner_name:
                        type: string
                        description: 主体名字  （公司名字）
                      last_login_country:
                        type: string
                        description: 上次登陆国家
                      last_login_province:
                        type: string
                        description: 上次登陆省份
                      name:
                        type: string
                        description: 此值等于  主体的名字
                    required:
                      - province
                      - auth_3rd_list
                      - desc
                      - gender
                      - gh_id
                      - nick_name
                      - change_info_list
                      - company_name
                      - reg_time
                      - registered_country
                      - registered_id
                      - service_phone
                      - verify_date
                      - verify_status
                      - wx_id
                      - reg_time_stamp
                      - verify_customer_type
                      - customer_type
                      - owner_name
                      - last_login_country
                      - last_login_province
                      - name
                    x-apifox-orders:
                      - change_info_list
                      - reg_time
                      - reg_time_stamp
                      - registered_id
                      - auth_3rd_list
                      - verify_customer_type
                      - gh_id
                      - customer_type
                      - registered_country
                      - company_name
                      - province
                      - gender
                      - wx_id
                      - owner_name
                      - verify_status
                      - desc
                      - service_phone
                      - last_login_country
                      - last_login_province
                      - name
                      - verify_date
                      - nick_name
                required:
                  - code
                  - msg
                  - data
                x-apifox-orders:
                  - code
                  - msg
                  - data
              example:
                code: 0
                msg: success
                data:
                  change_info_list: []
                  reg_time: '2013-07-19'
                  reg_time_stamp: 1374163200
                  registered_id: ''
                  auth_3rd_list:
                    - 传扬信息科技(上海)有限公司
                    - 北京清博大数据科技有限公司
                    - 武汉夜莺科技有限公司
                    - 上海新榜信息技术股份有限公司
                    - 提子科技(北京)有限公司
                    - 北京百度网讯科技有限公司
                  verify_customer_type: 政府认证
                  gh_id: gh_5127e91ae3d7
                  customer_type: 政府
                  registered_country: 中国
                  is_overseas: 0
                  company_name: 中国共产主义青年团河北省委员会
                  province: ''
                  gender: ''
                  wx_id: HBGQT87903800
                  owner_name: 中国共产主义青年团河北省委员会
                  verify_status: 已认证
                  desc: 服务广大青年，展示冀青风采！
                  service_phone: ''
                  last_login_country: 中国
                  last_login_province: 河北
                  name: 中国共产主义青年团河北省委员会
                  nick_name: 河北共青团
                  verify_date: '2024-03-29'
          headers: {}
          x-apifox-name: 成功
      security: []
      x-apifox-folder: 公众号账号搜索和账号基本信息
      x-apifox-status: released
      x-run-in-apifox: https://app.apifox.com/web/project/4919579/apis/api-199757379-run
components:
  schemas: {}
  securitySchemes: {}
servers:
  - url: https://www.dajiala.com
    description: 正式环境
security: []

```
