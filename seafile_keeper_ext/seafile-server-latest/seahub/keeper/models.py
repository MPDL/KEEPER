import traceback

from django.db import models

from picklefield.fields import PickledObjectField

from django.utils import timezone

from seahub.settings import SERVICE_URL

from operator import attrgetter

import logging

logger = logging.getLogger(__name__)


class CatalogManager(models.Manager):

    def get_by_repo_id(self, repo_id):
        """Get catalog entry by repo_id. Return None if nothing found"""
        try:
            c = self.get(repo_id=repo_id)
        except Catalog.DoesNotExist:
            return None
        return c

    def get_all(self):
        return super(CatalogManager, self).all()

    def delete_by_repo_id(self, repo_id):
        c = self.get_by_repo_id(repo_id)
        if c:
            # don not delete the entry, set it to rm
            # return c.delete()
            c.rm = timezone.now()
            c.save()
        return None

    def get_all_mds_ordered(self):
        mds = []
        for c in self.exclude(rm__isnull=False).order_by('-modified').all():
            c.md.update(
                catalog_id=c.catalog_id,
                repo_id=c.repo_id,
                is_archived=c.is_archived,
            )
            mds.append(c.md)
        return mds

    def get_mds_ordered(self, start=0, limit=25):
        """
        SELECT *,
            IF(EXISTS(SELECT 1 FROM doi_repos WHERE doi_repos.repo_id = c.repo_id AND doi_repos.rm is NULL) OR c.is_archived = 1, CONCAT('url', c.repo_id), NULL) AS
            landing_page_url
        FROM
            `keeper_catalog` AS c
        WHERE
            c.rm is NULL
        """
        mds = []
        for c in self.exclude(rm__isnull=False).order_by('-modified').all()[start:start + limit]:
            # add landing page link
            if c.is_archived == 1 or DoiRepo.objects.get_valid_doi_repos(c.repo_id):
                c.md["landing_page_url"] = '%s/landing-page/libs/%s/' % (SERVICE_URL, c.repo_id)
            c.md.update(
                catalog_id=c.catalog_id,
                repo_id=c.repo_id,
                is_archived=c.is_archived,
            )
            mds.append(c.md)
        return mds

    def get_mds_with_facets(self, author_facet=None, year_facet=None, institute_facet=None, director_facet=None,
                            start=0, limit=25):

        def _f(f):
            return f is None or not f.get("termsChecked")

        if _f(author_facet) and _f(year_facet) and _f(institute_facet) and _f(director_facet):
            return self.get_mds_ordered(start, limit)
        mds = []
        for c in self.exclude(rm__isnull=False).order_by('-modified').all():
            # author
            if "termsChecked" in author_facet:
                a_list = c.md.get("authors")
                if a_list:
                    a_list = [a.get("name") for a in c.md.get("authors")]
                    if a_list:
                        inter = set(author_facet["termsChecked"]).intersection(a_list)
                        if not (inter and list(inter)):
                            continue
                else:
                    continue
            # year
            if "termsChecked" in year_facet and len(year_facet.get("termsChecked")) > 0:
                y = c.md.get("year")
                if y and y.strip():
                    if not (y.strip() in year_facet["termsChecked"]):
                        continue
                else:
                    continue

            # add landing page link
            if c.is_archived == 1 or DoiRepo.objects.get_valid_doi_repos(c.repo_id):
                c.md["landing_page_url"] = '%s/landing-page/libs/%s/' % (SERVICE_URL, c.repo_id)
            c.md.update(
                catalog_id=c.catalog_id,
                repo_id=c.repo_id,
                is_archived=c.is_archived,
                _order_key="".join([a["name"] for a in c.md.get("authors")]),
            )
            mds.append(c.md)

        order = author_facet.get("order")
        if order:
            reverse = order == 'desc'
            mds = sorted(mds, key=lambda c: c["_order_key"], reverse=reverse)

        # clean up
        [m.pop("_order_key", None) for m in mds]

        return mds[start:limit]



    def get_mds_with_scope_ordered(self, scope=None, start=0, limit=25):

        #logging.error("s:%s, l:%s scope:%r", start, limit, scope)
        if not scope:
            return self.get_mds_ordered(start, limit)
        mds = []
        for c in self.exclude(rm__isnull=False).filter(catalog_id__in=scope).order_by('-modified').all():

            # add landing page link
            if c.is_archived == 1 or DoiRepo.objects.get_valid_doi_repos(c.repo_id):
                c.md["landing_page_url"] = '%s/landing-page/libs/%s/' % (SERVICE_URL, c.repo_id)
            c.md.update(
                catalog_id=c.catalog_id,
                repo_id=c.repo_id,
                is_archived=c.is_archived,
                #_author_key="".join([a["name"] for a in c.md.get("authors")]),
                #_year_key=c.md.get("year").strip(),
                # _inst_key=c.md.get("institute").
            )
            mds.append(c.md)

        # TODO: implement complex sorting in python
        # https://docs.python.org/3/howto/sorting.html#sort-stability-and-complex-sorts
        # order = author_facet.get("order")
        # if order:
        #     reverse = order == 'desc'
        #     mds = sorted(mds, key=lambda c: c["_order_key"], reverse=reverse)

        # clean up
        #[m.pop("_order_key", None) for m in mds]

        return mds[start:start + limit]

    def _get_catalog_items_with_refinement(self, in_cat):
        return self.exclude(rm__isnull=False).filter(catalog_id__in=in_cat).all() if in_cat and len(in_cat) > 0 \
            else self.exclude(rm__isnull=False).all()

    def get_md_authors_ordered(self, in_cat=None):
        """
        Get list of catalog authors ordered and list of catalog_ids of the corresponding author
        """
        a_entries = {}
        for c in self._get_catalog_items_with_refinement(in_cat):
            a_tmp = c.md.get("authors")
            if a_tmp:
                for a in a_tmp:
                    name = a.get("name")
                    if name:
                        if not name in a_entries:
                            a_entries[name] = [c.catalog_id]
                        else:
                            a_entries[name].append(c.catalog_id)
        authors = list(a_entries.keys())
        authors.sort()
        return [(a, a_entries[a]) for a in authors]

    def get_md_years_ordered(self, in_cat):
        """
        Get list of catalog years, sorted
        """
        years = set()
        y_count = {}
        for c in self._get_catalog_items_with_refinement(in_cat):
            y = c.md.get("year")
            if y:
                if not y in y_count:
                    y_count[y] = 1
                else:
                    y_count[y] += 1
                years.add(y)
        years = list(years)
        years.sort(reverse=True)
        return [(y, y_count[y]) for y in years]

    def get_md_institutes_ordered(self, in_cat=None):
        """
        Get list of catalog years, sorted
        """
        insts = set()
        i_count = {}
        for c in self._get_catalog_items_with_refinement(in_cat):
            inst = c.md.get("institute")
            if inst:
                i_split = inst.split(";")
                if len(i_split) > 0 and i_split[0]:
                    inst = i_split[0].strip()
                    if inst:
                        if not inst in i_count:
                            i_count[inst] = 1
                        else:
                            i_count[inst] += 1
                        insts.add(inst)
        insts = list(insts)
        insts.sort()
        return [(inst, i_count[inst]) for inst in insts]

    def get_md_directors_ordered(self, in_cat=None):
        """
        Get list of catalog years, sorted
        """
        directors = set()
        d_count = {}
        for c in self._get_catalog_items_with_refinement(in_cat):
            inst = c.md.get("institute")
            if inst:
                i_split = inst.split(";")
                if len(i_split) >= 3 and i_split[2]:
                    d = i_split[2].strip()
                    for d in d.split("|"):
                        d = d.strip()
                        if not d in d_count:
                            d_count[d] = 1
                        else:
                            d_count[d] += 1
                        directors.add(d)
        directors = list(directors)
        directors.sort()
        return [(d, d_count[d]) for d in directors]

    def get_with_metadata(self):
        """
        get all items with at least one filled md
        """
        return [c for c in self.get_all_mds_ordered() if 'is_certified' in c]

    def get_library_details_entries(self, owner):
        entries = []
        if owner:
            try:
                entries = Catalog.objects.extra(where=[
                    "owner='" + owner + "'",
                    "EXISTS (SELECT repo_id FROM doi_repos WHERE doi_repos.repo_id=keeper_catalog.repo_id AND doi_repos.rm is NULL) OR keeper_catalog.is_archived=1"
                ])
            except Exception as e:
                logger.error('Cannot retrieve library details entries: %s', e)
        return entries

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

    def add_or_update_by_repo_id(self, repo_id, owner, proj_md, repo_name):
        try:
            catalog = self.get(repo_id=repo_id)
            catalog.md = proj_md
            catalog.owner = owner
            catalog.repo_name = repo_name
        except Catalog.DoesNotExist:
            catalog = self.model(repo_id=repo_id, owner=owner, md=proj_md)
        catalog.save()
        return catalog

    def set_archived(self, repo_id):
        c = self.get_by_repo_id(repo_id)
        if c:
            c.is_archived = True
            c.save()


class Catalog(models.Model):
    """ Keeper Catalog DB model """

    repo_id = models.CharField(max_length=37, unique=True, null=False)
    # catalog_id = models.PositiveIntegerField()
    catalog_id = models.AutoField(primary_key=True)
    owner = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    md = PickledObjectField()
    rm = models.DateTimeField(blank=True, default=None, null=True)
    is_archived = models.BooleanField(default=False)
    repo_name = models.CharField(max_length=255, null=False)
    objects = CatalogManager()


class CDCManager(models.Manager):

    def get_by_repo(self, repo_id):
        """Get cdc_id by repo_id. Return None if nothing found"""
        try:
            c = self.get(repo_id=repo_id)
        except CDC.DoesNotExist:
            return None
        return c

    def get_cdc_id_by_repo(self, repo_id):
        cdc = self.get_by_repo(repo_id)
        return cdc.cdc_id if cdc else None

    def delete_by_repo_id(self, repo_id):
        c = self.get_by_repo(repo_id)
        if c:
            return c.delete()
        return None

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
        cdc = self.get_by_repo(repo_id=repo_id)
        if cdc is not None:
            cdc.modified = timezone.now()
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
def remove_keeper_entries(sender, **kwargs):
    repo_id = kwargs['repo_id']
    try:
        logging.info("Removing keeper entries for repo: " + repo_id + "...")
        Catalog.objects.delete_by_repo_id(repo_id)
        logging.info("Project Catalog: done.")
        cdc = CDC.objects.get_by_repo(repo_id)
        if cdc:
            cdc.delete()
        logging.info("CDC: done.")
        doi_repos = DoiRepo.objects.get_valid_doi_repos(repo_id)
        if doi_repos:
            doi_repos.update(rm=timezone.now())
        logging.info("DOI: done.")
    except Exception:
        logging.error(traceback.format_exc())


###### bloxberg certificate ######

class BCertificateManager(models.Manager):

    def add_bloxberg_certificate(self, transaction_id, repo_id, path, commit_id, created_time, owner, checksum):
        """
        Add to DB a new Bloxberg certificate, modify currently is not needed
        Returns Bloxberg certificate id and EVENT: db_create
        """
        b_certificate = BCertificate(transaction_id=transaction_id, repo_id=repo_id, path=path, commit_id=commit_id,
                                     created=created_time, owner=owner, checksum=checksum)
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
    commit_id = models.CharField(max_length=41, null=False)
    path = models.TextField(null=False)
    obj_id = models.AutoField(primary_key=True)
    created = models.DateTimeField()
    owner = models.CharField(max_length=255, null=False)
    checksum = models.CharField(max_length=64, null=False)
    objects = BCertificateManager()


###### DOI Repository ######
class DoiRepoManager(models.Manager):

    def add_doi_repo(self, repo_id, repo_name, doi, prev_doi, commit_id, owner, md):
        doi_repo = self.model(repo_id=repo_id, repo_name=repo_name, doi=doi, prev_doi=prev_doi, commit_id=commit_id,
                              owner=owner, md=md)
        doi_repo.save()
        return doi_repo

    def get_valid_doi_repos(self, repo_id):
        return super(DoiRepoManager, self).exclude(rm__isnull=False).filter(repo_id=repo_id)

    def get_doi_by_commit_id(self, repo_id, commit_id):
        return super(DoiRepoManager, self).filter(repo_id=repo_id, commit_id=commit_id)

    def get_active_doi_by_owner(self, owner):
        return super(DoiRepoManager, self).exclude(rm__isnull=False).filter(owner=owner)

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
