# 获取公众号头像、账号类型、公众号简介等基础信息

## OpenAPI Specification

```yaml
openapi: 3.0.1
info:
  title: ''
  description: ''
  version: 1.0.0
paths:
  /fbmain/monitor/v3/avatar_type:
    post:
      summary: 获取公众号头像、账号类型、公众号简介等基础信息
      deprecated: false
      description: >-
        **实时数据**

        |                 状态码                 |                       
        说明                         |

        |:-----------------------------------:|:-------------------------------------------------:|

        | {"message":"Internal Server Error"} |                  
        网络错误，请重试1~3次                    |

        |                  0                  |                       
        成功                         |

        |                 -1                  |            
        QPS超过上限，不得高于5次/秒，请5秒后再试！              |

        |                 104                 |                 
        短连接文章已被删除或文章被迁移                  |

        |                 106                 |              
        获取阅读点赞数频率过快，请暂停2秒后重试!               |

        |                 400                 |         短链接转化失败，建议先调用 短链接转长链接
        转化为长链接后继续调用         |

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

        | ['data']['name'] | 公众号名称 |

        | ['data']['biz'] |  公众号唯一标识 |

        | ['data']['type'] | 公众号类型 |

        | ['data']['avatar'] | 公众号头像 |

        | ['data']['desc'] |  公众号描述 |
      tags:
        - 公众号账号搜索和账号基本信息
      parameters: []
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                name:
                  type: string
                  description: 公众号名称 | 原始id | wxid (0.5元/次)
                key:
                  type: string
                  description: 极致了官网 key
                verifycode:
                  type: string
                  description: 附加码 (如设置了附加码verifycode，则此参数为必选，如未设置则为非必选)
              x-apifox-orders:
                - name
                - key
                - verifycode
              required:
                - name
                - key
            example:
              name: rmrbwx
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
                      name:
                        type: string
                        description: 公众号名称
                      biz:
                        type: string
                        description: ' 公众号唯一标识'
                      wxid:
                        type: string
                      type:
                        type: string
                        description: 公众号类型
                      avatar:
                        type: string
                        description: 公众号头像
                      desc:
                        type: string
                        description: ' 公众号描述'
                    required:
                      - name
                      - biz
                      - wxid
                      - type
                      - avatar
                      - desc
                    x-apifox-orders:
                      - name
                      - biz
                      - wxid
                      - type
                      - avatar
                      - desc
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
                  name: 人民日报
                  biz: MjM5MjAxNDM4MA==
                  wxid: rmrbwx
                  type: 订阅号
                  avatar: >-
                    http://mmbiz.qpic.cn/mmbiz_png/xrFYciaHL08D1hiaVU0brP9YwQH1wFm9D9AG7oAVaNE8RzGiaKekViaIovvgsjOicfxXcPUPiahpdZ1U1nndyYd4pP0w/0?wx_fmt=png
                  desc: 参与、沟通、记录时代。
          headers: {}
          x-apifox-name: 成功
      security: []
      x-apifox-folder: 公众号账号搜索和账号基本信息
      x-apifox-status: released
      x-run-in-apifox: https://app.apifox.com/web/project/4919579/apis/api-199760628-run
components:
  schemas: {}
  securitySchemes: {}
servers:
  - url: https://www.dajiala.com
    description: 正式环境
security: []

```
