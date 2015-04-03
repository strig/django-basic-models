from django.contrib.admin import ModelAdmin


class CreatedUpdatedBy(ModelAdmin):
    readonly_fields = ('created_by', 'updated_by')

    @staticmethod
    def _populate_created_and_updated_by(instance, user):
        if not instance.pk:
            instance.created_by = user
        instance.updated_by = user

    def save_model(self, request, obj, form, change):
        instance = form.save(commit=False)
        self._populate_created_and_updated_by(instance, request.user)
        instance.save()
        return instance

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            self._populate_created_and_updated_by(instance, request.user)
            instance.save()
        formset.save_m2m()


class NameSlug(ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}


class AutoGroupMeta(ModelAdmin):

    def get_form(self, request, obj=None, **kwargs):
        ModelForm = super(AutoGroupMeta, self).get_form(request, obj, **kwargs)
        return ModelForm

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = ['created_by', 'updated_by',
                           'created_at', 'updated_at']

        return filter(lambda field: hasattr(obj, field), readonly_fields)

    def get_fieldsets(self, request, obj=None):
        fieldsets = super(AutoGroupMeta, self).get_fieldsets(request, obj)
        meta_fields = ('is_active', 'created_at', 'created_by',
                       'updated_at', 'updated_by')
        meta_grouped = []

        # Remove Meta fields from any defined fieldsets
        for fieldset in fieldsets:
            key, fields = fieldset
            non_meta_fields = filter(lambda field: field not in meta_fields,
                                     fields['fields'])
            meta_grouped.append((key, {'fields': non_meta_fields}))

        # Add meta fields (if they exist on the instance) to a Meta fieldset
        exclude = self.exclude or []
        fields = filter(
            lambda field: hasattr(obj, field) and field not in exclude,
            meta_fields)

        meta_grouped.append(
            ('Meta', {'fields': fields, 'classes': ('collapse',)})
        )

        return meta_grouped


class LocalPreview(ModelAdmin):
    change_form_template = "admin/change_form_with_local_preview.html"
