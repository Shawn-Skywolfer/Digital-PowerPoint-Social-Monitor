# 获取api余额

## OpenAPI Specification

```yaml
openapi: 3.0.1
info:
  title: ''
  description: ''
  version: 1.0.0
paths:
  /fbmain/monitor/v3/get_remain_money:
    post:
      summary: 获取api余额
      deprecated: false
      description: |-
        | 字段 | 说明 |
        | --- | --- |
        code = 0  |调用成功


        ### 返回结果
        | 字段 | 说明 |
        | --- | --- |
        | ['code'] | 状态码 |
        | ['remain_money'] | 当前余额 |
        | ['yesterday_money'] | 昨日余额 |
        | ['request_time'] | 请求时间 |
      tags: []
      parameters: []
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                key:
                  type: string
                  description: key
                verifycode:
                  type: string
                  description: 如果设置了需要填写
              required:
                - key
                - verifycode
              x-apifox-orders:
                - key
                - verifycode
            example:
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
                    type: string
                    description: 状态码
                  remain_money:
                    type: string
                    description: 当前余额
                  yesterday_money:
                    type: string
                    description: 昨日余额
                  request_time:
                    type: string
                    description: 请求时间
                x-apifox-orders:
                  - code
                  - remain_money
                  - yesterday_money
                  - request_time
                required:
                  - code
                  - remain_money
                  - yesterday_money
                  - request_time
              example:
                code: 0
                remain_money: 41177.785
                yesterday_money: 41449.426
                request_time: '2025-07-12 19:13:57'
          headers: {}
          x-apifox-name: 成功
      security: []
      x-apifox-folder: ''
      x-apifox-status: released
      x-run-in-apifox: https://app.apifox.com/web/project/4919579/apis/api-247333202-run
components:
  schemas: {}
  securitySchemes: {}
servers:
  - url: https://www.dajiala.com
    description: 正式环境
security: []

```
