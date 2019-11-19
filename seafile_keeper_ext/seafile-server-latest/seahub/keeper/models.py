import logging
import traceback

from django.db import models

from picklefield.fields import PickledObjectField

from datetime import datetime

import logging
logger = logging.getLogger(__name__)


class CatalogManager(models.Manager):

    def get_by_repo_id(self, repo_id):
        return super(CatalogManager, self).get(repo_id=repo_id)

    def get_all(self):
        return super(CatalogManager, self).all()

    def delete_by_repo_id(self, repo_id):
        c = self.get_by_repo_id(repo_id)
        if c:
            return c.delete()
        return None

    def get_all_mds_ordered(self):
        mds = []
        for c in self.order_by('-modified').all():
            c.md['catalog_id'] = c.catalog_id
            mds.append(c.md)
        return mds

    def get_with_metadata(self):
        """
        get all items with at least one filled md
        """
        return [c for c in self.get_all_mds_ordered() if 'is_certified' in c]

    def get_certified(self):
        """
        get all certified item
        """
        return [c for c in self.get_with_metadata() if c['is_certified']]

    def update_md_by_repo_id(self, repo_id, proj_md):
        catalog = self.get_by_repo_id(repo_id)
        catalog.md = proj_md
        catalog.save()
        return proj_md

    def update_cert_status_by_repo_id(self, repo_id, status):
        """
        Set certification status:
            True if CDC has been issued,
            False if not,
            None if MD is not yet validated
        """
        catalog = self.get_by_repo_id(repo_id)
        if 'is_certified' in catalog.md:
            catalog.md['is_certified'] = status
            catalog.save()
            return status
        else:
            return None

    def add_or_update_by_repo_id(self, repo_id, owner, proj_md):
        try:
            catalog = self.get(repo_id=repo_id)
            catalog.md = proj_md
            catalog.owner = owner
        except Catalog.DoesNotExist:
            catalog = self.model(repo_id=repo_id, owner=owner, md=proj_md)
        catalog.save()
        return catalog


class Catalog(models.Model):

    """ Keeper Catalog DB model """

    repo_id = models.CharField(max_length=37, unique=True, null=False)
    # catalog_id = models.PositiveIntegerField()
    catalog_id = models.AutoField(primary_key=True)
    owner = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    md = PickledObjectField()
    objects = CatalogManager()


class CDCManager(models.Manager):

    def get_cdc_by_repo(self, repo_id):
        """Get cdc_id by repo_id. Return None if nothing found"""
        try:
            cdc = self.get(repo_id=repo_id)
        except CDC.DoesNotExist:
            return None
        return cdc

    def get_cdc_id_by_repo(self, repo_id):
        cdc = self.get_cdc_by_repo(repo_id)
        return cdc.cdc_id if cdc else None


    def is_certified(self, repo_id):
        """Check whether the repo is already certified"""
        return self.get_cdc_id_by_repo(repo_id) is not None

    def register_cdc_in_db(self, repo_id, owner):
        """
        Register in DB a new certificate or update modified field if already created
        Returns certificate id and EVENT: db_create
        """
        from keeper.cdc.cdc_manager import EVENT
        event = EVENT.db_create
        cdc = self.get_cdc_by_repo(repo_id=repo_id)
        if cdc is not None:
            cdc.modified = datetime.now()
            cdc.save()
            event = EVENT.db_update
        else:
            cdc = self.model(repo_id=repo_id, owner=owner)
            cdc.save()
            cdc = self.get(repo_id=repo_id)
            event = EVENT.db_create
        return cdc.cdc_id, event

class CDC(models.Model):

    """ Keeper Cared Data Certficate DB model"""

    class Meta:
        db_table = 'cdc_repos'

    repo_id = models.CharField(max_length=37, unique=True, null=False)
    cdc_id = models.AutoField(primary_key=True)
    owner = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    objects = CDCManager()



###### signal handlers
from django.dispatch import receiver
from seahub.signals import repo_deleted

@receiver(repo_deleted)
def remove_catalog_and_cdc_entry(sender, **kwargs):
    repo_id = kwargs['repo_id']
    logging.info("Repo deleted, id: %s" % repo_id)
    try:
        Catalog.objects.delete_by_repo_id(repo_id)
        CDC.objects.get(repo_id=repo_id).delete()
    except Exception:
        logging.error(traceback.format_exc())

@receiver(repo_deleted)
def remove_doi(sender, **kwargs):
    repo_id = kwargs['repo_id']
    try:
        doi_repos = DoiRepo.objects.get_valid_doi_repos(repo_id)
        doi_repos.update(rm=datetime.now())
    except Exception:
        logging.error(traceback.format_exc())


###### bloxberg certificate ######

class BCertificateManager(models.Manager):

    def add_bloxberg_certificate(self, transaction_id, repo_id, path, commit_id, created_time, owner, checksum):
        """
        Add to DB a new Bloxberg certificate, modify currently is not needed
        Returns Bloxberg certificate id and EVENT: db_create
        """
        b_certificate = BCertificate(transaction_id=transaction_id, repo_id=repo_id, path=path, commit_id=commit_id, created=created_time, owner=owner, checksum=checksum)
        b_certificate.save()
        return b_certificate.obj_id

    def has_bloxberg_certificate(self, repo_id, path, commit_id):
        return super(BCertificateManager, self).filter(repo_id=repo_id, path=path, commit_id=commit_id).count()

class BCertificate(models.Model):

    """ Bloxberg Certificate model """

    class Meta:
        db_table = 'bloxberg_certificate'

    transaction_id = models.CharField(max_length=255, null=False)
    repo_id = models.CharField(max_length=37, null=False)
    commit_id =  models.CharField(max_length=41, null=False)
    path = models.TextField(null=False)
    obj_id = models.AutoField(primary_key=True)
    created = models.DateTimeField()
    owner = models.CharField(max_length=255, null=False)
    checksum = models.CharField(max_length=64, null=False)
    objects = BCertificateManager()

###### DOI Repository ######
class DoiRepoManager(models.Manager):

    def add_doi_repo(self, repo_id, repo_name, doi, prev_doi, commit_id, owner, md):
        doi_repo = self.model(repo_id=repo_id, repo_name=repo_name, doi=doi, prev_doi=prev_doi, commit_id=commit_id, owner=owner, md=md)
        doi_repo.save()
        return doi_repo

    def get_valid_doi_repos(self, repo_id):
        return super(DoiRepoManager, self).exclude(rm__isnull=False).filter(repo_id=repo_id)

    def get_doi_by_commit_id(self, repo_id, commit_id):
        return super(DoiRepoManager, self).filter(repo_id=repo_id, commit_id=commit_id)

    def get_doi_by_owner(self, owner):
        return super(DoiRepoManager, self).filter(owner=owner)

    def get_doi_repos_by_repo_id(self, repo_id):
        return super(DoiRepoManager, self).filter(repo_id=repo_id)

class DoiRepo(models.Model):

    """ Doi Repository """
    class Meta:
        db_table = 'doi_repos'

    repo_id = models.CharField(max_length=37, null=False)
    repo_name = models.CharField(max_length=255, null=False)
    doi = models.CharField(primary_key=True, max_length=37, null=False)
    prev_doi = models.CharField(max_length=37, default=None)
    commit_id = models.CharField(max_length=41, default=None)
    owner = models.CharField(max_length=255, null=False)
    md = PickledObjectField()
    created = models.DateTimeField(auto_now_add=True)
    rm = models.DateTimeField(blank=True, default=None, null=True)
    objects = DoiRepoManager()