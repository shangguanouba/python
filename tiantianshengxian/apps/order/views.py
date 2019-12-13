from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import JsonResponse
from django.db import transaction
from django.views.generic import View
from django.conf import settings

from goods.models import GoodsSKU
from order.models import OrderInfo, OrderGoods
from user.models import Address

from django_redis import get_redis_connection
from utils.mixin import LoginRequiredMixin
from datetime import datetime
from alipay import AliPay
import os

# Create your views here.


# /order/place
class OrderPlaceView(LoginRequiredMixin, View):
    """提交订单页面显示"""
    def post(self, request):
        """提交订单页面显示"""
        # 获取登录的用户
        user = request.user
        # 获取参数sku_ids
        sku_ids = request.POST.getlist('sku_ids')
        # 校验参数
        if not sku_ids:
            # 跳转到购物车页面
            return redirect(reverse('cart:show'))
        # 获取redis链接
        conn = get_redis_connection('default')
        cart_key = 'cart_%d' % user.id
        # 遍历sku_ids获取用户购买商品的信息
        skus = []
        total_count = 0
        total_price = 0
        for sku_id in sku_ids:
            # 根据商品id获取商品的信息
            sku = GoodsSKU.objects.get(id=sku_id)
            # 根据商品id获取商品的数目
            count = conn.hget(cart_key, sku_id)
            # 计算商品小计
            amount = sku.price * int(count)
            # 动态给sku增加属性
            sku.count = int(count)
            sku.amount = amount
            # 追加
            skus.append(sku)
            total_count += int(count)
            total_price += amount

        # 运费：实际开发的时候，属于一个子系统
        transit_price = 10  # 写死
        # 实际付款
        total_pay = total_price + transit_price
        # 获取用户的收件地址
        addrs = Address.objects.filter(user=user)
        # 组织上下文
        sku_ids = ','.join(sku_ids)  # [1,2,3] ->1,2,3  拼接出字符串
        context = {
            'skus': skus,
            'total_count': total_count,
            'total_price': total_price,
            'transit_price': transit_price,
            'total_pay': total_pay,
            'addrs': addrs,
            'sku_ids': sku_ids
        }
        # 使用模板
        return render(request, 'place_order.html', context)


# /order/commit    悲观锁处理并发问题： 冲突表多的时候使用悲观锁
class OrderCommitView(View):
    """创建订单"""
    @transaction.atomic
    def post(self, request):
        """创建订单"""
        # 判断用户是否登录
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({'res': 0, 'errmsg': '请先登录'})
        # 接收参数
        addr_id = request.POST.get('addr_id')
        pay_method = request.POST.get('pay_method')
        sku_ids = request.POST.get('sku_ids')
        # 参数完整性校验
        if not all([addr_id, pay_method, sku_ids]):
            return JsonResponse({'res': 1, 'errmsg': '数据不完整'})
        # 校验支付方式
        if pay_method not in OrderInfo.PAY_METHODS.keys():
            return JsonResponse({'res': 2, 'errmsg': '请选择正确的支付方式'})
        # 校验地址
        try:
            addr = Address.objects.get(id=addr_id)
        except Address.DoesNotExist:
            return JsonResponse({'res': 3, 'errmsg': '地址不存在'})

        # todo:创建订单核心业务
        # 组织参数
        order_id = datetime.now().strftime('%Y%m%d%H%M%S')+str(user.id)  # 订单id: 20191122181630+用户id
        transit_price = 10  # 运费
        total_count = 0  # 总数目
        total_price = 0  # 总金额

        # 创建事务的保存点
        save_id = transaction.savepoint()
        try:
            # todo:向df_order_info表中添加一条数据
            order = OrderInfo.objects.create(order_id=order_id,
                                             user=user,
                                             addr=addr,
                                             pay_method=pay_method,
                                             total_count=total_count,
                                             total_price=total_price,
                                             transit_price=transit_price)
            # todo:用户的订单表中有几个商品，向df_order_goods表中加入几条记录
            conn = get_redis_connection('default')
            cart_key = 'cart_%d' % user.id
            sku_ids = sku_ids.split(',')
            for sku_id in sku_ids:
                # 获取商品信息
                try:
                    sku = GoodsSKU.objects.select_for_update().get(id=sku_id)  # 添加悲观锁
                except:
                    transaction.rollback(save_id)
                    return JsonResponse({'res': 4, 'errmsg': '商品不存在'})
                # 从redis中获取用户所购买的商品数据量
                count = conn.hget(cart_key, sku_id)

                # todo: 判断商品库存
                if int(count) > sku.stock:
                    return JsonResponse({'res': 6, 'errmsg': '商品库存不足'})

                # todo:向df_order_goods表中加入一条记录
                OrderGoods.objects.create(order=order,
                                          sku=sku,
                                          count=count,
                                          price=sku.price)
                # todo:更新商品库存库存和销量
                sku.stock -= int(count)
                sku.sales += int(count)
                sku.save()
                # todo：累加计算订单商品的总数量和总价格
                amount = sku.price*int(count)
                total_count += int(count)
                total_price += amount

            # todo:更新订单表中的商品总数量和总价格
            order.total_count = total_count
            order.total_price = total_price
            order.save()
        except Exception as e:
            transaction.rollback(save_id)
            return JsonResponse({'res': 7, 'errmsg': '下单失败'})

        # 提交事务
        transaction.savepoint_commit(save_id)

        # TODO：清除购物车中对应的记录
        conn.hdel(cart_key, *sku_ids)  # *代表把sku_ids列表拆分

        # 返回应答
        return JsonResponse({'res': 5, 'message': '创建成功'})


# /order/commit    乐观锁处理并发问题:冲突比较少的时候使用乐观锁，没有加锁和释放锁的开销
"""
class OrderCommitView1(View):
    

    @transaction.atomic
    def post(self, request):
        
        # 判断用户是否登录
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({'res': 0, 'errmsg': '请先登录'})
        # 接收参数
        addr_id = request.POST.get('addr_id')
        pay_method = request.POST.get('pay_method')
        sku_ids = request.POST.get('sku_ids')
        # 参数完整性校验
        if not all([addr_id, pay_method, sku_ids]):
            return JsonResponse({'res': 1, 'errmsg': '数据不完整'})
        # 校验支付方式
        if pay_method not in OrderInfo.PAY_METHODS.keys():
            return JsonResponse({'res': 2, 'errmsg': '请选择正确的支付方式'})
        # 校验地址
        try:
            addr = Address.objects.get(id=addr_id)
        except Address.DoesNotExist:
            return JsonResponse({'res': 3, 'errmsg': '地址不存在'})

        # todo:创建订单核心业务
        # 组织参数
        order_id = datetime.now().strftime('%Y%m%d%H%M%S') + str(user.id)  # 订单id: 20191122181630+用户id
        transit_price = 10  # 运费
        total_count = 0  # 总数目
        total_price = 0  # 总金额

        # 创建事务的保存点
        save_id = transaction.savepoint()
        try:
            # todo:向df_order_info表中添加一条数据
            order = OrderInfo.objects.create(order_id=order_id,
                                             user=user,
                                             addr=addr,
                                             pay_method=pay_method,
                                             total_count=total_count,
                                             total_price=total_price,
                                             transit_price=transit_price)
            # todo:用户的订单表中有几个商品，向df_order_goods表中加入几条记录
            conn = get_redis_connection('default')
            cart_key = 'cart_%d' % user.id
            sku_ids = sku_ids.split(',')
            for sku_id in sku_ids:
                for i in range(3):
                    # 获取商品信息
                    try:
                        sku = GoodsSKU.objects.get(id=sku_id)
                    except:
                        transaction.rollback(save_id)
                        return JsonResponse({'res': 4, 'errmsg': '商品不存在'})
                    # 从redis中获取用户所购买的商品数据量
                    count = conn.hget(cart_key, sku_id)

                    # todo: 判断商品库存
                    if int(count) > sku.stock:
                        return JsonResponse({'res': 6, 'errmsg': '商品库存不足'})
                    # todo:更新商品库存库存和销量
                    orgin_stock = sku.stock
                    new_stock = orgin_stock - int(count)
                    new_sales = sku.sales + int(count)
                    # 返回受影响的行数
                    res = GoodsSKU.objects.filter(id=sku_id, stock=orgin_stock).update(stock=new_stock, sales= new_sales)
                    if res == 0:
                        if i == 2:
                            # 尝试三次
                            transaction.savepoint_rollback(save_id)
                            return JsonResponse({'res': 7, 'errmsg': '商品库存不足,下单失败'})
                        continue
                    # todo:向df_order_goods表中加入一条记录
                    OrderGoods.objects.create(order=order,
                                              sku=sku,
                                              count=count,
                                              price=sku.price)

                    # todo：累加计算订单商品的总数量和总价格
                    amount = sku.price * int(count)
                    total_count += int(count)
                    total_price += amount
                    # 跳出循环
                    break

            # todo:更新订单表中的商品总数量和总价格
            order.total_count = total_count
            order.total_price = total_price
            order.save()
        except Exception as e:
            transaction.rollback(save_id)
            return JsonResponse({'res': 7, 'errmsg': '下单失败'})

        # 提交事务
        transaction.savepoint_commit(save_id)

        # TODO：清除购物车中对应的记录
        conn.hdel(cart_key, *sku_ids)  # *代表把sku_ids列表拆分

        # 返回应答
        return JsonResponse({'res': 5, 'message': '创建成功'})
"""


# /order/pay
class OrderPayView(View):
    """订单支付"""
    def post(self, request):
        """订单支付"""
        # 用户是否登录
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({'res': 0 , 'errmsg': '用户未登录'})
        # 接收参数
        order_id = request.POST.get('order_id')
        # 校验参数
        if not order_id:
            return JsonResponse({'res': 1 , 'errmsg': '无效的订单id'})
        try:
            order = OrderInfo.objects.get(order_id=order_id, user=user, pay_method=3, order_status=1)
        except OrderInfo.DoesNotExist:
            return JsonResponse({'res': 2 , 'errmsg': '订单错误'})
        # 业务处理：使用python sdk 调用支付宝接口
        # 初始化

        app_private_key_string = open(os.path.join(settings.BASE_DIR, 'apps/order/app_private_key.pem')).read()
        alipay_public_key_string = open(os.path.join(settings.BASE_DIR, 'apps/order/alipay_public_key.pem')).read()

        app_private_key_string == """
            -----BEGIN RSA PRIVATE KEY-----
            base64 encoded content
            -----END RSA PRIVATE KEY-----
        """

        alipay_public_key_string == """
            -----BEGIN PUBLIC KEY-----
            base64 encoded content
            -----END PUBLIC KEY-----
        """

        alipay = AliPay(
            appid="2016101500694289",  # 应用id
            app_notify_url=None,  # 默认回调url
            app_private_key_string=app_private_key_string,
            # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            alipay_public_key_string=alipay_public_key_string,
            sign_type="RSA2",  # RSA 或者 RSA2
            debug=True  # 默认False
        )
        # 调用支付接口
        # 电脑网站支付，需要跳转到https://openapi.alipaydev.com/gateway.do? + order_string
        total_pay = order.total_price+order.transit_price
        order_string = alipay.api_alipay_trade_page_pay(
            out_trade_no=order_id,  # 订单id
            total_amount=int(total_pay),  # 支付总金额
            subject='天天生鲜%s' % order_id,  # 标题
            return_url=None,
            notify_url=None  # 可选, 不填则使用默认notify url
        )
        # 返回应答
        pay_url = 'https://openapi.alipaydev.com/gateway.do?' + order_string
        return JsonResponse({'res': 3, 'pay_url': pay_url})


class OrderCheckView(View):
    """查看订单支付结果"""
    def post(self, request):
        """查看订单支付结果"""
        # 用户是否登录
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({'res': 0, 'errmsg': '用户未登录'})
        # 接收参数
        order_id = request.POST.get('order_id')
        # 校验参数
        if not order_id:
            return JsonResponse({'res': 1, 'errmsg': '无效的订单id'})
        try:
            order = OrderInfo.objects.get(order_id=order_id, user=user, pay_method=3, order_status=1)
        except OrderInfo.DoesNotExist:
            return JsonResponse({'res': 2, 'errmsg': '订单错误'})
        # 业务处理：使用python sdk 调用支付宝接口
        # 初始化

        app_private_key_string = open(os.path.join(settings.BASE_DIR, 'apps/order/app_private_key.pem')).read()
        alipay_public_key_string = open(os.path.join(settings.BASE_DIR, 'apps/order/alipay_public_key.pem')).read()

        app_private_key_string == """
                   -----BEGIN RSA PRIVATE KEY-----
                   base64 encoded content
                   -----END RSA PRIVATE KEY-----
               """

        alipay_public_key_string == """
                   -----BEGIN PUBLIC KEY-----
                   base64 encoded content
                   -----END PUBLIC KEY-----
               """

        alipay = AliPay(
            appid="2016101500694289",  # 应用id
            app_notify_url=None,  # 默认回调url
            app_private_key_string=app_private_key_string,
            # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            alipay_public_key_string=alipay_public_key_string,
            sign_type="RSA2",  # RSA 或者 RSA2
            debug=True  # 默认False
        )

        # 调用支付宝的交易查询接口
        while True:
            response = alipay.api_alipay_trade_query(order_id)
            # response = {
            #         "trade_no": "2017032121001004070200176844",  # 支付宝交易号
            #         "code": "10000",  # 接口调用是否成功
            #         "invoice_amount": "20.00",
            #         "open_id": "20880072506750308812798160715407",
            #         "fund_bill_list": [
            #             {
            #                 "amount": "20.00",
            #                 "fund_channel": "ALIPAYACCOUNT"
            #             }
            #         ],
            #         "buyer_logon_id": "csq***@sandbox.com",
            #         "send_pay_date": "2017-03-21 13:29:17",
            #         "receipt_amount": "20.00",
            #         "out_trade_no": "out_trade_no15",
            #         "buyer_pay_amount": "20.00",
            #         "buyer_user_id": "2088102169481075",
            #         "msg": "Success",
            #         "point_amount": "0.00",
            #         "trade_status": "TRADE_SUCCESS",  # 支付结果
            #         "total_amount": "20.00"
            #     }
            code = response.get('code')
            if code == '10000' and response.get('trade_status') == 'TRADE_SUCCESS' :
                # 支付成功
                # 获取支付宝交易号
                trade_no = response.get('trade_no')
                # 更新订单状态
                order.trade_no = trade_no
                order.order_status = 4
                order.save()
                # 返回结果
                return JsonResponse({'res': 3, 'message': '支付成功'})
            elif code == '40004' or (code == '10000' and response.get('trade_status') == 'WAIT_BUYER_PAY') :
                # 等待买家付款
                import  time
                time.sleep(5)
                continue
            else:
                # 支付出错
                return JsonResponse({'res': 4, 'errmsg': '支付失败'})


class CommentView(View):
    """订单评论"""
    def get(self, request, order_id):
        """提供评论页面"""
        user = request.user
        # 数据校验
        if not order_id:
            return redirect(reverse('user:order'))
        try:
            order = OrderInfo.objects.get(order_id=order_id, user=user)
        except OrderInfo.DoesNotExist:
            return redirect(reverse('user:order'))
        # 根据订单的状态获取订单的状态标题
        order.status_name = OrderInfo.ORDER_STATUS[order.order_status]
        # 获取订单商品信息
        order_skus = OrderGoods.objects.filter(order_id=order_id)
        for order_sku in order_skus:
            # 计算商品小计
            amount = order_sku.count*order_sku.price
            # 动态给order_sku增加amount属性
            order_sku.amount = amount
        # 动态给order增加属性order_skus，保存订单商品信息
        order.order_skus = order_skus
        # 使用模板
        return render(request, 'order_comment.html', {'order': order})

    def post(self, request, order_id):
        """处理评论内容"""
        user = request.user
        # 数据校验
        if not order_id:
            return redirect(reverse('user:order'))
        try:
            order = OrderInfo.objects.get(order_id=order_id, user=user)
        except OrderInfo.DoesNotExist:
            return redirect(reverse('user:order'))

        # 获取评论条数
        total_count = request.POST.get('total_count')
        total_count = int(total_count)
        for i in range(1, total_count +1):
            # 获取商品id
            sku_id = request.POST.get('sku_%d' % i)
            # 获取商品评论内容
            content = request.POST.get('content_%d' % i, '')
            try:
                order_goods = OrderGoods.objects.get(order=order, sku_id=sku_id)
            except OrderGoods.DoesNotExist:
                continue
            order_goods.comment = content
            order_goods.save()
        order.order_status = 5
        order.save()
        return redirect(reverse('user:order', kwargs={'page': 1}))