import logging

from django.db import models
from django.utils import timezone

from picklefield.fields import PickledObjectField

logger = logging.getLogger(__name__)

class CatalogManager(models.Manager):

    def get_by_repo_id(self, repo_id):
        return super(CatalogManager, self).using('keeper').get(repo_id=repo_id)

    def delete_by_repo_id(self, repo_id):
        return self.get_by_repo_id(repo_id).delete()

    def get_all_mds_ordered(self):
        mds = []
        for c in self.using('keeper').order_by('-catalog_id').all():
            c.md['catalog_id'] = c.catalog_id
            mds.append(c.md)
        return mds

    def update_md_by_repo_id(self, repo_id, proj_md):
        catalog = self.get_by_repo_id(repo_id)
        catalog.md = proj_md
        catalog.save(using='keeper')
        return proj_md

    def add_or_update_by_repo_id(self, repo_id, owner, proj_md):
        try:
            catalog = self.using('keeper').get(repo_id=repo_id)
            catalog.md = proj_md
            catalog.owner = owner
        except Catalog.DoesNotExist:
            catalog = self.model(repo_id=repo_id, owner=owner, md=proj_md)
        catalog.save(using='keeper')

        return catalog




class Catalog(models.Model):
    repo_id = models.CharField(max_length=37, unique=True, null=False)
    # catalog_id = models.PositiveIntegerField()
    catalog_id = models.AutoField(primary_key=True)
    owner = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    md = PickledObjectField()
    objects = CatalogManager()
