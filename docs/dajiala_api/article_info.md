# 获取公众号文章阅读、点赞、名字，文章标题和URL等信息

## OpenAPI Specification

```yaml
openapi: 3.0.1
info:
  title: ''
  description: ''
  version: 1.0.0
paths:
  /fbmain/monitor/v3/article_info:
    post:
      summary: 获取公众号文章阅读、点赞、名字，文章标题和URL等信息
      deprecated: false
      description: |
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
        | ['data'][i]['wx_name'] | 公众号名字 |
        | ['data'][i]['author'] | 文章作者 |
        | ['data'][i]['wxid'] | wxid |
        | ['data'][i]['ghid'] | 原始id |
        | ['data'][i]['title'] | 文章标题 |
        | ['data'][i]['url'] | 文章链接 |
        | ['data'][i]['idx'] | 第几条 |
        | ['data'][i]['hashid'] | 文章唯一id |
        | ['data'][i]['total_item_num'] | 本次发文总条数 |
        | ['data'][i]['cover'] | 文章封面 |
        | ['data'][i]['wx_head_img'] | 公众号头像 |
        | ['data'][i]['summary'] | 文章简介 |
        | ['data'][i]['source_url'] | 阅读原文链接 |
        | ['data'][i]['type'] | 类型 |
        | ['data'][i]['copyright_stat'] | 是否原创 |
        | ['data'][i]['read'] | 阅读数 |
        | ['data'][i]['praise'] | 点赞数 |
        | ['data'][i]['look'] | 在看数 |
        | ['data'][i]['public_time'] | 发布时间 |
      tags:
        - 公众号文章内容和互动数据等
        - 文章
      parameters: []
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                url:
                  type: string
                  description: 文章长链接(0.03元/次) 、文章短链接(0.05元/次)
                key:
                  type: string
                  description: 极致了官网 key
                verifycode:
                  type: string
                  description: 附加码 (如设置了附加码verifycode，则此参数为必选，如未设置则为非必选)
              required:
                - url
                - key
              x-apifox-orders:
                - url
                - key
                - verifycode
            example:
              url: >-
                https://mp.weixin.qq.com/s?__biz=MjM5MTM5NjUzNA==&mid=2652494556&idx=1&sn=4995d845ad2ef1205136936f65ae4adc&chksm=bd5b5d058a2cd4139bbd92c8cd23d52f65ef260eedf8cbc6d25a4ab0992f08d01da81#rd
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
                  cost:
                    type: number
                  remain_money:
                    type: number
                  data:
                    type: array
                    items:
                      type: object
                      properties:
                        wx_name:
                          type: string
                          description: 公众号名字
                        author:
                          type: string
                          description: 文章作者
                        wxid:
                          type: string
                          description: wxid
                        ghid:
                          type: string
                          description: 原始id
                        title:
                          type: string
                          description: 文章标题
                        url:
                          type: string
                          description: 文章链接
                        idx:
                          type: integer
                          description: 第几条
                        hashid:
                          type: string
                          description: 文章唯一id
                        total_item_num:
                          type: integer
                          description: 本次发文总条数
                        cover:
                          type: string
                          description: 文章封面
                        wx_head_img:
                          type: string
                          description: 公众号头像
                        summary:
                          type: string
                          description: 文章简介
                        source_url:
                          type: string
                          description: 阅读原文链接
                        type:
                          type: integer
                          description: 类型
                        copyright_stat:
                          type: integer
                          description: 是否原创
                        read:
                          type: integer
                          description: 阅读数
                        praise:
                          type: integer
                          description: 点赞数
                        look:
                          type: integer
                          description: 在看数
                        public_time:
                          type: string
                          description: 发布时间
                      x-apifox-orders:
                        - wx_name
                        - author
                        - wxid
                        - ghid
                        - title
                        - url
                        - idx
                        - hashid
                        - total_item_num
                        - cover
                        - wx_head_img
                        - summary
                        - source_url
                        - type
                        - copyright_stat
                        - read
                        - praise
                        - look
                        - public_time
                required:
                  - code
                  - msg
                  - cost
                  - remain_money
                  - data
                x-apifox-orders:
                  - code
                  - msg
                  - cost
                  - remain_money
                  - data
              examples:
                '1':
                  summary: 示例 1
                  value:
                    code: 0
                    msg: success
                    cost: 0.05
                    remain_money: 31751.299
                    data:
                      - wx_name: 河北共青团
                        author: 央视新闻
                        wxid: gh_5127e91ae3d7
                        ghid: gh_5127e91ae3d7
                        title: “四次准备结婚，一次都没成！”
                        url: >-
                          https://mp.weixin.qq.com/s?__biz=MjM5MTM5NjUzNA==&mid=2652494556&idx=1&sn=4995d845ad2ef1205136936f65ae4adc#rd
                        idx: 1
                        hashid: 4995d845ad2ef1205136936f65ae4adc
                        total_item_num: 1
                        cover: >-
                          http://mmbiz.qpic.cn/mmbiz_jpg/qR1zR3jHiclfb4nKhykKfVAyof5YEuEnF3DZ9cmYAFwMvPqpqlM4CGVITE0TLpW1Wtkp8gJwuiaaqefgGDKfcvbg/0?wx_fmt=jpeg
                        wx_head_img: >-
                          http://mmbiz.qpic.cn/mmbiz_png/qR1zR3jHicldEDbRIQXslP4AI7ecrf2EiaamJFWOrgicfWCjb9UUibUHOoRhCPyznstLYG9yXDfRDTsI4hIiaGlykZQ/0?wx_fmt=png
                        summary: ''
                        source_url: https://h5.54heb.com/#/StatisticsNew?rd=1618626285963
                        type: 9
                        copyright_stat: 2
                        read: 100001
                        praise: 6641
                        look: 2714
                        public_time: '2021-11-16 17:55:57'
                '2':
                  summary: 成功示例
                  value:
                    code: 101
                    msg: 文章打不开，原因为：该内容已被发布者删除
                    data: ''
                    cost: 0.06
                    remain: 4253.655
          headers: {}
          x-apifox-name: 成功
        x-200:文章被删除:
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
                    type: string
                  cost:
                    type: number
                  remain:
                    type: number
                required:
                  - code
                  - msg
                  - data
                  - cost
                  - remain
                x-apifox-orders:
                  - code
                  - msg
                  - data
                  - cost
                  - remain
          headers: {}
          x-apifox-name: 文章被删除
      security: []
      x-apifox-folder: 公众号文章内容和互动数据等
      x-apifox-status: released
      x-run-in-apifox: https://app.apifox.com/web/project/4919579/apis/api-199766293-run
components:
  schemas: {}
  securitySchemes: {}
servers:
  - url: https://www.dajiala.com
    description: 正式环境
security: []

```
