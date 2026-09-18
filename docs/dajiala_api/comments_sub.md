# 获取公众号文章二级评论

## OpenAPI Specification

```yaml
openapi: 3.0.1
info:
  title: ''
  description: ''
  version: 1.0.0
paths:
  /fbmain/monitor/v3/article_sub_comment:
    post:
      summary: 获取公众号文章二级评论
      deprecated: false
      description: |-
        **实时数据**
        |                 状态码                 |          说明          |
        |:-----------------------------------:|:--------------------:|
        | {"message":"Internal Server Error"} |     网络错误，请重试1~3次     |
        |                  0                  |          成功          |
        |                  102                  |         文章被删除，或状态异常         |
        |              103             |     文章没有开通评论功能     |
        |               500         |     请求失败，请稍后重试   |


        ### 返回结果
        | 字段 | 说明 |
        | --- | --- |
        | ['data'] | 评论列表 |
        | data[i].content | 评论内容 |
        | data[i]['create_time'] | 评论时间戳 |
        | data[i]['ip_wording']['country_name'] | 评论者国家 |
        |data[i]['ip_wording']['province_name'] | 评论者省份 |
        |data[i]['ip_wording']['city_name'] | 评论者城市 |
        | data[i]['logo_url'] | 头像链接 |
        | data[i]['nick_name'] | 评论者名称 |
        | data[i]['reply_like_num'] | 评论点赞数 |
        | data[i]['from_ai'] | 是否来自AI |
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
                  description: 文章长链接 0.06/次
                content_id:
                  type: string
                  description: 一级评论的content_id字段
                key:
                  type: string
                  description: 极致了官网 key. 注意使用key  请直接填入，不要带{{}} , 双括号是 apifox里面设置的全局变量
                verifycode:
                  type: string
                  description: 附加码 (如设置了附加码verifycode，则此参数为必选，如未设置则为非必选)
              required:
                - url
                - content_id
                - key
              x-apifox-orders:
                - url
                - content_id
                - key
                - verifycode
            example:
              url: >-
                https://mp.weixin.qq.com/s?__biz=MzI3OTE0NDIyNw==&mid=2247497162&idx=1&sn=742958142ac23f382f7e2873611a3fd9&chksm=ea8d0a49d9e29a19b7eeb150246e15de297f4cbfebbc4403e143c2caf96f5563849b4e1f9f08#rd
              content_id: '12393667065104302166'
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
                    type: array
                    items:
                      type: object
                      properties:
                        content:
                          type: string
                          description: ' 评论内容'
                        logo_url:
                          type: string
                          description: ' 头像地址'
                        nick_name:
                          type: string
                          description: ' 评论者的昵称'
                        create_time_stamp:
                          type: integer
                          description: ' 时间戳'
                        create_time:
                          type: string
                          description: ' 评论时间'
                        like_num:
                          type: integer
                          description: ' 评论点赞数'
                        reply_list:
                          type: string
                          description: ' 回复列表'
                        new_reply_list:
                          type: array
                          items:
                            type: string
                          description: 回复的回复
                        country_id:
                          type: string
                          description: ' 国家id'
                        country_name:
                          type: string
                          description: 国家名称
                        province_name:
                          type: string
                          description: ' 所在省份'
                        is_top:
                          type: integer
                          description: 1置顶  0不置顶
                      required:
                        - content
                        - logo_url
                        - nick_name
                        - create_time_stamp
                        - create_time
                        - like_num
                        - reply_list
                        - new_reply_list
                        - country_id
                        - country_name
                        - province_name
                        - is_top
                      x-apifox-orders:
                        - content
                        - is_top
                        - logo_url
                        - nick_name
                        - create_time_stamp
                        - create_time
                        - like_num
                        - reply_list
                        - new_reply_list
                        - country_id
                        - country_name
                        - province_name
                    description: 评论列表
                  total:
                    type: integer
                    description: ' 评论数'
                  buffer:
                    type: string
                    description: 下一页的buffer
                  continue_flag:
                    type: boolean
                    description: 能否继续翻页 此参数可能不准确，如果评论数小于100，则无法继续翻页。
                required:
                  - code
                  - msg
                  - data
                  - total
                  - buffer
                  - continue_flag
                x-apifox-orders:
                  - code
                  - msg
                  - data
                  - total
                  - buffer
                  - continue_flag
              examples:
                '1':
                  summary: 成功示例
                  value:
                    code: 0
                    msg: 成功
                    cost: 0.06
                    remain_money: 3945.53
                    data:
                      - author_like_status: 0
                        bizattr_servicetype: 0
                        can_share: true
                        content: 不拔以色列，伊朗永远别想过安宁的日子
                        create_time: 1776177809
                        from_ai: false
                        identity_name: oI8VzwyYyYej3oTCSgY6ssqiUIRE
                        identity_type: 0
                        ip_wording:
                          city_id: ''
                          city_name: ''
                          country_id: '156'
                          country_name: 中国
                          province_id: ''
                          province_name: 广东
                        is_from: 3
                        is_from_friend: 0
                        is_reward: 0
                        logo_url: >-
                          https://wx.qlogo.cn/mmopen/ANibjF6yfTfsY7XdtiaISDeAMhicku1cH7GBF94R3eib8Jibic2YYUUvdCsNwcXiaccjdp1WUIRsdjDiaErhYvBa0ibqBkVYL0ic4SNG8J/64
                        multi_info:
                          emojis: []
                          pictures: []
                        nick_name: 黄鸿生13434988837
                        openid: oI8VzwyYyYej3oTCSgY6ssqiUIRE
                        reply_dislike_status: 0
                        reply_id: 1
                        reply_like_num: 96
                        reply_like_status: 0
                        to_reply_del_flag: 0
                      - author_like_status: 0
                        bizattr_servicetype: 0
                        can_share: true
                        content: 坚决支持！
                        create_time: 1776177878
                        from_ai: false
                        identity_name: oI8Vzw0DZkh0FaO07uAwiFqp8mPo
                        identity_type: 0
                        ip_wording:
                          city_id: ''
                          city_name: ''
                          country_id: '156'
                          country_name: 中国
                          province_id: ''
                          province_name: 江苏
                        is_from: 3
                        is_from_friend: 0
                        is_reward: 0
                        logo_url: >-
                          https://wx.qlogo.cn/mmopen/naPHoFY2n5R8kM81BX3FJMhbI1jDibiaTVvX6ooHpfzeic01w3KvynW1xribKphaXzzepmLMZL47dgjt3AX2JAVrSZABzbQWaiaTB/64
                        multi_info:
                          emojis: []
                          pictures: []
                        nick_name: ms@L
                        openid: oI8Vzw0DZkh0FaO07uAwiFqp8mPo
                        reply_dislike_status: 0
                        reply_id: 2
                        reply_like_num: 307
                        reply_like_status: 0
                        to_reply_del_flag: 0
                      - author_like_status: 0
                        bizattr_servicetype: 0
                        can_share: true
                        content: 不急，等美国人民衰败，时间在我们这边，中东人民也可以封，只有以色列不敢等！
                        create_time: 1776178154
                        from_ai: false
                        identity_name: oI8Vzw9O0fkKNECUREAPo5B2jzgM
                        identity_type: 0
                        ip_wording:
                          city_id: ''
                          city_name: ''
                          country_id: '156'
                          country_name: 中国
                          province_id: ''
                          province_name: 江西
                        is_from: 3
                        is_from_friend: 0
                        is_reward: 0
                        logo_url: >-
                          https://wx.qlogo.cn/mmopen/0WYrIm4GPzKSVl1enfzIWkKbk4r2Nib30S8s0BiburHtRqCPYllJiaHqogAGQgiax1DTd6QF3Lb2quKicLLiaKVYw47vbLTQBiazWKMrlbBjEvtIvfnYFJfysmxJuwqTzvMgYZn/64
                        multi_info:
                          emojis: []
                          pictures: []
                        nick_name: 小北
                        openid: oI8Vzw9O0fkKNECUREAPo5B2jzgM
                        reply_dislike_status: 0
                        reply_id: 3
                        reply_like_num: 28
                        reply_like_status: 0
                        to_reply_del_flag: 0
                      - author_like_status: 0
                        bizattr_servicetype: 0
                        can_share: true
                        content: 是的，不知道怎么变成伊朗和美国为主了，不应该是主要打以色列吗
                        create_time: 1776178216
                        from_ai: false
                        identity_name: oI8Vzw_WvTLt5m1V2UX_TXfnr92w
                        identity_type: 0
                        ip_wording:
                          city_id: ''
                          city_name: ''
                          country_id: '156'
                          country_name: 中国
                          province_id: ''
                          province_name: 湖南
                        is_from: 3
                        is_from_friend: 0
                        is_reward: 0
                        logo_url: >-
                          https://wx.qlogo.cn/mmopen/0WYrIm4GPzIOX7Su27E24tPOicaKPmd2TYUjIE3pxVxoa2U4SicNFkgZCnAcuroFJKbZmLdZgicdTufNguz70tExPia2viagiax6KSRzchFATC6HYniaaqfCdEHwPzLeLuvZzdN/64
                        multi_info:
                          emojis: []
                          pictures: []
                        nick_name: 牛娃大叔
                        openid: oI8Vzw_WvTLt5m1V2UX_TXfnr92w
                        reply_dislike_status: 0
                        reply_id: 4
                        reply_like_num: 42
                        reply_like_status: 0
                        to_reply_del_flag: 0
                      - author_like_status: 0
                        bizattr_servicetype: 0
                        can_share: true
                        content: 不用。以色列🇮🇱灭亡是必然的，伊朗🇮🇷不必过度用力在这上面，发展好自己最重要。
                        create_time: 1776178360
                        from_ai: false
                        identity_name: oI8Vzw68UZ4XeqE0e6g5-2y94glk
                        identity_type: 0
                        ip_wording:
                          city_id: ''
                          city_name: ''
                          country_id: '156'
                          country_name: 中国
                          province_id: ''
                          province_name: 上海
                        is_from: 3
                        is_from_friend: 0
                        is_reward: 0
                        logo_url: >-
                          https://wx.qlogo.cn/mmopen/ANibjF6yfTftfyh9DH2jmJ3vTVNrI7vDQBEofl4oL6bQvUUYpQr4xkkGemslz70Edw5MuoP2zGwSxLLGicibia8QqLjbxeAr1GT6/64
                        multi_info:
                          emojis: []
                          pictures: []
                        nick_name: 文质彬彬
                        openid: oI8Vzw68UZ4XeqE0e6g5-2y94glk
                        reply_dislike_status: 0
                        reply_id: 5
                        reply_like_num: 22
                        reply_like_status: 0
                        to_reply_del_flag: 0
                      - author_like_status: 0
                        bizattr_servicetype: 0
                        can_share: true
                        content: 以色列有干儿子美国，不好搞。
                        create_time: 1776179329
                        from_ai: false
                        identity_name: oI8Vzw3q-KjOqVRF06JNJE25-4-g
                        identity_type: 0
                        ip_wording:
                          city_id: ''
                          city_name: ''
                          country_id: '156'
                          country_name: 中国
                          province_id: ''
                          province_name: 四川
                        is_from: 3
                        is_from_friend: 0
                        is_reward: 0
                        logo_url: >-
                          https://wx.qlogo.cn/mmopen/M22ibRibkvYnmDreob6yW6ictz9rc48ah1WgicSolYns5Jvh1IEb0BPDoLT8tTHOIltvkJjHS6k0bNt0YAibJrraVLL2b9oAvhjYF/64
                        multi_info:
                          emojis: []
                          pictures: []
                        nick_name: 白开水
                        openid: oI8Vzw3q-KjOqVRF06JNJE25-4-g
                        reply_dislike_status: 0
                        reply_id: 6
                        reply_like_num: 26
                        reply_like_status: 0
                        to_reply_del_flag: 0
                      - author_like_status: 0
                        bizattr_servicetype: 0
                        can_share: true
                        content: 不折后面的大锤，专心只拔这个钉子有用么？
                        create_time: 1776180200
                        from_ai: false
                        identity_name: oI8Vzw9eSC3AMzsIIbW2aEztBbIw
                        identity_type: 0
                        ip_wording:
                          city_id: ''
                          city_name: ''
                          country_id: '156'
                          country_name: 中国
                          province_id: ''
                          province_name: 广东
                        is_from: 3
                        is_from_friend: 0
                        is_reward: 0
                        logo_url: >-
                          https://wx.qlogo.cn/mmopen/ANibjF6yfTfsoBT0sMJNqpl7qWBhqaKPIyE4sIdBSIdQq6M9dZHr9rc84gJpL8oVd6o7Mz1pXFYUiaLConRoIicRd27XKhm57Yt/64
                        multi_info:
                          emojis: []
                          pictures: []
                        nick_name: 张辉
                        openid: oI8Vzw9eSC3AMzsIIbW2aEztBbIw
                        reply_dislike_status: 0
                        reply_id: 8
                        reply_like_num: 16
                        reply_like_status: 0
                        to_reply_del_flag: 0
                      - author_like_status: 0
                        bizattr_servicetype: 0
                        can_share: true
                        content: 距离远
                        create_time: 1776180219
                        from_ai: false
                        identity_name: oI8Vzw0gI-yA9GY2Ex6Uel1T7U3M
                        identity_type: 0
                        ip_wording:
                          city_id: ''
                          city_name: ''
                          country_id: '156'
                          country_name: 中国
                          province_id: ''
                          province_name: 新疆
                        is_from: 3
                        is_from_friend: 0
                        is_reward: 0
                        logo_url: >-
                          https://wx.qlogo.cn/mmopen/PiajxSqBRaEKHQBksfnSUt2gqMfGQt6jibiceVXbZIsXYZ6GJ5pazlyOicwx9fFOGOog48NZBhEWMB3x8JicQ6icXfLopsq61qASX29Yb2zZQdRiaibWBCU7IS0SC8mC1TXSGU9D/64
                        multi_info:
                          emojis: []
                          pictures: []
                        nick_name: '222'
                        openid: oI8Vzw0gI-yA9GY2Ex6Uel1T7U3M
                        reply_dislike_status: 0
                        reply_id: 9
                        reply_like_num: 12
                        reply_like_status: 0
                        to_reply_del_flag: 0
                      - author_like_status: 0
                        bizattr_servicetype: 1
                        can_share: true
                        content: >-
                          历次中东战争阿拉伯阵营的失败，虽有战术方面的原因，最主要还是各国心不齐，不同教派的国家，都希望其它教派当炮灰自己坐享其成，跟民国时期国民党阵营很像。只有阿拉伯世界完全摒弃教派嫌隙，形成反以合力，才能真的闯出一片新天地，摆脱历次抗争失败的宿命。
                        create_time: 1776180692
                        from_ai: false
                        identity_name: gh_f677a127980d
                        identity_type: 1
                        ip_wording:
                          city_id: ''
                          city_name: ''
                          country_id: '156'
                          country_name: 中国
                          province_id: ''
                          province_name: 北京
                        is_from: 3
                        is_from_friend: 0
                        is_reward: 0
                        logo_url: >-
                          http://wx.qlogo.cn/mmhead/KetjXWSVppszKxgxzSHr9ZpbtWiaibrt10RsdQ2BlhhLVZ223Razy5gkXkxDx7ENjmvqiaNZjxLiaZs/64
                        multi_info:
                          emojis: []
                          pictures: []
                        nick_name: 石蜡粉
                        openid: oI8Vzw4EZeWwhWwA0C3E-tbjzphc
                        reply_dislike_status: 0
                        reply_id: 10
                        reply_like_num: 69
                        reply_like_status: 0
                        to_reply_del_flag: 0
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
      x-run-in-apifox: https://app.apifox.com/web/project/4919579/apis/api-445204557-run
components:
  schemas: {}
  securitySchemes: {}
servers:
  - url: https://www.dajiala.com
    description: 正式环境
security: []

```
