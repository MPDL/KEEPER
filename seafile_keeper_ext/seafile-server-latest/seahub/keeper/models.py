import traceback

from django.db import models

from picklefield.fields import PickledObjectField

from django.utils import timezone

from seahub.settings import SERVICE_URL

from operator import attrgetter

import logging

logger = logging.getLogger(__name__)


def _get_sort_key(md, facets, facet_name):
    """
    Generate order keys for python complex sorting
    """
    idx = "_"
    f = facets.get(facet_name)
    if facet_name == "author":
        tcs = f.get("termsChecked")
        if tcs:
            if md.get("authors"):
                for tc in tcs:
                    if tc in [a.get("name") for a in md.get("authors")]:
                        idx += tc
    elif facet_name == "year":
        tcs = f.get("termsChecked")
        if tcs:
            y = md.get("year")
            if y and y in tcs:
                idx = y
    elif facet_name == "institute":
        tcs = f.get("termsChecked")
        if tcs:
            mm = md.get("institute")
            if mm:
                for tc in tcs:
                    if tc in mm:
                        idx += tc
    elif facet_name == "director":
        tcs = f.get("termsChecked")
        if tcs:
            mm = md.get("director")
            if mm:
                for tc in tcs:
                    if tc in mm:
                        idx += tc
    return idx


def _apply_sorts(mds, facets):
    """
    Apply facets sorting
    """
    for k in reversed(('author', 'year', 'institute', 'director')):
        f = facets.get(k)
        if f and f.get("termsChecked"):
            reverse = f.get("order", "asc") == "desc"
            # mds = sorted(mds, key=lambda md: _get_sort_key(md, facets, k), reverse=reverse)
            mds = sorted(mds, key=lambda md: md.get("_" + k[0], "_"), reverse=reverse)
    return mds


def _update_facets(facets, c):
    """
    Regenerate facets and sort keys in one run
    """

    def _f(fs, n, md, mn):
        return fs.get(n).get("termsChecked"), md.get(mn, None)

    def _update_entries(fs, to_upd):
        for k in to_upd.keys():
            upd = to_upd.get(k)
            entries = fs.get(k).get("termEntries")
            for term in upd.keys():
                val = upd[term]
                if term not in entries:
                    entries[term] = [val]
                elif val not in entries[term]:
                    entries[term].append(val)

    TO_UPD = {"author":{"sk": "_"}, "year":{"sk": "_"}, "institute": {"sk": "_"}, "director": {"sk": "_"}}

    terms, md = _f(facets, "author", c.md, "authors")
    if terms and not md:
        return False
    elif md:
        flag = False
        for a in md:
            a = a.get("name")
            if not terms or a in terms:
                flag = True
                TO_UPD["author"].update({
                    a: c.catalog_id,
                    "sk": TO_UPD["author"].get("sk") + a
                })
        if not flag:
            return False

    terms, md = _f(facets, "year", c.md, "year")
    if terms and not md:
        return False
    elif md:
        if not terms or md in terms:
            TO_UPD["year"].update({
                md: c.catalog_id,
                "sk": str(md),
            })
        else:
            return False

    terms, md = _f(facets, "institute", c.md, "institute")
    if terms and not md:
        return False
    elif md:
        md_split = md.split(";", 1)
        if len(md_split)>0 and md_split[0]:
            md = md_split[0].strip()
            if not terms or md in terms:
                TO_UPD["institute"].update({
                    md: c.catalog_id,
                    "sk": md,
                })
            else:
                return False

    terms, md = _f(facets, "director", c.md, "institute")
    if terms and not md:
        return False
    elif md:
        md_split = md.split(";")
        if len(md_split) == 3 and md_split[2]:
            d = md_split[2].strip()
            flag = False
            for d in d.split("|"):
                d = d.strip()
                if not terms or d in terms:
                    flag = True
                    TO_UPD["director"].update({
                        d: c.catalog_id,
                        "sk": TO_UPD["director"].get("sk") + d
                    })
            if not flag:
                return False

    #put search keys in md: _(a|y|...)
    for k in TO_UPD.keys():
        c.md.update({("_" + k[0]): TO_UPD[k].pop("sk")})

    _update_entries(facets, TO_UPD)

    return True


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
        for c in self.exclude(rm__isnull=False).order_by("-modified").all()[start:start + limit]:
            # add landing page link
            if c.is_archived == 1 or DoiRepo.objects.get_valid_doi_repos(c.repo_id):
                c.md["landing_page_url"] = "%s/landing-page/libs/%s/" % (SERVICE_URL, c.repo_id)
            c.md.update(
                catalog_id=c.catalog_id,
                repo_id=c.repo_id,
                is_archived=c.is_archived,
            )
            mds.append(c.md)
        return mds

    def get_mds_react(self, search_term=None, scope=None, facets=None, start=0, limit=25):
        """
        Get catalog entries, apply search_term, facets, orders and offset
        """

        def _search_term_in_md(st, md):
            """
            True if at least one md contains search_term
            """
            st = st.lower()
            for k in ("title", "description", "year", "institute", "owner", "owner_name"):
                m = md.get(k)
                if m and st in m.lower():
                    return True
            m = md.get("authors")
            if m:
                for a in m:
                    m = a.get("name")
                    if m and st in m.lower():
                        return True
                    m = a.get("affs")
                    if m and st in "".join(m).lower():
                        return True
            return False


        SCOPE = (" AND c.catalog_id IN ('%s')" % "','".join(str(x) for x in scope)) if scope else ""
        RAW = f"""
            SELECT *,
                IF(c.is_archived = 1 OR EXISTS(SELECT 1 FROM doi_repos WHERE doi_repos.repo_id = c.repo_id AND doi_repos.rm is NULL), 
                CONCAT('{SERVICE_URL}/landing-page/libs/', c.repo_id, '/'), NULL) AS lpu
            FROM
                `keeper_catalog` AS c,
                `cdc_repos` AS cdc
            WHERE
                c.rm is NULL
                AND cdc.repo_id=c.repo_id
            {SCOPE} 
            ORDER by c.modified DESC
            """

        # cat_entries = self.raw(RAW)
        cat_entries = self.raw(RAW)

        # q = self.exclude(rm__isnull=False).order_by('-modified')
        # if scope:
        #     q = q.filter(catalog_id__in=scope)
        #
        # cat_entries = q.all()

        if not cat_entries:
            return {"items": [], "total": 0}

        mds = []

        # always recalc termEntries
        for f in facets.values():
            f["termEntries"] = {}

        for c in cat_entries:

            if search_term and not _search_term_in_md(search_term, c.md):
                continue

            if not _update_facets(facets, c):
                continue

            #add landing page link
            if c.lpu:
                c.md.update(landing_page_url=c.lpu)
            c.md.update(
                catalog_id=c.catalog_id,
                repo_id=c.repo_id,
                is_archived=c.is_archived,
            )
            mds.append(c.md)

        # complex sorting in python:
        # https://docs.python.org/3/howto/sorting.html#sort-stability-and-complex-sorts
        mds = _apply_sorts(mds, facets)

        # clean up sort indexes
        for md in mds:
            for k in [kk for kk in md.keys() if kk.startswith("_")]:
                md.pop(k)

        # # recalc termsChecked by termEntries
        # for f in facets.values():
        #     # get termsChecked which are in recalculated termEntries
        #     f["termsChecked"] = [tc for tc in f.get("termsChecked") if tc in f.get("termEntries").keys()]

        return {"items": mds[start:start + limit], "scope": [md.get("catalog_id") for md in mds], "facets": facets}

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
                    "EXISTS (SELECT repo_id FROM doi_repos WHERE doi_repos.repo_id=keeper_catalog.repo_id AND doi_repos.rm is NULL) OR keeper_catalog.is_archived=1 OR EXISTS (SELECT repo_id FROM bloxberg_certificate WHERE bloxberg_certificate.repo_id=keeper_catalog.repo_id)"
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

    def add_bloxberg_certificate(self, transaction_id, content_type, content_name, repo_id, path, commit_id, created_time, owner, checksum, md, md_json, status):
        """
        Add to DB a new Bloxberg certificate, modify currently is not needed
        Returns Bloxberg certificate id and EVENT: db_create
        """
        b_certificate = BCertificate(transaction_id=transaction_id, content_type=content_type, content_name=content_name, repo_id=repo_id, path=path, commit_id=commit_id, created=created_time, owner=owner, checksum=checksum, md=md, md_json=md_json, status=status)
        b_certificate.save()
        return b_certificate.obj_id

    def get_latest_snapshot_certificate(self, repo_id, commit_id):
        return super(BCertificateManager, self).filter(repo_id=repo_id, path= '/', commit_id=commit_id).order_by('-created').first()

    def get_bloxberg_certificates_by_owner_by_repo_id(self, owner, repo_id):
        return super(BCertificateManager, self).exclude(content_type='child').filter(owner=owner, repo_id=repo_id).order_by('-created')

    def get_presentable_certificate(self, transaction_id, checksum):
        return super(BCertificateManager, self).exclude(content_type='child').filter(transaction_id=transaction_id, checksum=checksum).first()

    def get_children_bloxberg_certificates(self, transaction_id, repo_id):
        return super(BCertificateManager, self).filter(transaction_id=transaction_id, repo_id=repo_id, content_type='child')

    def get_bloxberg_certificate(self, transaction_id, checksum, path):
        return super(BCertificateManager, self).filter(transaction_id=transaction_id, checksum=checksum, path=path).first()

    def get_semi_bloxberg_certificate(self, transaction_id, checksum):
        return super(BCertificateManager, self).exclude(pdf__isnull=False).filter(transaction_id=transaction_id, checksum=checksum).first()

class BCertificate(models.Model):
    """ Bloxberg Certificate model """

    class Meta:
        db_table = 'bloxberg_certificate'

    transaction_id = models.CharField(max_length=255, null=False)
    content_type = models.CharField(max_length=16, null=False)
    content_name = models.CharField(max_length=255, null=False)
    repo_id = models.CharField(max_length=37, null=False)
    commit_id = models.CharField(max_length=41, null=False)
    path = models.TextField(null=False)
    obj_id = models.AutoField(primary_key=True)
    created = models.DateTimeField()
    owner = models.CharField(max_length=255, null=False)
    checksum = models.CharField(max_length=64, null=False)
    md = models.TextField(null=False)
    md_json = models.TextField(null=False)
    pdf = models.TextField(default=None) # null=True
    status = models.CharField(max_length=30, null=False)
    error_msg = models.TextField(default=None)
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
        return super(DoiRepoManager, self).filter(repo_id=repo_id).order_by('-created')


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
