from django.contrib.admin import ModelAdmin


class ActiveModelAdmin(ModelAdmin):
    """ModelAdmin subclass that adds activate and delete actions and situationally removes the delete action"""
    actions = ['activate_objects', 'deactivate_objects']

    def activate_objects(self, request, queryset):
        """Admin action to set is_active=True on objects"""
        count = queryset.update(is_active=True)
        self.message_user(request, _("Successfully activated %(count)d %(items)s.") % {
            "count": count, "items": model_ngettext(self.opts, count)
        })
    activate_objects.short_description = "Activate selected %(verbose_name_plural)s"

    def deactivate_objects(self, request, queryset):
        """Admin action to set is_active=False on objects"""
        count = queryset.update(is_active=False)
        self.message_user(request, _("Successfully deactivated %(count)d %(items)s.") % {
            "count": count, "items": model_ngettext(self.opts, count)
        })
    deactivate_objects.short_description = "Deactivate selected %(verbose_name_plural)s"

    def get_actions(self, request):
        actions = super(ActiveModelAdmin, self).get_actions(request)
        if not self.has_delete_permission(request):
            if 'delete_selected' in actions:
                del actions['delete_selected']
        return actions


class TimestampedModelAdmin(ModelAdmin):
    """ModelAdmin subclass that will set created_at and updated_at fields to readonly"""
    readonly_fields = ('created_at', 'updated_at')


class UserModelAdmin(ModelAdmin):
    """ModelAdmin subclass that will automatically update created_by and updated_by fields"""
    save_on_top = True
    readonly_fields = ('created_by', 'updated_by')

    def save_model(self, request, obj, form, change):
        instance = form.save(commit=False)
        self._update_instance(instance, request.user)
        instance.save()
        return instance

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            self._update_instance(instance, request.user)
            instance.save()
        formset.save_m2m()

    @staticmethod
    def _update_instance(instance, user):
        if not instance.pk:
            instance.created_by = user
        instance.updated_by = user


class DefaultModelAdmin(ActiveModelAdmin, UserModelAdmin, TimestampedModelAdmin):
    """ModelAdmin subclass that combines functionality of UserModel, ActiveModel, and TimestampedModel admins and defines a Meta fieldset"""
    readonly_fields = ('created_at', 'created_by', 'updated_at', 'updated_by')
    fieldsets = (
        ('Meta', {'fields': ('is_active', 'created_at', 'created_by', 'updated_at', 'updated_by'), 'classes': ('collapse',)}),
    )
    # Added by Hatch to simplify collapse-able Audit section of admins
    audit_fields = ('Audit', {'fields': ('created_at', 'created_by', 'updated_at', 'updated_by'),
                              'classes': ('collapse', )})


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
            key, field_options = fieldset
            field_options['fields'] = filter(
                lambda field_name: field_name not in meta_fields,
                field_options['fields'])
            meta_grouped.append((key, field_options))

        # Add meta fields (if they exist on the instance) to a Meta fieldset
        exclude = self.exclude or []
        fields = filter(
            lambda field: hasattr(obj, field) and field not in exclude,
            meta_fields)

        if fields:
            meta_grouped.append(
                ('Meta', {'fields': fields, 'classes': ('collapse',)})
            )

        return meta_grouped


class LocalPreview(ModelAdmin):
    change_form_template = "admin/change_form_with_local_preview.html"
