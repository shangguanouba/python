from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import View
from django.core.cache import cache
from django.core.paginator import Paginator
from goods.models import GoodsType, GoodsSKU, IndexGoodsBanner, IndexTypeGoodsBanner, IndexPromotionBanner
from django_redis import get_redis_connection
from order.models import OrderGoods

# Create your views here.


# http://127.0.0.1:8000
class IndexView(View):
    """首页"""
    def get(self, request):
        """显示首页"""
        # 尝试从缓存中获取数据
        context = cache.get('index_page_data')
        if context is None:
            # 获取商品种类
            types = GoodsType.objects.all()
            # 获取首页轮播商品信息
            goods_banners = IndexGoodsBanner.objects.all().order_by('index')
            # 获取首页促销活动信息
            promotion_banners = IndexPromotionBanner.objects.all().order_by('index')
            # 获取首页分类商品展示信息
            for type in types:
                # 获取type种类首页分类商品的图片展示信息
                image_banners = IndexTypeGoodsBanner.objects.filter(type=type, display_type=1).order_by('index')
                # 获取type种类首页分类商品的文字展示信息
                title_banners = IndexTypeGoodsBanner.objects.filter(type=type, display_type=0).order_by('index')
                # 动态给type增加属性，分别保存首页分类商品的图片展示信息和文件展示信息
                type.image_banners = image_banners
                type.title_banners = title_banners

            context = {'types': types,
                       'goods_banners': goods_banners,
                       'promotion_banners': promotion_banners}
            # 设置缓存
            cache.set('index_page_data', context, 3600)

        # 获取用户购物车中商品的数目
        user = request.user
        cart_count = 0
        if user.is_authenticated:
            # 用户已登录
            conn = get_redis_connection('default')
            cart_key = 'cart_%d' % user.id
            cart_count = conn.hlen(cart_key)

        # 组织模板上下文
        context.update(cart_count=cart_count)

        # 使用模板

        return render(request, 'index.html', context)


# /goods/商品id
class DetailView(View):
    """显示详情页"""
    def get(self, request, goods_id):
        try:
            sku = GoodsSKU.objects.get(id = goods_id)
        except GoodsSKU.DoesNotExist:
            # 商品不存在
            return redirect(reverse('goods:index'))
        # 获取商品分类信息
        types = GoodsSKU.objects.all()
        # 获取评论信息
        sku_orders = OrderGoods.objects.filter(sku=sku).exclude(comment='')
        # 获取新品信息
        new_skus = GoodsSKU.objects.filter(type=sku.type).order_by('-create_time')[:2]
        # 获取同一SPU的其他规格商品
        same_spu = GoodsSKU.objects.filter(goods=sku.goods).exclude(id=goods_id)
        # 获取用户购物车中商品的数目
        user = request.user
        cart_count = 0
        if user.is_authenticated:
            # 用户已登录
            conn = get_redis_connection('default')
            cart_key = 'cart_%d' % user.id
            cart_count = conn.hlen(cart_key)
            # 添加用户的历史浏览记录
            conn = get_redis_connection('default')
            history_key = 'history_%d' % user.id
            # 移除列表中的goods_id
            conn.lrem(history_key, 0, goods_id)
            # 吧goods_id添加到列表左边
            conn.lpush(history_key, goods_id)
            # 只保存用户最新浏览的5条记录
            conn.ltrim(history_key, 0, 4)
        # 组织模板上下文
        context = {
            'sku': sku,
            'sku_orders': sku_orders,
            'new_skus': new_skus,
            'same_spu': same_spu,
            'cart_count': cart_count
        }
        # 使用模板
        return render(request, 'detail.html', context)


class ListView(View):
    """商品列表"""
    def get(self, request, type_id, page):
        """显示列表页面"""
        # 获取种类信息
        try:
            type = GoodsType.objects.get(id=type_id)
        except GoodsType.DoesNotExist:
            # 种类不存在
            redirect(reverse('goods:index'))

        # 获取商品分类信息
        types = GoodsType.objects.all()
        # 获取排序方式
        sort = request.GET.get('sort')
        if sort == 'price':
            skus = GoodsSKU.objects.filter(type=type).order_by('price')
        elif sort == 'hot':
            skus = GoodsSKU.objects.filter(type=type).order_by('-sales')
        else:
            sort = 'default'
            skus = GoodsSKU.objects.filter(type=type).order_by('-id')

        # 数据进行分页
        paginator = Paginator(skus, 1)
        # 获取page页内容
        try:
            page = int(page)
        except Exception as e:
            page = 1
        if page > paginator.num_pages:
            page = 1
        skus_page = paginator.page(page)
        # todo: 进行页码的控制，最多显示5页
        # 1.总数小于5页，显示所有页码
        # 2.当前页是前三页，显示1-5
        # 3.当前页是后三页，显示后5页
        # 4.其他情况，显示当前页的前2页和后2页
        num_pages = paginator.num_pages
        if num_pages < 5:
            pages = range(1, num_pages+1)
        elif page <= 3:
            pages = range(1, 6)
        elif num_pages - page <= 2:
            pages = range(num_pages-4, num_pages+1)
        else:
            range(page-2, page+3)
        # 获取新品信息
        new_skus = GoodsSKU.objects.filter(type=type).order_by('-create_time')[:2]
        # 获取用户购物车中商品的数目
        user = request.user
        cart_count = 0
        if user.is_authenticated:
            # 用户已登录
            conn = get_redis_connection('default')
            cart_key = 'cart_%d' % user.id
            cart_count = conn.hlen(cart_key)
        # 组织模板上下文
        context = {
            'type': type,
            'types': types,
            'skus_page': skus_page,
            'new_skus': new_skus,
            'cart_count': cart_count,
            'sort': sort,
            'pages': pages
        }
        # 使用模板
        return render(request, 'list.html', context)