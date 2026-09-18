# 获取文章正文 HTML

## OpenAPI Specification

```yaml
openapi: 3.0.1
info:
  title: ''
  description: ''
  version: 1.0.0
paths:
  /fbmain/monitor/v3/article_html:
    post:
      summary: 获取文章正文 HTML
      deprecated: false
      description: |-
        |                 状态码                 |          说明          |
        |:-----------------------------------:|:--------------------:|
        | {"message":"Internal Server Error"} |     网络错误，请重试1~3次     |
        |                  0                  |          成功          |
        |              101        |     文章被删除或违规或公众号已迁移    |
        |             105,106        |          文章解析失败           |
        |             107        |          解析失败，请重试          |

        qps=5


        ### 返回结果
        | 字段 | 说明 |
        | --- | --- |
        | ['code'] | 状态码 |
        | ['msk'] | 消息 |
        | ['cost_money'] | 扣除金额 |
        | ['remain_money'] | 剩余金额 |
        | ['data'] | 返回数据 |
        | ['data']['title'] | 标题 |
        | ['data']['biz'] | biz |
        | ['data']['article_url'] | 文章链接 |
        | ['data']['mp_head_img'] | 公众号头像链接 |
        | ['data']['cover_url'] | 文章封面链接 |
        | ['data']['nickname'] | 昵称 |
        | ['data']['post_time'] | 发文时间 时间戳 |
        | ['data']['post_time_str'] | 发文时间 字符串格式 |
        | ['data']['gh_id'] | 原始ID |
        | ['data']['wxid'] | 微信ID |
        | ['data']['signature'] | 公众号简介 |
        | ['data']['author'] | 作者 |
        | ['data']['desc'] | 简介|
        | ['data']['copyright'] | 是否原创 |
        | ['data']['html'] | 文章正文 |
        | ['data']['ip_wording'] | ip属地 |
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
                  description: 微信文章链接 （0.04/次）
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
                - verifycode
            example:
              url: >-
                https://mp.weixin.qq.com/s?__biz=MjM5MjAxNDM4MA==&mid=2666900240&idx=1&sn=a130a51c16cbe0169dd776a470e63bba&chksm=bc1219084e2f51c60f29a7a5d8c25e6ed32554270bf36dbb032fdc6d39d05d2c24742d3367d2#rd
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
                  msk:
                    type: string
                    description: 消息
                  cost_money:
                    type: number
                    description: 扣除金额
                  remain_money:
                    type: number
                    description: 剩余金额
                  data:
                    type: object
                    properties:
                      title:
                        type: string
                        description: 标题
                      biz:
                        type: string
                        description: biz
                      article_url:
                        type: string
                        description: 文章链接
                      mp_head_img:
                        type: string
                        description: 公众号头像链接
                      cover_url:
                        type: string
                        description: 文章封面链接
                      nickname:
                        type: string
                        description: 昵称
                      post_time:
                        type: integer
                        description: 发文时间 时间戳
                      post_time_str:
                        type: string
                        description: 发文时间 字符串格式
                      gh_id:
                        type: string
                        description: 原始ID
                      wxid:
                        type: string
                        description: 微信ID
                      source_url:
                        type: string
                      signature:
                        type: string
                        description: 公众号简介
                      author:
                        type: string
                        description: 作者
                      desc:
                        type: string
                        description: 简介
                      copyright:
                        type: integer
                        description: 是否原创
                      html:
                        type: string
                        description: 文章正文
                      ip_wording:
                        type: string
                        description: ip属地
                    required:
                      - title
                      - biz
                      - article_url
                      - mp_head_img
                      - cover_url
                      - nickname
                      - post_time
                      - post_time_str
                      - gh_id
                      - wxid
                      - source_url
                      - signature
                      - author
                      - desc
                      - copyright
                      - html
                      - ip_wording
                    x-apifox-orders:
                      - title
                      - ip_wording
                      - biz
                      - article_url
                      - mp_head_img
                      - cover_url
                      - nickname
                      - post_time
                      - post_time_str
                      - gh_id
                      - wxid
                      - source_url
                      - signature
                      - author
                      - desc
                      - copyright
                      - html
                    description: 返回数据
                required:
                  - code
                  - msk
                  - cost_money
                  - remain_money
                  - data
                x-apifox-orders:
                  - code
                  - msk
                  - cost_money
                  - remain_money
                  - data
              examples:
                '1':
                  summary: 成功示例
                  value:
                    code: 0
                    msk: OK
                    cost_money: 0.02
                    remain_money: 999999.502
                    data:
                      title: 习近平：努力建设强大稳固的现代边海空防
                      biz: MjM5MjAxNDM4MA==
                      article_url: >-
                        http://mp.weixin.qq.com/s?__biz=MjM5MjAxNDM4MA==&amp;mid=2666855529&amp;idx=1&amp;sn=c37fd64d5aa29f4c8870427b49dc607b&amp;chksm=bdac952a8adb1c3ce35011d36e5de0ce85b90ad216ec5092f51ed9bae8d12012e99ff236c80b#rd
                      mp_head_img: >-
                        http://mmbiz.qpic.cn/mmbiz_png/xrFYciaHL08D1hiaVU0brP9YwQH1wFm9D9AG7oAVaNE8RzGiaKekViaIovvgsjOicfxXcPUPiahpdZ1U1nndyYd4pP0w/0?wx_fmt=png
                      cover_url: >-
                        https://mmbiz.qpic.cn/sz_mmbiz_jpg/xrFYciaHL08ABmrcAB7qN5uMLZN9uVfXViauP8uYZNmHL3xE95W4n6o6Vp6vpCMjcunBgibl3LsKDoU4bEg8svY9Q/0?wx_fmt=jpeg
                      nickname: 人民日报
                      post_time: 1722404576
                      post_time_str: 2024-07-31 13:42
                      gh_id: gh_363b924965e9
                      wxid: rmrbwx
                      source_url: https://www.peopleapp.com/
                      signature: 参与、沟通、记录时代。
                      author: ''
                      desc: ''
                      copyright: 0
                      html: "<!DOCTYPE html>\n        <html xmlns=\"http://www.w3.org/1999/xhtml\" class=\"view\" >\n\n        <head>\n            <meta name=\"referrer\" content=\"never\">\n            <meta charset=\"utf-8\">\n            <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n\n        <title>习近平：努力建设强大稳固的现代边海空防</title>\n        \n                    <style type=\"text/css\">\n        \timg{\n        \tdisplay:block;\n        \tmargin:0 auto !important;\n        \twidth:100%;\n        \t}\n        \tbody{\n        \t\twidth:75%;\n        \t\tmargin:0 auto !important;\n        \t}\n        </style>\n        </head>\n        <body>\n        <p><span style=\"color: rgb(0, 122, 170);\"><strong><span style=\"color: rgb(0, 122, 170);font-size: 18px;\">习近平在中共中央政治局第十六次集体学习时强调 强化使命担当 创新思路举措 狠抓工作落实 努力建设强大稳固的现代边海空防</span></strong></span></p><p><span style=\"font-size: 18px;\"><br  /></span></p><p><span style=\"font-size: 18px;\">　　中共中央政治局7月30日下午就推进现代边海空防建设进行第十六次集体学习。中共中央总书记习近平在主持学习时发表重要讲话强调，推进现代边海空防建设，是国防和军队现代化的内在要求，是以高水平安全保障高质量发展的应有之义，对以中国式现代化全面推进强国建设、民族复兴伟业具有重要意义。要坚持以新时代中国特色社会主义思想为指导，立足国家安全战略和军事战略全局，统筹国内国际两个大局，把握边海空防新情况新特点新要求，强化使命担当，创新思路举措，狠抓工作落实，努力建设强大稳固的现代边海空防。</span></p><p><br  /></p><p><span style=\"font-size: 18px;\">　　这次中央政治局集体学习在八一建军节前夕举行。习近平代表党中央和中央军委，向全体人民解放军指战员、武警部队官兵、军队文职人员、民兵预备役人员致以节日的祝贺！</span></p><p><br  /></p><p><span style=\"font-size: 18px;\">　　中央军委联合参谋部黄继忠同志就推进现代边海空防建设问题进行讲解，提出工作建议。中央政治局的同志认真听取了讲解，并进行了讨论。</span></p><p><br  /></p><p><span style=\"font-size: 18px;\">　　习近平在听取讲解和讨论后发表了重要讲话。他指出，边海空防是国家主权的重要标志、国家安全的重要门户、国家发展的重要保障，我们党历来高度重视。党的十八大以来，党中央坚持把边海空防建设摆在治国理政重要位置，加强党政军警民合力强边固防，领导实施边海空防领导管理体制、力量结构、政策制度等一系列重大改革，指挥开展边海空防一系列重大行动，有力捍卫了我国领土主权和海洋权益，维护了国家安全和发展战略主动。我国边海空防建设取得历史性成就，站在了新的起点上。</span></p><p><br  /></p><p><span style=\"font-size: 18px;\">　　习近平强调，当前，世界百年变局加速演进，我国边海空防内涵和外延发生深刻变化，影响因素更加错综复杂，边海空防建设面临新的机遇和挑战。要坚持系统观念，强化全局统筹，提高卫国戍边整体能力。要协调推进边海空防建设和沿边沿海地区经济社会发展，加强基础设施互联互通和共建共用，打造既能有效维护安全又能有力支撑发展的边海空防建设格局。要强化科技赋能，加强边海空防新型手段和条件建设，构建边海空防立体智能管控体系。要增进同有关国家睦邻友好和务实合作，为边海空防建设营造良好周边环境。</span></p><p><br  /></p><p><span style=\"font-size: 18px;\">　　习近平指出，要认真贯彻党的二十届三中全会精神，深化边海空防重大问题研究，巩固提升已有改革成果，抓好既定改革任务落实，加强后续改革筹划，推动边海空防建设创新发展。要坚持边运行、边改革、边完善，优化边海防领导管理体制，完善跨军地协调机制，加强相关法制建设，确保边海防各项工作规范有序、顺畅高效。要做好国家空中交通管理工作，促进低空经济健康发展。要优化人民防空建设模式，构建现代人民防空体系。</span></p><p><br  /></p><p><span style=\"font-size: 18px;\">　　习近平强调，边海空防涉及军地多个部门、多个层级，要加强党中央集中统一领导，发挥党政军警民合力强边固防优势，加强边海空防建设军地规划衔接、任务对接、资源统筹，加强军警民联防指挥和行动协同，形成一盘棋，拧成一股绳。军队要积极主动同地方搞好沟通协调，中央和国家机关有关部门、地方党委和政府要强化国防意识，认真履职尽责，不折不扣落实好建设和巩固国防的各项任务。</span></p><p><br  /></p><hr style=\"border-style: solid;border-width: 1px 0 0;border-color: rgba(0,0,0,0.1);-webkit-transform-origin: 0 0;-webkit-transform: scale(1, 0.5);transform-origin: 0 0;transform: scale(1, 0.5);\"  /><section style=\"margin-bottom: 0px;outline: 0px;font-family: &quot;PingFang SC&quot;, system-ui, -apple-system, BlinkMacSystemFont, &quot;Helvetica Neue&quot;, &quot;Hiragino Sans GB&quot;, &quot;Microsoft YaHei UI&quot;, &quot;Microsoft YaHei&quot;, Arial, sans-serif;letter-spacing: 0.544px;text-wrap: wrap;background-color: rgb(255, 255, 255);\"><span style=\"outline: 0px;font-size: 16px;\">来源：新华社</span></section><section style=\"margin-bottom: 0px;outline: 0px;font-family: &quot;PingFang SC&quot;, system-ui, -apple-system, BlinkMacSystemFont, &quot;Helvetica Neue&quot;, &quot;Hiragino Sans GB&quot;, &quot;Microsoft YaHei UI&quot;, &quot;Microsoft YaHei&quot;, Arial, sans-serif;letter-spacing: 0.544px;text-wrap: wrap;background-color: rgb(255, 255, 255);\"><span style=\"outline: 0px;font-size: 16px;\">本期编辑：石磊、林帆</span></section><p style=\"margin-bottom: 0px;outline: 0px;letter-spacing: 0.544px;text-wrap: wrap;font-family: -apple-system-font, system-ui, &quot;Helvetica Neue&quot;, &quot;PingFang SC&quot;, &quot;Hiragino Sans GB&quot;, &quot;Microsoft YaHei UI&quot;, &quot;Microsoft YaHei&quot;, Arial, sans-serif;background-color: rgb(255, 255, 255);\"><img class=\"__bg_gif rich_pages wxw-img\" data-backh=\"170\" data-backw=\"578\" data-before-oversubscription-url=\"https://mmbiz.qpic.cn/mmbiz/xrFYciaHL08BMq1Er5otH3veEWm0Gm4EcXDCzQM0GqPIQicibBUEVGskz2ElAmhtSqbPxvdIEWBslRSvlficibUDVeg/640?\" data-imgfileid=\"519371876\" data-ratio=\"0.29444444444444445\" src=\"https://mmbiz.qpic.cn/mmbiz/xrFYciaHL08BMq1Er5otH3veEWm0Gm4EcXDCzQM0GqPIQicibBUEVGskz2ElAmhtSqbPxvdIEWBslRSvlficibUDVeg/640?wx_fmt=gif&amp;tp=webp&amp;wxfrom=5&amp;wx_lazy=1\" data-type=\"gif\" width=\"300px\" style=\"outline: 0px;letter-spacing: 0.5525px;width: 677px !important;visibility: visible !important;\" width=\"auto\"  /><br style=\"outline: 0px;\"  /></p><p style=\"margin-bottom: 0px;outline: 0px;text-wrap: wrap;font-family: -apple-system-font, system-ui, &quot;Helvetica Neue&quot;, &quot;PingFang SC&quot;, &quot;Hiragino Sans GB&quot;, &quot;Microsoft YaHei UI&quot;, &quot;Microsoft YaHei&quot;, Arial, sans-serif;background-color: rgb(255, 255, 255);letter-spacing: 0.5525px;text-align: right;\"><strong style=\"outline: 0px;letter-spacing: 0.54px;font-family: 微软雅黑;line-height: 25.6px;\"><span style=\"outline: 0px;background-image: none;background-size: auto;bottom: auto;clear: none;color: rgb(255, 255, 255);height: auto;left: auto;max-height: none;min-height: 0px;min-width: 0px;top: auto;visibility: visible;z-index: auto;\"><strong style=\"outline: 0px;letter-spacing: 0.54px;line-height: 25.6px;\"></strong><strong style=\"outline: 0px;letter-spacing: 0.54px;font-size: 18px;line-height: 25.6px;\"><span style=\"outline: 0px;background-color: rgb(234, 6, 13);background-image: none;background-size: auto;bottom: auto;clear: none;font-size: 20px;height: auto;left: auto;max-height: none;min-height: 0px;min-width: 0px;top: auto;visibility: visible;z-index: auto;\">觉得好看，请点这里<strong style=\"outline: 0px;background-color: rgb(255, 255, 255);font-size: 18px;letter-spacing: 0.54px;line-height: 25.6px;\"><span style=\"outline: 0px;background-color: rgb(234, 6, 13);background-image: none;background-size: auto;bottom: auto;clear: none;height: auto;left: auto;max-height: none;min-height: 0px;min-width: 0px;top: auto;visibility: visible;z-index: auto;\">↓<strong style=\"outline: 0px;letter-spacing: 0.54px;line-height: 25.6px;\"><span style=\"outline: 0px;background-image: none;background-size: auto;bottom: auto;clear: none;height: auto;left: auto;max-height: none;min-height: 0px;min-width: 0px;top: auto;visibility: visible;z-index: auto;\"><strong style=\"outline: 0px;letter-spacing: 0.54px;line-height: 25.6px;\"><span style=\"outline: 0px;background-image: none;background-size: auto;bottom: auto;clear: none;font-size: 20px;height: auto;left: auto;max-height: none;min-height: 0px;min-width: 0px;top: auto;visibility: visible;z-index: auto;\"><strong style=\"outline: 0px;background-color: rgb(255, 255, 255);font-size: 18px;letter-spacing: 0.54px;line-height: 25.6px;\"><span style=\"outline: 0px;background-color: rgb(234, 6, 13);background-image: none;background-size: auto;bottom: auto;clear: none;height: auto;left: auto;max-height: none;min-height: 0px;min-width: 0px;top: auto;visibility: visible;z-index: auto;\">↓</span></strong></span></strong></span></strong></span></strong><strong style=\"outline: 0px;background-color: rgb(255, 255, 255);font-size: 18px;letter-spacing: 0.54px;line-height: 25.6px;\"><span style=\"outline: 0px;background-color: rgb(234, 6, 13);background-image: none;background-size: auto;bottom: auto;clear: none;height: auto;left: auto;max-height: none;min-height: 0px;min-width: 0px;top: auto;visibility: visible;z-index: auto;\">↓</span></strong></span></strong></span></strong></p><p style=\"display: none;\"><mp-style-type data-value=\"10000\"></mp-style-type></p>\n                </body>\n                </html>\n        "
                '2':
                  summary: 成功示例
                  value:
                    code: 101
                    msg: 文章打不开，原因为：该内容已被发布者删除
                    content_text: ''
                    cost_money: 0.04
                    remain_money: 4256.675
                '3':
                  summary: 成功示例
                  value:
                    code: 101
                    msg: 文章打不开，原因为：此账号已被屏蔽, 内容无法查看
                    content_text: ''
                    cost_money: 0.04
                    remain_money: 31419.534
                '4':
                  summary: 临时链接失效
                  value:
                    code: 101
                    msg: 文章打不开，原因为：临时链接已失效
                    content_text: ''
                    cost_money: 0.04
                    remain_money: 17255.424
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
                  cost_money:
                    type: number
                  remain_money:
                    type: number
                required:
                  - code
                  - msg
                  - content_text
                  - cost_money
                  - remain_money
                x-apifox-orders:
                  - code
                  - msg
                  - content_text
                  - cost_money
                  - remain_money
          headers: {}
          x-apifox-name: 文章被删除
        x-200:公众号封号:
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
                  cost_money:
                    type: number
                  remain_money:
                    type: number
                required:
                  - code
                  - msg
                  - content_text
                  - cost_money
                  - remain_money
                x-apifox-orders:
                  - code
                  - msg
                  - content_text
                  - cost_money
                  - remain_money
          headers: {}
          x-apifox-name: 公众号封号
        x-200:临时链接失效:
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
                  cost_money:
                    type: number
                  remain_money:
                    type: number
                required:
                  - code
                  - msg
                  - content_text
                  - cost_money
                  - remain_money
                x-apifox-orders:
                  - code
                  - msg
                  - content_text
                  - cost_money
                  - remain_money
              example:
                code: 101
                msg: 文章打不开，原因为：临时链接已失效
                content_text: ''
                cost_money: 0.04
                remain_money: 17255.424
          headers: {}
          x-apifox-name: 临时链接失效
      security: []
      x-apifox-folder: 公众号文章内容和互动数据等
      x-apifox-status: released
      x-run-in-apifox: https://app.apifox.com/web/project/4919579/apis/api-199736592-run
components:
  schemas: {}
  securitySchemes: {}
servers:
  - url: https://www.dajiala.com
    description: 正式环境
security: []

```
