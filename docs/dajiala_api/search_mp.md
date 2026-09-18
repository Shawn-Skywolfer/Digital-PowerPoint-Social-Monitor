# 根据关键字查询公众号

## OpenAPI Specification

```yaml
openapi: 3.0.1
info:
  title: ''
  description: ''
  version: 1.0.0
paths:
  /fbmain/monitor/v3/wx_account/search:
    post:
      summary: 根据关键字查询公众号
      deprecated: false
      description: >-
        **库里面数据，非实时数据**

        每页20条结果


        0.2元/条，按实际返回数据条数扣费

        <table data-v-73645c1e="" class="docs-body-table"><thead
        data-v-73645c1e=""><tr data-v-73645c1e=""><th data-v-73645c1e=""
        width="120px">状态码</th> <th data-v-73645c1e="">说明</th></tr></thead>
        <tbody data-v-73645c1e=""><tr data-v-73645c1e=""><td
        data-v-73645c1e="">{"message":"Internal Server Error"}</td> <td
        data-v-73645c1e="">网络错误，请重试1~3次</td></tr> <tr data-v-73645c1e=""><td
        data-v-73645c1e="">0</td> <td data-v-73645c1e="">成功</td></tr> <tr
        data-v-73645c1e=""><td data-v-73645c1e="">-1</td> <td
        data-v-73645c1e="">QPS超过上限，不得高于5次/秒，请5秒后再试！</td></tr> <tr
        data-v-73645c1e=""><td data-v-73645c1e="">100</td> <td
        data-v-73645c1e="">缺少参数 biz,name,url 三者必须至少有一个</td></tr> <tr
        data-v-73645c1e=""><td data-v-73645c1e="">101,102,103</td> <td
        data-v-73645c1e="">biz不合法，请检查。（Tips：biz必须是8-10位数字进行base64编码</td></tr>
        <tr data-v-73645c1e=""><td data-v-73645c1e="">104</td> <td
        data-v-73645c1e="">短连接文章已被删除或文章被迁移</td></tr> <tr data-v-73645c1e=""><td
        data-v-73645c1e="">105</td> <td
        data-v-73645c1e="">没找到该名称的公众号，建议您采用biz或者url作为参数获取！</td></tr> <tr
        data-v-73645c1e=""><td data-v-73645c1e="">110</td> <td
        data-v-73645c1e="">翻页内没有文章了！</td></tr> <tr data-v-73645c1e=""><td
        data-v-73645c1e="">111</td> <td data-v-73645c1e="">请求频繁，请稍后再试。</td></tr>
        <tr data-v-73645c1e=""><td data-v-73645c1e="">112</td> <td
        data-v-73645c1e="">请求失败，请稍后再试。</td></tr> <tr data-v-73645c1e=""><td
        data-v-73645c1e="">113</td> <td data-v-73645c1e="">鉴权失败，请稍后再试。</td></tr>
        <tr data-v-73645c1e=""><td data-v-73645c1e="">115</td> <td
        data-v-73645c1e="">该页以及后面的翻页内文章已全部被删除！</td></tr> <tr
        data-v-73645c1e=""><td data-v-73645c1e="">2003</td> <td
        data-v-73645c1e="">系统资源请求出错，请重新尝试。</td></tr> <tr data-v-73645c1e=""><td
        data-v-73645c1e="">2005</td> <td
        data-v-73645c1e="">系统错误，请2秒后重新尝试。</td></tr> <tr data-v-73645c1e=""><td
        data-v-73645c1e="">10002</td> <td
        data-v-73645c1e="">key或附加码不正确</td></tr> <tr data-v-73645c1e=""><td
        data-v-73645c1e="">20001</td> <td data-v-73645c1e="">金额不足，请充值</td></tr>
        <tr data-v-73645c1e=""><td data-v-73645c1e="">20002</td> <td
        data-v-73645c1e="">请输入正确的微信链接</td></tr> <tr data-v-73645c1e=""><td
        data-v-73645c1e="">20003</td> <td
        data-v-73645c1e="">文章链接有误，请检查文章链接url中的&amp;是否已经编码为%26</td></tr> <tr
        data-v-73645c1e=""><td data-v-73645c1e="">50000</td> <td
        data-v-73645c1e="">内部服务器错误</td></tr></tbody></table>



        ### 返回结果

        | 字段 | 说明 |

        | --- | --- |

        | ['data'][i]['name'] | 公众号名称 |

        | ['data'][i]['biz'] | 公众号唯一ID |

        | ['data'][i]['owner_name'] | 主体名字 |

        | ['data'][i]['customer_type'] | 账号类型 |

        | ['data'][i]['ghid'] | 公众号原始ID |

        | ['data'][i]['wxid'] | 微信号 |

        | ['data'][i]['fans'] | 粉丝数 |

        | ['data'][i]['avg_top_read'] | 头条平均阅读 |

        | ['data'][i]['avg_top_zan'] | 头条平均点赞 |

        | ['data'][i]['avatar'] | 头像 |

        | ['data'][i]['qrcode'] | 头像二维码 |

        | ['data'][i]['week_articles'] | 每周发文数 |

        | ['data'][i]['lastest_publish'] | 最后发文时间 |
      tags:
        - 公众号账号搜索和账号基本信息
      parameters: []
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                keyword:
                  type: string
                  description: 关键词
                page:
                  type: string
                  description: 页码
                size:
                  type: string
                  description: 一页大小
                key:
                  type: string
                  description: 极致了官网 key（0.2元/条）
                verifycode:
                  type: string
                  description: 附加码 (如设置了附加码verifycode，则此参数为必选，如未设置则为非必选)
                mode:
                  type: integer
                  description: 1：模糊搜索 2：精确搜索（默认为1）
              required:
                - keyword
                - page
                - size
                - key
                - mode
              x-apifox-orders:
                - keyword
                - page
                - size
                - key
                - verifycode
                - mode
            example:
              keyword: 人民日报
              page: '1'
              size: '20'
              mode: 1
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
                        name:
                          type: string
                          description: 公众号名称
                        biz:
                          type: string
                          description: 公众号唯一ID
                        owner_name:
                          type: string
                          description: 主体名字
                        customer_type:
                          type: string
                          description: 账号类型
                        ghid:
                          type: string
                          description: 公众号原始ID
                        wxid:
                          type: string
                          description: 微信号
                        fans:
                          type: integer
                          description: 粉丝数
                        avg_top_read:
                          type: integer
                          description: 头条平均阅读
                        avg_top_zan:
                          type: integer
                          description: 头条平均点赞
                        avatar:
                          type: string
                          description: 头像
                        qrcode:
                          type: string
                          description: 头像二维码
                        week_articles:
                          type: integer
                          description: 每周发文数
                        lastest_publish:
                          type: integer
                          description: 最后发文时间
                      required:
                        - name
                        - biz
                        - owner_name
                        - customer_type
                        - ghid
                        - wxid
                        - fans
                        - avg_top_read
                        - avg_top_zan
                        - avatar
                        - qrcode
                        - week_articles
                        - lastest_publish
                      x-apifox-orders:
                        - name
                        - biz
                        - owner_name
                        - customer_type
                        - ghid
                        - wxid
                        - fans
                        - avg_top_read
                        - avg_top_zan
                        - avatar
                        - qrcode
                        - week_articles
                        - lastest_publish
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
                msg: 成功
                data:
                  - name: 人民日报
                    biz: MjM5MjAxNDM4MA==
                    owner_name: 人民日报社
                    customer_type: 媒体
                    ghid: gh_363b924965e9
                    wxid: rmrbwx
                    fans: 55732800
                    avg_top_read: 100001
                    avg_top_zan: 10234
                    avatar: >-
                      https://wx.qlogo.cn/mmhead/Q3auHgzwzM5Dlw4H8vWoicXPXccEVkWYgrmSiavKwjaTkYuqswgXicqhA/0
                    qrcode: https://open.weixin.qq.com/qr/code?username=rmrbwx
                    week_articles: 58
                    lastest_publish: 1722402183
                  - name: 人民日报文创
                    biz: MzU4NTg3ODAwNQ==
                    owner_name: 人民日报文化传媒有限公司
                    customer_type: 企业
                    ghid: gh_c261034aa18d
                    wxid: rmrbwcapp
                    fans: 28045
                    avg_top_read: 492
                    avg_top_zan: 11
                    avatar: >-
                      https://wx.qlogo.cn/mmhead/Q3auHgzwzM5SxbiaF0eNZkiaGfkLw5Q4IIbwLMD602ldkkJAlGw4bFwQ/0
                    qrcode: https://open.weixin.qq.com/qr/code?username=rmrbwcapp
                    week_articles: 4
                    lastest_publish: 1721988293
                  - name: 人民日报新媒体
                    biz: MzU1MDg0NzA2MQ==
                    owner_name: 人民日报社
                    customer_type: 媒体
                    ghid: gh_34f9b5db4076
                    wxid: gh_34f9b5db4076
                    fans: 0
                    avg_top_read: 0
                    avg_top_zan: 0
                    avatar: >-
                      https://dajiala.oss-cn-hangzhou.aliyuncs.com/mp_avatar/dajiala.jpg
                    qrcode: >-
                      https://open.weixin.qq.com/qr/code?username=gh_34f9b5db4076
                    week_articles: 0
                    lastest_publish: 0
                  - name: 人民日报理论
                    biz: MzA5NTMzMDgzMA==
                    owner_name: 人民日报社
                    customer_type: 媒体
                    ghid: gh_a78405814c21
                    wxid: rmrbllb
                    fans: 344204
                    avg_top_read: 2716
                    avg_top_zan: 23
                    avatar: >-
                      https://wx.qlogo.cn/mmhead/Q3auHgzwzM7YQRnn54MJNgTJLqv4SibuOQyYIiaKFwMp0Y8iaKLbSIt8Q/0
                    qrcode: https://open.weixin.qq.com/qr/code?username=rmrbllb
                    week_articles: 13
                    lastest_publish: 1722333791
                  - name: 人民日报评论
                    biz: MzA4OTIyMjUyOQ==
                    owner_name: 人民日报社
                    customer_type: 媒体
                    ghid: gh_4a4914660bcd
                    wxid: rmrbpl
                    fans: 8066088
                    avg_top_read: 39454
                    avg_top_zan: 317
                    avatar: >-
                      https://wx.qlogo.cn/mmhead/Q3auHgzwzM5f5VHK824nX8LX0GD51hRoszPG4Td4gibBJhPthiceOMqQ/0
                    qrcode: https://open.weixin.qq.com/qr/code?username=rmrbpl
                    week_articles: 34
                    lastest_publish: 1722388334
                  - name: 人民日报图书馆
                    biz: MzUyNTMxODQxMA==
                    owner_name: 人民日报社
                    customer_type: 媒体
                    ghid: gh_f974081c64b2
                    wxid: gh_f974081c64b2
                    fans: 27390
                    avg_top_read: 1120
                    avg_top_zan: 14
                    avatar: >-
                      https://wx.qlogo.cn/mmhead/Q3auHgzwzM6kx4ibD1Xe2PrTYaUHUeYJPnqT6udj8n1c0X4XUyLiaZvw/0
                    qrcode: >-
                      https://open.weixin.qq.com/qr/code?username=gh_f974081c64b2
                    week_articles: 0
                    lastest_publish: 1719296279
                  - name: 人民日报数字江苏
                    biz: MzU4NjgwMzY2Ng==
                    owner_name: 人民日报数字传播(江苏)有限公司
                    customer_type: 企业
                    ghid: gh_ea0488052b09
                    wxid: ''
                    fans: 0
                    avg_top_read: 0
                    avg_top_zan: 0
                    avatar: >-
                      https://dajiala.oss-cn-hangzhou.aliyuncs.com/mp_avatar/5b7a61655087df8715a3e7ae6b1bfa62.jpg
                    qrcode: >-
                      https://open.weixin.qq.com/qr/code?username=gh_ea0488052b09
                    week_articles: 0
                    lastest_publish: 1588262400
                  - name: 人民日报行天下
                    biz: MzUzNTc5MDQxMw==
                    owner_name: 人民日报社
                    customer_type: 媒体
                    ghid: gh_6da5077ecb63
                    wxid: rmrbxtx
                    fans: 18261
                    avg_top_read: 494
                    avg_top_zan: 13
                    avatar: >-
                      https://mmbiz.qpic.cn/mmbiz_png/fJNicpu9tRiadjgFthRKHGb3E3a3IRicz20odCKia9st4Oib1lKtibAan8rK7sWhJ1zdus47fdlqxALNqG9v1TF6tf6A/0?wx_fmt=png
                    qrcode: https://open.weixin.qq.com/qr/code?username=rmrbxtx
                    week_articles: 1
                    lastest_publish: 1617893494
                  - name: 人民日报国际
                    biz: MzA5NDM1ODExOA==
                    owner_name: 人民日报社
                    customer_type: 媒体
                    ghid: gh_f342ffd5077b
                    wxid: rmrbgjbd
                    fans: 592112
                    avg_top_read: 1870
                    avg_top_zan: 30
                    avatar: >-
                      https://wx.qlogo.cn/mmhead/Q3auHgzwzM4GcMg33rhFc6My47zS71QvHea0Y4XdbykJhtZEKVQwuw/0
                    qrcode: https://open.weixin.qq.com/qr/code?username=rmrbgjbd
                    week_articles: 15
                    lastest_publish: 1722198600
                  - name: 人民日报政文
                    biz: MzAwMzAzNzQyOQ==
                    owner_name: 人民日报社
                    customer_type: 媒体
                    ghid: gh_4d468d70b180
                    wxid: rmrbzhw
                    fans: 399440
                    avg_top_read: 1849
                    avg_top_zan: 11
                    avatar: >-
                      https://wx.qlogo.cn/mmhead/Q3auHgzwzM7PVU0QbgA572z3DdCw8eeicNDok09kylP5cu4BgibXPk6Q/0
                    qrcode: https://open.weixin.qq.com/qr/code?username=rmrbzhw
                    week_articles: 15
                    lastest_publish: 1722332174
                  - name: 人民日报文艺
                    biz: MjM5OTM4OTIzOQ==
                    owner_name: 人民日报社
                    customer_type: 媒体
                    ghid: gh_f1f8332def6a
                    wxid: rmrbwy
                    fans: 264388
                    avg_top_read: 923
                    avg_top_zan: 13
                    avatar: >-
                      https://wx.qlogo.cn/mmhead/Q3auHgzwzM6JV3pPKap2qSXDSHax5E7bjepNkRCQaqOvqwWzMf6ichw/0
                    qrcode: https://open.weixin.qq.com/qr/code?username=rmrbwy
                    week_articles: 21
                    lastest_publish: 1722249597
                  - name: 人民日报数字传播
                    biz: MzU3MTc0MDM0NQ==
                    owner_name: 人民日报数字传播有限公司
                    customer_type: 媒体
                    ghid: gh_37ad338c91a7
                    wxid: peopledigital
                    fans: 210160
                    avg_top_read: 299
                    avg_top_zan: 4
                    avatar: >-
                      https://wx.qlogo.cn/mmhead/Q3auHgzwzM6KySwhWArYvbvSDUqvmz3RdhKicl50mO3T4ibjk9iarpOHA/0
                    qrcode: https://open.weixin.qq.com/qr/code?username=peopledigital
                    week_articles: 15
                    lastest_publish: 1722333055
                  - name: 人民日报媒体技术
                    biz: MzA4NDAyMzE3Nw==
                    owner_name: 人民日报媒体技术股份有限公司
                    customer_type: 企业
                    ghid: gh_9d490741e350
                    wxid: wxpdmi
                    fans: 2278
                    avg_top_read: 217
                    avg_top_zan: 4
                    avatar: >-
                      https://wx.qlogo.cn/mmhead/Q3auHgzwzM67LvHicjkJGwfq8Uf1lj1qkUno86U8QHPic0fibFEvhurcA/0
                    qrcode: https://open.weixin.qq.com/qr/code?username=wxpdmi
                    week_articles: 1
                    lastest_publish: 1708326953
                  - name: 人民日报体育
                    biz: MzAwNDA1OTUzMA==
                    owner_name: 人民日报社
                    customer_type: 媒体
                    ghid: gh_26d1f476e6a2
                    wxid: rmrbty
                    fans: 32906
                    avg_top_read: 1180
                    avg_top_zan: 14
                    avatar: >-
                      https://wx.qlogo.cn/mmhead/Q3auHgzwzM7ogcAFy1WHu5YBP4g6iaUClCj1vLkhtV8GZmicacgY9QCw/0
                    qrcode: https://open.weixin.qq.com/qr/code?username=rmrbty
                    week_articles: 3
                    lastest_publish: 1722156446
                  - name: 人民日报文创陕西频道
                    biz: MzAwNzc3MTQ0Mw==
                    owner_name: 人民日报传媒广告有限公司陕西分公司
                    customer_type: 企业
                    ghid: gh_b034447f10d2
                    wxid: ''
                    fans: 495
                    avg_top_read: 91
                    avg_top_zan: 1
                    avatar: >-
                      https://wx.qlogo.cn/mmhead/Q3auHgzwzM7stdibuVXYm4ibvN4phx5pEIvIWYFSeZ3PuvRovC1wQXgQ/0
                    qrcode: >-
                      https://open.weixin.qq.com/qr/code?username=gh_b034447f10d2
                    week_articles: 6
                    lastest_publish: 1599645533
                  - name: 人民日报客户端
                    biz: MzUxNTAzOTM0Ng==
                    owner_name: 人民日报社
                    customer_type: 媒体
                    ghid: gh_9b4dd8694d89
                    wxid: ''
                    fans: 0
                    avg_top_read: 0
                    avg_top_zan: 0
                    avatar: >-
                      https://dajiala.oss-cn-hangzhou.aliyuncs.com/mp_avatar/dajiala.jpg
                    qrcode: >-
                      https://open.weixin.qq.com/qr/code?username=gh_9b4dd8694d89
                    week_articles: 0
                    lastest_publish: 0
                  - name: 人民日报全媒体平台
                    biz: MzAwMTMyNDM2NQ==
                    owner_name: 人民日报媒体技术股份有限公司
                    customer_type: 媒体
                    ghid: gh_c05d66327906
                    wxid: rmrbqmtpt
                    fans: 9013
                    avg_top_read: 620
                    avg_top_zan: 3
                    avatar: >-
                      https://wx.qlogo.cn/mmhead/Q3auHgzwzM732EHoAVrxugC6zHLAGGhdV1VHNwrWy1Iumc1BwpZevw/0
                    qrcode: https://open.weixin.qq.com/qr/code?username=rmrbqmtpt
                    week_articles: 20
                    lastest_publish: 1490263112
                  - name: 人民日报发行服务号
                    biz: MzA5NTI5NDkxMg==
                    owner_name: 人民日报社
                    customer_type: 媒体
                    ghid: gh_b6dc9b1d0bbd
                    wxid: rmrbfwh
                    fans: 36616
                    avg_top_read: 2672
                    avg_top_zan: 43
                    avatar: >-
                      https://wx.qlogo.cn/mmhead/Q3auHgzwzM5j7TyFygQo0ia4iajUhPYOVXFdAccibtia0OFb1ubYGxV3dQ/0
                    qrcode: https://open.weixin.qq.com/qr/code?username=rmrbfwh
                    week_articles: 1
                    lastest_publish: 1714031666
                  - name: 人民日报美术收藏副刊
                    biz: MzA4MzI0MzYyMQ==
                    owner_name: 人名日报社文艺部
                    customer_type: 媒体
                    ghid: gh_e21ba322af29
                    wxid: rmrbmssc
                    fans: 9137
                    avg_top_read: 115
                    avg_top_zan: 3
                    avatar: >-
                      https://wx.qlogo.cn/mmhead/Q3auHgzwzM5J0yeejlrUicUibtNkaEDeiaAjMTLTXzLcTDicibHfM0cWymw/0
                    qrcode: https://open.weixin.qq.com/qr/code?username=rmrbmssc
                    week_articles: 2
                    lastest_publish: 1722152485
                  - name: 人民日报传媒海南 - 已注销
                    biz: MzA5NDg5NTMzMg==
                    owner_name: 人民日报传媒广告有限公司海南分公司
                    customer_type: 企业
                    ghid: gh_a06077f325b0
                    wxid: close_3094895332
                    fans: 0
                    avg_top_read: 0
                    avg_top_zan: 0
                    avatar: >-
                      https://mmbiz.qpic.cn/mmbiz/a5icZrUmbV8p5jb6RZ8aYfjfS2AVle8URwBt8QIu6XbGewB9wiaWYWkPwq4R7pfdsFibuLkic16UcxDSNYtB8HnC1Q/0/0
                    qrcode: >-
                      https://open.weixin.qq.com/qr/code?username=close_3094895332
                    week_articles: '0'
                    lastest_publish: 1579508529
          headers: {}
          x-apifox-name: 成功
      security: []
      x-apifox-folder: 公众号账号搜索和账号基本信息
      x-apifox-status: released
      x-run-in-apifox: https://app.apifox.com/web/project/4919579/apis/api-199762047-run
components:
  schemas: {}
  securitySchemes: {}
servers:
  - url: https://www.dajiala.com
    description: 正式环境
security: []

```
