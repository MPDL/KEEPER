# -*- coding: utf-8 -*-

import logging
import re
import urllib.request, urllib.error, urllib.parse
import json
import tempfile
from datetime import datetime

from django.core.cache import cache

from seahub.invitations.models import Invitation
from seahub.profile.models import Profile

from thirdpart.seafobj import fs_mgr, commit_mgr
from seaserv import seafile_api, get_repo
from seahub.settings import KEEPER_MPG_DOMAINS_URL, KEEPER_MPG_IP_LIST_URL, ARCHIVE_METADATA_TARGET, SERVER_EMAIL, DEBUG

from keeper.common import parse_markdown, get_repo_root_dir

from netaddr import IPAddress, IPSet

logger = logging.getLogger(__name__)

# List from http://colab.mpdl.mpg.de/mediawiki/Max_Planck_email_domains
# Format: Institutsname<Tab>Ort<Tab>eMail domain<Tab>Kommentar
EMAIL_DOMAIN_LIST = '''Bibliotheca Hertziana - Max-Planck-Institut für Kunstgeschichte	Rom	biblhertz.it
Deutsches Klimarechenzentrum	Hamburg	dkrz.de
Ernst Strüngmann Institute (ESI) for Neuroscience in Cooperation with Max-Planck-Society	Frankfurt am Main	esi-frankfurt.de	nicht Teil des MPG e.V. (RUFSI)
Forschungszentrum caesar (center of advanced european studies and research)	Bonn	caesar.de	nicht Teil des MPG e.V. (RUFSI)
Friedrich-Miescher-Laboratorium für biologische Arbeitsgruppen in der Max-Planck-Gesellschaft	Tübingen	tuebingen.mpg.de
Fritz-Haber-Institut der Max-Planck-Gesellschaft	Berlin	fhi-berlin.mpg.de
Generalverwaltung	München	gv.mpg.de
GWD Göttingen	Göttingen	gwdg.de
Halbleiterlabor der Max-Planck-Gesellschaft	München	hll.mpg.de
Haus der Astronomie	Heidelberg	hda-hd.de
Kunsthistorisches Institut in Florenz - Max-Planck-Institut	Florenz	khi.fi.it
Max Planck Computing and Data Facility	Garching	rzg.mpg.de
Max Planck Digital Library	München	mpdl.mpg.de
Max Planck Florida Institute for Neuroscience	FL 33458, USA	maxplanckflorida.org	nicht Teil des MPG e.V. (RUFSI)
Max Planck Florida Institute for Neuroscience	FL 33458, USA	mpfi.org	nicht Teil des MPG e.V. (RUFSI)
Max Planck Foundation for International Peace and the Rule of Law		mpfpr.de
Max Planck Institute Luxembourg for International, European and Regulatory Procedural Law	Luxemburg	mpi.lu	nicht Teil des MPG e.V. (RUFSI)
Max-Planck-Institut für Astronomie	Heidelberg	mpia.de
Max-Planck-Institut für Astrophysik	Garching	mpa-garching.mpg.de
Max-Planck-Institut für ausländisches öffentliches Recht und Völkerrecht	Heidelberg	mpil.de
Max-Planck-Institut für ausländisches und internationales Privatrecht	Hamburg	mpipriv.de
Max-Planck-Institut für ausländisches und internationales Strafrecht	Freiburg	mpicc.de
Max-Planck-Institut für Bildungsforschung	Berlin	mpib-berlin.mpg.de
Max-Planck-Institut für Biochemie	Martinsried	biochem.mpg.de
Max-Planck-Institut für Biogeochemie	Jena	bgc-jena.mpg.de
Max-Planck-Institut für Biologie des Alterns	Köln	age.mpg.de
Max-Planck-Institut für biologische Kybernetik	Tübingen	tuebingen.mpg.de
Max-Planck-Institut für Biophysik	Frankfurt am Main	mpibp-frankfurt.mpg.de
Max-Planck-Institut für Biophysik	Frankfurt am Main	biophys.mpg.de
Max-Planck-Institut für biophysikalische Chemie	Göttingen	mpibpc.mpg.de
Max-Planck-Institut für Chemie	Mainz	mpic.de
Max-Planck-Institut für chemische Energiekonversion	Mülheim an der Ruhr	cec.mpg.de
Max-Planck-Institut für chemische Ökologie	Jena	ice.mpg.de
Max-Planck-Institut für Chemische Physik fester Stoffe	Dresden	cpfs.mpg.de
Max-Planck-Institut für demografische Forschung	Rostock	demogr.mpg.de
Max-Planck-Institut für die Physik des Lichts	Erlangen	mpl.mpg.de
Max-Planck-Institut für Dynamik komplexer technischer Systeme	Magdeburg	mpi-magdeburg.mpg.de
Max-Planck-Institut für Dynamik und Selbstorganisation	Göttingen	ds.mpg.de
Max-Planck-Institut für Eisenforschung GmbH	Düsseldorf	mpie.de
Max-Planck-Institut für empirische Ästhetik	Frankfurt am Main	aesthetics.mpg.de
Max-Planck-Institut für Entwicklungsbiologie	Tübingen	tuebingen.mpg.de
Max-Planck-Institut für Entwicklungsbiologie	Tübingen	tue.mpg.de
Max-Planck-Institut für ethnologische Forschung	Halle (Saale)	eth.mpg.de
Max-Planck-Institut für europäische Rechtsgeschichte	Frankfurt/Main	mpier.uni-frankfurt.de
Max-Planck-Institut für europäische Rechtsgeschichte	Frankfurt/Main	rg.mpg.de
Max-Planck-Institut für evolutionäre Anthropologie	Leipzig	eva.mpg.de
Max-Planck-Institut für Evolutionsbiologie	Plön	evolbio.mpg.de
Max-Planck-Institut für experimentelle Medizin	Göttingen	em.mpg.de
Max-Planck-Institut für extraterrestrische Physik	Garching	mpe.mpg.de
Max-Planck-Institut für Festkörperforschung	Stuttgart	fkf.mpg.de
Max-Planck-Institut für Gesellschaftsforschung	Köln	mpifg.de
Max-Planck-Institut für Gravitationsphysik	Potsdam-Golm	aei.mpg.de
Max-Planck-Institut für Gravitationsphysik, Teilinstitut Hannover	Hannover	aei.mpg.de
Max-Planck-Institut für Herz- und Lungenforschung	Bad Nauheim	kerckhoff.mpg.de
Max-Planck-Institut für Herz- und Lungenforschung	Bad Nauheim	mpi-bn.mpg.de
Max-Planck-Institut für Hirnforschung	Frankfurt am Main	mpih-frankfurt.mpg.de
Max-Planck-Institut für Hirnforschung	Frankfurt am Main	brain.mpg.de
Max-Planck-Institut für Immunbiologie	Freiburg	immunbio.mpg.de
Max-Planck-Institut für Immunbiologie und Epigenetik	Freiburg	ie-freiburg.mpg.de
Max-Planck-Institut für Infektionsbiologie	Berlin	mpiib-berlin.mpg.de
Max-Planck-Institut für Informatik	Saarbrücken	mpi-inf.mpg.de
Max-Planck-Institut für Informatik	Saarbrücken	mpi-klsb.mpg.de
Max-Planck-Institut für Innovation und Wettbewerb	München	ip.mpg.de
Max-Planck-Institut für Intelligente Systeme, Standort Stuttgart	Stuttgart	is.mpg.de
Max-Planck-Institut für Intelligente Systeme, Standort Tübingen	Tübingen	tuebingen.mpg.de
Max-Planck-Institut für Kernphysik	Heidelberg	mpi-hd.mpg.de
Max-Planck-Institut für Kognitions- und Neurowissenschaften	Leipzig	cbs.mpg.de
Max-Planck-Institut für Kohlenforschung	Mülheim an der Ruhr	kofo.mpg.de
Max-Planck-Institut für Kolloid- und Grenzflächenforschung	Potsdam-Golm	mpikg-golm.mpg.de
Max-Planck-Institut für Kolloid- und Grenzflächenforschung	Potsdam-Golm	mpikg.mpg.de
Max-Planck-Institut für Limnologie	Plön	mpil-ploen.mpg.de	veraltet: Nachfolgeinstitut = MPI Evolutionsbiologie
Max-Planck-Institut für marine Mikrobiologie	Bremen	mpi-bremen.de
Max-Planck-Institut für Mathematik	Bonn	mpim-bonn.mpg.de
Max-Planck-Institut für Mathematik in den Naturwissenschaften	Leipzig	mis.mpg.de
Max-Planck-Institut für medizinische Forschung	Heidelberg	mpimf-heidelberg.mpg.de
Max-Planck-Institut für medizinische Forschung	Heidelberg	mr.mpg.de
Max-Planck-Institut für Menschheitsgeschichte	Jena	shh.mpg.de	Vorgängerinstitut = MPI Ökonomik
Max-Planck-Institut für Meteorologie	Hamburg	zmaw.de
Max-Planck-Institut für Meteorologie	Hamburg	mpimet.mpg.de
Max-Planck-Institut für Mikrostrukturphysik	Halle/Saale	mpi-halle.mpg.de
Max-Planck-Institut für Mikrostrukturphysik	Halle/Saale	mpi-halle.de
Max-Planck-Institut für molekulare Biomedizin	Münster	mpi-muenster.mpg.de
Max-Planck-Institut für molekulare Genetik	Berlin	molgen.mpg.de
Max-Planck-Institut für molekulare Pflanzenphysiologie	Potsdam-Golm	mpimp-golm.mpg.de
Max-Planck-Institut für molekulare Physiologie	Dortmund	cgc.mpg.de
Max-Planck-Institut für molekulare Physiologie	Dortmund	mpi-dortmund.mpg.de
Max-Planck-Institut für molekulare Zellbiologie und Genetik	Dresden	mpi-cbg.de
Max-Planck-Institut für Neurobiologie	Martinsried	neuro.mpg.de
Max-Planck-Institut für neurologische Forschung	Köln	nf.mpg.de	veraltet: Nachfolgeinstitut = MPI Stoffwechselforschung
Max-Planck-Institut für Ökonomik	Jena	econ.mpg.de	veraltet: Nachfolgeinstitut = MPI Menschheitsgeschichte
Max-Planck-Institut für Ornithologie	Seewiesen	orn.mpg.de
Max-Planck-Institut für Ornithologie, Teilinstitut Radolfzell	Radolfzell	orn.mpg.de
Max-Planck-Institut für Pflanzenzüchtungsforschung	Köln	mpipz.mpg.de
Max-Planck-Institut für Pflanzenzüchtungsforschung	Köln	mpiz-koeln.mpg.de
Max-Planck-Institut für Physik	München	mppmu.mpg.de
Max-Planck-Institut für Physik	München	mpp.mpg.de
Max-Planck-Institut für Physik komplexer Systeme	Dresden	pks.mpg.de
Max-Planck-Institut für Physik komplexer Systeme	Dresden	mpipks-dresden.mpg.de
Max-Planck-Institut für Plasmaphysik	Garching	ipp.mpg.de
Max-Planck-Institut für Plasmaphysik, Teilinstitut Greifswald	Greifswald	ipp.mpg.de
Max-Planck-Institut für Polymerforschung	Mainz	mpip-mainz.mpg.de
Max-Planck-Institut für Psychiatrie	München	mpipsykl.mpg.de
Max-Planck-Institut für Psychiatrie	München	psych.mpg.de
Max-Planck-Institut für Psycholinguistik	Nijmegen	mpi.nl
Max-Planck-Institut für Quantenoptik	Garching	mpq.mpg.de
Max-Planck-Institut für Radioastronomie	Bonn	mpifr.de
Max-Planck-Institut für Radioastronomie	Bonn	mpifr-bonn.mpg.de
Max-Planck-Institut für Softwaresysteme, Standort Kaiserslautern	Kaiserslautern	mpi-sws.org
Max-Planck-Institut für Softwaresysteme, Standort Kaiserslautern	Kaiserslautern	mpi-klsb.mpg.de
Max-Planck-Institut für Softwaresysteme, Standort Saarbrücken	Saarbrücken	mpi-klsb.mpg.de
Max-Planck-Institut für Sonnensystemforschung	Katlenburg-Lindau	mps.mpg.de
Max-Planck-Institut für Sozialrecht und Sozialpolitik	München	mpisoc.mpg.de
Max-Planck-Institut für Steuerrecht und Öffentliche Finanzen	München	tax.mpg.de
Max-Planck-Institut für Stoffwechselforschung	Köln	sf.mpg.de	Vorgängerinstitut = MPI neurologische Forschung
Max-Planck-Institut für Struktur und Dynamik der Materie	Hamburg	mpsd.mpg.de
Max-Planck-Institut für terrestrische Mikrobiologie	Marburg	mpi-marburg.mpg.de
Max-Planck-Institut für Wissenschaftsgeschichte	Berlin	mpiwg-berlin.mpg.de
Max-Planck-Institut zur Erforschung multireligiöser und multiethnischer Gesellschaften	Göttingen	mmg.mpg.de
Max-Planck-Institut zur Erforschung von Gemeinschaftsgütern	Bonn	coll.mpg.de
Max-Planck-Institut für VerhaltensbiologieKonstanzab.mpg.de	Konstanz	ab.mpg.de
Max-Planck-Forschungsstelle für die Wissenschaft der Pathogene	Berlin	mpusp.mpg.de
Mülheimer Institute	Mülheim an der Ruhr	mpi-muelheim.mpg.de	Nachfolgeinstitute: MPI chemische Energiekonversion + MPI Kohlenforschung
Stuttgarter Institute	Stuttgart	mpis.mpg.de	Nachfolgeinstitute: MPI Intelligente Systeme + MPI Festkörperforschung
'''
EMAIL_LIST_TIMESTAMP = 'Thu Aug 26 11:46:00 2019'
ACCOUNT_ACTIVATION_PATTERN = '^.*@(' + "|".join(
    map((lambda s: re.escape(s.split('\t')[2])), EMAIL_DOMAIN_LIST.splitlines())
) + ')$'
COMPILED_PATTERN = re.compile(ACCOUNT_ACTIVATION_PATTERN)

MPI_NAME_LIST_DEFAULT = [
    "Bibliotheca Hertziana - Max-Planck-Institut für Kunstgeschichte",
    "Deutsches Klimarechenzentrum (DKRZ)",
    "Friedrich-Miescher-Laboratorium für biologische Arbeitsgruppen in der Max-Planck-Gesellschaft",
    "Fritz-Haber-Institut der Max-Planck-Gesellschaft",
    "Generalverwaltung der Max-Planck-Gesellschaft",
    "Gesellschaft für wissenschaftliche Datenverarbeitung Göttingen",
    "Kunsthistorisches Institut in Florenz - Max-Planck-Institut",
    "Max Planck Digital Library",
    "Max-Planck-Forschungsstelle für die Wissenschaft der Pathogene",
    "Max Planck Innovation",
    "Max-Planck-Institut für Astronomie",
    "Max-Planck-Institut für Astrophysik",
    "Max-Planck-Institut für ausländisches öffentliches Recht und Völkerrecht",
    "Max-Planck-Institut für ausländisches und internationales Privatrecht",
    "Max-Planck-Institut für Bildungsforschung",
    "Max-Planck-Institut für Biochemie",
    "Max-Planck-Institut für Biogeochemie",
    "Max-Planck-Institut für Biologie des Alterns",
    "Max-Planck-Institut für biologische Kybernetik",
    "Max-Planck-Institut für Biophysik",
    "Max-Planck-Institut für biophysikalische Chemie (Karl-Friedrich-Bonhoeffer-Institut)",
    "Max-Planck-Institut für Chemie (Otto-Hahn-Institut)",
    "Max-Planck-Institut für chemische Energiekonversion",
    "Max-Planck-Institut für chemische Ökologie",
    "Max-Planck-Institut für Chemische Physik fester Stoffe",
    "Max-Planck-Institut für Cybersicherheit und Schutz der Privatsphäre",
    "Max-Planck-Institut für demografische Forschung",
    "Max-Planck-Institut für die Physik des Lichts",
    "Max-Planck-Institut für Dynamik komplexer technischer Systeme",
    "Max-Planck-Institut für Dynamik und Selbstorganisation",
    "Max-Planck-Institut für Eisenforschung",
    "Max-Planck-Institut für empirische Ästhetik",
    "Max-Planck-Institut für Entwicklungsbiologie",
    "Max-Planck-Institut für ethnologische Forschung",
    "Max-Planck-Institut für europäische Rechtsgeschichte",
    "Max-Planck-Institut für evolutionäre Anthropologie",
    "Max-Planck-Institut für Evolutionsbiologie",
    "Max-Planck-Institut für experimentelle Medizin",
    "Max-Planck-Institut für extraterrestrische Physik",
    "Max-Planck-Institut für Festkörperforschung",
    "Max-Planck-Institut für Gesellschaftsforschung",
    "Max-Planck-Institut für Gravitationsphysik (Albert-Einstein-Institut)",
    "Max-Planck-Institut für Herz- und Lungenforschung (W.G. Kerckhoff-Institut)",
    "Max-Planck-Institut für Hirnforschung und Max-Planck-Forschungsstelle für Neurogenetik",
    "Max-Planck-Institut für Immunbiologie und Epigenetik",
    "Max-Planck-Institut für Infektionsbiologie",
    "Max-Planck-Institut für Informatik",
    "Max-Planck-Institut für Innovation und Max-Planck-Institut für Steuerrecht",
    "Max-Planck-Institut für Intelligente Systeme",
    "Max-Planck-Institut für Kernphysik",
    "Max-Planck-Institut für Kognitions- und Neurowissenschaften",
    "Max-Planck-Institut für Kohlenforschung",
    "Max-Planck-Institut für Kolloid- und Grenzflächenforschung",
    "Max-Planck-Institut für marine Mikrobiologie",
    "Max-Planck-Institut für Mathematik",
    "Max-Planck-Institut für Mathematik in den Naturwissenschaften",
    "Max-Planck-Institut für medizinische Forschung",
    "Max-Planck-Institut für Menschheitsgeschichte",
    "Max-Planck-Institut für Meteorologie",
    "Max-Planck-Institut für Mikrostrukturphysik",
    "Max-Planck-Institut für molekulare Biomedizin",
    "Max-Planck-Institut für molekulare Genetik",
    "Max-Planck-Institut für molekulare Pflanzenphysiologie",
    "Max-Planck-Institut für molekulare Physiologie",
    "Max-Planck-Institut für molekulare Zellbiologie und Genetik",
    "Max-Planck-Institut für Neurobiologie",
    "Max-Planck-Institut für Ornithologie",
    "Max-Planck-Institut für Pflanzenzüchtungsforschung",
    "Max-Planck-Institut für Physik komplexer Systeme",
    "Max-Planck-Institut für Physik (Werner-Heisenberg-Institut)",
    "Max-Planck-Institut für Plasmaphysik",
    "Max-Planck-Institut für Polymerforschung",
    "Max-Planck-Institut für Psychiatrie",
    "Max-Planck-Institut für Psycholinguistik",
    "Max-Planck-Institut für Quantenoptik",
    "Max-Planck-Institut für Radioastronomie",
    "Max-Planck-Institut für Softwaresysteme",
    "Max-Planck-Institut für Sonnensystemforschung",
    "Max-Planck-Institut für Sozialrecht und Sozialpolitik",
    "Max-Planck-Institut für Stoffwechselforschung",
    "Max-Planck-Institut für Struktur und Dynamik der Materie",
    "Max-Planck-Institut für terrestrische Mikrobiologie",
    "Max-Planck Institut für Verhaltensbiologie",
    "Max-Planck-Institut für Wissenschaftsgeschichte",
    "Max-Planck-Institut zur Erforschung multireligiöser und multiethnischer Gesellschaften",
    "Max-Planck-Institut zur Erforschung von Gemeinschaftsgütern",
    "Max-Planck-Institut zur Erforschung von Kriminalität, Sicherheit und Recht",
]

# time to live of the mpg IP set: day
KEEPER_DOMAINS_TTL = 60 * 60 * 24

KEEPER_DOMAINS_KEY = 'KEEPER_DOMAINS'

KEEPER_DOMAINS_LAST_FETCHED_KEY = 'KEEPER_DOMAINS_LAST_FETCHED'

KEEPER_DOMAINS_TS_KEY = 'KEEPER_DOMAINS_TS'

TS_FORMAT = "%a %b %d %H:%M:%S %Y"

# time to live of the mpg IP set: day
IP_SET_TTL = 60 * 60 * 24


def has_to_be_updated(domains_dict):
    """
    Check rena domain list status for cache update
    """

    # False if domain list is empty
    if not domains_dict['details']:
        return False

    # False if mpdl domain is not in the list
    if not 'mpdl.mpg.de' in domains_dict['details']:
        return False

    # False if json ts is older or same
    d_cache = datetime.strptime(cache.get(KEEPER_DOMAINS_TS_KEY), TS_FORMAT)
    d_json =  datetime.strptime(domains_dict['timestamp'], TS_FORMAT)
    if d_json <= d_cache:
        return False

    return True

def get_domain_list_from_cache():
    """
    Get domain list from cache. If cache is empty, get the list from hardcoded
    starter and put it into the cache.
    """
    # get old domains from cache by default
    logger.info("Get domains from old cache by default...")
    domains = cache.get(KEEPER_DOMAINS_KEY)
    # init case: KEEPER_DOMAINS_KEY does not exist, populate from hardcoded
    # globvar
    if domains is None:
        logger.info("MPG DOMAIN LIST IS EMPTY, INITIALIZE FROM HARDCODED STARTER")
        domains = list(map((lambda s: s.split('\t')[2]), EMAIL_DOMAIN_LIST.splitlines()))
        cache.set(KEEPER_DOMAINS_KEY, domains, None)
        cache.set(KEEPER_DOMAINS_TS_KEY, EMAIL_LIST_TIMESTAMP, None)

    return domains


def get_domain_list():
    """
    Get MPG domain list ranges from cache or from rena service if cache is expired.
    Source of the list is http://colab.mpdl.mpg.de/mediawiki/Max_Planck_email_domains
    """

    domains = get_domain_list_from_cache()

    if cache.get(KEEPER_DOMAINS_LAST_FETCHED_KEY) is None:
        try:
            # get json from server
            response = urllib.request.urlopen(KEEPER_MPG_DOMAINS_URL)
            json_str = response.read()
            # parse json
            json_dict = json.loads(json_str)
            if has_to_be_updated(json_dict):
                domains = json_dict['details']
                logger.info("Domain list has been updated, refresh cache...")
                cache.set(KEEPER_DOMAINS_KEY, domains, None)
                cache.set(KEEPER_DOMAINS_TS_KEY, json_dict['timestamp'], None)
        except Exception as e:
            logger.info(
                "Cannot get/parse new MPG domian list: " +
                ": ".join(
                    str(i) for i in e))
        finally:
            # set expiration time for next retrieval from rena
            cache.set(
                KEEPER_DOMAINS_LAST_FETCHED_KEY,
                str(datetime.utcnow()),
                KEEPER_DOMAINS_TTL)

    return domains

def is_in_mpg_domain_list(email):
    """
    True if email is in MPG domain list
    """
    domain = email.partition('@')[2]
    if not domain:
        logger.error("Cannot parse email: {}".format(email))
        return False
    return domain in get_domain_list()


def get_mpg_ips_and_institutes():
    """
    Get MPG IP ranges from cache or from rena service if cache is expired
    """
    if cache.get('MPG_IP_LIST_LAST_FETCHED') is None:
        logger.info("Put IPs and MPI list to cache...")
        try:
            # get json from server
            response = urllib.request.urlopen(KEEPER_MPG_IP_LIST_URL)
            json_str = response.read()
            # parse json
            json_dict = json.loads(json_str)
            # get ip ranges
            ip_ranges = [(list(ipr.items()))[0][0] for ipr in json_dict['details']]
            ip_set = IPSet(ip_ranges)
            cache.set('KEEPER_CATALOG_MPG_IP_SET', ip_set, None)
            # get MPI names 
            institutes = [(list(ipr.items()))[0][1]["inst_name_de"] for ipr in json_dict['details']]
            #remove duplicates
            institutes = list(dict.fromkeys(institutes))
            cache.set('KEEPER_MPI_NAMES', institutes, None)
            cache.set(
                'MPG_IP_LIST_LAST_FETCHED',
                json_dict['timestamp'],
                IP_SET_TTL)
        except Exception as e:
            logger.info("Cannot get/parse MPG IPs: %s", e)
            logger.info("Get IPs from old cache")
            ip_set = cache.get('KEEPER_CATALOG_MPG_IP_SET')
            institutes = cache.get('KEEPER_MPI_NAMES')
    else:
        logger.info("Get ips and MPI names from cache...")
        ip_set = cache.get('KEEPER_CATALOG_MPG_IP_SET')
        institutes = cache.get('KEEPER_MPI_NAMES')
    return ip_set, institutes

def is_in_mpg_ip_range(ip):
    # only for tests!
    # return True
    if DEBUG:
        return True
    else:
        ip_set, _ = get_mpg_ips_and_institutes()
        return IPAddress(ip) in ip_set

def account_can_be_auto_activated(email):
    """
    True if account can be auto activated via activation token
    """
    # can if the uname in mpg domain
    yes_you_can =  is_in_mpg_domain_list(email)
    if not yes_you_can:
        try:
            invitations = Invitation.objects.filter(accepter=email)
            # can if at least one inviter in mpg domain
            for inv in invitations:
                if is_in_mpg_domain_list(inv.inviter):
                    return True
        except Exception as e:
            logger.error("Cannot lookup inviter: {}".format(e))

    return yes_you_can

def user_can_invite(email):
    """
    User can invite if he/she is in the mpg domain
    """
    return is_in_mpg_domain_list(email)


def get_user_name(user):
    """Get user name"""
    # default name is user id
    name = user
    try:
        p = Profile.objects.get_profile_by_user(user)
        if p is not None and p.nickname:
            name = p.nickname
    except Exception as e:
        logger.error(str(e))
    return name

# ARCHIVE METADATA
def validate_author(txt):
    """Author/Affiliations checking, format:
    Lastname1, Firstname1; Affiliation11, Affiliation12, ...
    Lastname2, Firstname2; Affiliation21, Affiliation22, ..
    ...

    returns None if valid, error message otherwise
    """

    msg = None 

    if txt:
        pattern = re.compile("^(\s*[\w-]+)+,(\s*[\w.-]+)+(;\s*\S+\s*)*", re.UNICODE)
        for line in txt.splitlines():
            if not re.match(pattern, line):
                msg = 'Wrong Author/Affiliation string: ' + line
    else:
        msg = 'Authors are empty'
    return msg


def validate_authors(authors):
    """Validate author structured list
    :returns: None if valid, error message otherwise  
    """
    msg = None 

    if authors and len(authors)>=1:
        idx = 1 
        for a in authors:
            # AUTHOR
            fn = a.get('firstName')
            ln = a.get('lastName')
            if not(fn and fn.strip()) and not(ln and ln.strip()):
                return 'Empty first and last names of author #%s.' % idx if idx>1 else 'Empty first and last author names.'

            #AFFILIATIONS check: TODO
            if a.get('affs'):
                pass

            idx += 1
    else:
        msg = 'Empty author list.'

def validate_directors(directors):
    """Validate directors structured list
    :returns: None if valid, error message otherwise  
    """
    msg = None 

    if directors and len(directors)>=1:
        idx = 1 
        for a in directors:
            fn = a.get('firstName')
            ln = a.get('lastName')
            if not(fn and fn.strip()) and not(ln and ln.strip()):
                return 'Empty first and last names of director #%s.' % idx if idx >1 else 'Empty first and last director names.'
            idx += 1
    else:
        msg = 'Empty director list.' 


def validate_institute(txt):
    """Institute checking, format:
    InstituionName; Department; Director(or PI)Name, Vorname|Abbr.

    returns None if valid, error message otherwise
    """

    msg = None
    
    t = txt
    t = t and t.strip()

    if not t: 
        return 'Empty institution string'

    # normalize 
    t = re.sub(r'\s+', ' ', t)
    t = re.sub(r'(\s*([;,])\s*)+', r'\g<2>', t)
    t = re.sub(r'(\s*\.\s*)+', '.', t)

    # print('txt: %s -- normalized: %s' % (t, txt))
    ins = t.strip(';').split(';')
    # print('len(ins):%s' % len(ins))

    if len(ins) >= 1:
        # Institute name
        if ins[0]:
            pattern = re.compile(r'^(\s*[\w-]+\s*)+$', re.UNICODE)
            if not re.match(pattern, ins[0]):
                msg = 'Wrong institution name'
        else:
            msg = 'Institution name is empty'

        # Department name
        if len(ins) >= 2:
            if ins[1]: 
                pattern = re.compile(r'^(\s*[\w-]+\s*)+$', re.UNICODE)
                if not re.match(pattern, ins[1]):
                    msg = 'Wrong department name'
            else:
                msg = 'Department name is empty'

            # Director name
            if len(ins) >= 3:
                if ins[2]:
                    pattern = re.compile(r'^\s*([\w-]+\s*)+?([\s,]+?([\w.-]+\s*)+?[\s;]*?)?$', re.UNICODE)
                    for d in ins[2].split('|'):
                        d_strip = d.strip()
                        if not re.match(pattern, d_strip):
                            msg = 'Wrong director or PI name: ' + d_strip
                            break
                else:
                    msg = 'Director or PI name is empty'
    else:
        msg = 'Empty institution string'

    if msg:
        msg += ': ' + txt

    return msg 

def validate_director(txt):
    """Institute checking, format:
    Director(or PI)Name, Vorname|Abbr.

    returns None if valid, error message otherwise
    """
    msg = None 
    if txt:                    #     Lastname       ,\s      Firstname or abbr     ;\s 
        # pattern = re.compile(r"^(\s* ([\w-]+\s*)+?  ([\s,]+? ([\w.-]+\s*)+? [\s;]*? )? )?$", re.UNICODE)
        pattern = re.compile(r"^\s*([\w-]+\s*)+?([\s,]+?([\w.-]+\s*)+?[\s;]*?)?$", re.UNICODE)
        if not re.match(pattern, txt):
            msg = 'Wrong director string: ' + txt
    else:
        msg = 'Institute is empty'
    return msg

def validate_year(txt):
    """Year checking

    returns None if valid, error message otherwise
    """
    msg = None
    format = "%Y"
    if txt:
        try:
            datetime.strptime(txt, format)
        except Exception as e:
            logger.error("exception: %s", e)
            msg = 'Wrong year: %s' % txt
    else:
        msg = 'Year is empty'
    return msg 

def validate_resource_type(txt):
    """resource_type checking, options:
    Libray, Project

    returns None if valid, error message otherwise
    """
    msg = None
    if txt:
        pattern = re.compile("^(Library|Project)$", re.UNICODE)
        if not re.match(pattern, txt):
            msg = 'Wrong Institution string: ' + txt
    else:
        msg = 'Empty Resource Type'
    return msg

def archive_metadata_form_validation(md):
    """
    Validate Archive Metadata

    returns dict with errors
    """
    # md_mandatory = ('title', 'authors', 'publisher', 'description',  'year', 'institute', 'resource-type')
    errors = {}

    if md:
        # 1. null/empty check 
        for k in ('title', 'publisher', 'description', 'year', 'institute', 'department', 'directors', 'resourceType'):
            v = md.get(k)
            logging.error("HERE!!!: k:%s,v:%r", k, v)
            if not(v) or (isinstance(v, str) and not(v.strip())):
                errors[k] = 'Empty mandatory field.'

        # 2. check content 
        for k in ('year', 'authors', 'directors'):
            val_func = globals().get('validate_' + k)
            if val_func and not(k in errors.keys()):
                v = val_func(md.get(k))
                if v: errors[k] = v

    return errors

ARCHIVE_METADATA_TARGET_HEADER = """\[](
//Please fill out the form at the end of this comment according to the following rules. We recommend to provide all //information in english.
//
//## Title 
//MANDATORY: Please enter the title of your research project
//
//## Author
//MANDATORY: Please enter the authors and affiliation of your research project e.g.
// Each line will be a new entry. Format is: Lastname, Firstname; Affiliation1 | Affiliation2 | ...
//
//## Publisher
// MANDATORY: Please enter the name of entity that holds, archives, publishes prints, distributes, releases, issues, or produces the resource
//
//## Description
// MANDATORY: Please enter the description of your research project
//
//## Year
// MANDATORY: Please enter year of project start
// 
// ## Institute
// MANDATORY: Please enter the enter the related Max Planck Institute for this research project
// Format is: Name; Department; Director<or PI>forschungsgruppenleiter, Lastname or Abbr.
//
// ## Resource Type
// MANDATORY: Please enter the resource type of the entity. Allowed values for this field: Library (default), Project
// 
// ## License
// OPTIONAL: Please enter the license
// 
)
"""

def save_archive_metadata(repo_id, md_dict):
    """
    Convert archive metadata dictionary into markdown format
    and put it into repo_id library
    """
    p = "## %s\n%s\n\n"
    md_markdown = ARCHIVE_METADATA_TARGET_HEADER 
    md_markdown += p % ('Title', md_dict.get('title', ''))

    # authors
    al = md_dict.get('authors', '') 
    a_res = []
    if al and type(al) is list:
        a_tmp = ""
        for a in al:
            # Name
            n_tmp = []
            ln = a.get('lastName', '').strip()
            ln and n_tmp.append(ln)
            fn = a.get('firstName', '').strip()
            fn and n_tmp.append(fn)
            a_tmp = ", ".join(n_tmp)

            # Affiliations
            affs = a.get('affs')
            affs_str = ''
            if affs:
                affs = [aff for aff in affs if aff and aff.strip()]
                if affs: 
                    affs_str = " | ".join(affs)

            a_res.append("; ".join(list(filter(None, [a_tmp, affs_str]))))
        
    md_markdown += p % ('Author', '\n'.join(a_res))
    md_markdown += p % ('Publisher', md_dict.get('publisher', ''))
    md_markdown += p % ('Description', md_dict.get('description', ''))
    md_markdown += p % ('Year', md_dict.get('year', ''))

    # institute
    dl = md_dict.get('directors', '')
    d_tmp = []
    if dl and type(dl) is list:
        for d in dl:
            n_tmp = []
            ln = d.get('lastName', '').strip()
            ln and n_tmp.append(ln)
            fn = d.get('firstName', '').strip()
            fn and n_tmp.append(fn)
            n_tmp and d_tmp.append(", ".join(n_tmp))

    md_markdown += p % ('Institute', "; ".join([ 
        md_dict.get('institute', ''),
        md_dict.get('department', ''),
        # TODO: mutiply directors revision!!!!
        " | ".join(d_tmp)
    ]))

    md_markdown += p % ('Resource Type', md_dict.get('resourceType', ''))
    md_markdown += p % ('License', md_dict.get('license', ''))
    md_markdown = md_markdown[:-2]

    try:
        with tempfile.NamedTemporaryFile() as fp:
            fp.write(md_markdown.encode())
            fp.flush()
            seafile_api.put_file(repo_id, fp.name, "/", ARCHIVE_METADATA_TARGET, SERVER_EMAIL, None)
    except Exception as e:
        logger.exception('Cannot put_file %s', ARCHIVE_METADATA_TARGET) 



def get_archive_metadata(repo_id):
    """
    Get ARCHIVE_METADATA_TARGET markdown file from library root, 
    parse and map it for the archive metadata form consume.
    """

    md = None
    dir = get_repo_root_dir(repo_id)
    # get latest version of the ARCHIVE_METADATA_TARGET
    file = dir.lookup(ARCHIVE_METADATA_TARGET)
    if file:
        content = file.get_content().decode()
        md = parse_markdown(content)

        for k in ('Title', 'Publisher', 'Description', 'Year', 'License'):
            v = md.get(k, '')
            md.update({k.lower(): v})
            md.pop(k, None)
        
        v = md.get('Resource Type', '')
        md.update(resourceType=v)
        md.pop('Resource Type', None)

        # Author
        author = md.get('Author')
        authors = [] 
        if author: 
            for a in author.splitlines():
                au = a.split(";")
                name, affs = au if len(au) == 2 else [a, None]
                # Name
                name = name.strip()
                name_split = name.split(",")
                ln, fn = [n.strip() for n in name_split] if len(name_split) == 2 else [name, ''] 
                # Affiliations
                if affs:
                    affs = affs.split("|")
                    affs = [aff.strip() for aff in affs]
                else: 
                    affs = ['']
                authors.append({'lastName': ln, 'firstName': fn, 'affs': affs})
          
        md.update(authors=authors)
        md.pop('Author', None)
                
        # Institute
        institute = md.get('Institute', '')
        department = ''
        directors = []
        if institute:
            name, department, directors_str = institute.split(";")
            if name:
                institute = name.strip()
            if department:
                department = department.strip()
            if directors_str:
                # TODO: define mutiply directors
                for d in directors_str.split("|"):
                    d_split = d.split(",")
                    ln, fn = [n.strip() for n in d_split] if len(d_split) == 2 else [d, '']
                    # Affiliations
                    directors.append({'lastName': ln, 'firstName': fn})
     
        md.update(institute=institute, department=department, directors=directors)
        md.pop('Institute', None)

    return md
    
# KEEPER ARCHIVING
from seahub.settings import KEEPER_ARCHIVING_ROOT, KEEPER_ARCHIVING_PORT, KEEPER_ARCHIVING_NODE
from urllib.parse import urljoin
import requests
from http import HTTPStatus

def do_request(params, end_point):
    url = urljoin(KEEPER_ARCHIVING_ROOT + ':' + KEEPER_ARCHIVING_PORT, end_point)
    resp = requests.get(url, params)
    return resp.json() if resp.status_code == HTTPStatus.OK \
        else {'status': 'ERROR', 'msg': resp.text}

def add_keeper_archiving_task(repo_id, owner):
    return do_request({'repo_id': repo_id, 'owner': owner}, '/add-task')

def query_keeper_archiving_status(repo_id, owner, version):
    return do_request({'repo_id': repo_id, 'owner': owner, 'version': version}, '/query-task-status')

def check_keeper_repo_archiving_status(repo_id, owner, action):
    return do_request({'repo_id': repo_id, 'owner': owner, 'action': action}, '/check-repo-archiving-status')
