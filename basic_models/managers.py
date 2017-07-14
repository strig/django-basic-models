from django.db import models
from django.db.models.query import QuerySet


class ActiveObjectsManager(models.Manager):

    def get_queryset(self):
        return super(ActiveObjectsManager, self).get_queryset() \
            .filter(is_active=True)


class CustomQuerySetManager(models.Manager):
    def __init__(self, query_set=None):
        self._custom_query_set = query_set
        super(CustomQuerySetManager, self).__init__()

    def get_queryset(self):
        if self._custom_query_set:
            return self._custom_query_set(self.model)
        return QuerySet(self.model)

    def __getattr__(self, attr, *args):
        if attr.startswith('_'):
            # Helps avoid problems when pickling a model.
            raise AttributeError
        # expose queryset methods as manager methods as well.
        return getattr(self.get_queryset(), attr, *args)


class ActiveQuerySet(QuerySet):
    def active(self):
        return self.filter(is_active=True)


class ActiveModelManager(CustomQuerySetManager):
    def __init__(self):
        super(ActiveModelManager, self).__init__(query_set=ActiveQuerySet)


class FilteredActiveObjectsManager(ActiveModelManager):
    def get_queryset(self):
        return super(FilteredActiveObjectsManager, self).get_queryset().filter(is_active=True)


class FilteredInactiveObjectsManager(ActiveModelManager):
    def get_queryset(self):
        return super(FilteredInactiveObjectsManager, self).get_queryset().filter(is_active=False)


class DefaultModelManager(ActiveModelManager):
    pass


class SlugManagerMixin(models.Manager):
    def get_by_natural_key(self, slug):
        return self.get(slug=slug)

    def get_or_none(self, **kwargs):
        try:
            return self.get(**kwargs)
        except self.model.DoesNotExist:
            return None


class SlugModelManager(SlugManagerMixin, DefaultModelManager):
    pass


class ActiveSlugModelManager(SlugManagerMixin, FilteredActiveObjectsManager):
    pass
