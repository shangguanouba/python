from django.shortcuts import render
from django.views.generic import View
from django.http import JsonResponse

from goods.models import GoodsSKU
from django_redis import get_redis_connection
from utils.mixin import LoginRequiredMixin
# Create your views here.


# /cart/add
class CartAddView(View):
    """购物车记录添加"""
    def post(self, request):
        """购物车记录添加"""
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({'res': 0, 'errmsg': '请先登录'})
        # 接收数据
        sku_id = request.POST.get('sku_id')
        count = request.POST.get('count')
        # 数据校验
        if not all([sku_id, count]):
            return JsonResponse({'res': 1, 'errmsg': '数据不完整'})
        # 校验商品数量
        try:
            count = int(count)
        except Exception as e:
            return JsonResponse({'res': 2, 'errmsg': '数据不正确'})
        # 校验商品是否存在
        try:
            sku = GoodsSKU.objects.get(id=sku_id)
        except Exception as e:
            return JsonResponse({'res': 3, 'errmsg': '商品不存在'})
        # 业务处理：添加购物车记录
        conn = get_redis_connection('default')
        cart_key = 'cart_%d' % user.id
        # 尝试获取sku_id是值
        cart_count = conn.hget(cart_key, sku_id)
        if cart_count:
            # 累加购物车中商品的数据
            count += int(cart_count)
        # 校验商品库存
        if count > sku.stock:
            return JsonResponse({'res': 4, 'errmsg': '库存不足'})
        # 设置hash中sku_id的值
        conn.hset(cart_key, sku_id, count)
        # 计算用户购物车中的条目数
        total_count = conn.hlen(cart_key)
        # 返回应答
        return JsonResponse({'res': 5, 'total_count': total_count, 'message': '添加成功'})


# /cart/
class CartInfoView(LoginRequiredMixin, View):
    """购物车页面显示"""
    def get(self, request):
        # 获取登录用户
        user = request.user
        # 获取用户购物车中商品信息
        conn = get_redis_connection('default')
        cart_ket = 'cart_%d' % user.id
        cart_dict = conn.hgetall(cart_ket)
        skus = []
        total_count = 0
        total_price = 0
        # 遍历获取商品信息
        for sku_id, count in cart_dict.items():
            # 获取商品信息
            sku = GoodsSKU.objects.get(id=sku_id)
            # 计算商品小计
            amount = sku.price*int(count)
            # 动态增加sku对象属性，小计和数量
            sku.amount = amount
            sku.count = int(count)
            # 添加进列表
            skus.append(sku)
            # 累加商品的总数和总价
            total_count += int(count)
            total_price += amount

        # 组织上下文
        context = {
            'total_count': total_count,
            'total_price': total_price,
            'skus': skus
        }
        # 使用模板
        return render(request, 'cart.html', context)


# /cart/update
class CartUpdateView(View):
    """购物车记录更新"""
    def post(self, request):
        """购物车记录更新"""
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({'res': 0, 'errmsg': '请先登录'})
        # 接收数据
        sku_id = request.POST.get('sku_id')
        count = request.POST.get('count')
        # 数据校验
        if not all([sku_id, count]):
            return JsonResponse({'res': 1, 'errmsg': '数据不完整'})
        # 校验商品数量
        try:
            count = int(count)
        except Exception as e:
            return JsonResponse({'res': 2, 'errmsg': '数据不正确'})
        # 校验商品是否存在
        try:
            sku = GoodsSKU.objects.get(id=sku_id)
        except Exception as e:
            return JsonResponse({'res': 3, 'errmsg': '商品不存在'})
        # 业务处理：更新购物车记录
        conn = get_redis_connection('default')
        cart_key = 'cart_%d' % user.id
        # 校验商品库存
        if count > sku.stock:
            return JsonResponse({'res': 4, 'errmsg': '商品库存不足'})
        # 更新
        conn.hset(cart_key, sku_id, count)
        # 计算购物车中的总件数
        total_count = 0
        vals = conn.hvals(cart_key)
        for val in vals:
            total_count += int(val)
        # 返回应答
        return JsonResponse({'res': 5, 'total_count': total_count, 'message': '更新成功'})


# /cart/delete
class CartDeleteView(View):
    """删除购物车记录"""
    def post(self, request):
        """删除购物车记录"""
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({'res': 0, 'errmsg': '请先登录'})
        # 接收参数
        sku_id = request.POST.get('sku_id')
        # 数据校验
        if not sku_id:
            return JsonResponse({'res': 1, 'errmsg': '无效商品'})
        # 校验商品是否存在
        try:
            sku = GoodsSKU.objects.get(id=sku_id)
        except GoodsSKU.DoesNotExist:
            # 商品不存在
            return JsonResponse({'res': 2, 'errmsg': '商品不存在'})
        # 业务处理：删除购物车记录
        conn = get_redis_connection('default')
        cart_key = 'cart_%d' % user.id
        # 删除
        conn.hdel(cart_key, sku_id)
        # 计算购物车中的总件数
        total_count = 0
        vals = conn.hvals(cart_key)
        for val in vals:
            total_count += int(val)
        # 返回应答
        return JsonResponse({'res': 3, 'total_count': total_count, 'message': '删除成功'})
