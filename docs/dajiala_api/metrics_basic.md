# 获取文章阅读、点赞、在看 

## OpenAPI Specification

```yaml
openapi: 3.0.1
info:
  title: ''
  description: ''
  version: 1.0.0
paths:
  /fbmain/monitor/v3/read_zan:
    post:
      summary: '获取文章阅读、点赞、在看 '
      deprecated: false
      description: >-
        **获取实时阅读点赞数据**

        |                 状态码                 |                       
        说明                         |

        |:-----------------------------------:|:-------------------------------------------------:|

        | {"message":"Internal Server Error"} |                  
        网络错误，请重试1~3次                    |

        |                  0                  |                       
        成功                         |

        |                 -1                  |            
        QPS超过上限，不得高于5次/秒，请5秒后再试！              |

        |              101        |     文章被删除或违规或公众号已迁移    |

        |             105,106        |          文章解析失败           |

        |             107        |          解析失败，请重试          |

        |                10002                |                   
        key或附加码不正确                     |

        |                20001                |                    
        金额不足，请充值                      |

        |                20002                |                   
        请输入正确的微信链接                     |

        |                20003                | 文章链接有误，请检查文章链接url中的&是否已经编码为%26  
        \|50000\|内部服务器错误 |


        ### 返回结果

        | 字段 | 说明 |

        | --- | --- |

        | ['data']['read'] | 阅读 |

        | ['data']['zan'] | 点赞 |

        | ['data']['looking'] | 在看 |

        | ['cost_money'] | 消费金额 |

        | ['remain_money'] | 所剩金额 |
      tags:
        - 公众号文章内容和互动数据等
        - 文章
      parameters:
        - name: Content-Type
          in: header
          description: ''
          required: false
          example: application/json
          schema:
            type: string
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                url:
                  type: string
                  description: 微信文章链接（0.04/次）
                key:
                  type: string
                  description: 极致了官网 key. 注意使用key  请直接填入，不要带{{}} , 双括号是 apifox里面设置的全局变量
                verifycode:
                  type: string
                  description: 附加码，如设置了附加码verifycode，则此参数为必选，如未设置则为非必选
              x-apifox-orders:
                - url
                - key
                - verifycode
              required:
                - url
                - key
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
                    description: 状态码
                  msg:
                    type: string
                    description: 消息
                  data:
                    type: object
                    properties:
                      read:
                        type: integer
                        description: 阅读
                      zan:
                        type: integer
                        description: 点赞
                      looking:
                        type: integer
                        description: 在看
                    required:
                      - read
                      - zan
                      - looking
                    x-apifox-orders:
                      - read
                      - zan
                      - looking
                  cost_money:
                    type: number
                    description: 消费金额
                  remain_money:
                    type: number
                    description: 所剩金额
                required:
                  - code
                  - msg
                  - data
                  - cost_money
                  - remain_money
                x-apifox-orders:
                  - code
                  - msg
                  - data
                  - cost_money
                  - remain_money
              examples:
                '1':
                  summary: 成功示例
                  value:
                    code: 0
                    msg: success
                    data:
                      read: 100001
                      zan: 1988
                      looking: 612
                    cost_money: 0.02
                    remain_money: 999999.372
                '2':
                  summary: 成功示例
                  value:
                    code: 101
                    msg: 文章打不开，原因为：该内容已被发布者删除
                    content_text: ''
                    cost: 0.04
                    data: ''
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
                  content_text:
                    type: string
                  cost:
                    type: number
                  data:
                    type: string
                required:
                  - code
                  - msg
                  - content_text
                  - cost
                  - data
                x-apifox-orders:
                  - code
                  - msg
                  - content_text
                  - cost
                  - data
          headers: {}
          x-apifox-name: 文章被删除
      security: []
      x-apifox-folder: 公众号文章内容和互动数据等
      x-apifox-status: released
      x-run-in-apifox: https://app.apifox.com/web/project/4919579/apis/api-199750063-run
components:
  schemas: {}
  securitySchemes: {}
servers:
  - url: https://www.dajiala.com
    description: 正式环境
security: []

```
