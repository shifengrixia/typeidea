# from django.contrib import admin
# from django.contrib.auth import get_permission_codename
# from django.contrib.admin.models import LogEntry
from django.shortcuts import reverse
from django.utils.html import format_html
import xadmin
from xadmin.filters import manager, RelatedFieldListFilter
from xadmin.layout import Row, Fieldset, Container

from .adminform import PostAdminForm
from .models import Category, Tag, Post
from typeidea.base_admin import BaseOwnerAdmin
from typeidea.custom_site import custom_site


class CategoryOwnerFilter(RelatedFieldListFilter):
    """自定义过滤器只展示当前用户分类"""

    # title = '分类过滤器'
    # parameter_name = 'owner_category'
    #
    # def lookups(self, request, model_admin):
    #     return Category.objects.filter(owner=request.user).values_list('id', 'name')
    #
    # def queryset(self, request, queryset):
    #     category_id = self.value()
    #     if category_id:
    #         return queryset.filter(category_id=self.value())
    #     return queryset
    def __init__(self, field, request, params, model, model_admin, field_path):
        super(CategoryOwnerFilter, self).__init__(field, request, params, model, model_admin, field_path)
        self.lookup_choices = Category.objects.filter(owner=request.user).values_list('id', 'name')

    @classmethod
    def test(cls, field, request, params, model, admin_view, field_path):
        return field.name == 'category'


manager.register(CategoryOwnerFilter, take_priority=True)


class PostInline:
    form_layout = (
        Container(
            'title',
            'desc',
            'content',
            'status',
            Row('tag', 'owner'),
            Row('pv', 'uv'),
        ),
    )
    extra = 1
    model = Post


@xadmin.sites.register(Category, site=custom_site)
class CategoryAdmin(BaseOwnerAdmin):
    list_display = ('name', 'status', 'is_nav', 'created_time', 'post_count')
    fields = ('name', 'status', 'is_nav')

    inlines = [PostInline, ]

    def post_count(self, obj):
        return obj.post_set.count()

    post_count.short_description = '文章数量'


@xadmin.sites.register(Tag, site=custom_site)
class TagAdmin(BaseOwnerAdmin):
    list_display = ('name', 'status', 'created_time')
    fields = ('name', 'status')


@xadmin.sites.register(Post, site=custom_site)
class PostAdmin(BaseOwnerAdmin):
    form = PostAdminForm

    list_display = (
        'title', 'category', 'status', 'created_time', 'operator'
    )
    list_display_links = []

    list_filter = ('category',)
    # filter_vertical = ('tag',)
    filter_horizontal = ('tag',)

    search_fields = ('title', 'category__name')

    actions_on_top = True
    actions_on_bottom = True

    save_on_top = True

    form_layout = (
        Fieldset(
            "基础信息",
            Row("title", "category"),
            "status",
            "tag"
        ),
        Fieldset(
            "内容信息",
            "desc",
            "content"
        )
    )

    # fields = (
    #     ('category', 'title'),
    #     'desc',
    #     'status',
    #     'content',
    #     'tag',
    # )
    # fieldsets = (
    #     ('基础配置', {
    #         'description': '基础配置描述',
    #         'fields': (
    #             ('title', 'category'),
    #             'status',
    #         ),
    #     }),
    #     ('内容', {
    #         'fields': (
    #             'desc',
    #             'content',
    #         )
    #     }),
    #     ('额外信息', {
    #         'classes': ('collapse',),
    #         'fields': ('tag',),
    #     })
    # )

    # def has_add_permission(self, request):
    #     opts = self.opts
    #     codename = get_permission_codename('add', opts)
    #     perm_code = '%s.%s' % (opts.app_label, codename)
    #     resp = request.get()
    #     if resp.status_code == 200:
    #         return True
    #     else:
    #         return False

    def operator(self, obj):
        # return format_html('<a href="{}">编辑</a>', reverse('cus_admin:blog_post_change', args=(obj.id,)))
        return format_html('<a href="{}">编辑</a>', reverse('xadmin:blog_post_change', args=(obj.id,)))

    operator.short_description = '操作'

    # class Media:
    #     css = {
    #         'all': ('https://cdn.bootcss.com/bootstrap/4.0.0-beta.2/css/bootstrap.min.css',),
    #     }
    #     js = ('https://cdn.bootcss.com/bootstrap/4.0.0-beta.2/js/bootstrap.bundle.js',)

# @admin.register(LogEntry, site=custom_site)
# class LogEntryAdmin(admin.ModelAdmin):
#     list_display = ('object_repr', 'object_id', 'action_flag', 'user', 'change_message')
