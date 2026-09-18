# 获取文章详情(纯文本,富文本,不带html文章格式)

## OpenAPI Specification

```yaml
openapi: 3.0.1
info:
  title: ''
  description: ''
  version: 1.0.0
paths:
  /fbmain/monitor/v3/article_detail:
    get:
      summary: 获取文章详情(纯文本,富文本,不带html文章格式)
      deprecated: false
      description: |-
        ## **关于图片显示
        ## 此图片来自微信公众平台
        ## 未经允许不可引用**

        解决办法：

        ```
        <head></head> 里面加上  一句

        <meta name="referrer" content="never">

        ```



        就可以正常显示了


        |                 状态码                 |          说明          |
        |:-----------------------------------:|:--------------------:|
        | {"message":"Internal Server Error"} |     网络错误，请重试1~3次     |
        |             0             |          成功          |
        |              101        |     文章被删除或违规或公众号已迁移    |
        |             105,106        |          文章解析失败           |
        |             107        |          解析失败，请重试          |

        qps=5


        ### 返回结果
        | 字段 | 说明 |
        | --- | --- |
        | ['code'] | 状态码 |
        | ['cost_money'] | 消费金额 |
        | ['remain_money'] | 所剩金额 |
        | ['type'] | 9 群发的有通知  10002 发布无通知 |
        | ['service_type'] | 0 公众号（原订阅号）  1 服务号 |
        | ['content'] | 纯文本格式正文 |
        | ['content_multi_text'] | 适用于富文本编辑器的html格式 |
        | ['title'] | 文章标题 |
        | ['url'] | 文章长链接 |
        | ['hashid'] | 文章唯一id |
        | ['mp_head_img'] | 公众号头像 |
        | ['picture_page_info_list'] | 文章中图片列表 |
        | ['cdn_url_1_1'] | 1:1的封面图 |
        | ['nick_name'] | 公众号名字 |
        | ['user_name'] | 公众号原始id |
        | ['idx'] | 文章位置，8篇里面第几篇 |
        | ['msg_daily_idx'] | 比如人民日报一天可以发10次，这是第几次发送 |
        | ['pubtime'] | 发文时间 |
        | ['create_time'] | 文章创建（定时）时间 |
        | ['biz'] | 公众号biz 唯一id 获取历史列表需要这个参数 |
        | ['alias'] | 公众号wxid |
        | ['source_url'] | 文章原文链接 （如果没有则为空） |
        | ['signature'] | 公众号简介 |
        | ['author'] | 文章作者 |
        | ['desc'] | 文章摘要 |
        | ['copyright_stat'] | 是否原创 （1 原创 0非原创 2转载） |
        | ['ip_wording'] | ip地址|
        | ['item_show_type'] | 0:图文 5:纯视频 7:纯音乐 8:纯图片 10:纯文字 11:转载文章 |
        | ['real_item_show_type'] | 0:图文 5:纯视频 7:纯音乐 8:纯图片 10:纯文字 11:转载文章 |
        | ['video_page_infos'] | 文章中的视频列表 |
      tags:
        - 公众号文章内容和互动数据等
        - 文章
      parameters:
        - name: url
          in: query
          description: 任意微信文章链接 （ 0.03/次）
          required: false
          example: https://mp.weixin.qq.com/s/NrR7SnT8DUwufP88uUESjg
          schema:
            type: string
        - name: key
          in: query
          description: 极致了官网 key. 注意使用key  请直接填入，不要带{{}} , 双括号是 apifox里面设置的全局变量
          required: false
          example: '{{key}}'
          schema:
            type: string
        - name: mode
          in: query
          description: '1.带图片标签纯文本    2.纯文字+富文本格式 '
          required: false
          example: '2'
          schema:
            type: string
        - name: verifycode
          in: query
          description: 附加码 (如设置了附加码verifycode，则此参数为必选，如未设置则为非必选)
          required: false
          schema:
            type: string
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
                  cost_money:
                    type: number
                    description: 消费金额
                  remain_money:
                    type: number
                    description: 所剩金额
                  title:
                    type: string
                    description: 文章标题
                  mp_head_img:
                    type: string
                    description: 公众号头像
                  source_url:
                    type: string
                    description: 文章原文链接 （如果没有则为空）
                  signature:
                    type: string
                    description: 公众号简介
                  author:
                    type: string
                    description: 文章作者
                  desc:
                    type: string
                    description: 文章摘要
                  content:
                    type: string
                    description: 纯文本格式正文
                  url:
                    type: string
                    description: 文章长链接
                  hashid:
                    type: string
                    description: 文章唯一id
                  pubtime:
                    type: string
                    description: 发文时间
                  biz:
                    type: string
                    description: 公众号biz
                  create_time:
                    type: string
                    description: 文章创建（定时）时间
                  msg_daily_idx:
                    type: string
                    description: 比如人民日报一天可以发10次，这是第几次发送
                  ip_wording:
                    type: string
                    description: ip地址
                  content_multi_text:
                    type: string
                    description: 适用于富文本编辑器的html格式
                  cdn_url_1_1:
                    type: string
                    description: 1:1的封面图
                  nick_name:
                    type: string
                    description: 公众号名字
                  user_name:
                    type: string
                    description: 公众号原始id
                  idx:
                    type: string
                    description: 文章位置，8篇里面第几篇
                  alias:
                    type: string
                    description: 公众号wxid
                  copyright_stat:
                    type: integer
                    description: 是否原创 （1 原创 0非原创 2转载）
                  picture_page_info_list:
                    type: array
                    items:
                      type: object
                      properties: {}
                      x-apifox-orders: []
                    description: 文章中图片列表
                  video_page_infos:
                    type: array
                    items:
                      type: object
                      properties: {}
                      x-apifox-orders: []
                    description: 文章中的视频列表
                  type:
                    type: string
                    description: 9 群发的有通知  10002 发布无通知
                  item_show_type:
                    type: integer
                    description: 0:图文 5:纯视频 7:纯音乐 8:纯图片 10:纯文字 11:转载文章
                  real_item_show_type:
                    type: integer
                    description: 0:图文 5:纯视频 7:纯音乐 8:纯图片 10:纯文字 11:转载文章
                  verify_status:
                    type: string
                    description: 2 蓝V认证  3 红V认证  1个人认证  0  未认证
                  service_type:
                    type: string
                    description: 0 公众号 （原订阅号） 1服务号
                required:
                  - code
                  - cost_money
                  - remain_money
                  - title
                  - url
                  - mp_head_img
                  - nick_name
                  - pubtime
                  - biz
                  - user_name
                  - alias
                  - source_url
                  - signature
                  - author
                  - desc
                  - copyright_stat
                  - content
                  - hashid
                  - idx
                  - create_time
                  - msg_daily_idx
                  - ip_wording
                  - content_multi_text
                  - cdn_url_1_1
                  - picture_page_info_list
                  - video_page_infos
                  - type
                  - item_show_type
                  - real_item_show_type
                  - verify_status
                  - service_type
                x-apifox-orders:
                  - code
                  - cost_money
                  - remain_money
                  - type
                  - service_type
                  - content
                  - content_multi_text
                  - title
                  - url
                  - hashid
                  - mp_head_img
                  - picture_page_info_list
                  - cdn_url_1_1
                  - nick_name
                  - user_name
                  - idx
                  - verify_status
                  - msg_daily_idx
                  - pubtime
                  - create_time
                  - biz
                  - alias
                  - source_url
                  - signature
                  - author
                  - desc
                  - copyright_stat
                  - ip_wording
                  - item_show_type
                  - real_item_show_type
                  - video_page_infos
              examples:
                '1':
                  summary: 成功示例
                  value:
                    cost_money: 0.03
                    remain_money: 48811.319
                    code: 0
                    biz: MzkxNjY0NTcwNA==
                    mid: '2247641306'
                    idx: '7'
                    user_name: gh_211aba30114d
                    nick_name: 医疗器械创新网
                    type: 9
                    service_type: '0'
                    verify_status: '2'
                    create_time: '2025-04-13 17:19:59'
                    req_id: 1411M5EK5TKfKTrRYJECgqxJ
                    msg_daily_idx: '1'
                    round_head_img: >-
                      http://mmbiz.qpic.cn/mmbiz_png/3aNX9kq7JM0q7ARwzZxflDltYplFsibWndwMdZMXmiaaLq25ic8Wb50DsHcMOWVk8Qw4iadIKHGaT9NhayutHL9MXQ/0?wx_fmt=png
                    signature: >-
                      用创新，链接每一位医械人！ 
                      最新资讯、品牌宣传、设计代工、投融资、会议定制、创新大赛....一站式医械创新综合服务平台！
                    ori_head_img_url: >-
                      http://wx.qlogo.cn/mmhead/VLjDyM7pibyK9pO6CHs1MXrIhOqQPxtX9mULb3j4FONqLrZytRVGorwu0j38G1YCzJ9JwU8eX99c/132
                    title: 曾是大三甲院长，违法被查！
                    desc: ''
                    cdn_url: >-
                      https://mmbiz.qpic.cn/mmbiz_jpg/3aNX9kq7JM0Q4WEBOI5uhotZpsOmVsYBAZcMM6yvq4g9iaSWib7RHoAIEnwRPmiapsndLMqfJycYho7ZHU4MOduHw/0?wx_fmt=jpeg
                    cdn_url_1_1: >-
                      https://mmbiz.qpic.cn/mmbiz_jpg/3aNX9kq7JM0Q4WEBOI5uhotZpsOmVsYBAZcMM6yvq4g9iaSWib7RHoAIEnwRPmiapsndLMqfJycYho7ZHU4MOduHw/0?wx_fmt=jpeg
                    cdn_url_235_1: >-
                      https://mmbiz.qpic.cn/mmbiz_jpg/3aNX9kq7JM0Q4WEBOI5uhotZpsOmVsYBtVaORZ23CZNmxMV8YpFFcJ47XV2MdVtsZiaGzqjWIFeDfKw6978DoDg/0?wx_fmt=jpeg
                    copyright_stat: 0
                    author: ''
                    comment_id: '3941686548529381382'
                    countryName: 中国
                    provinceName: 江苏
                    show_ip_wording: '1'
                    source_url: ''
                    picture_page_info_list:
                      - cdn_url: >-
                          https://mmbiz.qpic.cn/mmbiz_png/3aNX9kq7JM1MrwiaaTAfJGOEKdox57lLibNfPnElJL0NVl55bibIGClkHcIAicEqEtvgmSTkPvZ9uX3Aupb81kXBmA/640?wx_fmt=png&from=appmsg
                        width: 1080
                        height: 459
                      - cdn_url: >-
                          https://mmbiz.qpic.cn/sz_mmbiz_jpg/8IaXn7e7IyYdnjaCconlqHThKAfJrmq38uCtFrH9moWpiceuUJh8mFNTfGRgBZg3icFibcHibL1TaEWPJtQ8udxwDA/640?wx_fmt=jpeg
                        width: 1080
                        height: 455
                      - cdn_url: >-
                          https://mmbiz.qpic.cn/sz_mmbiz_png/8IaXn7e7IyYdnjaCconlqHThKAfJrmq3alyYQlHpiaCoFPDLNRiae2wXYu2mqJvP84FcmF7BEjETnyynOu7VYwRQ/640?wx_fmt=png&from=appmsg
                        width: 259
                        height: 333
                      - cdn_url: >-
                          https://mmbiz.qpic.cn/sz_mmbiz_jpg/8IaXn7e7IyYdnjaCconlqHThKAfJrmq3NicZj2K1OV96aIYtO2KZu9ictia9Kth8ZE2BSN1jnGlsUcFVdQzNS6BBQ/640?wx_fmt=jpeg&from=appmsg
                        width: 640
                        height: 480
                      - cdn_url: >-
                          https://mmbiz.qpic.cn/mmbiz_jpg/3aNX9kq7JM1AHyLeHEdIc5ic83kvLPJOMib52fqZ4NnpjGuGE1MIUppYHmibvfpUzpwV4icGMiasia6miak04guXDttWA/640?wx_fmt=other&from=appmsg&wxfrom=5&wx_lazy=1&wx_co=1&tp=webp
                        width: 1080
                        height: 1512
                      - cdn_url: >-
                          https://mmbiz.qpic.cn/mmbiz_gif/3aNX9kq7JM1zJ8XDwKQMtQtPlo00L5urUIm46Y71dS9KGXkyQ1UlgI8KSMhbkmBLZJoEQO51WkHVrQ5FRzOVAg/640?wx_fmt=gif&from=appmsg&wxfrom=5&wx_lazy=1&tp=webp
                        width: 1079
                        height: 459
                      - cdn_url: >-
                          https://mmbiz.qpic.cn/mmbiz_png/3aNX9kq7JM1fKnVgBdNzM2p3x1l4kgvibgK6wFJmkJ8PGyDPVN05pan6k9tUIPunQQvicyVn6qnlicEjoCiaouycqw/640?wx_fmt=other&from=appmsg&wxfrom=5&wx_lazy=1&wx_co=1&tp=webp
                        width: 1080
                        height: 230
                    video_page_infos: []
                    alias: gh_211aba30114d
                    item_show_type: 0
                    real_item_show_type: 0
                    ip_wording: 中国江苏
                    url: >-
                      http://mp.weixin.qq.com/s?__biz=MzkxNjY0NTcwNA==&mid=2247641306&idx=7&sn=fefba78e29799727e38950bc73cd15aa#rd
                    hashid: fefba78e29799727e38950bc73cd15aa
                    mp_head_img: >-
                      http://wx.qlogo.cn/mmhead/VLjDyM7pibyK9pO6CHs1MXrIhOqQPxtX9mULb3j4FONqLrZytRVGorwu0j38G1YCzJ9JwU8eX99c/0
                    content: >-
                      4月10日，据南粤清风网最新消息：广东省肇庆市政协原副主席、原肇庆医学高等专科学校校长李力强严重违法被取消相应退休待遇。经广东省委批准，广东省监委对肇庆市政协原副主席、原肇庆医学高等专科学校校长李力强严重违法问题进行了立案调查。经查，李力强违反组织要求，在职工录用工作中为他人谋利并收受财物;违反廉洁要求，要求管理服务对象承担单位违规接待费用，利用职权非法占有公款;公器私用，搞权钱交易，利用职务便利为他人在药品销售、项目承揽等方面谋利，并非法收受巨额财物。李力强行为已构成严重服务违法并涉嫌受贿犯罪，目在党的十八大后不收敛、不收手，性质严重，影响恶劣，应予严肃处理。依据《中华人民共和国监察法》《中华人民共和国公职人员政务处分法》等有关规定，由广东首监委给予其取消相应退休待遇处理；没收其违法所得；将其涉嫌犯罪问题移送检察机关依法审查起诉，所涉财物一并移送。李力强，男，汉族，1962年4月出生，湖南湘乡市人，硕士研究生，1981年11月参加工作，农工党员。曾任广东省肇庆市政协副主席、肇庆医学高等专科学校校长、肇庆市中医院院长、农工党广东省委会副主委。肇庆市中医院肇庆市中医院创建于1979年，是肇庆地区规模最大的一所集治未病、医疗、康复、科研、教学、养生养老为一体的地市级综合性中医院、国家三级甲等中医医院。医院建院四十年来，在各级党委、政府的领导下，在全体员工的共同努力下，乘改革开放的春风，坚持“弘扬中医药特色优势，全心全意为人民服务”的办院宗旨，同心同德，励精图治，开拓进取，取得了令人瞩目的成就。▲文章来源：南粤清风▲转载请标注以上来源声明：本文仅作信息传递之目的，仅供参考。本文不对投资及治疗构成任何建议，请谨慎甄别。如涉及作品内容、版权和其它问题，为保障双方权益，请与我们联系，我们将立即处理。如有平台转载本篇文章，须自行对该篇文章负责，医疗器械创新网不对转载引起的二次传播负责。往/期/回/顾裁员300+，BD也扛不住，饭碗“碎了一地”？5695万元，联影又双叒叕中标了！上市首日市值破109亿，医疗科技IPO市场迎来新标杆
                    content_multi_text: >-
                      <section data-role="outer" label="edit by 135editor"
                      style="margin-bottom: 0px;outline: 0px;background-color:
                      rgb(255, 255, 255);visibility: visible;"
                      data-mpa-powered-by="yiban.io" data-pm-slice="0 0
                      []"><section data-role="outer" label="edit by 135editor"
                      style="outline: 0px;visibility: visible;"><section
                      style="outline: 0px;line-height: 27.2px;visibility:
                      visible;"><section><section><a
                      href="https://mp.weixin.qq.com/s?__biz=MzkxNjY0NTcwNA==&amp;mid=2247640975&amp;idx=1&amp;sn=670f70d40734339af12887b14403bdf9&amp;scene=21#wechat_redirect"
                      imgurl="https://mmbiz.qpic.cn/mmbiz_png/3aNX9kq7JM1MrwiaaTAfJGOEKdox57lLibNfPnElJL0NVl55bibIGClkHcIAicEqEtvgmSTkPvZ9uX3Aupb81kXBmA/640?wx_fmt=png&amp;from=appmsg"
                      linktype="image" tab="innerlink" data-itemshowtype="0"
                      target="_blank" data-linktype="1"><span
                      style="width:100%;" class="js_jump_icon
                      h5_image_link"><img class="rich_pages wxw-img"
                      data-backh="246" data-backw="578"
                      data-imgfileid="100157300" data-ratio="0.425"
                      data-s="300,640"
                      data-src="https://mmbiz.qpic.cn/mmbiz_png/3aNX9kq7JM1MrwiaaTAfJGOEKdox57lLibNfPnElJL0NVl55bibIGClkHcIAicEqEtvgmSTkPvZ9uX3Aupb81kXBmA/640?wx_fmt=png&amp;from=appmsg"
                      data-type="png" data-w="1280" style="width:100%;"
                      type="block"  /></span></a></section></section><section
                      data-role="outer" label="edit by 135editor"><section
                      data-role="paragraph" style="height: 0px;"><span
                      leaf=""><br  /></span></section><section
                      style="margin-bottom: 24px;text-indent: 0em;line-height:
                      2em;text-align: center;"><p style="line-height:
                      1.75em;margin-bottom: 24px;margin-left: 8px;margin-right:
                      8px;text-align: justify;"><span style="color: rgb(0, 0,
                      0);font-size: 15px;letter-spacing: 0.5px;"><span
                      style="color: rgb(0, 0, 0);"><span leaf=""
                      data-pm-slice="1 1
                      [&quot;para&quot;,{&quot;tagName&quot;:&quot;section&quot;,&quot;attributes&quot;:{&quot;data-role&quot;:&quot;outer&quot;,&quot;label&quot;:&quot;edit
                      by
                      135editor&quot;,&quot;style&quot;:&quot;-webkit-tap-highlight-color:
                      transparent;margin-bottom: 0px;outline:
                      0px;background-color: rgb(255, 255, 255);visibility:
                      visible;&quot;,&quot;data-mpa-powered-by&quot;:&quot;yiban.io&quot;},&quot;namespaceURI&quot;:&quot;http://www.w3.org/1999/xhtml&quot;},&quot;para&quot;,{&quot;tagName&quot;:&quot;section&quot;,&quot;attributes&quot;:{&quot;data-role&quot;:&quot;outer&quot;,&quot;label&quot;:&quot;edit
                      by
                      135editor&quot;,&quot;style&quot;:&quot;-webkit-tap-highlight-color:
                      transparent;outline: 0px;visibility:
                      visible;&quot;},&quot;namespaceURI&quot;:&quot;http://www.w3.org/1999/xhtml&quot;},&quot;para&quot;,{&quot;tagName&quot;:&quot;section&quot;,&quot;attributes&quot;:{&quot;style&quot;:&quot;-webkit-tap-highlight-color:
                      transparent;outline: 0px;line-height: 27.2px;visibility:
                      visible;&quot;},&quot;namespaceURI&quot;:&quot;http://www.w3.org/1999/xhtml&quot;},&quot;para&quot;,{&quot;tagName&quot;:&quot;section&quot;,&quot;attributes&quot;:{&quot;data-role&quot;:&quot;outer&quot;,&quot;label&quot;:&quot;edit
                      by
                      135editor&quot;},&quot;namespaceURI&quot;:&quot;http://www.w3.org/1999/xhtml&quot;},&quot;para&quot;,{&quot;tagName&quot;:&quot;section&quot;,&quot;attributes&quot;:{&quot;style&quot;:&quot;margin-bottom:
                      24px;text-indent: 0em;line-height:
                      2em;&quot;},&quot;namespaceURI&quot;:&quot;http://www.w3.org/1999/xhtml&quot;},&quot;para&quot;,{&quot;tagName&quot;:&quot;p&quot;,&quot;attributes&quot;:{&quot;style&quot;:&quot;line-height:
                      1.75em;margin-bottom: 24px;margin-left: 8px;margin-right:
                      8px;&quot;},&quot;namespaceURI&quot;:&quot;http://www.w3.org/1999/xhtml&quot;},&quot;node&quot;,{&quot;tagName&quot;:&quot;span&quot;,&quot;attributes&quot;:{&quot;style&quot;:&quot;color:
                      rgb(0, 0, 0);font-size: 15px;letter-spacing:
                      0.5px;&quot;},&quot;namespaceURI&quot;:&quot;http://www.w3.org/1999/xhtml&quot;}]"><br 
                      /></span><span leaf=""><span textstyle=""
                      style="font-weight: normal;">4月10日，据南粤清风网最新消息：</span><span
                      textstyle="" style="font-weight:
                      bold;">广东省肇庆市政协原副主席、原肇庆医学高等专科学校校长李力强严重违法被取消相应退休待遇。</span></span></span></span></p><p
                      style="line-height: 1.75em;margin-bottom:
                      24px;margin-left: 8px;margin-right: 8px;text-align:
                      center;"><span style="color: rgb(0, 0, 0);font-size:
                      15px;letter-spacing: 0.5px;"><span style="color: rgb(0, 0,
                      0);"><span leaf=""><img
                      data-src="https://mmbiz.qpic.cn/sz_mmbiz_jpg/8IaXn7e7IyYdnjaCconlqHThKAfJrmq38uCtFrH9moWpiceuUJh8mFNTfGRgBZg3icFibcHibL1TaEWPJtQ8udxwDA/640?wx_fmt=jpeg"
                      alt="图片" class="rich_pages wxw-img js_img_placeholder
                      wx_img_placeholder" data-ratio="0.4212962962962963"
                      data-s="300,640" data-type="png" data-w="1080"
                      style="padding: 5px;font-family: system-ui, -apple-system,
                      BlinkMacSystemFont, &quot;Helvetica Neue&quot;,
                      &quot;PingFang SC&quot;, &quot;Hiragino Sans GB&quot;,
                      &quot;Microsoft YaHei UI&quot;, &quot;Microsoft
                      YaHei&quot;, Arial, sans-serif;font-size:
                      17px;letter-spacing: normal;border-width:
                      1px;border-style: solid;border-color: rgb(151, 152,
                      153);border-radius: 0px;box-shadow: rgb(151, 152, 153) 0px
                      0px 6px;width: 360px !important;height: 158.225px
                      !important;"
                      data-croporisrc="https://mmbiz.qpic.cn/sz_mmbiz_png/8IaXn7e7IyYdnjaCconlqHThKAfJrmq3rniabY5JwQdGr9Qr4SicY4JE7mw0nvLtiaxVwzNG878IYljjAJvBFSOXA/0?wx_fmt=png&amp;from=appmsg"
                      data-cropx2="1080" data-cropy2="456.2566844919786"
                      data-imgfileid="100052622"  /></span></span></span></p><p
                      style="line-height: 1.75em;margin-bottom:
                      24px;margin-left: 8px;margin-right: 8px;text-align:
                      justify;"><span leaf="" style="color: rgb(0, 0,
                      0);font-size: 15px;letter-spacing:
                      0.5px;">经广东省委批准，广东省监委对肇庆市政协原副主席、原肇庆医学高等专科学校校长李力强严重违法问题进行了立案调查。</span></p><p
                      style="line-height: 1.75em;margin-bottom:
                      24px;margin-left: 8px;margin-right: 8px;text-align:
                      justify;"><span leaf="" style="color: rgb(0, 0,
                      0);font-size: 15px;letter-spacing:
                      0.5px;">经查，李力强违反组织要求，在职工录用工作中为他人谋利并收受财物;违反廉洁要求，要求管理服务对象承担单位违规接待费用，利用职权非法占有公款;公器私用，搞权钱交易，利用职务便利为他人在药品销售、项目承揽等方面谋利，并非法收受巨额财物。</span></p><p
                      style="line-height: 1.75em;margin-bottom:
                      24px;margin-left: 8px;margin-right: 8px;text-align:
                      justify;"><span leaf="" style="color: rgb(0, 0,
                      0);font-size: 15px;letter-spacing:
                      0.5px;">李力强行为已构成严重服务违法并涉嫌受贿犯罪，目在党的十八大后不收敛、不收手，性质严重，影响恶劣，应予严肃处理。依据《中华人民共和国监察法》《中华人民共和国公职人员政务处分法》等有关规定，由广东首监委给予其取消相应退休待遇处理；没收其违法所得；将其涉嫌犯罪问题移送检察机关依法审查起诉，所涉财物一并移送。</span></p><p
                      style="line-height: 1.75em;margin-bottom:
                      24px;margin-left: 8px;margin-right: 8px;text-align:
                      justify;"><span leaf="" style="color: rgb(0, 0,
                      0);font-size: 15px;letter-spacing:
                      0.5px;">李力强，男，汉族，1962年4月出生，湖南湘乡市人，硕士研究生，1981年11月参加工作，农工党员。<span
                      textstyle="" style="font-weight:
                      bold;">曾任广东省肇庆市政协副主席、肇庆医学高等专科学校校长、肇庆市中医院院长、农工党广东省委会副主委。</span></span></p><section
                      style="margin-bottom: 24px;" nodeleaf=""><img
                      data-src="https://mmbiz.qpic.cn/sz_mmbiz_png/8IaXn7e7IyYdnjaCconlqHThKAfJrmq3alyYQlHpiaCoFPDLNRiae2wXYu2mqJvP84FcmF7BEjETnyynOu7VYwRQ/640?wx_fmt=png&amp;from=appmsg"
                      alt="图片" class="rich_pages wxw-img js_insertlocalimg
                      js_img_placeholder wx_img_placeholder"
                      data-ratio="1.2857142857142858" data-s="300,640"
                      data-type="png" data-w="259" style="width: 259px
                      !important;height: 333px !important;" type="block"
                      data-imgfileid="100052624"  /></section><span leaf=""
                      style="color: rgb(0, 0, 0);font-size: 15px;letter-spacing:
                      0.5px;" data-pm-slice="1 1
                      [&quot;para&quot;,{&quot;tagName&quot;:&quot;section&quot;,&quot;attributes&quot;:{&quot;data-role&quot;:&quot;outer&quot;,&quot;label&quot;:&quot;edit
                      by
                      135editor&quot;,&quot;style&quot;:&quot;-webkit-tap-highlight-color:
                      transparent;margin-bottom: 0px;outline:
                      0px;background-color: rgb(255, 255, 255);visibility:
                      visible;&quot;,&quot;data-mpa-powered-by&quot;:&quot;yiban.io&quot;},&quot;namespaceURI&quot;:&quot;http://www.w3.org/1999/xhtml&quot;},&quot;para&quot;,{&quot;tagName&quot;:&quot;section&quot;,&quot;attributes&quot;:{&quot;data-role&quot;:&quot;outer&quot;,&quot;label&quot;:&quot;edit
                      by
                      135editor&quot;,&quot;style&quot;:&quot;-webkit-tap-highlight-color:
                      transparent;outline: 0px;visibility:
                      visible;&quot;},&quot;namespaceURI&quot;:&quot;http://www.w3.org/1999/xhtml&quot;},&quot;para&quot;,{&quot;tagName&quot;:&quot;section&quot;,&quot;attributes&quot;:{&quot;style&quot;:&quot;-webkit-tap-highlight-color:
                      transparent;outline: 0px;line-height: 27.2px;visibility:
                      visible;&quot;},&quot;namespaceURI&quot;:&quot;http://www.w3.org/1999/xhtml&quot;},&quot;para&quot;,{&quot;tagName&quot;:&quot;section&quot;,&quot;attributes&quot;:{&quot;data-role&quot;:&quot;outer&quot;,&quot;label&quot;:&quot;edit
                      by
                      135editor&quot;},&quot;namespaceURI&quot;:&quot;http://www.w3.org/1999/xhtml&quot;},&quot;para&quot;,{&quot;tagName&quot;:&quot;section&quot;,&quot;attributes&quot;:{&quot;style&quot;:&quot;margin-bottom:
                      24px;text-indent: 0em;line-height:
                      2em;&quot;},&quot;namespaceURI&quot;:&quot;http://www.w3.org/1999/xhtml&quot;}]"><span
                      textstyle="" style="font-weight:
                      bold;">肇庆市中医院</span></span></section><section
                      style="text-align: center;margin-bottom: 24px;"
                      nodeleaf=""><img
                      data-src="https://mmbiz.qpic.cn/sz_mmbiz_jpg/8IaXn7e7IyYdnjaCconlqHThKAfJrmq3NicZj2K1OV96aIYtO2KZu9ictia9Kth8ZE2BSN1jnGlsUcFVdQzNS6BBQ/640?wx_fmt=jpeg&amp;from=appmsg"
                      alt="图片" class="rich_pages wxw-img js_insertlocalimg
                      js_img_placeholder wx_img_placeholder" data-ratio="0.75"
                      data-s="300,640" data-type="jpeg" data-w="640"
                      style="width: 360px !important;height: 270px !important;"
                      type="block" data-imgfileid="100052625" 
                      /></section><section style="margin-bottom:
                      24px;text-indent: 0em;line-height: 2em;text-align:
                      justify;"><span leaf="" style="color: rgb(0, 0,
                      0);font-size: 15px;letter-spacing: 0.5px;"
                      data-pm-slice="1 1
                      [&quot;para&quot;,{&quot;tagName&quot;:&quot;section&quot;,&quot;attributes&quot;:{&quot;data-role&quot;:&quot;outer&quot;,&quot;label&quot;:&quot;edit
                      by
                      135editor&quot;,&quot;style&quot;:&quot;-webkit-tap-highlight-color:
                      transparent;margin-bottom: 0px;outline:
                      0px;background-color: rgb(255, 255, 255);visibility:
                      visible;&quot;,&quot;data-mpa-powered-by&quot;:&quot;yiban.io&quot;},&quot;namespaceURI&quot;:&quot;http://www.w3.org/1999/xhtml&quot;},&quot;para&quot;,{&quot;tagName&quot;:&quot;section&quot;,&quot;attributes&quot;:{&quot;data-role&quot;:&quot;outer&quot;,&quot;label&quot;:&quot;edit
                      by
                      135editor&quot;,&quot;style&quot;:&quot;-webkit-tap-highlight-color:
                      transparent;outline: 0px;visibility:
                      visible;&quot;},&quot;namespaceURI&quot;:&quot;http://www.w3.org/1999/xhtml&quot;},&quot;para&quot;,{&quot;tagName&quot;:&quot;section&quot;,&quot;attributes&quot;:{&quot;style&quot;:&quot;-webkit-tap-highlight-color:
                      transparent;outline: 0px;line-height: 27.2px;visibility:
                      visible;&quot;},&quot;namespaceURI&quot;:&quot;http://www.w3.org/1999/xhtml&quot;},&quot;para&quot;,{&quot;tagName&quot;:&quot;section&quot;,&quot;attributes&quot;:{&quot;data-role&quot;:&quot;outer&quot;,&quot;label&quot;:&quot;edit
                      by
                      135editor&quot;},&quot;namespaceURI&quot;:&quot;http://www.w3.org/1999/xhtml&quot;},&quot;para&quot;,{&quot;tagName&quot;:&quot;section&quot;,&quot;attributes&quot;:{&quot;style&quot;:&quot;margin-bottom:
                      24px;text-indent: 0em;line-height:
                      2em;&quot;},&quot;namespaceURI&quot;:&quot;http://www.w3.org/1999/xhtml&quot;}]">肇庆市中医院创建于1979年，是肇庆地区规模最大的一所集治未病、医疗、康复、科研、教学、养生养老为一体的地市级综合性中医院、国家三级甲等中医医院。医院建院四十年来，在各级党委、政府的领导下，在全体员工的共同努力下，乘改革开放的春风，坚持“弘扬中医药特色优势，全心全意为人民服务”的办院宗旨，同心同德，励精图治，开拓进取，取得了令人瞩目的成就。</span></section><section
                      class="channels_iframe_wrp"
                      nodeleaf=""><mp-common-videosnap class="js_uneditable
                      custom_select_card channels_iframe videosnap_video_iframe
                      videosnap_video_iframe" data-pluginname="mpvideosnap"
                      data-url="https://findermp.video.qq.com/251/20304/stodownload?encfilekey=rjD5jyTuFrIpZ2ibE8T7YmwgiahniaXswqzaiaoI4bibsAyPI1wkiaic9B48BicHsBTbcMvm9afvLfLjC5ymGW7lbwEowzibsm4gSc2bFdArF8XlwMCJbQtN4ELkUMg&amp;token=AxricY7RBHdXLJhX3ovAoz2rknTdSoDLtYIaHHhpu17MCV1ZibIkmJDiae9avd9F72Pp7HzZKvuFibRhhP9HuTibRY3EeswS2WVOwaV7u6lZicCMaKbWcibQLPNItkLODj0bYAILhCJaNf4F5eEvPX1VrgPric9pOFVe2gzKcXHPElicqQGg&amp;idx=1&amp;hy=SH&amp;m=&amp;scene=2&amp;uzid=1"
                      data-headimgurl="http://wx.qlogo.cn/finderhead/98Nz5LFElxzXP4C9M0j13MpfNxuBJbjskibTVZG3B84e9IZFMNqtfvQ/0"
                      data-username="v2_060000231003b20faec8c4e78c1ac1d1cb03e837b07760612d8cd095e51db84b9e6029e23ab9@finder"
                      data-nickname="医疗器械创新网"
                      data-desc="第91届中国国际医疗器械（春季）博览会(CMEF)，医疗器械创新网带你云逛展~#CMEF
                      #医疗器械博览会 #ai #手术机器人 #医疗器械 

                      " data-nonceid="3422675150941744872" data-width="1920"
                      data-height="1080" data-type="video"
                      data-id="export/UzFfAgtgekIEAQAAAAAAbNIRxF3iAQAAAAstQy6ubaLX4KHWvLEZgBPEqoNoTW82D-KIzNPgMIuA1vLsiTE702lp0HplEa2z"></mp-common-videosnap></section><section
                      class="channels_iframe_wrp"
                      nodeleaf=""><mp-common-videosnap class="js_uneditable
                      custom_select_card channels_live_iframe"
                      data-pluginname="mpvideosnap"
                      data-headimgurl="https://wx.qlogo.cn/finderhead/98Nz5LFElxzXP4C9M0j13MpfNxuBJbjskibTVZG3B84e9IZFMNqtfvQ/0"
                      data-username="v2_060000231003b20faec8c4e78c1ac1d1cb03e837b07760612d8cd095e51db84b9e6029e23ab9@finder"
                      data-nickname="医疗器械创新网" data-desc="将在04月15日 20:00 直播"
                      data-type="live" data-intro="走进企业-海迈医疗"
                      data-noticeid="finderlivenotice-v2_060000231003b20faec8c4e78c1ac1d1cb03e837b07760612d8cd095e51db84b9e6029e23ab9@finder-1744266982446168-1359285704"
                      data-status="0"></mp-common-videosnap></section><section
                      class="channels_iframe_wrp"
                      nodeleaf=""><mp-common-videosnap class="js_uneditable
                      custom_select_card channels_live_iframe"
                      data-pluginname="mpvideosnap"
                      data-headimgurl="https://wx.qlogo.cn/finderhead/98Nz5LFElxzXP4C9M0j13MpfNxuBJbjskibTVZG3B84e9IZFMNqtfvQ/0"
                      data-username="v2_060000231003b20faec8c4e78c1ac1d1cb03e837b07760612d8cd095e51db84b9e6029e23ab9@finder"
                      data-nickname="医疗器械创新网" data-desc="将在04月23日 20:00 直播"
                      data-type="live" data-intro="中国医疗器械国际化洞察"
                      data-noticeid="finderlivenotice-v2_060000231003b20faec8c4e78c1ac1d1cb03e837b07760612d8cd095e51db84b9e6029e23ab9@finder-1744359489250182-1310660025"
                      data-status="0"></mp-common-videosnap></section><span
                      leaf="" style="-webkit-tap-highlight-color:
                      transparent;margin: 0px;padding: 0px;outline:
                      0px;max-width: 100%;box-sizing: border-box
                      !important;overflow-wrap: break-word !important;"><br 
                      /></span></section></section><section data-color="#AC1D10"
                      data-pm-slice="0 0 []" style="-webkit-tap-highlight-color:
                      transparent;margin-top: 0px;margin-right:
                      0px;margin-bottom: unset;margin-left: 0px;padding:
                      0px;outline: 0px;max-width: 100%;box-sizing: border-box
                      !important;overflow-wrap: break-word
                      !important;font-style: normal;font-variant-ligatures:
                      normal;font-variant-caps: normal;font-weight:
                      400;letter-spacing: 0.544px;orphans: 2;text-align:
                      justify;text-indent: 0px;text-transform: none;widows:
                      2;word-spacing: 0px;-webkit-text-stroke-width:
                      0px;white-space: normal;text-decoration-thickness:
                      initial;text-decoration-style:
                      initial;text-decoration-color: initial;background-color:
                      rgb(255, 255, 255);caret-color: rgba(0, 0, 0,
                      0);font-size: 14px;color: rgb(51, 51, 51);font-family:
                      system-ui, -apple-system, BlinkMacSystemFont,
                      &quot;Helvetica Neue&quot;, &quot;PingFang SC&quot;,
                      &quot;Hiragino Sans GB&quot;, &quot;Microsoft YaHei
                      UI&quot;, &quot;Microsoft YaHei&quot;, Arial,
                      sans-serif;visibility: visible;"><section
                      style="-webkit-tap-highlight-color: transparent;margin:
                      0px;padding: 0px;outline: 0px;max-width: 100%;box-sizing:
                      border-box !important;overflow-wrap: break-word
                      !important;font-size: 16px;visibility: visible;"><section
                      style="-webkit-tap-highlight-color:
                      transparent;margin-top: 0px;margin-right:
                      8px;margin-bottom: unset;margin-left: 8px;padding:
                      0px;outline: 0px;max-width: 100%;box-sizing: border-box
                      !important;overflow-wrap: break-word
                      !important;letter-spacing: 0.578px;text-indent:
                      0em;line-height: 1.75em;visibility: visible;"><section
                      style="-webkit-tap-highlight-color:
                      transparent;margin-top: 10px;margin-right:
                      0px;margin-bottom: unset;margin-left: 0px;padding:
                      0px;outline: 0px;max-width: 100%;box-sizing: border-box
                      !important;overflow-wrap: break-word !important;display:
                      flex;justify-content: flex-start;align-items:
                      center;visibility: visible;"><section data-width="45%"
                      style="-webkit-tap-highlight-color:
                      transparent;margin-top: 0px;margin-right:
                      0px;margin-bottom: unset;margin-left: 0px;padding:
                      0px;outline: 0px;max-width: 100%;box-sizing: border-box
                      !important;overflow-wrap: break-word !important;width:
                      297.448px;height: 1px;background-color: rgb(46, 70,
                      168);visibility: visible;"><span leaf=""
                      style="-webkit-tap-highlight-color: transparent;margin:
                      0px;padding: 0px;outline: 0px;max-width: 100%;box-sizing:
                      border-box !important;overflow-wrap: break-word
                      !important;"><br  /></span></section><section
                      style="-webkit-tap-highlight-color:
                      transparent;margin-top: 0px;margin-right:
                      0px;margin-bottom: unset;margin-left: 10px;padding:
                      0px;outline: 0px;max-width: 100%;box-sizing: border-box
                      !important;overflow-wrap: break-word !important;width:
                      5px;height: 13px;background-color: rgb(46, 70,
                      168);transform: skew(-25deg);visibility: visible;"><span
                      leaf="" style="-webkit-tap-highlight-color:
                      transparent;margin: 0px;padding: 0px;outline:
                      0px;max-width: 100%;box-sizing: border-box
                      !important;overflow-wrap: break-word !important;"><br 
                      /></span></section><section
                      style="-webkit-tap-highlight-color:
                      transparent;margin-top: 0px;margin-right:
                      0px;margin-bottom: unset;margin-left: 6px;padding:
                      0px;outline: 0px;max-width: 100%;box-sizing: border-box
                      !important;overflow-wrap: break-word !important;width:
                      5px;height: 18px;background-color: rgb(46, 70,
                      168);transform: skew(-25deg);visibility: visible;"><span
                      leaf="" style="-webkit-tap-highlight-color:
                      transparent;margin: 0px;padding: 0px;outline:
                      0px;max-width: 100%;box-sizing: border-box
                      !important;overflow-wrap: break-word !important;"><br 
                      /></span></section><section
                      style="-webkit-tap-highlight-color:
                      transparent;margin-top: 0px;margin-right:
                      0px;margin-bottom: unset;margin-left: 6px;padding:
                      0px;outline: 0px;max-width: 100%;box-sizing: border-box
                      !important;overflow-wrap: break-word !important;width:
                      5px;height: 13px;background-color: rgb(46, 70,
                      168);transform: skew(-25deg);visibility: visible;"><span
                      leaf="" style="-webkit-tap-highlight-color:
                      transparent;margin: 0px;padding: 0px;outline:
                      0px;max-width: 100%;box-sizing: border-box
                      !important;overflow-wrap: break-word !important;"><br 
                      /></span></section><section data-width="45%"
                      style="-webkit-tap-highlight-color:
                      transparent;margin-top: 0px;margin-right:
                      0px;margin-bottom: unset;margin-left: 10px;padding:
                      0px;outline: 0px;max-width: 100%;box-sizing: border-box
                      !important;overflow-wrap: break-word !important;width:
                      297.448px;height: 1px;background-color: rgb(46, 70,
                      168);visibility: visible;"><span leaf=""
                      style="-webkit-tap-highlight-color: transparent;margin:
                      0px;padding: 0px;outline: 0px;max-width: 100%;box-sizing:
                      border-box !important;overflow-wrap: break-word
                      !important;"><br 
                      /></span></section></section></section></section></section><section
                      style="-webkit-tap-highlight-color:
                      transparent;margin-top: 0px;margin-right:
                      0px;margin-bottom: unset;margin-left: 0px;padding:
                      0px;outline: 0px;max-width: 100%;box-sizing: border-box
                      !important;overflow-wrap: break-word
                      !important;font-family: &quot;PingFang SC&quot;,
                      system-ui, -apple-system, BlinkMacSystemFont,
                      &quot;Helvetica Neue&quot;, &quot;Hiragino Sans GB&quot;,
                      &quot;Microsoft YaHei UI&quot;, &quot;Microsoft
                      YaHei&quot;, Arial, sans-serif;font-style:
                      normal;font-variant-ligatures: normal;font-variant-caps:
                      normal;font-weight: 400;letter-spacing: 0.544px;orphans:
                      2;text-align: justify;text-indent: 0px;text-transform:
                      none;widows: 2;word-spacing:
                      0px;-webkit-text-stroke-width: 0px;white-space:
                      normal;text-decoration-thickness:
                      initial;text-decoration-style:
                      initial;text-decoration-color: initial;background-color:
                      rgb(255, 255, 255);visibility: visible;font-size:
                      15px;caret-color: rgba(0, 0, 0, 0);color: rgb(51, 51,
                      51);"><section style="-webkit-tap-highlight-color:
                      transparent;margin-top: 0px;margin-right:
                      0px;margin-bottom: unset;margin-left: 0px;padding:
                      0px;outline: 0px;max-width: 100%;box-sizing: border-box
                      !important;overflow-wrap: break-word
                      !important;visibility: visible;"><section
                      style="-webkit-tap-highlight-color:
                      transparent;margin-top: 0px;margin-right:
                      8px;margin-bottom: unset;margin-left: 8px;padding:
                      0px;outline: 0px;max-width: 100%;box-sizing: border-box
                      !important;overflow-wrap: break-word
                      !important;visibility: visible;"><span
                      style="-webkit-tap-highlight-color: transparent;margin:
                      0px;padding: 0px;outline: 0px;max-width: 100%;box-sizing:
                      border-box !important;overflow-wrap: break-word
                      !important;font-family: system-ui, -apple-system,
                      BlinkMacSystemFont, &quot;Helvetica Neue&quot;,
                      &quot;PingFang SC&quot;, &quot;Hiragino Sans GB&quot;,
                      &quot;Microsoft YaHei UI&quot;, &quot;Microsoft
                      YaHei&quot;, Arial, sans-serif;font-size:
                      16px;letter-spacing: 1px;visibility: visible;color: rgb(0,
                      0, 0);"><span leaf="" style="-webkit-tap-highlight-color:
                      transparent;margin: 0px;padding: 0px;outline:
                      0px;max-width: 100%;box-sizing: border-box
                      !important;overflow-wrap: break-word !important;"><span
                      textstyle="" style="color: rgb(0, 0, 0);font-weight:
                      normal;">▲文章来源：</span>南粤清风</span></span></section><section
                      style="-webkit-tap-highlight-color:
                      transparent;margin-top: 0px;margin-right:
                      8px;margin-bottom: unset;margin-left: 8px;padding:
                      0px;outline: 0px;max-width: 100%;box-sizing: border-box
                      !important;overflow-wrap: break-word
                      !important;visibility: visible;"><span
                      style="-webkit-tap-highlight-color: transparent;margin:
                      0px;padding: 0px;outline: 0px;max-width: 100%;box-sizing:
                      border-box !important;overflow-wrap: break-word
                      !important;font-family: system-ui, -apple-system,
                      BlinkMacSystemFont, &quot;Helvetica Neue&quot;,
                      &quot;PingFang SC&quot;, &quot;Hiragino Sans GB&quot;,
                      &quot;Microsoft YaHei UI&quot;, &quot;Microsoft
                      YaHei&quot;, Arial, sans-serif;font-size:
                      16px;letter-spacing: 1px;visibility: visible;color: rgb(0,
                      0, 0);"><span leaf="" style="-webkit-tap-highlight-color:
                      transparent;margin: 0px;padding: 0px;outline:
                      0px;max-width: 100%;box-sizing: border-box
                      !important;overflow-wrap: break-word !important;"><span
                      textstyle="" style="color: rgb(0, 0, 0);font-weight:
                      normal;">▲转载请标注以上来源</span></span></span></section><section
                      style="-webkit-tap-highlight-color: transparent;margin:
                      0px 8px;padding: 0px;outline: 0px;max-width:
                      100%;box-sizing: border-box !important;overflow-wrap:
                      break-word !important;line-height: 1.75em;visibility:
                      visible;"><span style="-webkit-tap-highlight-color:
                      transparent;margin: 0px;padding: 0px;outline:
                      0px;max-width: 100%;box-sizing: border-box
                      !important;overflow-wrap: break-word !important;font-size:
                      12px;color: rgb(136, 136, 136);letter-spacing:
                      1px;visibility: visible;"><span leaf=""
                      style="-webkit-tap-highlight-color: transparent;margin:
                      0px;padding: 0px;outline: 0px;max-width: 100%;box-sizing:
                      border-box !important;overflow-wrap: break-word
                      !important;"><br  /></span></span></section><section
                      style="-webkit-tap-highlight-color: transparent;margin:
                      0px 8px;padding: 0px;outline: 0px;max-width:
                      100%;box-sizing: border-box !important;overflow-wrap:
                      break-word !important;font-family: system-ui,
                      -apple-system, BlinkMacSystemFont, &quot;Helvetica
                      Neue&quot;, &quot;PingFang SC&quot;, &quot;Hiragino Sans
                      GB&quot;, &quot;Microsoft YaHei UI&quot;, &quot;Microsoft
                      YaHei&quot;, Arial, sans-serif;font-size:
                      16px;letter-spacing: 0.578px;text-indent: 0em;line-height:
                      1.75em;visibility: visible;"><span
                      style="-webkit-tap-highlight-color: transparent;margin:
                      0px;padding: 0px;outline: 0px;max-width: 100%;box-sizing:
                      border-box !important;overflow-wrap: break-word
                      !important;color: rgb(136, 136, 136);font-family:
                      &quot;Helvetica Neue&quot;, &quot;Hiragino Sans GB&quot;,
                      &quot;Microsoft YaHei&quot;, 黑体, Arial,
                      sans-serif;font-size: 12px;caret-color: rgb(0, 0,
                      0);letter-spacing: 1px;visibility: visible;"><span leaf=""
                      style="-webkit-tap-highlight-color: transparent;margin:
                      0px;padding: 0px;outline: 0px;max-width: 100%;box-sizing:
                      border-box !important;overflow-wrap: break-word
                      !important;">声明：本文仅作信息传递之目的，仅供参考。本文不对投资及治疗构成任何建议，请谨慎甄别。如涉及作品内容、版权和其它问题，为保障双方权益，请与我们联系，我们将立即处理。如有平台转载本篇文章，须自行对该篇文章负责，医疗器械创新网不对转载引起的二次传播负责。</span></span></section></section></section><section
                      nodeleaf="" style="-webkit-tap-highlight-color:
                      transparent;margin: 0px 8px;padding: 0px;outline:
                      0px;max-width: 100%;box-sizing: border-box
                      !important;overflow-wrap: break-word
                      !important;font-family: &quot;PingFang SC&quot;,
                      system-ui, -apple-system, BlinkMacSystemFont,
                      &quot;Helvetica Neue&quot;, &quot;Hiragino Sans GB&quot;,
                      &quot;Microsoft YaHei UI&quot;, &quot;Microsoft
                      YaHei&quot;, Arial, sans-serif;font-style:
                      normal;font-variant-ligatures: normal;font-variant-caps:
                      normal;font-weight: 400;letter-spacing: 0.544px;orphans:
                      2;text-indent: 0px;text-transform: none;widows:
                      2;word-spacing: 0px;-webkit-text-stroke-width:
                      0px;white-space: normal;text-decoration-thickness:
                      initial;text-decoration-style:
                      initial;text-decoration-color: initial;background-color:
                      rgb(255, 255, 255);caret-color: rgba(0, 0, 0,
                      0);font-size: 14px;color: rgb(51, 51, 51);text-align:
                      center;line-height: 1.75em;"><img
                      data-src="https://mmbiz.qpic.cn/mmbiz_jpg/3aNX9kq7JM1AHyLeHEdIc5ic83kvLPJOMib52fqZ4NnpjGuGE1MIUppYHmibvfpUzpwV4icGMiasia6miak04guXDttWA/640?wx_fmt=other&amp;from=appmsg&amp;wxfrom=5&amp;wx_lazy=1&amp;wx_co=1&amp;tp=webp"
                      alt="图片" class="rich_pages wxw-img" data-ratio="1.4"
                      data-s="300,640" data-type="jpeg" data-w="1080"
                      style="-webkit-tap-highlight-color: transparent;margin:
                      0px;padding: 0px;outline: 0px;max-width: 100%;box-sizing:
                      border-box !important;overflow-wrap: break-word
                      !important;vertical-align: bottom;height: auto
                      !important;border-radius: 8px;background-size: 16px
                      !important;visibility: visible !important;width: 644.734px
                      !important;" data-backw="578" data-backh="809"
                      data-imgfileid="100157023"  /></section><section
                      style="-webkit-tap-highlight-color: transparent;margin:
                      0px 8px;padding: 0px;outline: 0px;max-width:
                      100%;box-sizing: border-box !important;overflow-wrap:
                      break-word !important;font-family: &quot;PingFang
                      SC&quot;, system-ui, -apple-system, BlinkMacSystemFont,
                      &quot;Helvetica Neue&quot;, &quot;Hiragino Sans GB&quot;,
                      &quot;Microsoft YaHei UI&quot;, &quot;Microsoft
                      YaHei&quot;, Arial, sans-serif;font-style:
                      normal;font-variant-ligatures: normal;font-variant-caps:
                      normal;font-weight: 400;letter-spacing: 0.544px;orphans:
                      2;text-indent: 0px;text-transform: none;widows:
                      2;word-spacing: 0px;-webkit-text-stroke-width:
                      0px;white-space: normal;text-decoration-thickness:
                      initial;text-decoration-style:
                      initial;text-decoration-color: initial;background-color:
                      rgb(255, 255, 255);caret-color: rgba(0, 0, 0,
                      0);font-size: 14px;color: rgb(51, 51, 51);text-align:
                      center;line-height: 1.75em;"><span leaf=""
                      style="-webkit-tap-highlight-color: transparent;margin:
                      0px;padding: 0px;outline: 0px;max-width: 100%;box-sizing:
                      border-box !important;overflow-wrap: break-word
                      !important;"><br  /></span></section><section
                      data-pm-slice="0 0 []" style="-webkit-tap-highlight-color:
                      transparent;margin: 0px 8px;padding: 0px;outline:
                      0px;max-width: 100%;box-sizing: border-box
                      !important;overflow-wrap: break-word
                      !important;font-style: normal;font-variant-ligatures:
                      normal;font-variant-caps: normal;font-weight:
                      400;letter-spacing: 0.544px;orphans: 2;text-indent:
                      0px;text-transform: none;widows: 2;word-spacing:
                      0px;-webkit-text-stroke-width: 0px;white-space:
                      normal;text-decoration-thickness:
                      initial;text-decoration-style:
                      initial;text-decoration-color: initial;background-color:
                      rgb(255, 255, 255);font-size: 15px;font-family: system-ui,
                      -apple-system, BlinkMacSystemFont, &quot;Helvetica
                      Neue&quot;, &quot;PingFang SC&quot;, &quot;Hiragino Sans
                      GB&quot;, &quot;Microsoft YaHei UI&quot;, &quot;Microsoft
                      YaHei&quot;, Arial, sans-serif;color: rgb(137, 137,
                      137);caret-color: rgba(0, 0, 0, 0);visibility:
                      visible;text-align: center;line-height: 1.75em;"><span
                      style="-webkit-tap-highlight-color: transparent;margin:
                      0px;padding: 0px;outline: 0px;max-width: 100%;box-sizing:
                      border-box !important;overflow-wrap: break-word
                      !important;letter-spacing: 1px;"><strong
                      style="-webkit-tap-highlight-color: transparent;margin:
                      0px;padding: 0px;outline: 0px;max-width: 100%;box-sizing:
                      border-box !important;overflow-wrap: break-word
                      !important;color: rgb(84, 116, 194);font-size:
                      20px;letter-spacing: 2px;visibility: visible;"><span
                      leaf="" style="-webkit-tap-highlight-color:
                      transparent;margin: 0px;padding: 0px;outline:
                      0px;max-width: 100%;box-sizing: border-box
                      !important;overflow-wrap: break-word
                      !important;">往/期/回/顾</span></strong></span></section><section
                      data-support="96编辑器" data-style-id="39346"
                      style="-webkit-tap-highlight-color: transparent;margin:
                      0px;padding: 0px;outline: 0px;max-width: 100%;box-sizing:
                      border-box !important;overflow-wrap: break-word
                      !important;font-style: normal;font-variant-ligatures:
                      normal;font-variant-caps: normal;font-weight: 400;orphans:
                      2;text-indent: 0px;text-transform: none;widows:
                      2;word-spacing: 0px;-webkit-text-stroke-width:
                      0px;white-space: normal;text-decoration-thickness:
                      initial;text-decoration-style:
                      initial;text-decoration-color: initial;background-color:
                      rgb(255, 255, 255);letter-spacing: 0.578px;font-size:
                      15px;font-family: system-ui, -apple-system,
                      BlinkMacSystemFont, &quot;Helvetica Neue&quot;,
                      &quot;PingFang SC&quot;, &quot;Hiragino Sans GB&quot;,
                      &quot;Microsoft YaHei UI&quot;, &quot;Microsoft
                      YaHei&quot;, Arial, sans-serif;text-align: start;color:
                      rgb(137, 137, 137);caret-color: rgba(0, 0, 0,
                      0);visibility: visible;"><section
                      style="-webkit-tap-highlight-color: transparent;margin:
                      10px 0px;padding: 0px;outline: 0px;max-width:
                      100%;box-sizing: border-box !important;overflow-wrap:
                      break-word !important;visibility: visible;"><section
                      style="-webkit-tap-highlight-color: transparent;margin:
                      0px 0px 0em;padding: 0px;outline: 0px;max-width:
                      100%;box-sizing: border-box !important;overflow-wrap:
                      break-word !important;text-align: center;visibility:
                      visible;"><section style="-webkit-tap-highlight-color:
                      transparent;margin: -11px 8px 0px;padding: 0px;outline:
                      0px;max-width: 100%;box-sizing: border-box
                      !important;overflow-wrap: break-word
                      !important;visibility: visible;line-height:
                      1.75em;"><section style="-webkit-tap-highlight-color:
                      transparent;margin: 0px;padding: 0px 14px 8px;outline:
                      0px;max-width: 100%;box-sizing: border-box
                      !important;overflow-wrap: break-word
                      !important;background-color: rgb(84, 116, 194);display:
                      inline-block;visibility: visible;"><section
                      style="-webkit-tap-highlight-color: transparent;margin:
                      0px auto;padding: 0px;outline: 0px;max-width:
                      100%;box-sizing: border-box !important;overflow-wrap:
                      break-word !important;width: 15px;height:
                      15px;border-style: solid solid none none;border-width:
                      3px;border-radius: 0px;border-color: rgb(254, 254,
                      254);transform: rotateZ(135deg);visibility:
                      visible;"><span leaf=""
                      style="-webkit-tap-highlight-color: transparent;margin:
                      0px;padding: 0px;outline: 0px;max-width: 100%;box-sizing:
                      border-box !important;overflow-wrap: break-word
                      !important;"><br 
                      /></span></section></section></section></section><section
                      style="-webkit-tap-highlight-color: transparent;margin:
                      0px 8px;padding: 20px 14px;outline: 0px;max-width:
                      100%;box-sizing: border-box !important;overflow-wrap:
                      break-word !important;background-color: rgb(238, 243,
                      255);visibility: visible;line-height: 1.75em;"><section
                      style="-webkit-tap-highlight-color: transparent;margin:
                      0px;padding: 0px;outline: 0px;max-width: 100%;box-sizing:
                      border-box !important;overflow-wrap: break-word
                      !important;display: flex;align-items:
                      flex-start;"><section style="-webkit-tap-highlight-color:
                      transparent;margin: 8px 0px 0px;padding: 0px;outline:
                      0px;max-width: 100%;box-sizing: border-box
                      !important;overflow-wrap: break-word !important;width:
                      8px;height: 8px;background-color: rgb(84, 116,
                      194);border-radius: 50%;text-align: justify;"><span
                      leaf="" style="-webkit-tap-highlight-color:
                      transparent;margin: 0px;padding: 0px;outline:
                      0px;max-width: 100%;box-sizing: border-box
                      !important;overflow-wrap: break-word !important;"><br 
                      /></span></section><section data-width="96%"
                      style="-webkit-tap-highlight-color: transparent;margin:
                      0px 0px 0px 12px;padding: 0px;outline: 0px;max-width:
                      100%;box-sizing: border-box !important;overflow-wrap:
                      break-word !important;width: 528px;"><section
                      style="-webkit-tap-highlight-color: transparent;margin:
                      0px;padding: 0px;outline: 0px;max-width: 100%;box-sizing:
                      border-box !important;overflow-wrap: break-word
                      !important;"><h1 style="-webkit-tap-highlight-color:
                      transparent;margin: 0px 0px 14px;padding: 0px;outline:
                      0px;font-weight: bold;font-size: 22px;max-width:
                      100%;box-sizing: border-box !important;overflow-wrap:
                      break-word !important;line-height: 1.4;color: rgba(0, 0,
                      0, 0.898);letter-spacing: 0.544px;text-align:
                      justify;"><span style="-webkit-tap-highlight-color:
                      transparent;margin: 0px;padding: 0px;outline:
                      0px;max-width: 100%;box-sizing: border-box
                      !important;overflow-wrap: break-word !important;font-size:
                      17px;"><strong style="-webkit-tap-highlight-color:
                      transparent;margin: 0px;padding: 0px;outline:
                      0px;max-width: 100%;box-sizing: border-box
                      !important;overflow-wrap: break-word !important;"><span
                      style="-webkit-tap-highlight-color: transparent;margin:
                      0px;padding: 0px;outline: 0px;max-width: 100%;box-sizing:
                      border-box !important;overflow-wrap: break-word
                      !important;letter-spacing: 1px;text-decoration-style:
                      solid;text-decoration-color: rgb(87, 107, 149);"><span
                      leaf=""><a style="-webkit-tap-highlight-color: rgba(0, 0,
                      0, 0);margin: 0px;padding: 0px;outline: 0px;color:
                      var(--weui-LINK);text-decoration: none;-webkit-user-drag:
                      none;cursor: default;max-width: 100%;box-sizing:
                      border-box !important;overflow-wrap: break-word
                      !important;"
                      href="https://mp.weixin.qq.com/s?__biz=MzkxNjY0NTcwNA==&amp;mid=2247638789&amp;idx=1&amp;sn=35795bf2883304269eb587860906d33d&amp;scene=21#wechat_redirect"
                      textvalue="超6亿，百年光学巨头再加码中国！‍" data-itemshowtype="0"
                      target="_blank" linktype="text"
                      data-linktype="2">裁员300+，BD也扛不住，饭碗“碎了一地”？</a></span></span></strong></span></h1></section></section></section></section><section
                      style="-webkit-tap-highlight-color: transparent;margin:
                      12px 0px 0px;padding: 0px;outline: 0px;max-width:
                      100%;box-sizing: border-box !important;overflow-wrap:
                      break-word !important;"><section
                      style="-webkit-tap-highlight-color: transparent;margin:
                      0px 8px;padding: 20px 14px;outline: 0px;max-width:
                      100%;box-sizing: border-box !important;overflow-wrap:
                      break-word !important;background-color: rgb(238, 243,
                      255);line-height: 1.75em;"><section
                      style="-webkit-tap-highlight-color: transparent;margin:
                      0px;padding: 0px;outline: 0px;max-width: 100%;box-sizing:
                      border-box !important;overflow-wrap: break-word
                      !important;display: flex;align-items:
                      flex-start;"><section style="-webkit-tap-highlight-color:
                      transparent;margin: 8px 0px 0px;padding: 0px;outline:
                      0px;max-width: 100%;box-sizing: border-box
                      !important;overflow-wrap: break-word !important;width:
                      8px;height: 8px;background-color: rgb(84, 116,
                      194);border-radius: 50%;text-align: justify;"><span
                      leaf="" style="-webkit-tap-highlight-color:
                      transparent;margin: 0px;padding: 0px;outline:
                      0px;max-width: 100%;box-sizing: border-box
                      !important;overflow-wrap: break-word !important;"><br 
                      /></span></section><section data-width="96%"
                      style="-webkit-tap-highlight-color: transparent;margin:
                      0px 0px 0px 12px;padding: 0px;outline: 0px;max-width:
                      100%;box-sizing: border-box !important;overflow-wrap:
                      break-word !important;width: 528px;"><span
                      style="-webkit-tap-highlight-color: transparent;margin:
                      0px;padding: 0px;outline: 0px;max-width: 100%;box-sizing:
                      border-box !important;overflow-wrap: break-word
                      !important;"><strong style="-webkit-tap-highlight-color:
                      transparent;margin: 0px;padding: 0px;outline:
                      0px;max-width: 100%;box-sizing: border-box
                      !important;overflow-wrap: break-word !important;"><span
                      style="-webkit-tap-highlight-color: transparent;margin:
                      0px;padding: 0px;outline: 0px;max-width: 100%;box-sizing:
                      border-box !important;overflow-wrap: break-word
                      !important;text-decoration-style:
                      solid;text-decoration-color: rgb(87, 107, 149);"><span
                      style="-webkit-tap-highlight-color: transparent;margin:
                      0px;padding: 0px;outline: 0px;max-width: 100%;box-sizing:
                      border-box !important;overflow-wrap: break-word
                      !important;letter-spacing: 1px;text-decoration-style:
                      solid;text-decoration-color: rgb(87, 107, 149);"><span
                      leaf=""><a style="-webkit-tap-highlight-color: rgba(0, 0,
                      0, 0);margin: 0px;padding: 0px;outline: 0px;color:
                      var(--weui-LINK);text-decoration: none;-webkit-user-drag:
                      none;cursor: default;max-width: 100%;font-size:
                      17px;box-sizing: border-box !important;overflow-wrap:
                      break-word !important;"
                      href="https://mp.weixin.qq.com/s?__biz=MzkxNjY0NTcwNA==&amp;mid=2247638932&amp;idx=1&amp;sn=4b27c10d76d0a6c70a28a17dfa979be3&amp;scene=21#wechat_redirect"
                      textvalue="‍18.2亿元收购！2025疼痛市场要 “变天”？‍"
                      data-itemshowtype="0" target="_blank" linktype="text"
                      data-linktype="2">5695万元，联影又双叒叕中标了！</a></span></span></span></strong></span></section></section></section></section><section
                      style="-webkit-tap-highlight-color: transparent;margin:
                      12px 0px 0px;padding: 0px;outline: 0px;max-width:
                      100%;box-sizing: border-box !important;overflow-wrap:
                      break-word !important;"><section
                      style="-webkit-tap-highlight-color: transparent;margin:
                      0px 8px;padding: 20px 14px;outline: 0px;max-width:
                      100%;box-sizing: border-box !important;overflow-wrap:
                      break-word !important;background-color: rgb(238, 243,
                      255);line-height: 1.75em;"><section
                      style="-webkit-tap-highlight-color: transparent;margin:
                      0px;padding: 0px;outline: 0px;max-width: 100%;box-sizing:
                      border-box !important;overflow-wrap: break-word
                      !important;display: flex;align-items:
                      flex-start;"><section style="-webkit-tap-highlight-color:
                      transparent;margin: 8px 0px 0px;padding: 0px;outline:
                      0px;max-width: 100%;box-sizing: border-box
                      !important;overflow-wrap: break-word !important;width:
                      8px;height: 8px;background-color: rgb(84, 116,
                      194);border-radius: 50%;text-align: justify;"><span
                      leaf="" style="-webkit-tap-highlight-color:
                      transparent;margin: 0px;padding: 0px;outline:
                      0px;max-width: 100%;box-sizing: border-box
                      !important;overflow-wrap: break-word !important;"><br 
                      /></span></section><section data-width="96%"
                      style="-webkit-tap-highlight-color: transparent;margin:
                      0px 0px 0px 12px;padding: 0px;outline: 0px;max-width:
                      100%;box-sizing: border-box !important;overflow-wrap:
                      break-word !important;width: 528px;"><section
                      style="-webkit-tap-highlight-color: transparent;margin:
                      0px;padding: 0px;outline: 0px;max-width: 100%;box-sizing:
                      border-box !important;overflow-wrap: break-word
                      !important;color: rgb(0, 0, 0);letter-spacing:
                      2px;font-size: 14px;line-height: 1.75em;transform:
                      rotateZ(0deg);"><h1 style="-webkit-tap-highlight-color:
                      transparent;margin: 0px;padding: 0px;outline:
                      0px;font-weight: 400;font-size: 16px;max-width:
                      100%;box-sizing: border-box !important;overflow-wrap:
                      break-word !important;"><span
                      style="-webkit-tap-highlight-color: transparent;margin:
                      0px;padding: 0px;outline: 0px;max-width: 100%;box-sizing:
                      border-box !important;overflow-wrap: break-word
                      !important;"><strong style="-webkit-tap-highlight-color:
                      transparent;margin: 0px;padding: 0px;outline:
                      0px;max-width: 100%;box-sizing: border-box
                      !important;overflow-wrap: break-word !important;"><span
                      style="-webkit-tap-highlight-color: transparent;margin:
                      0px;padding: 0px;outline: 0px;max-width: 100%;box-sizing:
                      border-box !important;overflow-wrap: break-word
                      !important;color: var(--weui-LINK);text-decoration-style:
                      solid;text-decoration-color: rgb(87, 107, 149);"><span
                      style="-webkit-tap-highlight-color: transparent;margin:
                      0px;padding: 0px;outline: 0px;max-width: 100%;box-sizing:
                      border-box !important;overflow-wrap: break-word
                      !important;color: var(--weui-LINK);letter-spacing:
                      1px;text-decoration-style: solid;text-decoration-color:
                      rgb(87, 107, 149);"><span leaf=""><a
                      style="-webkit-tap-highlight-color: rgba(0, 0, 0,
                      0);margin: 0px;padding: 0px;outline: 0px;color:
                      var(--weui-LINK);text-decoration: none;-webkit-user-drag:
                      none;cursor: default;max-width: 100%;box-sizing:
                      border-box !important;overflow-wrap: break-word
                      !important;"
                      href="https://mp.weixin.qq.com/s?__biz=MzkxNjY0NTcwNA==&amp;mid=2247639343&amp;idx=1&amp;sn=96a750757f8c936c68b520437e77e1ec&amp;scene=21#wechat_redirect"
                      textvalue="‍上市首日市值破109亿，医疗科技IPO市场迎来新标杆‍"
                      data-itemshowtype="0" target="_blank" linktype="text"
                      data-linktype="2">上市首日市值破109亿，医疗科技IPO市场迎来新标杆</a></span></span></span></strong></span></h1></section></section></section></section></section></section></section><section
                      nodeleaf="" style="-webkit-tap-highlight-color:
                      transparent;margin: 0px 8px;padding: 0px;outline:
                      0px;max-width: 100%;box-sizing: border-box
                      !important;overflow-wrap: break-word
                      !important;font-style: normal;font-variant-ligatures:
                      normal;font-variant-caps: normal;font-weight:
                      400;letter-spacing: 0.544px;orphans: 2;text-align:
                      justify;text-indent: 0px;text-transform: none;widows:
                      2;word-spacing: 0px;-webkit-text-stroke-width:
                      0px;white-space: normal;text-decoration-thickness:
                      initial;text-decoration-style:
                      initial;text-decoration-color: initial;background-color:
                      rgb(255, 255, 255);color: rgb(34, 34, 34);font-size:
                      15px;font-family: system-ui, -apple-system,
                      BlinkMacSystemFont, &quot;Helvetica Neue&quot;,
                      &quot;PingFang SC&quot;, &quot;Hiragino Sans GB&quot;,
                      &quot;Microsoft YaHei UI&quot;, &quot;Microsoft
                      YaHei&quot;, Arial, sans-serif;line-height: 1.75em;"><img
                      data-src="https://mmbiz.qpic.cn/mmbiz_gif/3aNX9kq7JM1zJ8XDwKQMtQtPlo00L5urUIm46Y71dS9KGXkyQ1UlgI8KSMhbkmBLZJoEQO51WkHVrQ5FRzOVAg/640?wx_fmt=gif&amp;from=appmsg&amp;wxfrom=5&amp;wx_lazy=1&amp;tp=webp"
                      alt="图片" class="rich_pages wxw-img __bg_gif"
                      data-ratio="0.42539388322520855" data-type="gif"
                      data-w="1079" style="-webkit-tap-highlight-color:
                      transparent;margin: 0px;padding: 0px;outline:
                      0px;max-width: 100%;box-sizing: border-box
                      !important;overflow-wrap: break-word
                      !important;vertical-align: bottom;height: auto
                      !important;border-radius: 8px;font-size:
                      16px;letter-spacing: 0.578px;text-align:
                      center;background-size: 16px !important;visibility:
                      visible !important;width: 645px !important;"
                      data-cropselx1="0" data-cropselx2="562" data-cropsely1="0"
                      data-cropsely2="239" data-backw="562" data-backh="239"
                      data-imgfileid="100157067"  /></section><section
                      nodeleaf="" style="-webkit-tap-highlight-color:
                      transparent;margin: 0px 8px;padding: 0px;outline:
                      0px;max-width: 100%;box-sizing: border-box
                      !important;overflow-wrap: break-word
                      !important;font-style: normal;font-variant-ligatures:
                      normal;font-variant-caps: normal;font-weight:
                      400;letter-spacing: 0.544px;orphans: 2;text-align:
                      justify;text-indent: 0px;text-transform: none;widows:
                      2;word-spacing: 0px;-webkit-text-stroke-width:
                      0px;white-space: normal;text-decoration-thickness:
                      initial;text-decoration-style:
                      initial;text-decoration-color: initial;background-color:
                      rgb(255, 255, 255);color: rgb(34, 34, 34);font-size:
                      15px;font-family: system-ui, -apple-system,
                      BlinkMacSystemFont, &quot;Helvetica Neue&quot;,
                      &quot;PingFang SC&quot;, &quot;Hiragino Sans GB&quot;,
                      &quot;Microsoft YaHei UI&quot;, &quot;Microsoft
                      YaHei&quot;, Arial, sans-serif;line-height: 1.75em;"><img
                      data-src="https://mmbiz.qpic.cn/mmbiz_png/3aNX9kq7JM1fKnVgBdNzM2p3x1l4kgvibgK6wFJmkJ8PGyDPVN05pan6k9tUIPunQQvicyVn6qnlicEjoCiaouycqw/640?wx_fmt=other&amp;from=appmsg&amp;wxfrom=5&amp;wx_lazy=1&amp;wx_co=1&amp;tp=webp"
                      alt="图片" class="rich_pages wxw-img"
                      data-ratio="0.21296296296296297" data-s="300,640"
                      data-type="png" data-w="1080"
                      style="-webkit-tap-highlight-color: transparent;margin:
                      0px;padding: 0px;outline: 0px;max-width: 100%;box-sizing:
                      border-box !important;overflow-wrap: break-word
                      !important;vertical-align: bottom;height: auto
                      !important;border-radius: 8px;background-size: 16px
                      !important;visibility: visible !important;width: 645px
                      !important;" data-backw="562" data-backh="120"
                      data-imgfileid="100157065" 
                      /></section></section></section><p style="display:
                      none;"><mp-style-type data-value="3"></mp-style-type></p>
                    pubtime: '2025-04-13 17:19:59'
                '2':
                  summary: 文章被删除
                  value:
                    cost_money: 0.03
                    remain_money: 4261.375
                    code: 101
                    msg: 文章打不开，原因为：该内容已被发布者删除
                '3':
                  summary: 成功示例
                  value:
                    cost_money: 0.03
                    remain_money: 4261.375
                    code: 101
                    msg: 文章打不开，原因为：该内容已被发布者删除
                '4':
                  summary: 示例 1
                  value:
                    cost_money: 0.03
                    remain_money: 31202.794
                    code: 101
                    msg: 文章打不开，原因为：文章未通过腾讯审核，暂时无法查看。
          headers: {}
          x-apifox-name: 成功
        x-200:文章被删除:
          description: ''
          content:
            application/json:
              schema:
                type: object
                properties:
                  cost_money:
                    type: number
                  remain_money:
                    type: number
                  code:
                    type: integer
                  msg:
                    type: string
                required:
                  - cost_money
                  - remain_money
                  - code
                  - msg
                x-apifox-orders:
                  - cost_money
                  - remain_money
                  - code
                  - msg
              example:
                code: 101
                msg: 文章打不开，原因为：该内容已被发布者删除
                content_text: ''
                cost_money: 0.04
                remain_money: 17255.424
          headers: {}
          x-apifox-name: 文章被删除
        x-200:文章审核失败:
          description: ''
          content:
            application/json:
              schema:
                type: object
                properties:
                  cost_money:
                    type: number
                  remain_money:
                    type: number
                  code:
                    type: integer
                  msg:
                    type: string
                required:
                  - cost_money
                  - remain_money
                  - code
                  - msg
                x-apifox-orders:
                  - cost_money
                  - remain_money
                  - code
                  - msg
              example:
                code: 101
                msg: 文章打不开，原因为：文章审核失败。
                content_text: ''
                cost_money: 0.04
                remain_money: 17255.424
          headers: {}
          x-apifox-name: 文章审核失败
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
      x-run-in-apifox: https://app.apifox.com/web/project/4919579/apis/api-220474677-run
components:
  schemas: {}
  securitySchemes: {}
servers:
  - url: https://www.dajiala.com
    description: 正式环境
security: []

```
