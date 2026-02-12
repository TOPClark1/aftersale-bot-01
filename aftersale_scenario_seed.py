"""Seed data for after-sale situation library."""

SCENARIO_SEEDS = [
    {
        "scenario_key": "delay_no_update",
        "tags": "#延迟未更新,#未送达",
        "language": "en",
        "title": "延迟未更新 / 未送达",
        "reply_template": """Hi there,
I’m really sorry for the delay. I’ve already contacted the courier — sometimes their system takes longer to update even when the package is still moving. Please give it a little more time; tracking should update soon.
Thank you so much for your patience!
Best,
Clark""",
    },
    {
        "scenario_key": "lost_package_insurance",
        "tags": "#丢件,#保险理赔",
        "language": "en",
        "title": "丢件 / 保险理赔",
        "reply_template": """Hi there,
I just checked your order, and it looks like the courier lost your package. I’m really sorry about that.
Since you purchased shipping insurance, please file a claim for a refund or replacement here 👇
👉 https://www.imfish.com/pages/worry-free-purchase
This ensures your refund is processed smoothly and securely.
Best,
Clark""",
    },
    {
        "scenario_key": "delivered_not_received",
        "tags": "#显示送达未收到,#误投",
        "language": "en",
        "title": "显示送达未收到 / 误投",
        "reply_template": """Hi there,
The tracking shows your package was delivered, and the courier confirmed delivery on their end.
Unfortunately, we can’t take further action once it’s marked as delivered. If you purchased insurance, please file a claim here 👇
👉 https://www.imfish.com/pages/worry-free-purchase
Otherwise, please check with your local post office or neighbors — sometimes it’s left nearby.
Best,
Clark""",
    },
    {
        "scenario_key": "reship_same_tracking",
        "tags": "#原单补发,#重发",
        "language": "en",
        "title": "原单补发 / 重发",
        "reply_template": """Hi there,
I’m really sorry for the delay. It looks like we had a system issue between our warehouse and the local post office that caused this problem, and for that, I am truly sorry.
Your order has been reprocessed and reshipped under the same tracking number according to the courier’s policy. You should start seeing new tracking updates within 1–2 days.
As a further apology for this inconvenience, please accept this mfish5 coupon for your next purchase.
Thank you for your patience!
Best,
Clark""",
    },
    {
        "scenario_key": "wait_for_update",
        "tags": "#等待更新,#建议等待",
        "language": "en",
        "title": "等待更新 / 建议等待",
        "reply_template": """Hi there,
Thanks for checking in! Sometimes tracking updates are delayed even when the package is still on the way. We’ve seen a few cases where it didn’t move for 10–15 days and then suddenly got delivered.
Please give it a bit more time — I’m monitoring it and will update you once there’s movement.
Best,
Clark""",
    },
    {
        "scenario_key": "wrong_color",
        "tags": "#发错颜色,#错误发货",
        "language": "en",
        "title": "发错颜色 / 错误发货",
        "reply_template": """Hi there,
I’m really sorry — our system shows the correct item, but it looks like the warehouse made a sorting mistake. I’ve already warned them about this issue.
As an apology, I can offer a $3 refund, or we can discuss an exchange depending on stock.
Best,
Clark""",
    },
    {
        "scenario_key": "damaged_not_working",
        "tags": "#产品损坏,#不工作",
        "language": "en",
        "title": "产品损坏 / 不工作",
        "reply_template": """Hi there,
I’m really sorry to hear that your item isn’t working. Could you please send a short video showing the issue? And your order id! Once I receive it, I’ll verify and arrange a replacement right away. And please be noticed that we only deal with our website aftersale!
Best,
Clark""",
    },
    {
        "scenario_key": "tiktok_order",
        "tags": "#TikTok订单,#第三方平台",
        "language": "en",
        "title": "TikTok订单 / 第三方平台",
        "reply_template": """Hi there,
Thank you for sharing the details! It looks like your order was placed through TikTok Shop, so we’re unable to process after-sales directly.
Please contact TikTok Shop support via the app — they’ll assist with your replacement or refund.
Best,
Clark""",
    },
    {
        "scenario_key": "amazon_order",
        "tags": "#亚马逊订单,#第三方平台",
        "language": "en",
        "title": "亚马逊订单 / 第三方平台",
        "reply_template": """Hello,
Thank you for sharing the details! It appears your order was placed through Amazon, so we are unable to directly handle after-sales matters.
Please contact Amazon customer service through the app—they will assist you with the exchange or refund process.
Best regards,
Clark""",
    },
    {
        "scenario_key": "insurance_policy_explain",
        "tags": "#保险政策解释,#客户抱怨要填表",
        "language": "en",
        "title": "保险政策解释 / 客户抱怨要填表",
        "reply_template": """Hi there,
I understand this feels inconvenient, and I’m really sorry. However, under the Worry-Free Protection policy, all claims must be filed through the insurance form — we’re not permitted to issue direct refunds or replacements once it’s active.
This protects both sides and guarantees your refund.
👉 https://www.imfish.com/pages/worry-free-purchase
Best,
Clark""",
    },
    {
        "scenario_key": "emotion_scam_complaint",
        "tags": "#客户指责诈骗,#情绪安抚",
        "language": "en",
        "title": "客户指责诈骗 / 情绪安抚",
        "reply_template": """Hi there,
I completely understand your frustration, and I’m truly sorry this experience has made you feel that way. Please rest assured we’re not a scam company — you’ve successfully received previous orders from us, and we’re doing everything we can to resolve this issue.
Sometimes courier systems fail to update or mis-handle shipments, but I promise we’re on it.
Best,
Clark""",
    },
    {
        "scenario_key": "replacement_tracking_notice",
        "tags": "#补发单号通知,#情绪安抚",
        "language": "en",
        "title": "补发单号通知 / 情绪安抚",
        "reply_template": """Hi there,
Good news — your replacement has just been shipped out! 🎉
Here’s your tracking number: []
You can follow it directly on the carrier’s website for updates.
Please allow a little time for the first scan to appear in the system.
Thank you again for your patience and understanding!
Best,
Clark""",
    },
    {
        "scenario_key": "charger_not_powerbank",
        "tags": "#误会充电器是充电宝,#140W/65W",
        "language": "en",
        "title": "误会充电器是充电宝（140W/65W）",
        "reply_template": """Hi there,
Just to clarify — the mfish 140W/65W is a wall charger, not a power bank.
It does not store power, so it will shut off unless it’s plugged into a wall outlet.
If you can send me a short video of how you’re using it, I’ll help you check it step by step.
Best,
Clark""",
    },
    {
        "scenario_key": "wrong_port_no_fast_charge",
        "tags": "#插错口不快充,#不充电",
        "language": "en",
        "title": "插错口不快充 / 不充电",
        "reply_template": """Hi there,
From many cases we’ve seen, this usually happens when the device is plugged into the output-only port instead of the fast-charging port.
Could you send me a short video showing which port you're using?
I’ll help you confirm immediately.
Best,
Clark""",
    },
    {
        "scenario_key": "flashlight_temp_sensor",
        "tags": "#闪光灯温度感应,#Funky,#模块",
        "language": "en",
        "title": "闪光灯温度感应（Funky / 模块）",
        "reply_template": """Hi there,
The flashlight module uses a temperature-sensitive button, so it may not respond when cold.
Try warming your fingertip and tapping again stay at least 5s — it will activate normally.
We are improving this in the next version.
Best,
Clark""",
    },
    {
        "scenario_key": "mystery_box_capacity",
        "tags": "#盲盒容量误会,#10000mAh无数字屏",
        "language": "en",
        "title": "盲盒容量误会（10,000mAh 无数字屏）",
        "reply_template": """Hi there,
The mystery box version is the simplified model — it is 10,000mAh and does not include the digital display.
If you need a version with a screen or higher capacity, feel free to let me know.
Best,
Clark""",
    },
    {
        "scenario_key": "gift_no_aftersale",
        "tags": "#赠品无售后,#铠甲线,#盲盒赠品",
        "language": "en",
        "title": "赠品无售后（铠甲线 / 盲盒赠品）",
        "reply_template": """Hi there,
The free cable included in the promotion is a simplified gift version, so it does not include full after-sales coverage.
If it’s still usable, we’re not able to replace it.
Best,
Clark""",
    },
    {
        "scenario_key": "coupon_not_stackable",
        "tags": "#优惠券不能叠加,#newmfisher10",
        "language": "en",
        "title": "优惠券不能叠加",
        "reply_template": """Hi there,
Our discount codes are stand-alone codes and cannot be stacked with other promotions, bundles, or automatic discounts — that’s why the system couldn’t apply it.
Best,
Clark""",
    },
    {
        "scenario_key": "address_change_after_12h",
        "tags": "#地址填错超过12小时无法修改",
        "language": "en",
        "title": "地址填错超过12小时无法修改",
        "reply_template": """Hi there,
We can only change the shipping address within 12 hours of the order being placed.
After the package is shipped, the address cannot be changed from our side — please contact the courier for interception.
Best,
Clark""",
    },
    {
        "scenario_key": "weekend_warehouse_closed",
        "tags": "#仓库周六周日不发货,#tracking不更新",
        "language": "en",
        "title": "仓库周六周日不发货",
        "reply_template": """Hi there,
Your order was placed over the weekend — our warehouse is closed on Saturday and Sunday, so the package will be scanned once they reopen.
Thank you for your patience!
Best,
Clark""",
    },
    {
        "scenario_key": "led_button_operation",
        "tags": "#灯光不会关,#按键按不下,#E-Tank,#Mushroom",
        "language": "en",
        "title": "灯光不会关 / 按键按不下",
        "reply_template": """Hi there,
The button is designed to be shallow.
A light tap changes colors; long-press for 5 seconds to turn the LED ring off completely.
Best,
Clark""",
    },
    {
        "scenario_key": "charging_mode_explain",
        "tags": "#电磁兽充电模式说明,#快充,#慢充",
        "language": "en",
        "title": "电磁兽充电模式说明",
        "reply_template": """Hi there,
Solid light = Fast charging mode
Double-tap the button → Breathing light = Low-current mode (for earbuds & watches).
Best,
Clark""",
    },
    {
        "scenario_key": "wireless_charge_issue",
        "tags": "#无线充电不工作,#MagSafe不吸附",
        "language": "en",
        "title": "无线充电不工作 / MagSafe不吸附",
        "reply_template": """Hi there,
Could you please send a short video showing the issue?
Most MagSafe problems are related to:
• phone case thickness
• alignment
• coil position
Once I see the video, I’ll help you fix or replace it.
Best,
Clark""",
    },
    {
        "scenario_key": "opened_package_no_return",
        "tags": "#包装已开无法退货,#退货政策",
        "language": "en",
        "title": "包装已开无法退货",
        "reply_template": """Hi there,
We can only accept returns if the product is completely unopened with full original packaging.
Once opened, it cannot be restocked, so a return isn’t possible.
If you’d like, I can offer a small courtesy refund instead.
Best,
Clark""",
    },
    {
        "scenario_key": "extra_compensation_request",
        "tags": "#要求额外补偿,#要求赔偿",
        "language": "en",
        "title": "要求额外补偿 / 要求赔偿",
        "reply_template": """Hi there,
I completely understand your frustration.
While we can’t offer compensation beyond the order itself, I can provide a goodwill discount code for your next purchase: mfish5.
Best,
Clark""",
    },
    {
        "scenario_key": "replacement_approved",
        "tags": "#确认问题成立后安排补发,#ReplacementApproved",
        "language": "en",
        "title": "确认问题成立后—安排补发",
        "reply_template": """Hi there,
Thank you for sending the video — I’ve reviewed it carefully, and the issue is confirmed.
We will arrange a replacement for you right away.
I'm truly sorry you've encountered this issue. As with all electronics, yield rate issues can occur. We're working with the factory to resolve it! Once again, my apologies.
Before we ship it out, could you please provide your full shipping address (name + street + city + state + ZIP)?
Once the replacement is sent, I’ll share the tracking number with you so you can follow the delivery.
Thank you for your patience — I’ll take care of this for you.
Best,
Clark""",
    },
    {
        "scenario_key": "refund_unopened",
        "tags": "#需要退货退款,#产品未开封",
        "language": "en",
        "title": "需要退货退款（产品未开封）",
        "reply_template": """Hi, sorry it arrived later than expected.
To generate your FedEx return label for a full refund, please send:
1. A photo showing the package(s) unopened/sealed
2. The package dimensions (L × W × H)
3. The packed weight
4. Your return-from address
Once I have these, I’ll create the label and send it over. After you receive it, please drop the package off at a FedEx location. We’ll process the full refund after it’s received and checked in.
Best,
Clark""",
    },
    {
        "scenario_key": "seel_claim_delivered_not_received",
        "tags": "#显示送达没收到,#找保险,#Seel",
        "language": "en",
        "title": "显示送达没收到（找保险）",
        "reply_template": """Hi, sorry about this.
Our tracking shows the package was marked delivered, but since you didn’t receive it, the next step is to file a claim through Seel Shipping Protection for a missing package — Seel will refund the full amount according to their policy. We don’t control the carrier once it’s in their network.
Please submit your claim here: https://resolve.seel.com
Select “Delivered but not received” and enter your order number + email to complete the claim.
Best,
Clark""",
    },
    {
        "scenario_key": "return_non_quality",
        "tags": "#不符合需求,#买错,#不喜欢,#非质量原因",
        "language": "en",
        "title": "非质量原因退货",
        "reply_template": """Hi, sorry about that — I understand it’s not what you needed.
We can help you return your order.
To generate your FedEx return label, please reply with:
1. Item(s) to return: [Item list]
2. Confirm items are unused and in original packaging
3. Outer box dimensions (L × W × H) and packed weight
4. Return-from address (the address you’ll ship from)
Once received, we’ll send the label. Please drop off at a FedEx location. After our warehouse receives and checks the return, we’ll process the refund.
Best,
Clark""",
    },
    {
        "scenario_key": "chargeback_process",
        "tags": "#银行拒付,#拒付流程",
        "language": "zh",
        "title": "银行拒付处理",
        "reply_template": """1. 首先确认是否可以接受拒付（是否与客户有过沟通，判断主要责任方）。
2. 无沟通记录、非我方过错可在独立站订单页面提交相关证据。""",
    },
    {
        "scenario_key": "case_closed_thanks",
        "tags": "#已处理完成,#客户表示感谢",
        "language": "en",
        "title": "已处理完成（客户表示感谢）",
        "reply_template": """Hi there,
Thank you so much for liking it, it's an honor to be chosen by you, have a great day!
Best,
Clark""",
    },
    {
        "scenario_key": "replacement_over_return",
        "tags": "#确认问题沟通补发,#避免寄回",
        "language": "en",
        "title": "确认问题后建议补发",
        "reply_template": """Hello, sorry about this.
But returns will incur high shipping costs, and there is a risk of loss during the return process. If the package is lost, no refund will be issued. If I send you a new product, that would be the best outcome. Do you think that's okay? If you agree, I will ship it to you immediately.
Best,
Clark""",
    },
]
