# from django import forms
#
#
# class PostAdminForm(forms.ModelForm):
#     desc = forms.CharField(widget=forms.Textarea, label='摘要', required=False)
from dal import autocomplete
from ckeditor_uploader.widgets import CKEditorUploadingWidget

from django import forms
from django.forms import Media

from .models import Category, Tag, Post


class PostAdminForm(forms.ModelForm):
    desc = forms.CharField(widget=forms.Textarea(attrs={'style': 'resize: none'}), label='摘要', required=False)
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        widget=autocomplete.ModelSelect2(url='category-autocomplete'),
        label='分类',
    )
    tag = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=autocomplete.ModelSelect2Multiple(url='tag-autocomplete'),
        # widget=forms.Textarea,
        label='标签'
    )
    content_ck = forms.CharField(widget=CKEditorUploadingWidget(), label='正文', required=False)
    content_md = forms.CharField(widget=forms.Textarea(), label='正文', required=False)
    content = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Post
        fields = ('category', 'tag', 'desc', 'title', 'is_md', 'content', 'content_md', 'content_ck', 'status',)

    def __init__(self, instance=None, initial=None, **kwargs):
        initial = initial or {}
        if instance:
            if instance.is_md:
                initial['content_md'] = instance.content
            else:
                initial['content_ck'] = instance.content
        super(PostAdminForm, self).__init__(instance=instance, initial=initial, **kwargs)

    def clean(self):
        is_md = self.cleaned_data.get('is_md')
        if is_md:
            content_field_name = 'content_md'
        else:
            content_field_name = 'content_ck'
        content = self.cleaned_data.get(content_field_name)
        if not content:
            self.add_error(content_field_name, '必填')
            return
        self.cleaned_data['content'] = content
        return super(PostAdminForm, self).clean()

    # 类Media将存储每个字段所需的js/css文件，并为了保持顺序使用merge方法将进行对不同字段中js/css文件去重然后使用拓扑排序合并到一起。
    @property
    def media(self):
        media = Media()
        for field in self.fields.values():
            media = media + field.widget.media
        media._js_lists.append(['autocomplete_light/select2.js', '/static/xadmin/vendor/select2/select2.js'])
        return media

    class Media:
        js = ('js/post_editor.js',)
